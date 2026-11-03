"""Export one unpowered P1 fit kit with native assembly and printable gauges.

Arguments: integrated CAD folder, cached external-cable folder, output folder.
Uses the actual source shapes; print-only gauges do not select real components.
"""
from pathlib import Path
import hashlib
import json
import sys

sys.path.insert(0, '/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as App
import Part
import Mesh
import MeshPart

ROOT = Path(__file__).resolve().parents[1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    source = Path(sys.argv[1]).resolve()
    cable = Path(sys.argv[2]).resolve()
    out = Path(sys.argv[3]).resolve()
    out.mkdir(parents=True, exist_ok=True)
    (out / 'stl').mkdir(exist_ok=True)
    cache = out / 'view-meshes'
    cache.mkdir(exist_ok=True)
    report = json.loads((source / 'review.json').read_text())
    cable_report = json.loads((cable / 'review.json').read_text())
    assert sha(source / 'PrototypeP1.FCStd') == report['native_sha256']
    assert sha(cable / 'P1ChargingCable.FCStd') == cable_report['native_sha256']
    product = App.openDocument(str(source / 'PrototypeP1.FCStd'))
    charger = App.openDocument(str(cable / 'P1ChargingCable.FCStd'))
    doc = App.newDocument('P1DryFitKit')
    doc.Label = 'P1 dry-fit kit / gauges and unpowered assembly / no wear use'
    groups = {name: doc.addObject('App::DocumentObjectGroup', name) for name in
              ('BodyFitParts', 'FlangeFitParts', 'Gauges', 'ExternalCable', 'ReferenceWires')}
    items, view_meshes = [], {}

    def mesh(shape, path):
        clean = shape.copy().cleaned()
        m = MeshPart.meshFromShape(Shape=clean, LinearDeflection=.04,
                                   AngularDeflection=.12, Relative=False)
        method = 'OCC deflection0.04 / angle0.12'
        if not m.isSolid():
            # Global remeshing resolves OCC tessellation seams without filling
            # holes or removing native part material.
            m = MeshPart.meshFromShape(Shape=clean, Fineness=2, SecondOrder=0,
                                      Optimize=1, AllowQuad=0, MaxLength=1., MinLength=.05)
            method = 'Netgen global surface remesh / max1.0 min0.05'
        assert m.isSolid(), ('Open/nonmanifold mesh', path)
        m.write(str(path))
        back = Mesh.Mesh(str(path))
        assert back.isSolid(), ('Open/nonmanifold STL', path)
        assert back.CountFacets > 0
        native_box, mesh_box = shape.optimalBoundingBox(False, False), back.BoundBox
        bound_delta = max(abs(getattr(native_box, a)-getattr(mesh_box, a))
                          for a in ('XMin', 'YMin', 'ZMin', 'XMax', 'YMax', 'ZMax'))
        volume_delta = abs(abs(back.Volume)-shape.Volume)
        assert bound_delta < .05, (path, bound_delta)
        assert volume_delta < max(.1, shape.Volume*.005), (path, volume_delta, shape.Volume)
        return {'sha256': sha(path), 'triangles': back.CountFacets,
                'closed_mesh': back.isSolid(), 'mesher': method,
                'maximum_bound_delta_mm': bound_delta, 'volume_delta_mm3': volume_delta}

    def add(name, roles, group, *, owner=product, quantity=1, rotation=None, note=''):
        shapes = [owner.getObject(n).Shape.copy() for n in roles]
        shape = shapes[0] if len(shapes) == 1 else shapes[0].multiFuse(shapes[1:]).removeSplitter()
        assert shape.isValid() and len(shape.Solids) == 1, (name, len(shape.Solids))
        obj = doc.addObject('PartDesign::Feature', name)
        obj.Shape, obj.Label = shape, name.replace('_', ' ')
        obj.addProperty('App::PropertyStringList', 'SourceRoles', 'Provenance')
        obj.SourceRoles = roles
        obj.addProperty('App::PropertyString', 'Use', 'Prototype')
        obj.Use = note or 'Dry-fit copy; final material, fits and physical assembly unverified'
        groups[group].addObject(obj)
        view_path = cache / (name+'.stl')
        view_meshes[name] = mesh(shape, view_path)['sha256']
        printed = shape.copy()
        if rotation:
            printed.rotate(App.Vector(), App.Vector(*rotation[0]), rotation[1])
        b = printed.optimalBoundingBox(False, False)
        translation = [-b.XMin, -b.YMin, -b.ZMin]
        printed.translate(App.Vector(*translation))
        target = out / 'stl' / (name+'.stl')
        check = mesh(printed, target)
        b = printed.optimalBoundingBox(False, False)
        assert abs(b.ZMin) < 1e-6
        items.append({'name': name, 'file': 'stl/'+target.name, 'quantity': quantity,
                      'source_roles': roles, 'group': group, 'note': obj.Use,
                      'print_rotation_axis_degrees': rotation,
                      'print_translation_xyz_mm': translation,
                      'size_xyz_mm': [b.XLength, b.YLength, b.ZLength],
                      'solid_count': 1, 'volume_mm3': printed.Volume, **check})
        print('KIT', name, 'qty', quantity, 'closed mesh', check['triangles'], flush=True)
        return obj

    along_y = ((1, 0, 0), 90.)
    for name, role in [('Body', 'KeyedBodyR25'), ('NoseCap', 'MotorSeatCapR25'),
                       ('MotorMount', 'ShellMotorMountR25'), ('BodyCarrier', 'PackAnchoredCarrierR37'),
                       ('BodyBoardKeeper', 'PCBOnlyKeeperR25'), ('TipCarrier', 'StationaryTipCarrierR26')]:
        add(name, [role], 'BodyFitParts', rotation=along_y)
    for name, role in [('LeftHub', 'PoweredConnectedPackTailLeftHubR34'),
                       ('RightHub', 'PoweredServiceablePackHubR36'), ('PackLid', 'PackLidR33'),
                       ('LowerFlangeSkin', 'FlangeCoverLower'), ('UpperFlangeSkin', 'FlangeCoverUpper'),
                       ('ChargingCover', 'P1FlangeCover'), ('FlangeBoardKeeper', 'ButtonKeeperR31')]:
        add(name, [role], 'FlangeFitParts', rotation=along_y)
    for name, substrate, body in [('BodyBoardGauge', 'BodyPCB_R17', True),
                                  ('FlangeBoardGauge', 'FlangePCB_R17', False)]:
        roles = [substrate]
        for role, record in report['roles'].items():
            if role.startswith('R17_'):
                b = record['bounds_xyz_mm']
                if (body and b[1] > 15) or (not body and b[4] < 0):
                    roles.append(role)
        add(name, roles, 'Gauges', rotation=None if body else along_y,
            note='PRINT-ONLY populated-board envelope. Plug gauges are separate so the board can load unplugged. Supports/fragile features may need finishing; no actual switch operation.')
    for ref in ('J3', 'J5', 'J6', 'J1', 'J7'):
        add('PlugGauge_'+ref, ['R17Mate_'+ref], 'Gauges', rotation=along_y,
            note='REMOVABLE PRINT-ONLY seated-plug envelope. Tape to the connector face after loading the board, or use the real mate. No functional socket/crimp is modeled.')
    add('TipBoardGauge', ['TipPCB', 'TipComponentEnvelope'], 'Gauges', rotation=along_y,
        note='PRINT-ONLY tip-board/component envelope; no temperature-sensing function.')
    add('BatteryGauge', ['PackPublishedGaugeR33'], 'Gauges',
        note='PRINT-ONLY 33 x8 x20 mm reference block. Battery remains unselected.')
    add('MotorGauge', ['MotorMaxEnvelope'], 'Gauges', rotation=along_y,
        note='PRINT-ONLY source capsule allowance. Printed mount does not establish vibration transfer or motor clamp performance.')
    add('PackConnectorGauge', ['P1PackMateSpace'], 'Gauges',
        note='PRINT-ONLY conditional coupled-connector/boot budget. Dress at the current position; actual connector and lead maxima unconfirmed.')
    add('TemperatureHeadGauge', ['PackNTCHeadR33_1'], 'Gauges', quantity=2,
        note='PRINT TWO; source NTC-head envelope. Tape to the battery gauge for the routing trial; not an actual sensor.')
    add('ChargingCableHousing', ['P1CableHousing'], 'ExternalCable', owner=charger, rotation=along_y,
        note='External insulating housing candidate. Dry fit first; contact/magnet/bond/current and cable grip remain unqualified.')
    for name in ['P1DockWire1', 'P1DockWire2', 'P1PackMateWire1', 'P1PackMateWire2',
                 'P1PackStockWire1', 'P1PackStockWire2']:
        obj = doc.addObject('PartDesign::Feature', name)
        obj.Shape = product.getObject(name).Shape.copy()
        obj.Label = name+' / REFERENCE ONLY / route actual flexible wire'
        groups['ReferenceWires'].addObject(obj)
        view_meshes[name] = mesh(obj.Shape, cache / (name+'.stl'))['sha256']
    # Real native sections for the interior picture, not a schematic cutaway.
    clip = Part.makeBox(200, 200, 50, App.Vector(-100, -50, -50))
    for name in ('Body', 'NoseCap', 'LowerFlangeSkin'):
        shape = doc.getObject(name).Shape.copy().common(clip.copy())
        path = cache / (name+'-half.stl')
        MeshPart.meshFromShape(Shape=shape, LinearDeflection=.06,
                              AngularDeflection=.15, Relative=False).write(str(path))
        view_meshes[name+'-half'] = sha(path)
    cap_overlap = product.getObject('KeyedBodyR25').Shape.copy().common(
        product.getObject('MotorSeatCapR25').Shape.copy()).Volume
    assert cap_overlap < 1e-5, ('Body/cap interference', cap_overlap)
    doc.recompute()
    native = out / 'P1DryFitKit.FCStd'
    doc.saveAs(str(native))
    hardware = [{'role': n, 'label': product.getObject(n).Label,
                 'bounds_xyz_mm': q['bounds_xyz_mm']} for n, q in report['roles'].items()
                if q['group'] == 'FastenerAllowances']
    result = {'native_sha256': sha(native), 'source_assembly_sha256': report['native_sha256'],
              'source_cable_sha256': cable_report['native_sha256'], 'builder_sha256': sha(Path(__file__)),
              'units': 'mm', 'unique_STLs': len(items), 'printed_piece_count': sum(q['quantity'] for q in items),
              'items': items, 'view_meshes_sha256': view_meshes,
              'body_cap_intersection_mm3': cap_overlap, 'hardware_envelopes_not_purchase_list': hardware,
              'scope': 'Closed single-solid part/gauge STLs, source-bound native fit assembly and nominal wire references. Print orientation is a starting pose, not a sliced or physically validated print. No product BOM adoption, selected pack, powered test, seal/cleaning or wear validation. Gauges do not prove actual connectors, component tolerances or switch/motor function.'}
    (out / 'kit-manifest.json').write_text(json.dumps(result, indent=2)+'\n')
    App.closeDocument(doc.Name)
    check = App.openDocument(str(native))
    check.recompute()
    for q in items:
        shape = check.getObject(q['name']).Shape
        assert shape.isValid() and len(shape.Solids) == 1
        assert abs(shape.Volume-q['volume_mm3']) < 1e-5
    App.closeDocument(check.Name)
    print('SAVED', len(items), 'unique STLs;', result['printed_piece_count'], 'pieces; native readback OK', flush=True)


if __name__ == '__main__':
    main()
