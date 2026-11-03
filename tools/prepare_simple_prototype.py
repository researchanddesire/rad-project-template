"""Make a legible assembly review from the existing R37 geometry.

No new keeper, connector cage, joint comb, screw or invented wire route.
Detailed parametric part history stays in the named source document.
"""
from pathlib import Path
import hashlib
import json
import sys

sys.path.insert(0, '/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as App
import Part
import MeshPart
import simple_flange_cover_p1
import simple_motor_wires_p1
import simple_charging_wires_p1
import simple_pack_routing_p1

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT / 'hardware/cad/prototype-p1'
SOURCE = ROOT / 'hardware/cad/pack-assembly-r37/power-f/ConditionalPackPowerR37.FCStd'
REPORT = SOURCE.with_name('geometry-report.json')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def category(name):
    if name in ('KeyedBodyR25', 'MotorSeatCapR25', 'FlangeCoverLower',
                'FlangeCoverUpper', 'ButtonServiceCoverR31'):
        return 'Exterior'
    if name.startswith(('R17_', 'BodyPCB_', 'FlangePCB_', 'R17Mate_', 'TipPCB',
                        'TipComponent')):
        return 'Electronics'
    if name.startswith(('PackPublished', 'PackNTCHead', 'PackNTCContact')):
        return 'BatteryReference'
    if name.startswith(('Button',)):
        return 'Controls'
    if name.startswith(('MotorMax', 'ShellMotor', 'MotorClamp')):
        return 'Motor'
    if any(word in name for word in ('Wire', 'Lead', 'Bare', 'Solder', 'Splice',
                                    'Joint', 'Coating', 'CoreR36', 'Space',
                                    'ThermalGel', 'DielectricBond', 'Process',
                                    'ContactFilm', 'AnchorPad', 'SoftPad')):
        return 'WiringAndProcessAllowances'
    if any(word in name for word in ('Screw', 'HubBolt', 'HubNut', 'KeeperScrew')):
        return 'FastenerAllowances'
    return 'Supports'


def color(name, group):
    if name.startswith(('FlangeCover', 'ButtonServiceCover', 'ButtonBoot')):
        return (0.18, 0.39, 0.40)
    if name == 'KeyedBodyR25' or name == 'MotorSeatCapR25':
        return (0.76, 0.79, 0.82)
    return {'Electronics': (0.16, 0.52, 0.33),
            'BatteryReference': (0.27, 0.56, 0.72),
            'Controls': (0.36, 0.49, 0.57),
            'Motor': (0.78, 0.55, 0.25),
            'WiringAndProcessAllowances': (0.64, 0.48, 0.26),
            'FastenerAllowances': (0.40, 0.43, 0.47),
            'Supports': (0.69, 0.69, 0.63)}.get(group, (0.65, 0.67, 0.69))


def inventory(shape):
    b = shape.optimalBoundingBox(False, False)
    return {'valid': shape.isValid(), 'solid_count': len(shape.Solids),
            'volume_mm3': shape.Volume,
            'bounds_xyz_mm': [getattr(b, k) for k in
                              ('XMin', 'YMin', 'ZMin', 'XMax', 'YMax', 'ZMax')]}


def boundary_samples(shape):
    """Finite saved-shape check; not a proof of continuous material equality."""
    points = [v.Point for v in shape.Vertexes]
    for edge in shape.Edges:
        lo, hi = edge.ParameterRange
        points.extend(edge.valueAt(lo + (hi-lo)*i/8) for i in range(9))
    return sorted(tuple(round(v, 6) for v in (p.x, p.y, p.z)) for p in points)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for directory in ('display', 'exchange', 'fit-mockup'):
        (OUT / directory).mkdir(exist_ok=True)
    source_hash = sha(SOURCE)
    report = json.loads(REPORT.read_text())
    assert report['native_sha256'] == source_hash
    assert report['all_static_screens_clear']
    names = report['fixed_roles'] + list(report['new_roles'])
    assert len(names) == len(set(names))
    source = App.openDocument(str(SOURCE))
    doc = App.newDocument('PrototypeP1')
    doc.Label = 'P1 simple assembly review / battery choice open'
    groups = {}
    objects = {}
    records = {}
    for name in names:
        original = source.getObject(name)
        assert original is not None and original.Shape.isValid(), name
        kind = category(name)
        if kind not in groups:
            groups[kind] = doc.addObject('App::DocumentObjectGroup', kind)
        obj = doc.addObject('PartDesign::Feature', name)
        obj.Shape = original.Shape.copy()
        obj.Label = original.Label
        obj.addProperty('App::PropertyString', 'DetailedSource', 'Provenance')
        obj.DetailedSource = str(SOURCE.relative_to(ROOT)) + '#' + name
        obj.addProperty('App::PropertyString', 'DesignStatus', 'Provenance')
        obj.DesignStatus = ('Reference/space allowance; not a purchased part'
                            if kind in ('BatteryReference', 'WiringAndProcessAllowances',
                                        'FastenerAllowances') else
                            'Prototype geometry; actual fit and material untested')
        groups[kind].addObject(obj)
        if obj.ViewObject:
            obj.ViewObject.ShapeColor = color(name, kind)
            obj.ViewObject.Visibility = kind == 'Exterior'
        records[name] = {'group': kind, **inventory(obj.Shape)}
        objects[name] = obj
    cover_result = simple_flange_cover_p1.build(doc, names)
    (OUT / 'cover-review.json').write_text(json.dumps(cover_result['review'], indent=2) + '\n')
    assert not cover_result['review']['unexpected_intersections'], 'Repair new cover clashes before adopting'
    construction = doc.addObject('App::DocumentObjectGroup', 'Construction')
    for obj in cover_result['construction']:
        construction.addObject(obj)
    active_names = [n for n in names if n != 'ButtonServiceCoverR31']
    records.pop('ButtonServiceCoverR31')
    for obj in cover_result['objects']:
        group = 'Exterior' if obj.Name == 'P1FlangeCover' else 'WiringAndProcessAllowances' if 'Allowance' in obj.Name else 'Charging'
        if group not in groups:
            groups[group] = doc.addObject('App::DocumentObjectGroup', group)
        groups[group].addObject(obj)
        records[obj.Name] = {'group': group, **inventory(obj.Shape)}
        active_names.append(obj.Name)
        if obj.ViewObject:
            obj.ViewObject.ShapeColor = (.18, .39, .40) if group == 'Exterior' else (.8, .65, .25)
            obj.ViewObject.Visibility = group == 'Exterior'
    motor_result = simple_motor_wires_p1.build(doc, active_names)
    (OUT / 'motor-wire-review.json').write_text(json.dumps(motor_result['review'], indent=2) + '\n')
    assert not motor_result['review']['unexpected_intersections'], 'Repair motor wire clashes before adopting'
    assert not any(p['hits'] for p in motor_result['review']['motor_mate_listed_poses']), 'Repair motor plug access'
    for obj in motor_result['construction']:
        construction.addObject(obj)
    for obj in motor_result['objects']:
        groups['WiringAndProcessAllowances'].addObject(obj)
        records[obj.Name] = {'group': 'WiringAndProcessAllowances', **inventory(obj.Shape)}
        active_names.append(obj.Name)
    pack_result = simple_pack_routing_p1.build(doc, active_names)
    for name in pack_result['replaced_active_names']:
        active_names.remove(name)
        records.pop(name)
        groups['WiringAndProcessAllowances'].removeObject(doc.getObject(name))
    for obj in pack_result['construction']:
        construction.addObject(obj)
    for obj in pack_result['objects']:
        groups['WiringAndProcessAllowances'].addObject(obj)
        records[obj.Name] = {'group': 'WiringAndProcessAllowances', **inventory(obj.Shape)}
        active_names.append(obj.Name)
    charging_result = simple_charging_wires_p1.build(doc, active_names)
    for obj in charging_result['construction']:
        construction.addObject(obj)
    for obj in charging_result['objects']:
        groups['WiringAndProcessAllowances'].addObject(obj)
        records[obj.Name] = {'group': 'WiringAndProcessAllowances', **inventory(obj.Shape)}
        active_names.append(obj.Name)
    note = doc.addObject('App::FeaturePython', 'AssemblyNotes')
    note.addProperty('App::PropertyStringList', 'Instructions', 'Prototype')
    note.Instructions = [
        'Front-loaded one-piece metal body; 15 mm neck; independent metal motor clamp.',
        'Two primary PCBs joined by flexible wires; small wired tip-sensor PCB.',
        'No R38 comb/return plug or R39 connector cage is adopted.',
        'Insulate splices individually. Hand dress wiring in open hub recesses.',
        'Use removable electronics-compatible silicone tacks on insulated jackets/housing.',
        'Keep battery, connector release and service fasteners accessible; do not pot the pack.',
        'Tack cure/adhesion and real connected assembly must be tried on the fit mockup.',
        'Contact seats and bonded-magnet pockets are integral to the cover; sealing process still unqualified.',
        'Battery is an open choice; the displayed 33 x 8 x 20 mm block is a size reference.',
    ]
    doc.recompute()
    native = OUT / 'PrototypeP1.FCStd'
    doc.saveAs(str(native))
    # Reopen the saved review assembly. Compare every role to the source rather
    # than treating successful saving as evidence of shape preservation.
    App.closeDocument(doc.Name)
    doc = App.openDocument(str(native))
    for name in names:
        obj = doc.getObject(name)
        a = source.getObject(name).Shape
        b = obj.Shape
        assert b.isValid() and len(a.Solids) == len(b.Solids), name
        assert abs(a.Volume-b.Volume) < max(1e-6, a.Volume*1e-9), name
        ba, bb = inventory(a)['bounds_xyz_mm'], inventory(b)['bounds_xyz_mm']
        assert max(abs(x-y) for x, y in zip(ba, bb)) < 1e-6, name
        assert boundary_samples(a) == boundary_samples(b), name
    print('Saved/reopened assembly matches', len(names), 'source role geometry screens', flush=True)
    objects = {n: doc.getObject(n) for n in active_names}

    # Separate native meshes support readable overview and interior views.
    meshes = {}
    for name, obj in objects.items():
        p = OUT / 'display' / (name + '.stl')
        MeshPart.meshFromShape(Shape=obj.Shape, LinearDeflection=.10,
                              AngularDeflection=.20, Relative=False).write(str(p))
        meshes[name] = sha(p)
    sections = {}
    clip = Part.makeBox(200, 200, 50, App.Vector(-100, -50, -50))
    for name in ('KeyedBodyR25', 'MotorSeatCapR25', 'FlangeCoverLower'):
        shape = objects[name].Shape.copy().common(clip.copy())
        p = OUT / 'display' / (name + '-half.stl')
        MeshPart.meshFromShape(Shape=shape, LinearDeflection=.10,
                              AngularDeflection=.20, Relative=False).write(str(p))
        sections[name] = sha(p)
    parts = ['KeyedBodyR25', 'MotorSeatCapR25', 'ShellMotorMountR25',
             'PackAnchoredCarrierR37', 'PCBOnlyKeeperR25',
             'PoweredConnectedPackTailLeftHubR34', 'PoweredServiceablePackHubR36',
             'PackLidR33', 'StationaryTipCarrierR26', 'P1FlangeCover']
    exports = {}
    for name in parts:
        obj = objects[name]
        path = OUT / 'exchange' / (name + '.step')
        obj.Shape.exportStep(str(path))
        back = Part.Shape()
        back.read(str(path))
        assert back.isValid(), name
        assert len(back.Solids) == len(obj.Shape.Solids), name
        va, vb = obj.Shape.Volume, back.Volume
        assert abs(va - vb) < max(.02, va * 1e-5), (name, va, vb)
        ba = inventory(obj.Shape)['bounds_xyz_mm']
        bb = inventory(back)['bounds_xyz_mm']
        assert max(abs(x-y) for x, y in zip(ba, bb)) < .02, name
        exports[name] = {'path': str(path.relative_to(ROOT)), 'sha256': sha(path),
                         'readback_valid': True, 'solid_count': len(back.Solids),
                         'volume_delta_mm3': vb-va,
                         'scope': 'Validity, solids, volume and bounds; no fit/strength claim'}
        if name != 'ShellMotorMountR25':
            mesh = OUT / 'fit-mockup' / (name + '.stl')
            MeshPart.meshFromShape(Shape=obj.Shape, LinearDeflection=.04,
                                  AngularDeflection=.15, Relative=False).write(str(mesh))
    result = {
        'native': str(native.relative_to(ROOT)), 'native_sha256': sha(native),
        'source_native': str(SOURCE.relative_to(ROOT)), 'source_sha256': source_hash,
        'builder_sha256': sha(Path(__file__)),
        'saved_geometry_screens_match_source': True,
        'saved_geometry_screen_scope': 'All role solid counts, volume, bounds, vertices and nine samples per edge. Finite samples do not prove continuous material equivalence.',
        'source_role_count': len(names), 'new_custom_retention_parts': 0,
        'active_role_count': len(active_names),
        'cover_integration': cover_result['review'],
        'cover_builder_sha256': sha(Path(simple_flange_cover_p1.__file__)),
        'motor_wiring': motor_result['review'],
        'motor_wire_builder_sha256': sha(Path(simple_motor_wires_p1.__file__)),
        'charging_wiring': charging_result['review'],
        'charging_wire_builder_sha256': sha(Path(simple_charging_wires_p1.__file__)),
        'pack_routing': pack_result['review'],
        'pack_routing_builder_sha256': sha(Path(simple_pack_routing_p1.__file__)),
        'removed_from_selected_architecture': ['R38 comb, return plug, pads and screw',
                                               'R39 connector cage and lap covers'],
        'retention_process': 'Individual joint insulation; hand-dressed wiring; small removable silicone tacks on jackets/housing, pack removable. Process trial pending.',
        'roles': records, 'meshes_sha256': meshes, 'native_half_sections_sha256': sections,
        'part_exports': exports,
        'battery': 'OPEN; displayed block is only a published body-size reference',
        'prototype_build_consideration_ready': False,
        'remaining': ['Try connected loading and simple wiring restraint in fit mockup',
                      'Trial received motor/dock leads and cover service in the fit mockup',
                      'Resolve shell/cover/contact seal details for cleanable metal build',
                      'Confirm candidate pack and received dimensions before ordering/fabrication'],
        'scope': 'Simplified review assembly. Existing geometry, individual parts and wire space claims retained; no new physical validation. Adhesive process, finished dock and seals are not modeled as solved. Detailed parametric source remains in R37 and its ancestors.'
    }
    for filename, detail in [('charging-wire-review.json', charging_result['review']),
                             ('pack-routing-review.json', pack_result['review'])]:
        detail['native_sha256'] = sha(native)
        (OUT / filename).write_text(json.dumps(detail, indent=2) + '\n')
    (OUT / 'review.json').write_text(json.dumps(result, indent=2) + '\n')
    App.closeDocument(doc.Name)
    App.closeDocument(source.Name)
    assert sha(SOURCE) == source_hash
    print('P1 review assembly, ten part exchanges and fit meshes saved', flush=True)


if __name__ == '__main__':
    main()
