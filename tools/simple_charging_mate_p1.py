"""One-piece, rear-potted charging cable housing for the current P1 targets.

Reuse only the dimensional contact references from R3, not its bench fixture.
Generate meshes in a local cache; keep native CAD and part exchange in the repo.
"""
from pathlib import Path
import hashlib
import itertools
import json
import sys
import zipfile
import xml.etree.ElementTree as ET

sys.path.insert(0, '/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as App
import Part
import MeshPart

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'hardware/cad/prototype-p1/charging-cable'
CACHE = Path('/private/tmp/buttplug-p1-charging-meshes')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    OUT.mkdir(exist_ok=True)
    CACHE.mkdir(exist_ok=True)
    product_path = OUT.parent / 'PrototypeP1.FCStd'
    product_report = json.loads((OUT.parent / 'review.json').read_text())
    assert sha(product_path) == product_report['native_sha256']
    ref_dir = ROOT / 'hardware/cad/dock-mate-r3'
    ref_report = json.loads((ref_dir / 'geometry-report.json').read_text())
    ref_path = ref_dir / 'DockMateR3Bench.FCStd'
    assert sha(ref_path) == ref_report['outputs'][ref_path.name]
    product = App.openDocument(str(product_path))
    refs = App.openDocument(str(ref_path))
    doc = App.newDocument('P1ChargingCable')
    doc.Label = 'P1 simple charging cable / nominal candidate / no physical test'
    parts = []
    construction = []

    def feature(name, shape, label):
        obj = doc.addObject('PartDesign::Feature', name)
        obj.Shape, obj.Label = shape, label
        return obj

    def box(name, b):
        x, y, z, u, v, w = b
        obj = doc.addObject('Part::Box', name)
        obj.Length, obj.Width, obj.Height = u-x, v-y, w-z
        obj.Placement.Base = App.Vector(x, y, z)
        construction.append(obj)
        return obj

    def cyl(name, radius, x, y, z, length):
        obj = doc.addObject('Part::Cylinder', name)
        obj.Radius, obj.Height = radius, length
        obj.Placement = App.Placement(App.Vector(x, y, z),
                                     App.Rotation(App.Vector(0, 0, 1), App.Vector(0, 1, 0)))
        construction.append(obj)
        return obj

    def boolean(kind, name, a, b):
        obj = doc.addObject('Part::'+kind, name)
        obj.Base, obj.Tool, obj.Refine = a, b, True
        construction.append(obj)
        return obj

    def overlap(a, b):
        aa, bb = a.BoundBox, b.BoundBox
        if any(min(getattr(aa, k+'Max'), getattr(bb, k+'Max')) <=
               max(getattr(aa, k+'Min'), getattr(bb, k+'Min')) + 1e-7 for k in 'XYZ'):
            return 0.
        return a.copy().common(b.copy()).Volume

    raw = box('CableCaseBlank', [-42, -47, -13, -16, -30.4, 16])
    rounded = doc.addObject('Part::Fillet', 'CableCaseRounded')
    rounded.Base, rounded.Edges = raw, [(i, .8, .8) for i in range(1, 13)]
    construction.append(rounded)
    # Leave the existing buttons uncovered. The left side connects both magnets
    # and contacts; the bottom arm carries the second magnet.
    notch = box('ButtonClearance', [-29.5, -47.1, -.5, -15.8, -30.3, 11.5])
    body = boolean('Cut', 'CaseWithButtonClearance', rounded, notch)
    arm = box('IndexArm', [-47.1, -33, -4, -41.5, -30.4, 4])
    finger = box('IndexFinger', [-47.1, -33, -4, -45.3, -25.5, 4])
    body = boolean('Fuse', 'CaseWithIndexArm', body, arm)
    body = boolean('Fuse', 'CaseWithIndexFinger', body, finger)
    tools = [box('RearTerminationTrough', [-39, -47.1, -11, -30.5, -42, 15]),
             cyl('JacketEntry', 2.1, -35.5, -48, -7, 7)]
    for tag, z in [('Ground', 8.), ('Positive', 12.)]:
        # The fixed contact collar seats at Y-32.83. Load it from the rear,
        # soldered to its lead first; cure the rear bond after confirming stroke.
        tools += [cyl(tag+'ContactRearWell', 1.4, -32, -47.1, z, 14.27),
                  cyl(tag+'ContactFrontBore', .825, -32, -32.83, z, 2.53)]
        for role in ('SpringFixedBody', 'SeatedPlunger'):
            shape = refs.getObject(tag+role).Shape.copy()
            shape.translate(App.Vector(-2, 0, 0))
            obj = feature(tag+role, shape, tag+' / 0973 dimensional reference / translated X-2')
            parts.append(obj)
    for i, (x, z) in enumerate([(-37.75, 0.), (-21., -8.)]):
        tools.append(cyl('MagnetRearBore'+str(i), 2.15, x, -47.1, z, 16.3))
        magnet = cyl('CableMagnet'+str(i), 2., x, -32.3, z, 1.5)
        construction.remove(magnet)
        parts.append(magnet)
    for i, tool in enumerate(tools):
        body = boolean('Cut', 'P1CableHousing' if i == len(tools)-1 else 'CaseCut'+str(i), body, tool)
    construction.remove(body)
    body.Label = 'One-piece printed charging housing / rear-potted contacts and magnets / no screws'
    parts.insert(0, body)
    doc.recompute()
    assert body.Shape.isValid() and len(body.Shape.Solids) == 1
    for obj in parts:
        assert obj.Shape.isValid() and len(obj.Shape.Solids) == 1, obj.Name
    # Reference contact dimensions are copied unchanged apart from X-2.
    for tag in ('Ground', 'Positive'):
        for role in ('SpringFixedBody', 'SeatedPlunger'):
            original = refs.getObject(tag+role).Shape
            copied = doc.getObject(tag+role).Shape.copy()
            copied.translate(App.Vector(2, 0, 0))
            assert abs(copied.Volume-original.Volume) < 1e-6
    hits = []
    for a, b in itertools.combinations(parts, 2):
        v = overlap(a.Shape, b.Shape)
        if v > 1e-5:
            hits.append({'a': a.Name, 'b': b.Name, 'intersection_mm3': v})
    for obj in parts:
        for name in product_report['roles']:
            v = overlap(obj.Shape, product.getObject(name).Shape)
            if v > 1e-5:
                hits.append({'a': obj.Name, 'b': name, 'intersection_mm3': v})
    print('Cable installed hard-part hits:', hits, flush=True)
    assert not hits
    # Check rear axial loading of the fixed barrels and magnets. Flexible leads
    # and bond material are not rigid-stage substitutes in this screen.
    loading = []
    for obj in parts[1:]:
        if 'Plunger' in obj.Name:
            continue
        for offset in (-18., -12., -6., -3., -1., 0.):
            moved = obj.Shape.copy()
            moved.translate(App.Vector(0, offset, 0))
            v = overlap(moved, body.Shape)
            loading.append({'part': obj.Name, 'Y_offset_mm': offset, 'housing_intersection_mm3': v})
    assert all(q['housing_intersection_mm3'] < 1e-5 for q in loading)
    # Correct approach stays clear. The asymmetric side finger blocks the
    # three listed reversed-yaw samples well before the free tips reach Y-30.
    approach = []
    for offset in (-6., -4., -2., -1., -.6, 0.):
        moved = body.Shape.copy()
        moved.translate(App.Vector(0, offset, 0))
        bad = [name for name in product_report['roles']
               if overlap(moved, product.getObject(name).Shape) > 1e-5]
        approach.append({'Y_offset_mm': offset, 'hits': bad})
    assert not any(q['hits'] for q in approach)
    reverse = []
    for angle in (170., 180., 190.):
        moved = body.Shape.copy()
        moved.rotate(App.Vector(-32, -30, 10), App.Vector(0, 1, 0), angle)
        moved.translate(App.Vector(0, -4., 0))
        blockers = [name for name in ('P1FlangeCover', 'FlangeCoverLower', 'FlangeCoverUpper')
                    if overlap(moved, product.getObject(name).Shape) > 1e-5]
        reverse.append({'yaw_deg': angle, 'Y_offset_mm': -4., 'blockers': blockers,
                        'free_tip_gap_to_target_plane_mm': 3.4})
    assert all(q['blockers'] for q in reverse)
    note = doc.addObject('App::FeaturePython', 'AssemblyInstructions')
    note.addProperty('App::PropertyStringList', 'Steps', 'Prototype')
    note.Steps = ['Solder two cable conductors to the contact cups off the housing.',
                  'Load contacts from rear until collars seat. Keep moving tips dry.',
                  'Bond magnets in the blind bores with polarity matched to the product.',
                  'Trial pin compression, polarity and holding before rear encapsulation.',
                  'Rear encapsulation secures fixed bodies/jacket; no separate lid or screws.',
                  'Dry attended bench candidate only; bond, strain relief and holding unqualified.']
    native = OUT / 'P1ChargingCable.FCStd'
    doc.saveAs(str(native))
    part_records = {}
    for obj in parts:
        p = CACHE / (obj.Name+'.stl')
        MeshPart.meshFromShape(Shape=obj.Shape, LinearDeflection=.05,
                              AngularDeflection=.15, Relative=False).write(str(p))
        bb = obj.Shape.optimalBoundingBox(False, False)
        part_records[obj.Name] = {'valid': True, 'solids': 1, 'volume_mm3': obj.Shape.Volume,
                                  'bounds_xyz_mm': [getattr(bb, k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')],
                                  'mesh_sha256': sha(p)}
    # The housing is the only custom manufactured component.
    step = OUT / 'P1CableHousing.step'
    body.Shape.exportStep(str(step))
    back = Part.Shape()
    back.read(str(step))
    assert back.isValid() and len(back.Solids) == 1
    assert abs(back.Volume-body.Shape.Volume) < .01
    mesh = OUT / 'P1CableHousing.stl'
    MeshPart.meshFromShape(Shape=body.Shape, LinearDeflection=.05,
                          AngularDeflection=.15, Relative=False).write(str(mesh))
    App.closeDocument(doc.Name)
    # Inspect the saved native with history restored.
    doc = App.openDocument(str(native))
    doc.recompute()
    for name, q in part_records.items():
        s = doc.getObject(name).Shape
        assert s.isValid() and len(s.Solids) == 1
        assert abs(s.Volume-q['volume_mm3']) < 1e-5
    App.closeDocument(doc.Name)
    App.closeDocument(refs.Name)
    App.closeDocument(product.Name)
    # Visibility only; hide cutters and references without altering geometry.
    with zipfile.ZipFile(native) as z:
        payload = [(i, z.read(i)) for i in z.infolist()]
        names = [o.get('name') for o in ET.fromstring(z.read('Document.xml')).findall('Objects/Object')]
    gui = ET.Element('Document', SchemaVersion='1', HasExpansion='1')
    ET.SubElement(gui, 'Expand', count='0')
    vpdata = ET.SubElement(gui, 'ViewProviderData', Count=str(len(names)))
    for i, name in enumerate(names):
        vp = ET.SubElement(vpdata, 'ViewProvider', name=name, expanded='0', treeRank=str(i))
        properties = ET.SubElement(vp, 'Properties', Count='1', TransientCount='0')
        prop = ET.SubElement(properties, 'Property', name='Visibility', type='App::PropertyBool', status='1')
        ET.SubElement(prop, 'Bool', value='true' if name in part_records else 'false')
    temp = native.with_suffix('.view-tmp')
    with zipfile.ZipFile(temp, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for info, data in payload:
            if info.filename != 'GuiDocument.xml':
                z.writestr(info, data)
        z.writestr('GuiDocument.xml', ET.tostring(gui, encoding='utf-8', xml_declaration=True))
    with zipfile.ZipFile(temp) as z:
        assert all(z.read(i.filename) == data for i, data in payload if i.filename != 'GuiDocument.xml')
    temp.replace(native)
    review = {'native_sha256': sha(native), 'builder_sha256': sha(Path(__file__)),
              'product_native_sha256': product_report['native_sha256'],
              'spring_reference_native_sha256': ref_report['outputs'][ref_path.name],
              'parts': part_records, 'mesh_cache': str(CACHE), 'new_custom_parts': 1,
              'new_fasteners': 0, 'unexpected_installed_intersections': hits,
              'rear_loading_samples': loading, 'correct_approach': approach,
              'reversed_yaw_samples': reverse,
              'contact_axes_xyz_mm': [[-32, -30, 8], [-32, -30, 12]],
              'nominal_spring_compression_mm': .6, 'nominal_magnet_face_gap_mm': 1.6,
              'housing_STEP_sha256': sha(step), 'housing_STL_sha256': sha(mesh),
              'saved_native_recompute': 'All seven part solid counts and volumes match',
              'scope': 'Nominal geometry, copied spring references and finite loading/orientation samples only. No all-misalignment protection, tolerance/force/current, actual pin stroke, potting, cable strain relief, magnetic holding or physical acceptance. The contacts, magnets, cable and material remain candidates. Battery/BOM/product geometry unchanged.'}
    (OUT / 'review.json').write_text(json.dumps(review, indent=2)+'\n')
    print('Saved one-piece P1 charging housing, rear load samples and reversed-yaw blockers', flush=True)


if __name__ == '__main__':
    main()
