"""R36 sensor-lead and insulated-joint study, starting from R34J/R35F.

Moves the two sensor/guard assemblies +10X; source body/boards/motor stay fixed.
Routes actual-length factory lead allowances, not four short orphan stubs.
"""
from pathlib import Path
import hashlib
import json
import math
import sys
sys.path.insert(0, '/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part
import Sketcher

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'hardware/cad/pack-harness-r34/pigtail-j'
OUT = Path(sys.argv[1]).resolve()
OUT.mkdir(parents=True, exist_ok=True)
assert not any(OUT.iterdir())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
r = json.loads((SOURCE / 'geometry-report.json').read_text())
source = SOURCE / 'PackPigtailTransitR34.FCStd'
before = sha(source)
assert before == r['native_sha256']
D = A.openDocument(str(source))

def box_shape(b):
    x, y, z, u, v, w = b
    return Part.makeBox(u-x, v-y, w-z, A.Vector(x, y, z))

def feature(name, shape, label):
    obj = D.addObject('PartDesign::Feature', name)
    obj.Shape = shape
    obj.Label = label
    return obj

def volume(a, b):
    u, v = a.BoundBox, b.BoundBox
    if any(min(getattr(u, k+'Max'), getattr(v, k+'Max')) <=
           max(getattr(u, k+'Min'), getattr(v, k+'Min'))+1e-7 for k in 'XYZ'):
        return 0.
    return a.copy().common(b.copy()).Volume

def inventory(shape):
    b = shape.optimalBoundingBox(False, False)
    return {'valid': shape.isValid(), 'solids': len(shape.Solids), 'volume_mm3': shape.Volume,
            'bounds_xyz_mm': [getattr(b, k) for k in ['XMin','YMin','ZMin','XMax','YMax','ZMax']]}

def sweep(name, edges, origin, radius, label):
    path = feature(name+'Path', Part.Wire(edges), 'Exact tangent native path')
    profile = D.addObject('Sketcher::SketchObject', name+'Profile')
    profile.Placement = A.Placement(origin, A.Rotation(A.Vector(0,0,1), A.Vector(-1,0,0)))
    profile.addGeometry(Part.Circle(A.Vector(), A.Vector(0,0,1), radius), False)
    obj = D.addObject('Part::Sweep', name)
    obj.Sections = [profile]
    obj.Spine = path
    obj.Solid = True
    obj.Frenet = True
    obj.Label = label
    D.recompute()
    assert obj.Shape.isValid() and len(obj.Shape.Solids) == 1, name
    return obj

moved = []
prefixes = ['PackNTCHeadR33_', 'PackNTCContactFilmR33_', 'PackNTCLeadStubR33_',
            'PackNTCMotionR33_', 'PackNTCWindowR33_', 'PackGuardBlankR33_']
for obj in D.Objects:
    if any(obj.Name.startswith(p) for p in prefixes):
        obj.Placement.Base += A.Vector(10, 0, 0)
        moved.append(obj.Name)
D.recompute()

# Sensor pair pitch is unchanged at the head. Each lead fans 0.5mm in Z
# after 4.5mm of straight wire. The joints then have 2.3mm centre spacing.
factory_radius = 6.6
delta = .5
angle = math.acos(1-delta/(2*factory_radius))
fan_start_x = 25.5
fan_end_x = fan_start_x-2*factory_radius*math.sin(angle)
coat_end_x = 21.8
assert fan_end_x > coat_end_x
plans, new, channel_parts = [], {}, []
factory_stubs = ['PackNTCLeadStubR33_'+str(i)+'_'+str(j) for i in [1,2] for j in [1,2]]
for sensor, pair, root_z, final_z, function in [
    (1,1,-2.35,-1.85,'GND_SENSE'), (1,2,-3.65,-4.15,'PACK_NTC'),
    (2,1,3.65,4.15,'PACK_GUARD'), (2,2,2.35,1.85,'GND_SENSE')]:
    sign = 1 if final_z > root_z else -1
    y = -14.43
    origin = A.Vector(30, y, root_z)
    start = A.Vector(fan_start_x, y, root_z)
    # Construct S-turn explicitly in XZ with a tangent -X entrance/exit.
    first_centre = A.Vector(fan_start_x, y, root_z+sign*factory_radius)
    a0 = -sign*math.pi/2
    a1 = a0-sign*angle
    def circle(c, a):
        return A.Vector(c.x+factory_radius*math.cos(a), y,
                        c.z+factory_radius*math.sin(a))
    middle = circle(first_centre, a1)
    second_centre = A.Vector(fan_end_x, y, final_z-sign*factory_radius)
    b0 = sign*math.pi/2-sign*angle
    b1 = sign*math.pi/2
    end = A.Vector(fan_end_x, y, final_z)
    assert (middle-circle(second_centre, b0)).Length < 1e-7
    edges = [Part.makeLine(origin, start),
             Part.Arc(start, circle(first_centre, (a0+a1)/2), middle).toShape(),
             Part.Arc(middle, circle(second_centre, (b0+b1)/2), end).toShape(),
             Part.makeLine(end, A.Vector(coat_end_x, y, final_z))]
    name = 'FactoryNTCWireR36_'+str(sensor)+'_'+str(pair)
    wire = sweep(name, edges, origin, .6, function+' / factory OD1.2 allowance / soldered adapter candidate')
    new[name] = wire.Shape.copy()
    channel_parts.append(sweep(name+'Channel', edges, origin, .8, 'Factory-wire clearance tool, not material'))
    joint_name = 'NTCSpliceSpaceR36_'+str(sensor)+'_'+str(pair)
    joint = feature(joint_name, Part.makeCylinder(.9, 5., A.Vector(17.3, y, final_z), A.Vector(1,0,0)),
                    'Insulated lap-joint OD1.8 x5 PROCESS BUDGET / not qualified part')
    new[joint_name] = joint.Shape.copy()
    channel_parts.append(feature(joint_name+'Channel', Part.makeCylinder(1.1, 5.4, A.Vector(17.1,y,final_z), A.Vector(1,0,0)), 'Joint clearance tool'))
    # Four stripped millimetres are available after the insulated factory path.
    bare_name = 'FactoryNTCBareR36_'+str(sensor)+'_'+str(pair)
    bare = feature(bare_name, Part.makeCylinder(.2,4.,A.Vector(17.8,y,final_z),A.Vector(1,0,0)),
                   'Factory bare lead D0.4 process allowance, inside joint budget')
    new[bare_name] = bare.Shape.copy()
    length = sum(e.Length for e in edges)
    assert length < 33., length
    plans.append({'sensor':'TH'+str(sensor),'pair_lead':pair,'function':function,
                  'coated_OD_allowance_mm':1.2,'head_exit_xyz_mm':list(origin),
                  'first_straight_mm':4.5,'minimum_centre_radius_mm':6.6,
                  'minimum_inside_radius_mm':6.,'fan_end_x_mm':fan_end_x,
                  'coated_end_xyz_mm':[coat_end_x,y,final_z],
                  'exact_coated_path_mm':length,'available_conservative_coated_length_mm':33.,
                  'bare_length_mm':4.,'joint_process_bounds':inventory(joint.Shape),
                  'trim_and_process':'First-build fixture/coupon must establish factory-wire cut/strip and solder process; no live sensor or pack has been trimmed.'})
    print('factory lead', name, 'length', length, flush=True)

tool = D.addObject('Part::MultiFuse','SensorWireChannelsR36')
tool.Shapes = channel_parts
tool.Refine = True
old_right = D.getObject('PackTailRightHubR34')
right = D.addObject('Part::Cut','SensorWiredRightHubR36')
right.Base = old_right
right.Tool = tool
right.Refine = True
D.recompute()
assert right.Shape.isValid() and len(right.Shape.Solids) == 1
original_capture = D.getObject('HarnessRightHubR30').Shape.copy()
capture_loss = original_capture.copy().cut(right.Shape.copy()).Volume
# The R34 lower channel is intentional; require these new sensor channels
# to preserve precisely the already-channelled capture material.
capture_witness = original_capture.copy().common(old_right.Shape.copy())
new_capture_loss = capture_witness.copy().cut(right.Shape.copy()).Volume
assert abs(new_capture_loss) < 1e-5, new_capture_loss

fixed = {n:D.getObject(n).Shape.copy() for n in r['fixed_roles']
         if n not in factory_stubs+['PackTailRightHubR34']}
fixed[right.Name] = right.Shape.copy()
fixed.update({n:D.getObject(n).Shape.copy() for n in
              ['PackPigtailWireR34_'+str(i) for i in range(1,6)]+['PackBareLeadR34_'+str(i) for i in range(1,6)]})
hits, named, pair_count = [], [], 0
for name, shape in new.items():
    local = []
    for other, solid in fixed.items():
        pair_count += 1
        v = volume(shape, solid)
        if v > 1e-5:
            local.append({'new':name,'fixed':other,'intersection_mm3':v})
    hits += local
    print('static', name, local, flush=True)
# A joint intentionally contains its matching bare lead and short coating ends.
names = list(new)
for i, name in enumerate(names):
    for other in names[i+1:]:
        pair_count += 1
        v = volume(new[name], new[other])
        if v <= 1e-5:
            continue
        same_pair = name.rsplit('_',2)[-2:] == other.rsplit('_',2)[-2:]
        row = {'a':name,'b':other,'intersection_mm3':v}
        (named if same_pair and ('SpliceSpace' in name or 'SpliceSpace' in other) else hits).append(row)

out = OUT/'PackSensorRouteR36.FCStd'
D.Label = 'R36 full factory sensor leads and insulated joint PROCESS STUDY / pack OPEN'
D.saveAs(str(out))
result = {'native_sha256':sha(out),'source_native_sha256':before,'builder_sha256':sha(Path(__file__)),
          'source_R34_report_sha256':sha(SOURCE/'geometry-report.json'),
          'sensor_translation_mm':[10,0,0],'translated_objects':moved,
          'replaced_short_stubs':factory_stubs,'factory_lead_plan':plans,
          'new_roles':{n:inventory(s) for n,s in new.items()},
          'fixed_roles':list(fixed),'changed_right_hub':inventory(right.Shape),
          'new_channel_loss_of_already_channelled_original_capture_mm3':new_capture_loss,
          'source_original_capture_loss_including_R34_channel_mm3':capture_loss,
          'static_pairs':pair_count,'unexpected_intersections':hits,'named_joint_interfaces':named,
          'all_static_screens_clear':not hits,
          'scope':'Four full insulated factory-wire allowances and four lap-joint process spaces. Body-side pigtails still stop at R34 endpoints; their complete extensions/branch/power mate/restraints/loading remain open. Sensor/guard assemblies shift+10X and tray recomputes; source exterior, boards, motor and pack gauge unchanged. Joint material/geometry, received dimensions and strip/solder/thermal/physical acceptance unqualified; batteryOPEN/BOM unchanged.'}
(OUT/'geometry-report.json').write_text(json.dumps(result,indent=2)+'\n')
A.closeDocument(D.Name)
assert sha(source) == before
print('SAVED R36:', len(new),'new roles; unexpected',hits, flush=True)
