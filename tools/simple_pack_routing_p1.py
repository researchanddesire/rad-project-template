"""Make room for the dock leads by dressing the unselected pack mate forward.

Same connector space budget, pack/body endpoints, boards and hub geometry.
The mating pigtail uses a single broad return bend instead of an S bend.
"""
import math
import FreeCAD as App
import Part


def build(doc, active_names):
    from simple_charging_wires_p1 import overlap
    old_names = ['PackMateProcessSpaceR37'] + [prefix+str(pin) for pin in (1, 2)
                 for prefix in ('StockPackLeadR37_', 'SpareMateLeadR37_')]
    fixed = {n: doc.getObject(n).Shape for n in active_names if n not in old_names}
    objects, construction, paths = [], [], []
    yc, zc = -17., -12.8
    n = App.Vector(0, math.cos(math.radians(20)), math.sin(math.radians(20)))
    root = App.Vector(7, -20, -9)
    delta = App.Vector(0, yc-root.y, zc-root.z)
    theta = math.acos(1-delta.Length/22)
    shrink_x = 7-22*math.sin(theta)-(21.8-22*theta)
    stock_x, male_x = shrink_x-4, shrink_x-18.8

    def box(name, x0, x1, width, thick):
        obj = doc.addObject('Part::Box', name)
        obj.Length, obj.Width, obj.Height = x1-x0, width, thick
        rotation = App.Rotation(App.Vector(1, 0, 0), 20)
        # Assign the complete placement; nested Placement.Base edits can be copies.
        obj.Placement = App.Placement(App.Vector(0, yc, zc)+
                                     rotation.multVec(App.Vector(x0, -width/2, -thick/2)), rotation)
        construction.append(obj)
        return obj

    housing = box('P1PackConnectorBox', male_x-.8, stock_x+.8, 8.8, 4.2)
    shrink = box('P1PackConnectorBootSpace', stock_x-.8, stock_x+4., 6.4, 4.2)
    coupler = doc.addObject('Part::Fuse', 'P1PackMateSpace')
    coupler.Base, coupler.Tool, coupler.Refine = housing, shrink, True
    coupler.Label = 'Unselected protected-pack mate / same space budget / forward1.8, down0.4'
    objects.append(coupler)

    def sweep(name, edges, radius, label):
        spine = doc.addObject('Part::Feature', name+'Path')
        spine.Shape = Part.Wire(edges)
        profile = doc.addObject('Part::Feature', name+'Profile')
        profile.Shape = Part.Wire([Part.makeCircle(radius, edges[0].Vertexes[0].Point,
                                                  edges[0].tangentAt(edges[0].FirstParameter))])
        obj = doc.addObject('Part::Sweep', name)
        obj.Sections, obj.Spine, obj.Solid, obj.Frenet = [profile], spine, True, False
        obj.Label = label
        doc.recompute()
        assert obj.Shape.isValid() and len(obj.Shape.Solids) == 1
        construction.extend([spine, profile])
        objects.append(obj)
        return obj

    for pin, sign in ((1, 1), (2, -1)):
        start, direction = root+n*sign, App.Vector(-1, 0, 0)
        transverse = delta/delta.Length
        middle = start+direction*(11*math.sin(theta))+transverse*(11*(1-math.cos(theta)))
        end = start+direction*(22*math.sin(theta))+delta
        a = start+direction*(11*math.sin(theta/2))+transverse*(11*(1-math.cos(theta/2)))
        b = end-direction*(11*math.sin(theta/2))-transverse*(11*(1-math.cos(theta/2)))
        endpoint = App.Vector(shrink_x, yc, zc)+n*sign
        stock_edges = [Part.Arc(start, a, middle).toShape(), Part.Arc(middle, b, end).toShape(),
                       Part.makeLine(end, endpoint)]
        stock = sweep('P1PackStockWire'+str(pin), stock_edges, .9,
                      'Protected-pack lead / OD1.8 and exit/length remain receiving conditions')
        assert abs(sum(e.Length for e in stock_edges)-21.8) < 1e-6
        # Preserve the original body-wire, bare-tail and solder-joint positions.
        bare = fixed['SpareMateBareR37_'+str(pin)].BoundBox
        target = App.Vector(bare.XMin, bare.Center.y, bare.Center.z)
        start = App.Vector(male_x, yc, zc)+n*sign
        transverse = App.Vector(0, target.y-start.y, target.z-start.z)
        radius, end = transverse.Length/2, start+transverse
        assert target.x > end.x
        mate_edges = [Part.Arc(start, start+App.Vector(-radius, 0, 0)+transverse/2, end).toShape(),
                      Part.makeLine(end, target)]
        mate = sweep('P1PackMateWire'+str(pin), mate_edges, .6,
                     'Prewired mate / one broad return bend / trim only after received fit')
        for section, obj, es, r in [('stock', stock, stock_edges, 11.),
                                    ('mate', mate, mate_edges, radius)]:
            for a, b in zip(es, es[1:]):
                assert (a.Vertexes[-1].Point-b.Vertexes[0].Point).Length < 1e-6
                assert a.tangentAt(a.LastParameter).dot(b.tangentAt(b.FirstParameter)) > 1-1e-6
            paths.append({'pin': pin, 'role': obj.Name, 'section': section,
                          'path_length_mm': sum(e.Length for e in es),
                          'minimum_centreline_radius_mm': r,
                          'start_xyz_mm': list(es[0].Vertexes[0].Point),
                          'end_xyz_mm': list(es[-1].Vertexes[-1].Point)})
    hits, intentional = [], []
    for obj in objects:
        for name, shape in fixed.items():
            volume = overlap(obj.Shape, shape)
            if volume <= 1e-5:
                continue
            row = {'a': obj.Name, 'b': name, 'intersection_mm3': volume}
            matching_joint = obj.Name.startswith('P1PackMateWire') and name == 'PackPowerJointSpaceR37_'+obj.Name[-1]
            (intentional if matching_joint else hits).append(row)
    for i, a in enumerate(objects):
        for b in objects[i+1:]:
            volume = overlap(a.Shape, b.Shape)
            if volume > 1e-5:
                row = {'a': a.Name, 'b': b.Name, 'intersection_mm3': volume}
                (intentional if coupler in (a, b) else hits).append(row)
    assert not hits, hits
    return {'objects': objects,
            'construction': construction+[doc.getObject(n) for n in old_names],
            'replaced_active_names': old_names,
            'review': {'connector_centre_YZ_mm': [yc, zc],
                       'previous_connector_centre_YZ_mm': [-18.8, -12.4],
                       'paths': paths, 'unexpected_intersections': hits,
                       'named_connector_and_joint_interfaces': intentional,
                       'unchanged': ['Metal body/cap', 'Boards', 'Hubs and retention parts',
                                     'Pack body/lead roots', 'Body power wires', 'All bare tails and joints'],
                       'new_custom_parts': 0, 'new_fasteners': 0,
                       'scope': 'Nominal revised dressing of existing conditional pack/mate envelopes. No connector or pack selected. Stock lead21.8mm / OD1.8, mating OD1.2, real bend limits, supplied usable length, insulation/termination and hand dressing need receiving/fit trials. No battery, BOM, wire rating, pull strength or physical assembly acceptance.'}}
