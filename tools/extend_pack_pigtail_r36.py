"""Connect the body pigtail to four factory NTC joint budgets, plus return Y branch.

Pack power ends are parked separately for their later mate; no live pack work.
"""
from pathlib import Path
import hashlib
import itertools
import json
import math
import sys
sys.path.insert(0, '/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part
import Sketcher

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT/'hardware/cad/pack-sensor-r36/candidate-c'
OUT = Path(sys.argv[1]).resolve()
OUT.mkdir(parents=True, exist_ok=True)
assert not any(OUT.iterdir())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
r = json.loads((SOURCE/'geometry-report.json').read_text())
prefix = json.loads((ROOT/'hardware/cad/pack-harness-r34/pigtail-j/geometry-report.json').read_text())
source = SOURCE/'PackSensorRouteR36.FCStd'
before = sha(source)
assert before == r['native_sha256'] and r['all_static_screens_clear']
D = A.openDocument(str(source))

def feature(n, s, label):
    o = D.addObject('PartDesign::Feature',n)
    o.Shape = s
    o.Label = label
    return o

def vec(p):
    return p if isinstance(p,A.Vector) else A.Vector(*p)

def line(edges, a, b):
    a,b=vec(a),vec(b)
    if (a-b).Length>1e-8:
        edges.append(Part.makeLine(a,b))
    return b

def s_turn(edges, start, direction, delta, radius):
    start,direction,delta=vec(start),vec(direction),vec(delta)
    amount=delta.Length
    if amount<1e-8:
        return start
    assert abs(direction.dot(delta))<1e-7 and amount<=4*radius
    normal=delta/amount
    theta=math.acos(1-amount/(2*radius))
    middle=start+direction*(radius*math.sin(theta))+normal*(radius*(1-math.cos(theta)))
    first_mid=start+direction*(radius*math.sin(theta/2))+normal*(radius*(1-math.cos(theta/2)))
    end=start+direction*(2*radius*math.sin(theta))+delta
    second_mid=end-direction*(radius*math.sin(theta/2))-normal*(radius*(1-math.cos(theta/2)))
    edges.extend([Part.Arc(start,first_mid,middle).toShape(),Part.Arc(middle,second_mid,end).toShape()])
    return end

def old_edge(q):
    if q['kind']=='line':
        return Part.makeLine(vec(q['start_xyz_mm']),vec(q['end_xyz_mm']))
    a,b=q['angles_rad'];c=q['centre_in_plane_mm'];rad=q['radius_mm'];fixed=q['fixed_coordinate_mm']
    def pt(t):
        u=c[0]+rad*math.cos(t);v=c[1]+rad*math.sin(t)
        return A.Vector(u,fixed,v) if q['plane']=='XZ' else A.Vector(fixed,u,v) if q['plane']=='YZ' else A.Vector(u,v,fixed)
    return Part.Arc(pt(a),pt((a+b)/2),pt(b)).toShape()

def sweep(name, edges, start, radius, label):
    path=feature(name+'Path',Part.Wire(edges),'Exact tangent path / R4 minimum new bends')
    profile=D.addObject('Sketcher::SketchObject',name+'Profile')
    profile.Placement=A.Placement(vec(start),A.Rotation(A.Vector(0,0,1),edges[0].tangentAt(edges[0].FirstParameter)))
    profile.addGeometry(Part.Circle(A.Vector(),A.Vector(0,0,1),radius),False)
    obj=D.addObject('Part::Sweep',name)
    obj.Sections=[profile];obj.Spine=path;obj.Solid=True;obj.Frenet=True;obj.Label=label
    D.recompute()
    assert obj.Shape.isValid() and len(obj.Shape.Solids)==1,name
    return obj

def overlap(a,b):
    u,v=a.BoundBox,b.BoundBox
    if any(min(getattr(u,k+'Max'),getattr(v,k+'Max'))<=max(getattr(u,k+'Min'),getattr(v,k+'Min'))+1e-7 for k in 'XYZ'):
        return 0.
    return a.copy().common(b.copy()).Volume

new,plans,tools={},[],[]
lap_bares={}
for row in r['factory_lead_plan']:
    sensor=row['sensor'].removeprefix('TH');pair=str(row['pair_lead'])
    key=sensor+'_'+pair
    z=row['coated_end_xyz_mm'][2]
    edges=[];start=A.Vector(21.8,-14.43,z)
    end=s_turn(edges,start,[-1,0,0],[0,-.45,0],6.6)
    line(edges,end,[17.8,-14.88,z])
    bare=sweep('FactoryLapBareR36_'+key,edges,start,.2,'Factory bare lead offset -0.45Y for separate solder lap / D0.4 budget')
    new[bare.Name]=bare.Shape.copy();lap_bares[key]=bare
joint_window=Part.makeBox(3.2,1.8,3.2,A.Vector(10.,-14.53,-2.75))
joint=feature('SensorReturnYJointR36',joint_window,'Insulated three-way return joint PROCESS BUDGET / no qualified material')
new[joint.Name]=joint.Shape.copy()
tools.append(feature('SensorReturnYJointChannelR36',Part.makeBox(3.6,2.2,3.6,A.Vector(9.8,-14.73,-2.95)),'Y joint clearance tool'))

for plan in prefix['wire_plan']:
    i=plan['wire_index'];function=plan['net_function'];lane=plan['end_xyz_mm'][0]
    edges=[old_edge(q) for q in plan['segments'][:-1]]
    start=vec(plan['segments'][-1]['start_xyz_mm'])
    if function=='GND_SENSE':
        start=line(edges,start,[lane,8.,-4.2])
        start=s_turn(edges,start,[0,-1,0],[0,0,-.7],4.)
    turn_y={'PACK_P':-8.2,'GND_POWER':-9.,'GND_SENSE':-9.63,'PACK_NTC':-10.43,'PACK_GUARD':-11.13}[function]
    start=line(edges,start,[lane,turn_y,start.z])
    center=A.Vector(lane+4,turn_y,start.z)
    middle=center+A.Vector(-4/math.sqrt(2),-4/math.sqrt(2),0)
    end=center+A.Vector(0,-4,0)
    edges.append(Part.Arc(start,middle,end).toShape());start=end
    if function=='GND_SENSE':
        start=s_turn(edges,start,[1,0,0],[0,0,-1.85-start.z],4.)
        start=s_turn(edges,start,[1,0,0],[0,-.8,0],4.)
    elif function=='PACK_NTC':
        start=s_turn(edges,start,[1,0,0],[0,0,.05],4.)
    elif function=='PACK_GUARD':
        start=s_turn(edges,start,[1,0,0],[0,0,8.35],4.5)
        start=s_turn(edges,start,[1,0,0],[0,.7,0],4.)
    target_x=14. if function in ['PACK_P','GND_POWER'] else 17.8
    assert start.x<target_x,(function,list(start),target_x)
    endpoint=A.Vector(target_x,start.y,start.z)
    line(edges,start,endpoint)
    wire=sweep('PackConnectedWireR36_'+str(i),edges,plan['start_xyz_mm'],.3,function+' / OD0.6 engineering allowance')
    tools.append(sweep('PackConnectedWireChannelR36_'+str(i),edges,plan['start_xyz_mm'],.5,'Wire clearance tool'))
    if function=='GND_SENSE':
        coat=D.addObject('Part::Cut','SensorReturnCoatingR36')
        coat.Base=wire;coat.Tool=joint;coat.Refine=True;D.recompute()
        assert coat.Shape.isValid() and len(coat.Shape.Solids)==2
        new[coat.Name]=coat.Shape.copy()
        # Conductive process core continues through the intentionally stripped window.
        core=sweep('SensorReturnCoreR36',edges,plan['start_xyz_mm'],.2,'D0.4 conductive-process core allowance / same net as return joint')
        new[core.Name]=core.Shape.copy()
    else:
        new[wire.Name]=wire.Shape.copy()
    # Candidate solder tails into the four factory joint budgets. Power ends
    # remain coated/parked for the unfinished protected-pack mate.
    if function not in ['PACK_P','GND_POWER']:
        bare_edges=[]
        bare_end=s_turn(bare_edges,endpoint,[1,0,0],[0,.45,0],4.)
        line(bare_edges,bare_end,[21.3,endpoint.y+.45,endpoint.z])
        bare=sweep('PackAdapterBareR36_'+str(i),bare_edges,endpoint,.2,'Solder lap bareD0.4 offset +0.45Y / process allowance')
        new[bare.Name]=bare.Shape.copy()
    joins=[]
    for a,b in zip(edges,edges[1:]):
        gap=(a.Vertexes[-1].Point-b.Vertexes[0].Point).Length
        ta,tb=a.tangentAt(a.LastParameter),b.tangentAt(b.FirstParameter)
        cosine=ta.dot(tb)/(ta.Length*tb.Length)
        assert gap<1e-6 and cosine>1-1e-6,(function,gap,cosine)
        joins.append({'gap_mm':gap,'tangent_dot':cosine})
    plans.append({'function':function,'body_J2_pin':plan['body_logical_J2_pin'],
                  'body_native_pad':prefix['native_R35F_bindings']['land_map'][i-1]['native_pad'],
                  'coated_route_end_xyz_mm':list(endpoint),'exact_route_length_mm':sum(e.Length for e in edges),
                  'minimum_new_centre_radius_mm':4.,'tangent_joins':joins,
                  'termination':'Unfinished power mate' if function in ['PACK_P','GND_POWER'] else 'Factory NTC lap-joint budget'})
    print('extended',function,'end',list(endpoint),flush=True)

# The second NTC return branches inside one insulated three-way joint. Both
# coated runs are cut back to this process window; their conductive cores
# intentionally meet the same-net joint volume.
branch_start=A.Vector(10.8,-13.63,-1.85)
edges=[]
end=s_turn(edges,branch_start,[1,0,0],[0,-.8,3.7],4.)
assert end.x<17.8
line(edges,end,[17.8,-14.43,1.85])
branch=sweep('UpperSensorReturnRawR36',edges,branch_start,.3,'Second sensor return branch / OD0.6 allowance')
tools.append(sweep('UpperSensorReturnChannelR36',edges,branch_start,.5,'Branch clearance tool'))
coat=D.addObject('Part::Cut','UpperSensorReturnCoatingR36')
coat.Base=branch;coat.Tool=joint;coat.Refine=True;D.recompute()
assert coat.Shape.isValid() and len(coat.Shape.Solids)==1
new[coat.Name]=coat.Shape.copy()
core=sweep('UpperSensorReturnCoreR36',edges,branch_start,.2,'D0.4 conductive-process core / tied inside Y joint')
new[core.Name]=core.Shape.copy()
bare_edges=[];bare_start=A.Vector(17.8,-14.43,1.85)
bare_end=s_turn(bare_edges,bare_start,[1,0,0],[0,.45,0],4.)
line(bare_edges,bare_end,[21.3,-13.98,1.85])
bare=sweep('UpperSensorReturnBareR36',bare_edges,bare_start,.2,'Upper return separate lap bare / +0.45Y / D0.4 budget')
new[bare.Name]=bare.Shape.copy()

joint_construction=[]
for key,adapter_name in [('1_1','PackAdapterBareR36_2'),('1_2','PackAdapterBareR36_4'),
                         ('2_1','PackAdapterBareR36_5'),('2_2','UpperSensorReturnBareR36')]:
    factory=lap_bares[key].Shape.copy();adapter=new[adapter_name].copy()
    assert overlap(factory,adapter)<1e-5,(key,'bare cores overlap')
    z=next(q['coated_end_xyz_mm'][2] for q in r['factory_lead_plan']
           if q['sensor']=='TH'+key[0] and str(q['pair_lead'])==key[2])
    solder=Part.makeCylinder(.7,3.,A.Vector(18.3,-14.43,z),A.Vector(1,0,0))
    solder=solder.cut(factory).cut(adapter)
    assert solder.isValid() and len(solder.Solids)==1
    obj=feature('NTCSolderBridgeR36_'+key,solder,'Solder-process target within D1.4 envelope; bare-core budgets subtracted')
    new[obj.Name]=obj.Shape.copy()
    joint_construction.append({'pair':key,'factory_bare':lap_bares[key].Name,'adapter_bare':adapter_name,
                               'native_bare_gap_mm':factory.distToShape(adapter)[0],
                               'bare_overlap_mm3':overlap(factory,adapter),'solder_bridge':obj.Name,
                               'solder_outer_budget_mm':[1.4,3.],
                               'scope':'Geometric solder/insulation process target; no actual alloy, wetting or received wire/profile qualification.'})

all_tools=D.addObject('Part::MultiFuse','ConnectedPackChannelsR36')
all_tools.Shapes=tools;all_tools.Refine=True
hub_replacements={}
hub_changes={}
for name in ['PackTailLeftHubR34','SensorWiredRightHubR36']:
    base=D.getObject(name)
    obj=D.addObject('Part::Cut','Connected'+name)
    obj.Base=base;obj.Tool=all_tools;obj.Refine=True;D.recompute()
    assert obj.Shape.isValid() and len(obj.Shape.Solids)==1,(name,len(obj.Shape.Solids))
    loss=base.Shape.copy().cut(obj.Shape.copy())
    outside=0. if loss.isNull() or loss.Volume<1e-7 else loss.copy().cut(all_tools.Shape.copy()).Volume
    assert outside<1e-5
    hub_replacements[name]=obj
    hub_changes[name]={'replacement':obj.Name,'removed_mm3':loss.Volume,
                       'removal_outside_declared_tools_mm3':outside}

old_wires=['PackPigtailWireR34_'+str(i) for i in range(1,6)]
fixed={n:D.getObject(n).Shape.copy() for n in r['fixed_roles'] if n not in old_wires+list(hub_replacements)}
fixed.update({o.Name:o.Shape.copy() for o in hub_replacements.values()})
fixed.update({n:D.getObject(n).Shape.copy() for n in r['new_roles'] if not n.startswith('FactoryNTCBareR36_')})
hits,named=[],[]
pair_count=0
def intended(a,b):
    sensor_map={'PackAdapterBareR36_2':'1_1','PackAdapterBareR36_4':'1_2','PackAdapterBareR36_5':'2_1','UpperSensorReturnBareR36':'2_2',
                'SensorReturnCoatingR36':'1_1','SensorReturnCoreR36':'1_1','PackConnectedWireR36_4':'1_2','PackConnectedWireR36_5':'2_1',
                'UpperSensorReturnCoatingR36':'2_2','UpperSensorReturnCoreR36':'2_2'}
    for x,y in [(a,b),(b,a)]:
        if x.startswith('NTCSpliceSpaceR36_') and sensor_map.get(y)==x.removeprefix('NTCSpliceSpaceR36_'):
            return True
        if x.startswith('NTCSpliceSpaceR36_') and y.startswith(('FactoryLapBareR36_','NTCSolderBridgeR36_')):
            return x.rsplit('_',2)[-2:]==y.rsplit('_',2)[-2:]
    if {a,b} in [{'SensorReturnCoatingR36','SensorReturnCoreR36'},
                 {'UpperSensorReturnCoatingR36','UpperSensorReturnCoreR36'}]:
        return True
    return_cores={'SensorReturnCoreR36','UpperSensorReturnCoreR36'}
    if (a=='SensorReturnYJointR36' and b in return_cores) or (b=='SensorReturnYJointR36' and a in return_cores):
        return True
    if a in return_cores and b in return_cores:
        common=new[a].copy().common(new[b].copy())
        return common.copy().cut(joint.Shape.copy()).Volume<1e-5
    for x,y in [(a,b),(b,a)]:
        if x.startswith('FactoryNTCBareR36_') and sensor_map.get(y)==x.removeprefix('FactoryNTCBareR36_'):
            common=(new.get(x) or fixed[x]).copy().common((new.get(y) or fixed[y]).copy())
            name='NTCSpliceSpaceR36_'+sensor_map[y]
            return common.copy().cut(fixed[name].copy()).Volume<1e-5
    return False
for a,shape in new.items():
    local=[]
    for b,solid in fixed.items():
        pair_count+=1;v=overlap(shape,solid)
        if v>1e-5:
            row={'a':a,'b':b,'intersection_mm3':v}
            (named if intended(a,b) else local).append(row)
    hits+=local
    print('static',a,local,flush=True)
for (a,shape),(b,solid) in itertools.combinations(new.items(),2):
    pair_count+=1;v=overlap(shape,solid)
    if v>1e-5:
        row={'a':a,'b':b,'intersection_mm3':v}
        (named if intended(a,b) else hits).append(row)

out=OUT/'ConnectedPackSensorsR36.FCStd'
D.Label='R36 connected dual-NTC candidate / power mate unfinished / process unqualified'
D.saveAs(str(out))
result={'native_sha256':sha(out),'source_native_sha256':before,'builder_sha256':sha(Path(__file__)),
        'source_report_sha256':sha(SOURCE/'geometry-report.json'),'native_R35F_bindings':prefix['native_R35F_bindings'],
        'wire_plan':plans,'new_roles':list(new),'fixed_roles':list(fixed),'hub_changes':hub_changes,
        'joint_construction':joint_construction,
        'static_pairs':pair_count,'unexpected_intersections':hits,'named_process_interfaces':named,
        'all_static_screens_clear':not hits,
        'sensor_return_branch':{'start_xyz_mm':list(branch_start),'end_xyz_mm':[17.8,-14.43,1.85],
                                'exact_path_length_mm':sum(e.Length for e in edges),'minimum_centre_radius_mm':4.,
                                'insulation':'Removed within the three-way process window; conductive core and joint volumes intentionally connect.'},
        'scope':'Connected sensor-wire/branch geometry to full factory-wire and insulated lap-joint process spaces. Joint process shapes and D0.4 cores are engineering budgets, not actual solder/material profiles. Power ends parked atX14, not a complete protected-pack mate. Loading/restraints, moved-sensor/source material and reserve reviews, supplier/process/electrical/thermal/physical qualification remain open. BatteryOPEN/humanBOM unchanged.'}
(OUT/'geometry-report.json').write_text(json.dumps(result,indent=2)+'\n')
A.closeDocument(D.Name)
assert sha(source)==before
print('SAVED connected sensor candidate:',pair_count,'pairs; unexpected',hits,flush=True)
