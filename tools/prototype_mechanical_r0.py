"""Build editable native FreeCAD packaging geometry and measure actual solids.

Run with FreeCAD's bundled Python. The body uses editable Sketcher meridians
and native revolutions, including endpoint tangent constraints at the nose.
Selected dimensions drive spreadsheet expressions; JSON regeneration remains
the complete parameter route. Component shapes are reservations, not models
of selected purchased parts.
"""
from pathlib import Path
import json
import math
import sys
import zipfile
import xml.etree.ElementTree as ET
import argparse

sys.path.insert(0, '/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as App
import Part
import Sketcher
import Mesh

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--revision', choices=['r0','r1'], default='r0')
parser.add_argument('--parameters', type=Path)
parser.add_argument('--output', type=Path)
args = parser.parse_args()
OUT = args.output.resolve() if args.output else ROOT / ('hardware/cad/prototype-'+args.revision)
OUT.mkdir(parents=True,exist_ok=True)
PARAMETERS_PATH = (args.parameters or OUT / 'parameters.json').resolve()
P = json.loads(PARAMETERS_PATH.read_text())
DOC = App.newDocument('ButtplugPrototype'+args.revision.upper())
sheet = DOC.addObject('Spreadsheet::Sheet', 'Parameters')
sheet.Label = args.revision.upper()+' packaging inputs — unapproved fit / supplier review'
sheet.set('A1', 'Parameter'); sheet.set('B1', 'mm'); sheet.set('C1', 'Study input; not a production specification')
for row, (name, value) in enumerate(((k, v) for k, v in P.items() if type(v) in (int, float)), 2):
    sheet.set(f'A{row}', name)
    sheet.set(f'B{row}', f'={value} mm')
    sheet.setAlias(f'B{row}', name)
sheet.setColumnWidth('A', 245)
sheet.setColumnWidth('C', 360)


def link(obj, prop, expression):
    obj.setExpression(prop, expression)


def native_cylinder(name, radius, height, x=0, y=0, z=0):
    obj = DOC.addObject('Part::Cylinder', name)
    obj.Radius = radius; obj.Height = height
    obj.Placement = App.Placement(App.Vector(x, y, z), App.Rotation(App.Vector(0, 0, 1), App.Vector(0, 1, 0)))
    return obj


def native_box(name, lx, ly, lz, x, y, z):
    obj = DOC.addObject('Part::Box', name)
    obj.Length = lx; obj.Width = ly; obj.Height = lz
    obj.Placement.Base = App.Vector(x, y, z)
    return obj


def fuse(name, objects):
    obj = DOC.addObject('Part::MultiFuse', name)
    obj.Shapes = objects
    obj.Refine = True
    return obj


def cut(name, base, tool):
    obj = DOC.addObject('Part::Cut', name)
    obj.Base = base; obj.Tool = tool; obj.Refine = True
    return obj


def common(name, base, tool):
    obj = DOC.addObject('Part::Common', name)
    obj.Base = base; obj.Tool = tool; obj.Refine = True
    return obj


def capsule(name, length, width, height, bottom_y):
    # X = anterior/posterior study axis, Y = tip direction, Z = left/right study axis.
    mid = native_box(name+'Web', length-width, height, width, -(length-width)/2, bottom_y, -width/2)
    left = native_cylinder(name+'Front', width/2, height, -(length-width)/2, bottom_y)
    right = native_cylinder(name+'Rear', width/2, height, (length-width)/2, bottom_y)
    return fuse(name, [mid, left, right])


def link_capsule(name, length, width, height, bottom_y):
    """Drive the native primitive capsule constituents from spreadsheet values."""
    web = DOC.getObject(name+'Web')
    for prop, expr in [('Length',f'({length}) - ({width})'),('Width',height),('Height',width),
                       ('Placement.Base.x',f'-(({length}) - ({width})) / 2'),
                       ('Placement.Base.y',bottom_y),('Placement.Base.z',f'-({width}) / 2')]:
        link(web,prop,expr)
    for suffix, sign in [('Front','-'),('Rear','')]:
        end = DOC.getObject(name+suffix)
        link(end,'Radius',f'({width}) / 2'); link(end,'Height',height)
        link(end,'Placement.Base.x',f'{sign}(({length}) - ({width})) / 2')
        link(end,'Placement.Base.y',bottom_y)


def section(name, y_expr, d_expr, y_value, diameter):
    sk = DOC.addObject('Sketcher::SketchObject', name)
    sk.Placement = App.Placement(App.Vector(0, y_value, 0), App.Rotation(App.Vector(1, 0, 0), 90))
    idx = sk.addGeometry(Part.Circle(App.Vector(0, 0, 0), App.Vector(0, 0, 1), diameter/2), False)
    sk.addConstraint(Sketcher.Constraint('Coincident', idx, 3, -1, 1))
    dc = sk.addConstraint(Sketcher.Constraint('Diameter', idx, diameter))
    link(sk, f'Constraints[{dc}]', d_expr)
    link(sk, 'Placement.Base.y', y_expr)
    return sk


def loft(name, profiles):
    obj = DOC.addObject('Part::Loft', name)
    obj.Sections = profiles; obj.Solid = True; obj.Ruled = False; obj.Closed = False
    return obj


def feature(name, shape, label):
    obj = DOC.addObject('Part::Feature', name)
    obj.Shape = shape; obj.Label = label
    return obj


def meridian_revolution(prefix, inner=False):
    """An editable closed profile with a tangent-constrained spherical nose.

    Endpoint tangents are passed to OCCT's C1 interpolation and also retained
    as native Sketcher constraints. Editing spline poles therefore preserves
    the neck and nose tangent connections instead of reintroducing a crease.
    Interior pole positions remain editable geometry, regenerated from JSON
    when all profile study dimensions need to be reapplied together.
    """
    wall = P['radial_wall_study'] if inner else 0.0
    radius = P['nose_radius_study'] - wall
    neck_radius = P['neck_outer_diameter']/2 - wall
    center_y = P['body_length'] - P['nose_radius_study']
    theta = math.radians(20)
    sin_a, cos_a = math.sin(theta), math.cos(theta)
    points = [App.Vector(neck_radius, P['neck_length'], 0)]
    for frac, ratio in [(.35,.88),(.56,1.0),(.75,.88),(.86,.59),(.90,.49)]:
        points.append(App.Vector(P['body_max_diameter']*ratio/2-wall, P['body_length']*frac, 0))
    points.append(App.Vector(radius*cos_a, center_y+radius*sin_a, 0))
    curve = Part.BSplineCurve()
    curve.interpolate(Points=points, InitialTangent=App.Vector(0,1,0),
                      FinalTangent=App.Vector(-sin_a,cos_a,0))
    sk = DOC.addObject('Sketcher::SketchObject', prefix+'Meridian')
    sk.Label = prefix+' editable meridian / C1 nose tangent'
    sk.addGeometry(Part.LineSegment(App.Vector(neck_radius,0,0),points[0]),False)
    sk.addGeometry(curve,False)
    sk.addGeometry(Part.ArcOfCircle(Part.Circle(App.Vector(0,center_y,0),App.Vector(0,0,1),radius),theta,math.pi/2),False)
    sk.addGeometry(Part.LineSegment(App.Vector(0,center_y+radius,0),App.Vector(0,0,0)),False)
    sk.addGeometry(Part.LineSegment(App.Vector(0,0,0),App.Vector(neck_radius,0,0)),False)
    constraints = [
        Sketcher.Constraint('Vertical',0),
        Sketcher.Constraint('DistanceX',0,1,neck_radius),
        Sketcher.Constraint('Distance',0,P['neck_length']),
        Sketcher.Constraint('Tangent',0,2,1,1),
        Sketcher.Constraint('Tangent',1,2,2,1),
        Sketcher.Constraint('Radius',2,radius),
        Sketcher.Constraint('DistanceX',2,3,0.0),
        Sketcher.Constraint('DistanceY',2,3,center_y),
        Sketcher.Constraint('DistanceY',2,1,center_y+radius*sin_a),
        Sketcher.Constraint('Coincident',2,2,3,1),
        Sketcher.Constraint('Vertical',3),
        Sketcher.Constraint('Coincident',3,2,-1,1),
        Sketcher.Constraint('Coincident',3,2,4,1),
        Sketcher.Constraint('Coincident',4,2,0,1),
        Sketcher.Constraint('Horizontal',4)]
    sk.addConstraint(constraints)
    radius_expr = 'Parameters.nose_radius_study' + (' - Parameters.radial_wall_study' if inner else '')
    neck_expr = 'Parameters.neck_outer_diameter / 2' + (' - Parameters.radial_wall_study' if inner else '')
    for index, expr in [(1,neck_expr),(2,'Parameters.neck_length'),(5,radius_expr),
                        (7,'Parameters.body_length - Parameters.nose_radius_study'),
                        (8,f'Parameters.body_length - Parameters.nose_radius_study + ({radius_expr}) * {sin_a}')]:
        link(sk,f'Constraints[{index}]',expr)
    sk.addProperty('App::PropertyString','EditRoute','Prototype')
    sk.EditRoute = 'Edit spline poles in Sketcher; native endpoint tangent constraints remain active. Regenerate from parameters.json to reapply all station dimensions.'
    if sk.solve() != 0:
        raise ValueError(prefix+' meridian constraints did not solve')
    rev = DOC.addObject('Part::Revolution',prefix+'BodyRevolution')
    rev.Source = sk; rev.Axis = App.Vector(0,1,0); rev.Base = App.Vector(0,0,0)
    rev.Angle = 360; rev.Solid = True
    return rev, sk


if args.revision == 'r1':
    import importlib.util
    spec = importlib.util.spec_from_file_location('mechanical_r1',ROOT/'hardware/cad/prototype-r1/build.py')
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    builder.build(globals())
    sys.exit(0)

outer, outer_meridian = meridian_revolution('Outer')
inner, inner_meridian = meridian_revolution('Inner',True)
shoulder = native_cylinder('MetalShoulder', P['metal_shoulder_diameter']/2, 1, y=-1)
link(shoulder, 'Radius', 'Parameters.metal_shoulder_diameter / 2')
shaft = native_cylinder('CaptureGrooveShaft', P['capture_groove_diameter']/2, 6, y=-7)
link(shaft, 'Radius', 'Parameters.capture_groove_diameter / 2')
collar = native_cylinder('CaptureLip', P['collar_outer_diameter']/2, 1, y=P['collar_bottom_y'])
link(collar, 'Radius', 'Parameters.collar_outer_diameter / 2')
link(collar, 'Placement.Base.y', 'Parameters.collar_bottom_y')
bore = native_cylinder('OpenNeckBore', P['neck_outer_diameter']/2-P['radial_wall_study'], 10, y=-9)
link(bore, 'Radius', 'Parameters.neck_outer_diameter / 2 - Parameters.radial_wall_study')
body = cut('MetalBody', fuse('OuterBodyAndCollar', [outer, shoulder, shaft, collar]), fuse('BodyCavity', [inner, bore]))
body.Label = 'Plan A hollow metal body — wall and casting details for supplier review'

L, W, D = P['flange_ap_length'], P['flange_lr_width'], P['flange_depth']
outer_base = capsule('FlangeOuterBlank', L, W, D, -D)
link_capsule('FlangeOuterBlank','Parameters.flange_ap_length','Parameters.flange_lr_width',
             'Parameters.flange_depth','-Parameters.flange_depth')
contour = DOC.addObject('Part::Cylinder', 'PelvicContourTool')
contour.Radius = P['flange_contour_radius']; contour.Height = W+4
contour.Placement.Base = App.Vector(-P['posterior_contour_offset'], -P['flange_contour_radius'], -W/2-2)
for prop,expr in [('Radius','Parameters.flange_contour_radius'),('Height','Parameters.flange_lr_width + 4 mm'),
                  ('Placement.Base.x','-Parameters.posterior_contour_offset'),
                  ('Placement.Base.y','-Parameters.flange_contour_radius'),
                  ('Placement.Base.z','-Parameters.flange_lr_width / 2 - 2 mm')]:
    link(contour,prop,expr)
contoured = common('FlangeContouredBlank', outer_base, contour)
platform = native_cylinder('JointSeatPlatform', 20, 5, y=-5)
outer_base = fuse('FlangeOuterWithSeat', [contoured, platform])
inner_base = capsule('FlangeCavityBlank', L-4, W-4, D+2, -D-2)
link_capsule('FlangeCavityBlank','Parameters.flange_ap_length - 2 * Parameters.flange_wall',
             'Parameters.flange_lr_width - 2 * Parameters.flange_wall',
             'Parameters.flange_depth + 2 mm','-Parameters.flange_depth - 2 mm')
inner_contour = DOC.addObject('Part::Cylinder', 'FlangeRoofTool')
inner_contour.Radius = P['flange_contour_radius']-P['flange_roof']; inner_contour.Height = W+4
inner_contour.Placement.Base = contour.Placement.Base
for prop,expr in [('Radius','Parameters.flange_contour_radius - Parameters.flange_roof'),
                  ('Height','Parameters.flange_lr_width + 4 mm'),
                  ('Placement.Base.x','-Parameters.posterior_contour_offset'),
                  ('Placement.Base.y','-Parameters.flange_contour_radius'),
                  ('Placement.Base.z','-Parameters.flange_lr_width / 2 - 2 mm')]:
    link(inner_contour,prop,expr)
cavity = common('FlangeCavity', inner_base, inner_contour)
flange_shell = cut('FlangeHollowBlank', outer_base, cavity)
neck_port = native_cylinder('FlangeNeckPort', 15.25, D+4, y=-D-2)
link(neck_port,'Height','Parameters.flange_depth + 4 mm')
link(neck_port,'Placement.Base.y','-Parameters.flange_depth - 2 mm')
shoulder_pocket = native_cylinder('ShoulderPocket', 17.25, 4, y=-2)
retainer_pocket = native_cylinder('RetainerPocket', 18.25, 3.0, y=-7.0)
flange = cut('PolymerFlange', flange_shell, fuse('FlangeJointPockets', [neck_port, shoulder_pocket, retainer_pocket]))
flange.Label = 'Whole polymer flange — contoured envelope, open service side'

bosses, cover_holes, insert_holes = [], [], []
for i, (x,z) in enumerate([(-24,-14),(-24,14),(24,-14),(24,14)]):
    bosses.append(native_cylinder(f'CoverBoss{i}', 3.5, D-5, x=x, y=-D, z=z))
    insert_holes.append(native_cylinder(f'InsertStudyBore{i}', P['cover_boss_bore_study']/2, 8, x=x, y=-D-.1, z=z))
    cover_holes.append(native_cylinder(f'CoverClearance{i}', P['cover_screw_clearance']/2, 5, x=x, y=-D-4, z=z))
    link(bosses[-1],'Height','Parameters.flange_depth - 5 mm')
    link(bosses[-1],'Placement.Base.y','-Parameters.flange_depth')
    link(insert_holes[-1],'Radius','Parameters.cover_boss_bore_study / 2')
    link(insert_holes[-1],'Placement.Base.y','-Parameters.flange_depth - 0.1 mm')
    link(cover_holes[-1],'Radius','Parameters.cover_screw_clearance / 2')
    link(cover_holes[-1],'Placement.Base.y','-Parameters.flange_depth - 4 mm')
flange = cut('FlangeWithBosses', fuse('FlangeAndBosses', [flange]+bosses), fuse('InsertBoreTools', insert_holes))
flange.Label = 'Polymer flange housing — insert bores are reservations, insert not selected'
cover = cut('ServiceCover', capsule('CoverBlank', L-1, W-1, P['cover_thickness'], -D-P['cover_thickness']), fuse('CoverScrewHoles', cover_holes))
link_capsule('CoverBlank','Parameters.flange_ap_length - 1 mm','Parameters.flange_lr_width - 1 mm',
             'Parameters.cover_thickness','-Parameters.flange_depth - Parameters.cover_thickness')
cover.Label = 'Outward service cover — screw clearances, perimeter seal still to detail'

ring = cut('SplitRetainerRing', native_cylinder('RetainerOuter', P['retainer_outer_diameter']/2, P['retainer_thickness'], y=P['retainer_bottom_y']), native_cylinder('RetainerInner', P['retainer_inner_diameter']/2, 4, y=P['retainer_bottom_y']-1))
front = common('FrontRetainer', ring, native_box('FrontRetainerHalfSpace', 30, 5, 50, -30.25, P['retainer_bottom_y']-1, -25))
rear = common('RearRetainer', ring, native_box('RearRetainerHalfSpace', 30, 5, 50, .25, P['retainer_bottom_y']-1, -25))
front.Label = 'Split capture retainer / anterior half — fastening/preload unresolved'
rear.Label = 'Split capture retainer / posterior half — fastening/preload unresolved'
gasket_shape = Part.makeCylinder(16.8, P['seal_reservation_thickness'], App.Vector(0,-2,0), App.Vector(0,1,0)).cut(Part.makeCylinder(15.3, 3, App.Vector(0,-3,0), App.Vector(0,1,0)))
gasket = feature('FaceSealReservation', gasket_shape, 'Face-seal volume only — compound, groove and compression unresolved')

xh = P['pcb_crossbar_length']/2; by = P['pcb_crossbar_bottom_y']; ty = by+P['pcb_crossbar_depth']
n, b = P['pcb_neck_width']/2, P['pcb_tongue_width']/2
xy = [(-xh,by),(xh,by),(xh,ty-3),(25,ty),(n,ty),(n,20),(b,30),(b,74),(3,P['pcb_tip_y']),(-3,P['pcb_tip_y']),(-b,74),(-b,30),(-n,20),(-n,ty),(-xh,ty)]
poly = Part.makePolygon([App.Vector(x,y,P['pcb_min_z']) for x,y in xy]+[App.Vector(*xy[0],P['pcb_min_z'])])
pcb = feature('TBoardReservation', Part.Face(Part.Wire(poly.Edges)).extrude(App.Vector(0,0,P['pcb_thickness'])), 'Single T-shaped PCB reservation — no circuit placement; tongue narrowed for insertion')
motor = native_cylinder('MotorReservation', P['motor_reservation_diameter']/2, P['motor_reservation_length'], y=P['motor_start_y'], z=P['motor_center_z'])
for prop,expr in [('Radius','Parameters.motor_reservation_diameter / 2'),
                  ('Height','Parameters.motor_reservation_length'),
                  ('Placement.Base.y','Parameters.motor_start_y'),('Placement.Base.z','Parameters.motor_center_z')]:
    link(motor,prop,expr)
motor.Label = 'Motor space claim Ø13 ×34 — candidate NFP-E1015 not confirmed'
bx,by,bz = P['pack_reservation_min_xyz']; sx,sy,sz = P['pack_reservation_xyz']
pack = native_box('PackReservation', sx,sy,sz,bx,by,bz)
pack.Label = 'Candidate Bitcraze 350mAh envelope only — cable, adapter and NTC not fitted'
rails = []
for x in (-8.2,7.2):
    rails.append(native_box('BoardGuideLeft' if x<0 else 'BoardGuideRight',1,58,2,x,22,-6.8))
carrier = fuse('CarrierGuideStudy', rails)
carrier.Label = 'Dielectric board-guide study — motor retention and assembly attachment open'

DOC.recompute()
parts = [body, flange, cover, front, rear, gasket, pcb, motor, pack, carrier]
for o in DOC.Objects:
    if getattr(o, 'ViewObject', None) is not None:
        o.ViewObject.Visibility = o in parts
colors = [(0.72,0.77,0.83),(0.22,0.34,0.49),(0.25,0.39,0.55),(0.72,0.5,0.24),(0.72,0.5,0.24),(0.18,0.62,0.52),(0.17,0.57,0.36),(0.76,0.51,0.22),(0.39,0.64,0.78),(0.8,0.8,0.7)]
for o,color in zip(parts,colors):
    if getattr(o, 'ViewObject', None) is not None:
        o.ViewObject.ShapeColor = color
    o.addProperty('App::PropertyString','ReleaseBoundary','Prototype')
    o.ReleaseBoundary = 'R0 packaging development — not fabrication, body-contact or electrical validation'

report = {'revision':P['revision'], 'freecad_version':App.Version(), 'units':'mm', 'parts':{}, 'collisions':[], 'assembly_insertion':{}, 'open_items':['Anatomical fit and flange size unapproved','Supplier review of casting process, wall, finish and joint','Retainer fastening/preload and both seal designs','Actual battery, wiring and full populated board envelopes','Motor retention, supports and final carrier','Local controls, charging-contact mount and RF volume','Finished material/thermal/cleaning evaluation']}
for o in parts:
    s = o.Shape
    if s.isNull():
        print('NULL FINAL SHAPE', o.Name, o.State)
        for item in DOC.Objects:
            if hasattr(item, 'Shape') and item.Shape.isNull():
                print('NULL DEPENDENCY', item.Name, item.State, getattr(item, 'ExpressionEngine', []))
        DOC.saveAs(str(OUT/'debug-incomplete.FCStd'))
        raise ValueError(f'{o.Name} has a null shape')
    points, faces = s.tessellate(.18)
    sampled_bounds = [max(v[i] for v in points)-min(v[i] for v in points) for i in range(3)]
    report['parts'][o.Name] = {'valid':s.isValid(), 'solids':len(s.Solids), 'volume_mm3':s.Volume, 'conservative_occt_bounds_xyz_mm':[s.BoundBox.XLength,s.BoundBox.YLength,s.BoundBox.ZLength], 'tessellated_bounds_xyz_mm':sampled_bounds, 'bounds_note':'OCCT B-spline bounds can be loose; mesh bounds approximate actual extents at 0.18 mm tessellation, not a precision dimension inspection'}
    if not s.isValid() or len(s.Solids)!=(2 if o is carrier else 1):
        raise ValueError(f'{o.Name} is invalid or not a single solid')
    s.exportStep(str(OUT/(o.Name+'.step')))
    mesh = Mesh.Mesh(s.tessellate(.18)); mesh.write(str(OUT/(o.Name+'.stl')))
for i,a in enumerate(parts):
    for b in parts[i+1:]:
        vol=a.Shape.common(b.Shape).Volume
        if vol>1e-5: report['collisions'].append({'a':a.Name,'b':b.Name,'overlap_mm3':vol})
# Conservative continuous insertion envelopes over the metal-body Y extent.
# The PCB sweep uses its widest stem all the way down to the opening; this
# contains every translated stem position rather than sampling discrete poses.
half_stem=P['pcb_tongue_width']/2
sweep_xy=[(-half_stem,-9),(half_stem,-9),(half_stem,74),(3,P['pcb_tip_y']),(-3,P['pcb_tip_y']),(-half_stem,74)]
sweep_wire=Part.makePolygon([App.Vector(x,y,P['pcb_min_z']) for x,y in sweep_xy]+[App.Vector(*sweep_xy[0],P['pcb_min_z'])])
board_sweep=Part.Face(Part.Wire(sweep_wire.Edges)).extrude(App.Vector(0,0,P['pcb_thickness']))
motor_sweep=Part.makeCylinder(P['motor_reservation_diameter']/2,P['motor_start_y']+P['motor_reservation_length']+9,App.Vector(0,-9,P['motor_center_z']),App.Vector(0,1,0))
guide_sweeps=[Part.makeBox(1,89,2,App.Vector(x,-9,-6.8)) for x in (-8.2,7.2)]
overlaps={name:shape.common(body.Shape).Volume for name,shape in [('board',board_sweep),('motor',motor_sweep),('left_guide',guide_sweeps[0]),('right_guide',guide_sweeps[1])]}
report['assembly_insertion']={'translation_axis':'Y','method':'Continuous conservative sweep envelopes of inserted board, motor and guide reservations over all metal-body Y positions','metal_overlap_mm3_by_envelope':overlaps,'passes_nominal_continuous_envelope':all(v<1e-5 for v in overlaps.values()),'scope':'Rigid dummy geometry only; crossbar stays outside metal body. No wire/lead, populated PCB, tolerance, fastening or physical assembly validation.'}
report['pcb_outline_vertices_xy_mm']=xy
profile_checks = {}
for name,sk in [('outer',outer_meridian),('inner',inner_meridian)]:
    neck_tangent = sk.Geometry[0].tangent(sk.Geometry[0].LastParameter)[0]
    spline_start = sk.Geometry[1].tangent(sk.Geometry[1].FirstParameter)[0]
    spline_end = sk.Geometry[1].tangent(sk.Geometry[1].LastParameter)[0]
    cap_start = sk.Geometry[2].tangent(sk.Geometry[2].FirstParameter)[0]
    join_point = sk.Geometry[1].value(sk.Geometry[1].LastParameter)
    revolution = outer if name == 'outer' else inner
    join_normals = []
    for face in revolution.Shape.Faces:
        if type(face.Surface).__name__ != 'Plane' and face.distToShape(Part.Vertex(join_point))[0] < 1e-5:
            u,v = face.Surface.parameter(join_point)
            join_normals.append(face.normalAt(u,v))
    if len(join_normals) != 2:
        raise ValueError(name+' nose join does not have the expected two adjacent faces')
    normal_angle = math.degrees(math.acos(max(-1,min(1,abs(join_normals[0].dot(join_normals[1]))))))
    profile_checks[name] = {
        'neck_to_spline_tangent_angle_deg':math.degrees(neck_tangent.getAngle(spline_start)),
        'spline_to_spherical_cap_tangent_angle_deg':math.degrees(spline_end.getAngle(cap_start)),
        'revolved_surface_join_normal_angle_deg':normal_angle,
        'native_sketch_tangent_constraints':True,
        'solver_status':sk.solve()}
    if profile_checks[name]['solver_status'] != 0 or max(normal_angle,profile_checks[name]['neck_to_spline_tangent_angle_deg'],profile_checks[name]['spline_to_spherical_cap_tangent_angle_deg']) > 1e-4:
        raise ValueError(name+' meridian lost endpoint tangent continuity')
report['nose_continuity'] = {
    'construction':'Editable native Sketcher C1-interpolated meridians with endpoint Tangent constraints, exact circular nose arcs and Part::Revolution features',
    'outer_spherical_radius_mm':P['nose_radius_study'],
    'tip_y_mm':body.Shape.BoundBox.YMax,
    'checks':profile_checks,
    'scope':'Tangent/normal continuity at nominal geometry; no C2 curvature, minimum wall, finished-surface or anatomical validation'}
clearance_parts = [body,flange,cover,front,rear,gasket,pcb]
pack_distances = {o.Name:round(pack.Shape.distToShape(o.Shape)[0],6) for o in clearance_parts}
report['pack_nominal_clearances'] = {
    'pack_min_xyz_mm':P['pack_reservation_min_xyz'],
    'pack_size_xyz_mm':P['pack_reservation_xyz'],
    'flange_depth_mm':P['flange_depth'],
    'distances_mm':pack_distances,
    'minimum_mm':min(pack_distances.values()),
    'passes_1_5mm_nominal_screen':all(v >= 1.5-1e-6 for v in pack_distances.values()),
    'scope':'Nominal solids only; excludes supplier tolerances, pouch allowance, cradle, cable, connector, adapter and NTC'}
report['parameter_editing'] = {
    'native':'Body meridians/revolutions, selected flange primitives and motor dimensions have native editable geometry/expressions',
    'complete_parameter_route':'Edit parameters.json and regenerate; interior spline station/pole positions, PCB outline, carrier and several joint studies are not all driven by spreadsheet expressions'}
section_box=Part.makeBox(160,180,60,App.Vector(-80,-50,0))
for o in (body,flange,cover):
    clipped=o.Shape.cut(section_box)
    Mesh.Mesh(clipped.tessellate(.18)).write(str(OUT/(o.Name+'-section.stl')))
DOC.recompute()
DOC.saveAs(str(OUT/'ButtplugPrototypeR0.FCStd'))
Part.export(parts,str(OUT/'ButtplugPrototypeR0.step'))
# Headless FreeCAD does not create ViewObjects. Persist only the ordinary
# SchemaVersion=1 Visibility booleans verified in a GUI-saved FCStd, without
# material-array files or any geometry substitution. GUI appearance itself is
# not validated by creating this XML.
view_root = ET.Element('Document',SchemaVersion='1',HasExpansion='1')
ET.SubElement(view_root,'Expand',count='0')
view_data = ET.SubElement(view_root,'ViewProviderData',Count=str(len(DOC.Objects)))
for rank,obj in enumerate(DOC.Objects):
    vp = ET.SubElement(view_data,'ViewProvider',name=obj.Name,expanded='0',treeRank=str(rank))
    props = ET.SubElement(vp,'Properties',Count='1',TransientCount='0')
    prop = ET.SubElement(props,'Property',name='Visibility',type='App::PropertyBool',status='1')
    ET.SubElement(prop,'Bool',value='true' if obj in parts else 'false')
with zipfile.ZipFile(OUT/'ButtplugPrototypeR0.FCStd','a',compression=zipfile.ZIP_DEFLATED) as archive:
    if 'GuiDocument.xml' not in archive.namelist():
        archive.writestr('GuiDocument.xml',ET.tostring(view_root,encoding='utf-8',xml_declaration=True))
report['native_view_state'] = {
    'visible_final_objects':[o.Name for o in parts],
    'hidden_construction_objects':len(DOC.Objects)-len(parts),
    'scope':'Persisted visibility flags only; no GUI visual inspection claimed'}
(OUT/'geometry-report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'native':str(OUT/'ButtplugPrototypeR0.FCStd'),'valid_feature_count':len(report['parts']),'collisions':report['collisions'],'insertion':report['assembly_insertion']},indent=2))
App.closeDocument(DOC.Name)
