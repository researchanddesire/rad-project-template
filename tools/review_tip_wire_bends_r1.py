"""Read saved Full05 wire reservation; bound fixed-polyline fillet feasibility.

No CAD source is recomputed/saved and no wire or routing geometry is selected.
This deliberately does not equate a corner sphere to a valid wire bend.
"""
from pathlib import Path
import ast
import hashlib
import json
import math
import sys

sys.path.insert(0, '/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as App
import Part

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'hardware/design/tip-wire-bend-r1-references'
NATIVE = ROOT / 'hardware/cad/prototype-r2/full-05/ButtplugPrototypeR2Full05.FCStd'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())


def main():
    manifest = read(OUT / 'input-manifest.json')
    inputs = {**manifest['source_files_sha256'],
              str(Path(__file__).relative_to(ROOT)): sha(Path(__file__)),
              str((OUT / 'input-manifest.json').relative_to(ROOT)): sha(OUT / 'input-manifest.json')}
    assert all(sha(ROOT / p) == h for p, h in inputs.items())
    baseline = read(ROOT / 'hardware/cad/prototype-r2/full05-route-review/route-review.json')
    report = read(ROOT / 'hardware/cad/prototype-r2/full-05/geometry-report.json')
    observation = read(OUT / 'manufacturer-observation.json')
    source_tree = ast.parse((ROOT / 'hardware/cad/prototype-r2/build.py').read_text())
    recipe = next(n for n in ast.walk(source_tree) if isinstance(n, ast.Call)
                  and isinstance(n.func, ast.Name) and n.func.id == 'route'
                  and n.args and isinstance(n.args[0], ast.Constant)
                  and n.args[0].value == 'TipMainHarnessCorridor')
    recipe_points = ast.literal_eval(recipe.args[1])
    recipe_radius = ast.literal_eval(recipe.args[2])
    doc = App.openDocument(str(NATIVE))
    role = doc.getObject('TipMainHarnessCorridor')
    # Match the frozen route review's exact opened-world Shape.copy recipe.
    shape = role.Shape.copy()
    world_hash = hashlib.sha256(shape.exportBrepToString().encode()).hexdigest()
    assert world_hash == baseline['source_world_checks'][role.Name]['world_BRep_sha256']
    assert shape.isValid() and abs(shape.Volume - report['parts'][role.Name]['volume_mm3']) < 1e-6
    leaves = {}
    def walk(obj):
        if not obj.OutList:
            leaves[obj.Name] = obj
        else:
            assert obj.TypeId == 'Part::Fuse'
            assert obj.Placement.isIdentity()
            for child in obj.OutList:
                walk(child)
    walk(role)
    assert len(leaves) == 19
    points = []
    primitives = []
    for i in range(10):
        obj = leaves[f'TipMainHarnessCorridor{i}']
        assert obj.TypeId == 'Part::Cylinder' and abs(obj.Radius.Value - recipe_radius) < 1e-12
        a = obj.Placement.multVec(App.Vector())
        b = obj.Placement.multVec(App.Vector(0, 0, obj.Height.Value))
        assert (a - App.Vector(*recipe_points[i])).Length < 1e-9
        assert (b - App.Vector(*recipe_points[i + 1])).Length < 1e-9
        if points:
            assert (a - points[-1]).Length < 1e-9
        else:
            points.append(a)
        points.append(b)
        primitives.append({'name': obj.Name, 'type': obj.TypeId,
                           'start_xyz_mm': list(a), 'end_xyz_mm': list(b),
                           'radius_mm': obj.Radius.Value, 'length_mm': obj.Height.Value})
    for i in range(9):
        obj = leaves[f'TipMainHarnessCorridorBend{i}']
        assert obj.TypeId == 'Part::Sphere'
        assert (obj.Placement.Base - points[i + 1]).Length < 1e-9
        assert abs(obj.Radius.Value - recipe_radius) < 1e-12
    lengths = [(b - a).Length for a, b in zip(points, points[1:])]
    angles = [0.0] * len(points)
    factors = [0.0] * len(points)
    for i in range(1, len(points) - 1):
        u, v = points[i] - points[i-1], points[i+1] - points[i]
        cosine = u.dot(v) / (u.Length * v.Length)
        angles[i] = math.acos(max(-1.0, min(1.0, cosine)))
        factors[i] = math.tan(angles[i] / 2)
    nominal = observation['insulated_OD_nominal_inch']
    tolerance = observation['insulated_OD_tolerance_plus_minus_inch']
    diameters = [(nominal - tolerance) * 25.4, (nominal + tolerance) * 25.4]
    radii = [d * observation['manufacturer_bend_radius_multiple_of_cable_diameter'] for d in diameters]
    segments = []
    for i, length in enumerate(lengths):
        k = factors[i] + factors[i+1]
        demand = [r * k for r in radii]
        segments.append({'segment_index': i, 'length_mm': length,
                         'adjacent_turn_angles_deg': [math.degrees(angles[i]), math.degrees(angles[i+1])],
                         'unit_radius_tangent_setback_sum': k,
                         'uniform_radius_upper_bound_mm': length / k if k else None,
                         'required_setback_sum_at_OD_min_max_mm': demand,
                         'overlap_at_OD_min_max_mm': [max(0.0, x - length) for x in demand],
                         'fixed_polyline_fillet_fits_OD_max_example': demand[-1] <= length})
    basis_screen = []
    for name, factor in [('outside radius', 9.5), ('centerline radius', 10.0), ('inside radius', 10.5)]:
        # Conversion for one circular insulated wire section only. This brackets
        # three explicit interpretations; the manufacturer has not chosen one.
        center_radii = [factor * diameter for diameter in diameters]
        basis_screen.append({'interpretation_of_10xOD': name,
                             'equivalent_single_wire_centerline_radius_min_max_mm': center_radii,
                             'critical_segment_2_setback_min_max_mm': [2 * radius for radius in center_radii],
                             'fixed_polyline_fillet_fits_at_minimum_OD': all(center_radii[0] * (factors[i] + factors[i+1]) <= length for i, length in enumerate(lengths))})
    # One exact, deliberately local outside-point witness at the first 90deg turn.
    # It is not a Hausdorff/maximum-deviation test or proof that every reroute fails.
    r = radii[-1]
    u = (points[1] - points[0]); u.normalize()
    v = (points[2] - points[1]); v.normalize()
    assert abs(u.dot(v)) < 1e-12
    center = points[1] - u * r + v * r
    midpoint = center + (u - v) * (r / math.sqrt(2))
    distance = shape.distToShape(Part.Vertex(midpoint))[0]
    result = {
        'status': 'Read-only native route and fixed-polyline circular-fillet screen complete',
        'inputs_sha256': inputs,
        'native_role': role.Name, 'saved_world_BRep_sha256': world_hash,
        'saved_world_geometry_matches_frozen_route_review': True,
        'native_radius_mm': recipe_radius, 'native_primitives': primitives,
        'points_xyz_mm': [list(p) for p in points],
        'corner_sphere_count': 9,
        'polyline_center_length_mm': sum(lengths),
        'center_length_is_cut_length_or_lower_bound': False,
        'wire_example_not_selected': observation['wire_example'],
        'wire_OD_min_max_mm': diameters,
        'explicit_10xOD_centerline_scenario_mm': radii,
        'radius_basis_limit': 'Manufacturer table does not state radius measurement basis. Main table and point witness use an explicit 10xOD single-centerline scenario. Outside/centerline/inside interpretations are separately bracketed as9.5/10/10.5xOD for one circular insulated wire; none is asserted to be the accepted manufacturer definition or a four-wire bundle model.',
        'radius_basis_interpretation_screens': basis_screen,
        'method': 'At each fixed vertex circular fillet tangent setback is R*tan(turn/2). Adjacent setbacks cannot exceed their shared straight-segment length. This necessary condition applies only to fillets preserving these segment directions/vertices, not every possible curve in available space.',
        'segments': segments,
        'maximum_uniform_fillet_radius_with_fixed_vertices_mm': min(s['uniform_radius_upper_bound_mm'] for s in segments if s['uniform_radius_upper_bound_mm'] is not None),
        'fixed_polyline_fillet_fits_at_smallest_catalog_OD': all(s['overlap_at_OD_min_max_mm'][0] == 0 for s in segments),
        'first_corner_max_OD_fillet_midpoint': {'xyz_mm': list(midpoint), 'minimum_distance_to_actual_reservation_mm': distance,
            'inside_current_reservation': shape.isInside(midpoint, 1e-7, True),
            'scope': 'Single exact point-to-solid minimum-distance/inside witness only. No maximum surface deviation, whole path containment or physical clearance is inferred.'},
        'decision': 'The current fixed-vertex polyline fails the explicit centerline, inside and outside-radius interpretations for this documented wire example, even at its minimum OD. It cannot simply receive those circular fillets. Reroute actual conductors with real bends/fanouts/slack and recheck surrounding parts, or qualify a different actual wire construction. Do not shrink an accepted bend radius to fit the current corridor.',
        'limits': ['No actual wire/terminal/tool selected; no current, crimp, fatigue, insulation, I2C or installed routing qualification.',
                   'A centerline and round bundle reservation do not specify four individual wire paths, twist, pitch exits, tip terminations, slack or cut/strip lengths.',
                   'No claim that every smooth reroute is impossible, no whole-path or physical acceptance, no source geometry mutation.'],
        'native_recompute_save_or_new_export': False,
        'BOM_changed': False, 'battery_selection': 'OPEN',
        'inputs_unchanged': all(sha(ROOT / p) == h for p, h in inputs.items())}
    assert result['inputs_unchanged']
    (OUT / 'native-bend-review.json').write_text(json.dumps(result, indent=2) + '\n')
    App.closeDocument(doc.Name)
    print(json.dumps({'polyline_mm': result['polyline_center_length_mm'],
                      'maximum_uniform_radius_mm': result['maximum_uniform_fillet_radius_with_fixed_vertices_mm'],
                      'smallest_catalog_OD_example_fits': result['fixed_polyline_fillet_fits_at_smallest_catalog_OD'],
                      'outside_midpoint_distance_mm': distance}))


if __name__ == '__main__':
    main()
