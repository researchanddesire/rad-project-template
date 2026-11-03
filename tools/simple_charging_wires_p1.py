"""P1 dock wires: hand-dressed routes, no additional retainer or PCB change.

Called by prepare_simple_prototype. Running this file adds the same routes to
the existing P1 assembly without regenerating unchanged part exports/meshes.
"""
from pathlib import Path
import hashlib
import json
import math
import sys
import zipfile
import xml.etree.ElementTree as ET

sys.path.insert(0, '/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as App
import Part
import MeshPart
import kicad_sexp as S

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'hardware/cad/prototype-p1'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def overlap(a, b):
    u, v = a.BoundBox, b.BoundBox
    if any(min(getattr(u, k+'Max'), getattr(v, k+'Max')) <=
           max(getattr(u, k+'Min'), getattr(v, k+'Min')) + 1e-7 for k in 'XYZ'):
        return 0.
    return a.copy().common(b.copy()).Volume


def path(pin, opening=0.):
    x, left, rear, z = {1: (-16.5, -37.5, -24., 12.),
                        2: (-17.5, -36.5, -23., 8.)}[pin]
    left += opening / 2
    points = [(x, -16.7125, -8.1125), (x, -16.7125, -10.2),
              (x, rear, -10.2), (left, rear, -10.2), (left, rear, z),
              (-32., rear, z), (-32., -25.71-opening, z)]
    p = [App.Vector(*v) for v in points]
    edges, last, previous_trim = [], p[0], 0.
    for i in range(1, len(p)-1):
        incoming, outgoing = p[i]-p[i-1], p[i+1]-p[i]
        incoming.normalize()
        outgoing.normalize()
        angle = math.acos(max(-1., min(1., incoming.dot(outgoing))))
        radius = 2.0 if i == 1 else 1.5
        trim = radius*math.tan(angle/2)
        assert trim + previous_trim <= (p[i]-p[i-1]).Length + 1e-7
        assert trim <= (p[i+1]-p[i]).Length + 1e-7
        a, b = p[i]-incoming*trim, p[i]+outgoing*trim
        if (a-last).Length > 1e-7:
            edges.append(Part.makeLine(last, a))
        bisector = outgoing-incoming
        bisector.normalize()
        centre = p[i]+bisector*(radius/math.cos(angle/2))
        middle = (a-centre)+(b-centre)
        middle.normalize()
        edges.append(Part.Arc(a, centre+middle*radius, b).toShape())
        last, previous_trim = b, trim
    if (p[-1]-last).Length > 1e-7:
        edges.append(Part.makeLine(last, p[-1]))
    return Part.Wire(edges), points


def wire_shape(spine):
    profile = Part.Wire([Part.makeCircle(.3, spine.Vertexes[0].Point,
                                        App.Vector(0, 0, -1))])
    return spine.makePipeShell([profile], True, False)


def build(doc, active_names):
    # Verify pin order on the actual current board, not a mating-face guess.
    pcb = ROOT / 'hardware/pcb/pack-pigtail-r35/candidate-f/flange/flange-r35.kicad_pcb'
    circuit = json.loads(pcb.parent.parent.joinpath('saved-circuit-review.json').read_text())
    assert sha(pcb) == circuit['boards']['flange']['sha256']
    tree = S.parse(pcb.read_text())
    fp = next(f for f in S.children(tree, 'footprint') if
              any(t[1].value == 'reference' and t[2].value == 'J1'
                  for t in S.children(f, 'fp_text')))
    assert [float(a.value) for a in S.child(fp, 'at')[1:]] == [81.5, 152., 180.]
    pads = {p[1].value: p for p in S.children(fp, 'pad') if p[1].value in ('1', '2')}
    for n, local_x, net in [('1', -.5, 'DOCK_5V'), ('2', .5, 'GND')]:
        assert float(S.child(pads[n], 'at')[1].value) == local_x
        assert S.child(pads[n], 'net')[2].value == net
    fixed = {n: doc.getObject(n).Shape for n in active_names}
    mate_role = 'P1PackMateSpace' if 'P1PackMateSpace' in fixed else 'PackMateProcessSpaceR37'
    moving = {n for n in fixed if n.startswith('P1') and
              any(s in n for s in ('Contact', 'Magnet', 'Encapsulation'))}
    moving.add('P1FlangeCover')
    objects, construction, plans, poses = [], [], [], []
    baseline_lengths = {}
    for opening in (0., 1., 2., 3.):
        samples = []
        for pin in (1, 2):
            spine, points = path(pin, opening)
            shape = wire_shape(spine)
            assert shape.isValid() and len(shape.Solids) == 1
            hits = []
            for name, original in fixed.items():
                target = original.copy()
                if name in moving:
                    target.translate(App.Vector(0, -opening, 0))
                volume = overlap(shape, target)
                if volume > 1e-5:
                    hits.append({'fixed': name, 'intersection_mm3': volume})
            assert not hits, (opening, pin, hits)
            samples.append(shape)
            row = {'pin': pin, 'net': 'DOCK_5V' if pin == 1 else 'GND',
                   'sharp_corner_control_points_xyz_mm': points,
                   'path_length_mm': spine.Length,
                   'pack_mate_gap_mm': shape.distToShape(fixed[mate_role])[0],
                   'unexpected_intersections': hits}
            if opening == 0:
                baseline_lengths[pin] = spine.Length
                obj_path = doc.addObject('Part::Feature', 'P1DockPath'+str(pin))
                obj_path.Shape = spine
                profile = doc.addObject('Part::Feature', 'P1DockProfile'+str(pin))
                profile.Shape = Part.Wire([Part.makeCircle(.3, spine.Vertexes[0].Point,
                                                          App.Vector(0, 0, -1))])
                obj = doc.addObject('Part::Sweep', 'P1DockWire'+str(pin))
                obj.Sections, obj.Spine, obj.Solid, obj.Frenet = [profile], obj_path, True, False
                obj.Label = 'J1.'+str(pin)+' / '+row['net']+' / conditional OD0.60 route'
                doc.recompute()
                assert obj.Shape.isValid() and len(obj.Shape.Solids) == 1
                assert abs(obj.Shape.Volume-shape.Volume) < 1e-5
                construction += [obj_path, profile]
                objects.append(obj)
                plans.append(row)
            assert abs(spine.Length-baseline_lengths[pin]) < 1e-6
        assert overlap(*samples) < 1e-5
        poses.append({'cover_opening_Y_mm': -opening,
                      'wires': [dict(pin=i+1, path_length_mm=path(i+1, opening)[0].Length)
                                for i in range(2)], 'unexpected_intersections': [],
                      'wire_pair_intersection_mm3': overlap(*samples)})
    print('P1 charging wires clear; constant-length samples at 0/1/2/3 mm cover opening', flush=True)
    return {'objects': objects, 'construction': construction,
            'review': {'native_flange_sha256': sha(pcb), 'paths': plans,
                       'wire_OD_allowance_mm': .6, 'first_bend_centreline_radius_mm': 2.,
                       'other_bend_centreline_radius_mm': 1.5,
                       'cover_wire_pose_samples': poses, 'unexpected_intersections': [],
                       'new_custom_parts': 0, 'new_fasteners': 0,
                       'scope': 'Conditional nominal wire envelopes and four equal-length flex shapes, not a continuous flexible-wire or complete-cover motion proof. J1 numeric X order is native-board verified; Y/Z wire exits assume the nominal mate-envelope centre. Actual prewired lead exit, OD <=0.60, permitted bend radius <=1.50 mm, current rating, strip/termination and hand-dressed closure require a received-part trial. First bend2.0mm; other bends1.5mm. Nominal pack-mate gap about0.508mm is not a tolerance margin or physical acceptance. Do not force a thicker/stiffer lead into this route. No pack/BOM/PCB change.'}}


def main():
    source_dir = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else OUT
    destination = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else OUT
    destination.mkdir(parents=True, exist_ok=True)
    (destination / 'display').mkdir(exist_ok=True)
    source_native = source_dir / 'PrototypeP1.FCStd'
    native = destination / 'PrototypeP1.FCStd'
    report = json.loads((source_dir / 'review.json').read_text())
    before = sha(source_native)
    assert before == report['native_sha256']
    doc = App.openDocument(str(source_native))
    assert doc.getObject('P1DockWire1') is None, 'Already integrated; rebuild from source for a changed route'
    old_shapes = {n: doc.getObject(n).Shape.copy() for n in report['roles']}
    import simple_pack_routing_p1
    pack = simple_pack_routing_p1.build(doc, list(report['roles']))
    for name in pack['replaced_active_names']:
        old = doc.getObject(name)
        for group in doc.Objects:
            if group.TypeId == 'App::DocumentObjectGroup' and old in group.Group:
                group.removeObject(old)
        report['roles'].pop(name)
        report['meshes_sha256'].pop(name, None)
    for obj in pack['construction']:
        doc.getObject('Construction').addObject(obj)
    from prepare_simple_prototype import inventory, boundary_samples
    for obj in pack['objects']:
        doc.getObject('WiringAndProcessAllowances').addObject(obj)
        report['roles'][obj.Name] = {'group': 'WiringAndProcessAllowances', **inventory(obj.Shape)}
    result = build(doc, list(report['roles']))
    for obj in result['objects']:
        doc.getObject('WiringAndProcessAllowances').addObject(obj)
    for obj in result['construction']:
        doc.getObject('Construction').addObject(obj)
    new_names = [obj.Name for obj in pack['objects']+result['objects']]
    doc.recompute()
    staging = Path('/private/tmp/PrototypeP1-charging-integrated.FCStd')
    doc.saveAs(str(staging))
    App.closeDocument(doc.Name)
    doc = App.openDocument(str(staging))
    roundtrip_normalized = []
    for n, original in old_shapes.items():
        saved = doc.getObject(n).Shape
        assert saved.isValid() and len(saved.Solids) == len(original.Solids), n
        assert abs(saved.Volume-original.Volume) < 1e-6, n
        assert boundary_samples(saved) == boundary_samples(original), n
        if saved.exportBrepToString() != original.exportBrepToString():
            # OCC normalizes some direction cosines on roundtrip (~1e-16).
            # Do not call those byte-identical; additionally check both cuts.
            assert original.copy().cut(saved.copy()).Volume < 1e-6, n
            assert saved.copy().cut(original.copy()).Volume < 1e-6, n
            roundtrip_normalized.append(n)
    for name in new_names:
        saved = doc.getObject(name)
        assert saved.Shape.isValid() and len(saved.Shape.Solids) == 1
        report['roles'][saved.Name] = {'group': 'WiringAndProcessAllowances', **inventory(saved.Shape)}
        mesh = destination / 'display' / (saved.Name+'.stl')
        MeshPart.meshFromShape(Shape=saved.Shape, LinearDeflection=.05,
                              AngularDeflection=.15, Relative=False).write(str(mesh))
        report['meshes_sha256'][saved.Name] = sha(mesh)
    App.closeDocument(doc.Name)
    # Show the exterior by default; construction/wire details remain selectable.
    with zipfile.ZipFile(staging) as z:
        payload = [(i, z.read(i)) for i in z.infolist()]
        names = [o.get('name') for o in ET.fromstring(z.read('Document.xml')).findall('Objects/Object')]
    gui = ET.Element('Document', SchemaVersion='1', HasExpansion='1')
    ET.SubElement(gui, 'Expand', count='0')
    providers = ET.SubElement(gui, 'ViewProviderData', Count=str(len(names)))
    visible = {n for n, q in report['roles'].items() if q['group'] == 'Exterior'}
    for rank, name in enumerate(names):
        vp = ET.SubElement(providers, 'ViewProvider', name=name, expanded='0', treeRank=str(rank))
        properties = ET.SubElement(vp, 'Properties', Count='1', TransientCount='0')
        prop = ET.SubElement(properties, 'Property', name='Visibility', type='App::PropertyBool', status='1')
        ET.SubElement(prop, 'Bool', value='true' if name in visible else 'false')
    pending = native.with_suffix('.charging-tmp')
    with zipfile.ZipFile(pending, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for info, data in payload:
            if info.filename != 'GuiDocument.xml':
                z.writestr(info, data)
        z.writestr('GuiDocument.xml', ET.tostring(gui, encoding='utf-8', xml_declaration=True))
    with zipfile.ZipFile(pending) as z:
        assert all(z.read(i.filename) == data for i, data in payload if i.filename != 'GuiDocument.xml')
    pending.replace(native)
    result['review'].update({'native_sha256': sha(native), 'prior_native_sha256': before,
                             'old_role_geometry_screens_pass': len(old_shapes),
                             'roundtrip_serialization_normalized_roles': roundtrip_normalized,
                             'old_role_check_scope': 'Valid solids, volumes and finite boundary samples; byte comparison otherwise, plus bidirectional zero-volume cuts where OCC normalizes serialization. Numerical geometry evidence, not physical fit.',
                             'builder_sha256': sha(Path(__file__))})
    report.update({'native_sha256': sha(native), 'active_role_count': len(report['roles']),
                   'charging_wiring': result['review'],
                   'pack_routing': pack['review'],
                   'pack_routing_builder_sha256': sha(Path(simple_pack_routing_p1.__file__)),
                   'charging_wire_builder_sha256': sha(Path(__file__)),
                   'builder_sha256': sha(ROOT / 'tools/prepare_simple_prototype.py'),
                   'incremental_integration_prior_native_sha256': before})
    report['remaining'] = ['Try complete connected loading and fitted wiring in the dry mockup',
                           'Resolve shell/cover/contact seals for the cleanable metal build',
                           'Review pack envelope, actual leads and electrical limits; battery OPEN']
    report['gui_configuration'] = {'all_non_GUI_archive_members_unchanged_by_visibility_edit': True,
                                    'visible_roles': sorted(visible)}
    pack['review'].update({'native_sha256': sha(native), 'builder_sha256': sha(Path(simple_pack_routing_p1.__file__))})
    (destination / 'pack-routing-review.json').write_text(json.dumps(pack['review'], indent=2)+'\n')
    (destination / 'charging-wire-review.json').write_text(json.dumps(result['review'], indent=2)+'\n')
    (destination / 'review.json').write_text(json.dumps(report, indent=2)+'\n')
    print('Saved P1 with two dock wires;', len(old_shapes), 'old role geometry screens pass', flush=True)


if __name__ == '__main__':
    main()
