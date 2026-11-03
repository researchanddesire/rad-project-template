"""Integral P1 cover: connected button bosses and bonded charging targets.

Called by the P1 assembly builder. Existing geometry stays as a construction
reference; new features are editable native primitives/booleans.
"""
import itertools
import FreeCAD as App
import Part


def build(doc, active_names):
    base = doc.getObject('ButtonServiceCoverR31')
    additions = []
    tools = []

    def box(name, bounds):
        x, y, z, u, v, w = bounds
        obj = doc.addObject('Part::Box', name)
        obj.Length, obj.Width, obj.Height = u-x, v-y, w-z
        obj.Placement.Base = App.Vector(x, y, z)
        return obj

    def cyl(name, radius, x, y, z, length):
        obj = doc.addObject('Part::Cylinder', name)
        obj.Radius, obj.Height = radius, length
        obj.Placement = App.Placement(App.Vector(x, y, z),
                                     App.Rotation(App.Vector(0, 0, 1), App.Vector(0, 1, 0)))
        return obj

    def fuse(name, a, b):
        obj = doc.addObject('Part::Fuse', name)
        obj.Base, obj.Tool, obj.Refine = a, b, True
        return obj

    def cut(name, a, b):
        obj = doc.addObject('Part::Cut', name)
        obj.Base, obj.Tool, obj.Refine = a, b, True
        return obj

    def common_volume(a, b):
        aa, bb = a.BoundBox, b.BoundBox
        if any(min(getattr(aa, k+'Max'), getattr(bb, k+'Max')) <=
               max(getattr(aa, k+'Min'), getattr(bb, k+'Min')) + 1e-7 for k in 'XYZ'):
            return 0.
        return a.copy().common(b.copy()).Volume

    # Two bezel posts join directly to the rear plate, outside the membrane.
    for i, (x, z) in enumerate([(-26.8, 1.8), (-9.2, 9.)], 1):
        additions.append(cyl('P1BezelPostBridge'+str(i), 1.9, x, -27.5, z, 2.1))
        tools.append(cyl('P1BezelPilot'+str(i), .625, x, -28.1, z, 4.2))
    # Connect the small second guide to its stop boss, then to the cover above
    # the silicone rim. The inter-button wire corridor remains open.
    additions += [
        box('P1GuideToStopRib', [-16., -25.4, 5.8, -14.7, -24.3, 6.6]),
        box('P1StopUprightRib', [-16.05, -25.45, 9.3, -14.65, -24.15, 11.5]),
        box('P1StopToPlateRib', [-16.05, -27.65, 10.7, -14.65, -24.15, 11.5]),
        # Replace the old insert window with cover material. No separate insert.
        box('P1ContactWindowFill', [-32.5, -30., 5.9, -27.5, -27.35, 14.1]),
    ]
    # Preserve the existing bezel seat where the old dock window and button
    # recess share a corner. Shift the two contact axes left to give real wall.
    tools.append(box('P1PreservedBezelSeat', [-29.1, -30.1, -.1, -6.9, -28., 11.1]))
    contacts = []
    allowances = []
    for tag, z in [('Ground', 8.), ('Positive', 12.)]:
        x = -32.
        additions.append(cyl('P1'+tag+'ContactBoss', 1.8, x, -27.6, z, 3.1))
        tools += [cyl('P1'+tag+'StemClearance', .8, x, -30.1, z, 5.7),
                  cyl('P1'+tag+'HeadSeat', .97, x, -30.1, z, .86),
                  cyl('P1'+tag+'RearWell', 1.3, x, -27.3, z, 2.9)]
        head = cyl('P1'+tag+'ContactHead', .915, x, -30., z, .76)
        stem = cyl('P1'+tag+'ContactStem', .675, x, -29.24, z, 3.53)
        contact = fuse('P1'+tag+'Contact', head, stem)
        contact.Label = tag+' target / Mill-Max 1941 nominal reference / fit to received part'
        contacts.append(contact)
        outer = cyl('P1'+tag+'PottingOuter', 1.3, x, -27.3, z, 2.4)
        inner = cyl('P1'+tag+'PottingCore', .675, x, -27.4, z, 2.6)
        fill = cut('P1'+tag+'EncapsulationAllowance', outer, inner)
        fill.Label = 'Insulating rear seal/retention process SPACE / material and adhesion unqualified'
        allowances.append(fill)
    magnets = []
    for tag, x, z in [('Left', -37.75, 0.), ('Right', -21., -8.)]:
        magnet = cyl('P1'+tag+'Magnet', 2., x, -29.2, z, 1.5)
        magnet.Label = 'Magnet reference D4 x1.5 / bond in existing blind pocket'
        magnets.append(magnet)
        # Pocket exists in the source cover. A thin rear encapsulation cap
        # captures the magnet without a dedicated screw-on keeper.
        fill = cyl('P1'+tag+'MagnetEncapsulationAllowance', 2.15, x, -27.7, z, 1.)
        fill.Label = 'Rear magnet bond/cap process SPACE / material and adhesion unqualified'
        allowances.append(fill)
    solid = base
    for i, obj in enumerate(additions):
        solid = fuse('P1CoverUnion'+str(i), solid, obj)
    for i, obj in enumerate(tools):
        solid = cut('P1FlangeCover' if i == len(tools)-1 else 'P1CoverCut'+str(i), solid, obj)
    doc.recompute()
    cover = solid
    cover.Label = 'One-piece P1 flange cover / integral contact seats / bonded magnet pockets'
    doc.recompute()
    assert cover.Shape.isValid() and len(cover.Shape.Solids) == 1, 'Cover must be one connected solid'
    fixed = [n for n in active_names if n != base.Name]
    installed = [cover] + contacts + magnets
    hits = []
    inherited = []
    screw_interfaces = []
    added = cover.Shape.copy().cut(base.Shape.copy())
    for obj in installed:
        for name in fixed:
            target = doc.getObject(name).Shape
            volume = common_volume(obj.Shape, target)
            if volume < 1e-5:
                continue
            row = {'a': obj.Name, 'b': name, 'intersection_mm3': volume}
            if obj == cover and name in ('ButtonRetainerScrewR31_1', 'ButtonRetainerScrewR31_2'):
                screw_interfaces.append(row)
            elif obj == cover and common_volume(added, target) < 1e-5:
                inherited.append(row)
            else:
                hits.append(row)
    for a, b in itertools.combinations(installed, 2):
        volume = common_volume(a.Shape, b.Shape)
        if volume > 1e-5:
            hits.append({'a': a.Name, 'b': b.Name, 'intersection_mm3': volume})
    print('P1 cover connected; new installed collisions:', hits, flush=True)
    return {
        'objects': installed + allowances,
        'construction': [o for o in doc.Objects if o.Name.startswith('P1') and
                         o not in installed + allowances] + [base],
        'review': {
            'cover_valid_single_solid': True,
            'source_cover_solids': len(base.Shape.Solids),
            'added_material_mm3': added.Volume,
            'unexpected_intersections': hits,
            'inherited_cover_interfaces': inherited,
            'named_unmodeled_screw_pilot_interfaces': screw_interfaces,
            'contact_face_xyz_mm': {'GND': [-32, -30, 8], 'DOCK_5V': [-32, -30, 12]},
            'new_retention_fasteners': 0,
            'scope': 'Nominal installed hard-part check only. Contacts and magnets are dimensional references. Potting/seal shapes are process allowances, not qualified materials, bond, force, leakage or magnetic holding results.'
        }
    }
