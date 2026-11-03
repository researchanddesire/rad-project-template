"""Conditional prewired pack mate plus body power wires, on the unchanged boards.

Native paths/sections and local hub reliefs are implemented. OEM lead-exit,
shrink and bend assumptions remain receiving inputs, not adopted pack facts.
"""
from pathlib import Path
import hashlib,itertools,json,math,sys
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part,Sketcher
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/'hardware/cad/joint-retention-r38/sensor-c';SCREEN=ROOT/'hardware/cad/pack-assembly-r37/power-screen-d/placement-screen.json';OUT=Path(sys.argv[1]).resolve();OUT.mkdir(parents=True,exist_ok=True);assert not any(OUT.iterdir());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();r=json.loads((SOURCE/'geometry-report.json').read_text());screen=json.loads(SCREEN.read_text());case=next(c for c in screen['cases']if c['alpha_X_deg']==20. and c['coupler_centre_YZ_mm']==[-18.8,-12.4]);source=SOURCE/'RetainedSensorJointsR38.FCStd';before=sha(source);assert before==r['native_sha256'];D=A.openDocument(str(source))
def feature(n,s,label):
 o=D.addObject('PartDesign::Feature',n);o.Shape=s;o.Label=label;return o
def line(edges,a,b):
 if(a-b).Length>1e-8:edges.append(Part.makeLine(a,b))
 return b
def s_turn(edges,start,direction,delta,radius):
 amount=delta.Length
 if amount<1e-8:return start
 assert amount<4*radius and abs(direction.dot(delta))<1e-7
 n=delta/amount;t=math.acos(1-amount/(2*radius));middle=start+direction*(radius*math.sin(t))+n*(radius*(1-math.cos(t)));end=start+direction*(2*radius*math.sin(t))+delta
 first_mid=start+direction*(radius*math.sin(t/2))+n*(radius*(1-math.cos(t/2)));second_mid=end-direction*(radius*math.sin(t/2))-n*(radius*(1-math.cos(t/2)));edges.extend([Part.Arc(start,first_mid,middle).toShape(),Part.Arc(middle,second_mid,end).toShape()]);return end
def sweep(name,edges,radius,label):
 path=feature(name+'Path',Part.Wire(edges),'Exact native tangent path');profile=D.addObject('Sketcher::SketchObject',name+'Profile');origin=edges[0].Vertexes[0].Point;axis=edges[0].tangentAt(edges[0].FirstParameter);profile.Placement=A.Placement(origin,A.Rotation(A.Vector(0,0,1),axis));profile.addGeometry(Part.Circle(A.Vector(),A.Vector(0,0,1),radius),False);obj=D.addObject('Part::Sweep',name);obj.Sections=[profile];obj.Spine=path;obj.Solid=True;obj.Frenet=True;obj.Label=label;D.recompute();assert obj.Shape.isValid()and len(obj.Shape.Solids)==1,name;return obj
def vol(a,b):
 u,v=a.BoundBox,b.BoundBox
 if any(min(getattr(u,k+'Max'),getattr(v,k+'Max'))<=max(getattr(u,k+'Min'),getattr(v,k+'Min'))+1e-7 for k in 'XYZ'):return 0.
 return a.copy().common(b.copy()).Volume
def inv(s):
 b=s.optimalBoundingBox(False,False);return {'valid':s.isValid(),'solids':len(s.Solids),'volume_mm3':s.Volume,'bounds_xyz_mm':[getattr(b,k)for k in ['XMin','YMin','ZMin','XMax','YMax','ZMax']]}
def rotated_box(x0,x1,width,thick,y,z,alpha):
 s=Part.makeBox(x1-x0,width,thick,A.Vector(x0,-width/2,-thick/2));s.rotate(A.Vector(),A.Vector(1,0,0),alpha);s.translate(A.Vector(0,y,z));return s
def old_edge(q):
 if q['kind']=='line':return Part.makeLine(A.Vector(*q['start_xyz_mm']),A.Vector(*q['end_xyz_mm']))
 a,b=q['angles_rad'];c=q['centre_in_plane_mm'];rad=q['radius_mm'];fixed=q['fixed_coordinate_mm']
 def pt(t):
  u=c[0]+rad*math.cos(t);v=c[1]+rad*math.sin(t);return A.Vector(u,fixed,v)if q['plane']=='XZ'else A.Vector(fixed,u,v)if q['plane']=='YZ'else A.Vector(u,v,fixed)
 return Part.Arc(pt(a),pt((a+b)/2),pt(b)).toShape()
alpha=20.;ar=math.radians(alpha);n=A.Vector(0,math.cos(ar),math.sin(ar));v=A.Vector(0,math.cos(ar+math.radians(80)),math.sin(ar+math.radians(80)));yc,zc=-9.5,-11.5;root=A.Vector(7,-20,-9);delta=A.Vector(0,yc-root.y,zc-root.z);theta=math.acos(1-delta.Length/24);rest=24.-24*theta;shrink_x=7-24*math.sin(theta)-rest;stock_x=shrink_x-4.;male_x=stock_x-14.8
housing=rotated_box(male_x-.8,stock_x+.8,8.8,4.2,yc,zc,alpha);shrink=rotated_box(stock_x-.8,stock_x+4.,6.4,4.2,yc,zc,alpha);coupler=feature('PackMateProcessSpaceR39',housing.fuse(shrink).removeSplitter(),'Molex51005/51006 + shrink engineering budget / unselected pack and unmeasured maxima')
new={coupler.Name:coupler.Shape.copy()};tools=[];plans=[];joint_map={};core_pairs=[]
prefix=json.loads((ROOT/'hardware/cad/pack-harness-r34/pigtail-j/geometry-report.json').read_text())
for pin,sign,wire_index,target_height in [(1,1,1,-5.6),(2,-1,3,-6.5)]:
 net='PACK_P'if pin==1 else'GND_POWER';start=root+n*sign;edges=[]
 direction=A.Vector(-1,0,0);normal=delta/delta.Length;binormal=direction.cross(normal);c=n.dot(normal);b=n.dot(binormal);r1=12-sign*c;r2=12+sign*c;assert min(r1,r2)>=11.
 centre1=root+normal*12+binormal*(sign*b);first_end=centre1+direction*(r1*math.sin(theta))-normal*(r1*math.cos(theta));first_mid=centre1+direction*(r1*math.sin(theta/2))-normal*(r1*math.cos(theta/2));edges.append(Part.Arc(start,first_mid,first_end).toShape())
 endcentre=root+direction*(24*math.sin(theta))+delta;centre2=endcentre-normal*12+binormal*(sign*b);end=endcentre+n*sign;second_mid=centre2+normal*(r2*math.cos(theta/2))-direction*(r2*math.sin(theta/2));edges.append(Part.Arc(first_end,second_mid,end).toShape());line(edges,end,A.Vector(shrink_x,yc,zc)+n*sign);assert abs(sum(e.Length for e in edges)-24.)<1e-6
 stock=sweep('StockPackLeadR39_'+str(pin),edges,.9,'Protected-pack lead OD1.8 CONDITION; exit/bend/length not controlled OEM data');new[stock.Name]=stock.Shape.copy();tools.append(sweep('StockPackLeadChannelR39_'+str(pin),edges,1.1,'Clearance tool'))
 mstart=A.Vector(male_x,yc,zc)+n*sign;medges=[];umid=mstart+A.Vector(-4.75,0,0)+v*4.75;uend=mstart+v*9.5;medges.append(Part.Arc(mstart,umid,uend).toShape());mend=s_turn(medges,uend,A.Vector(1,0,0),n*(sign*.6),4.);remaining=18.5-sum(e.Length for e in medges);assert remaining>0;mend=line(medges,mend,mend+A.Vector(remaining,0,0))
 mate=sweep('SpareMateLeadR39_'+str(pin),medges,.6,'Prewired OEM mate OD1.2 CONDITION; trim/strip after receiving');new[mate.Name]=mate.Shape.copy();tools.append(sweep('SpareMateChannelR39_'+str(pin),medges,.8,'Mate-wire clearance tool'))
 joint=feature('PackPowerJointSpaceR39_'+str(pin),Part.makeCylinder(1.25,5.5,A.Vector(mend.x-1.5,mend.y+.35,mend.z),A.Vector(1,0,0)),'D2.5 x5.5 insulated-joint process target / not qualified part');new[joint.Name]=joint.Shape.copy();tools.append(feature('PackPowerJointChannelR39_'+str(pin),Part.makeCylinder(1.45,5.9,A.Vector(mend.x-1.7,mend.y+.35,mend.z),A.Vector(1,0,0)),'Joint clearance tool'))
 factory_core=feature('SpareMateBareR39_'+str(pin),Part.makeCylinder(.4,2.5,mend,A.Vector(1,0,0)),'OEM bareD0.8 process bound; actual wire/strip unqualified');new[factory_core.Name]=factory_core.Shape.copy()
 plan=next(q for q in prefix['wire_plan']if q['wire_index']==wire_index);bedges=[old_edge(q)for q in plan['segments'][:-1]];bend_start=A.Vector(*plan['segments'][-1]['start_xyz_mm']);bend_start=line(bedges,bend_start,A.Vector(plan['end_xyz_mm'][0],-8.1,-4.2));bend_start=s_turn(bedges,bend_start,A.Vector(0,-1,0),A.Vector(0,0,target_height+4.2),4.);centre=bend_start+A.Vector(-4,0,0);turn_mid=centre+A.Vector(4/math.sqrt(2),-4/math.sqrt(2),0);turn_end=centre+A.Vector(0,-4,0);bedges.append(Part.Arc(bend_start,turn_mid,turn_end).toShape());bend_start=turn_end
 bend_start=s_turn(bedges,bend_start,A.Vector(-1,0,0),A.Vector(0,0,mend.z-bend_start.z),4.)
 delta_y=mend.y+.7-bend_start.y
 bend_start=s_turn(bedges,bend_start,A.Vector(-1,0,0),A.Vector(0,delta_y,0),max(4.,abs(delta_y)/2+.1));body_end=A.Vector(mend.x+2.5,mend.y+.7,mend.z);assert bend_start.x>body_end.x,(pin,list(bend_start),list(body_end));line(bedges,bend_start,body_end)
 body=sweep('BodyPackPowerWireR39_'+str(pin),bedges,.3,net+' / unchanged body/anchor prefix; loose-end forming after hub closure');new[body.Name]=body.Shape.copy();tools.append(sweep('BodyPackPowerChannelR39_'+str(pin),bedges,.5,'Body power clearance tool'))
 body_core=feature('BodyPackPowerBareR39_'+str(pin),Part.makeCylinder(.2,2.5,body_end,A.Vector(-1,0,0)),'Body28AWG bareD0.4 process allowance');new[body_core.Name]=body_core.Shape.copy();assert vol(factory_core.Shape,body_core.Shape)<1e-5
 solder=Part.makeCylinder(.9,1.8,A.Vector(mend.x+.35,mend.y+.35,mend.z),A.Vector(1,0,0)).cut(factory_core.Shape.copy()).cut(body_core.Shape.copy());assert solder.isValid()and len(solder.Solids)==1;bridge=feature('PackPowerSolderBridgeR39_'+str(pin),solder,'D1.8 x1.8 solder-process target, bare-core bounds subtracted');new[bridge.Name]=bridge.Shape.copy()
 joint_map[pin]=[joint.Name,mate.Name,factory_core.Name,body.Name,body_core.Name,bridge.Name]
 core_pairs.append({'pin':pin,'factory_core':factory_core.Name,'body_core':body_core.Name,'native_bare_gap_mm':factory_core.Shape.distToShape(body_core.Shape)[0],'native_bare_overlap_mm3':vol(factory_core.Shape,body_core.Shape),'solder_bridge':bridge.Name})
 for label,es in [('stock',edges),('mate',medges),('body',bedges)]:
  joins=[]
  for a,b in zip(es,es[1:]):
   gap=(a.Vertexes[-1].Point-b.Vertexes[0].Point).Length;ta,tb=a.tangentAt(a.LastParameter),b.tangentAt(b.FirstParameter);cosine=ta.dot(tb)/(ta.Length*tb.Length);assert gap<1e-6 and cosine>1-1e-6,(pin,label,gap,cosine);joins.append({'gap_mm':gap,'tangent_dot':cosine})
  plans.append({'pin':pin,'net_function':net,'section':label,'exact_path_length_mm':sum(e.Length for e in es),'minimum_circle_radius_mm':min(e.Curve.Radius for e in es if hasattr(e.Curve,'Radius')),'tangent_joins':joins})
 print('power pin',pin,'body end',list(body_end),'body length',sum(e.Length for e in bedges),flush=True)

cut_tools=D.addObject('Part::MultiFuse','PackPowerClearanceToolsR39');cut_tools.Shapes=tools;cut_tools.Refine=True
hub_changes={};replacements={}
for name in ['PoweredConnectedPackTailLeftHubR34','JointRetainingHubR38']:
 base=D.getObject(name);obj=D.addObject('Part::Cut','ForwardWire'+name);obj.Base=base;obj.Tool=cut_tools;obj.Refine=True;D.recompute();assert obj.Shape.isValid()and len(obj.Shape.Solids)==1
 removed=base.Shape.copy().cut(obj.Shape.copy());outside=0. if removed.isNull()or removed.Volume<1e-7 else removed.copy().cut(cut_tools.Shape.copy()).Volume;assert outside<1e-5
 witnesses={}
 seat_boxes=[]
 for z in [5.5,-13.5]:
  seat_boxes.append(Part.makeBox(5.5,6.,8.,A.Vector(-13.,-14.5,z)).fuse(Part.makeBox(5.5,6.,8.,A.Vector(7.5,-14.5,z))))
 for key,shape in [('front_capture_Y_at_least_minus8',base.Shape.copy().common(Part.makeBox(120,108,120,A.Vector(-60,-8,-60)))),('upper_bolt_end_seats',base.Shape.copy().common(seat_boxes[0])),('lower_bolt_end_seats',base.Shape.copy().common(seat_boxes[1]))]:
  lost=0. if shape.isNull()or shape.Volume<1e-7 else shape.copy().cut(obj.Shape.copy()).Volume;witnesses[key]=lost
 midweb=base.Shape.copy().common(Part.makeBox(15.,6.,8.,A.Vector(-7.5,-14.5,-13.5)));midweb_loss=0. if midweb.isNull()else midweb.copy().cut(obj.Shape.copy()).Volume
 replacements[name]=obj;hub_changes[name]={'replacement':obj.Name,'removed_mm3':removed.Volume,'removal_outside_tools_mm3':outside,'protected_region_loss_mm3':witnesses,'lower_bolt_midweb_region_loss_mm3':midweb_loss,'structural_scope':'Named end-seat/capture material is checked separately. Midweb channel loss is reported, not waived or interpreted as strength acceptance; first-build loads/material review remain required.'}
oldpower=json.loads((ROOT/'hardware/cad/pack-assembly-r37/power-f/geometry-report.json').read_text())
fixed={n:D.getObject(n).Shape.copy()for n in r['fixed_roles']+list(r['new_roles'])if n not in list(oldpower['new_roles'])+list(replacements)};fixed.update({o.Name:o.Shape.copy()for o in replacements.values()});hits=[];named=[];pairs=0
for name,s in new.items():
 local=[]
 for other,a in fixed.items():
  pairs+=1;overlap=vol(s,a)
  if overlap>1e-5:local.append({'new':name,'fixed':other,'intersection_mm3':overlap})
 hits+=local;print('static',name,local,flush=True)
for(a,s),(b,t)in itertools.combinations(new.items(),2):
 pairs+=1;overlap=vol(s,t)
 if overlap<=1e-5:continue
 intentional=(a==coupler.Name and b.startswith(('StockPackLeadR39_','SpareMateLeadR39_')))or(b==coupler.Name and a.startswith(('StockPackLeadR39_','SpareMateLeadR39_')))
 for roles in joint_map.values():
  if a in roles and b in roles and(a.startswith('PackPowerJointSpaceR39_')or b.startswith('PackPowerJointSpaceR39_')):intentional=True
 row={'a':a,'b':b,'intersection_mm3':overlap};(named if intentional else hits).append(row)
out=OUT/'ForwardPackPowerR39.FCStd';D.Label='R39 forward conditional pack power / battery OPEN / no completed retention or receiving proof';D.saveAs(str(out));result={'native_sha256':sha(out),'source_R38C_sha256':before,'placement_screen_sha256':sha(SCREEN),'builder_sha256':sha(Path(__file__)),'conditional_case':{'coupler_centre_YZ_mm':[yc,zc],'male_housing_back_X_mm':male_x,'stock_female_back_X_mm':stock_x,'source':'Required24mm usable flexible lead; body/exit reference only, battery OPEN'},'wire_plan':plans,'new_roles':{n:inv(s)for n,s in new.items()},'fixed_roles':list(fixed),'hub_changes':hub_changes,'bare_core_pairs':core_pairs,'native_R35F_bindings':prefix['native_R35F_bindings'],'static_pairs':pairs,'unexpected_intersections':hits,'named_process_interfaces':named,'all_static_screens_clear':not hits,'all_named_retention_regions_conserved':all(abs(v)<1e-5 for q in hub_changes.values()for v in q['protected_region_loss_mm3'].values()),'receiving_conditions':dict(screen['reference_assumptions'],conditional_flexible_stock_lead_mm=24.,reference_inferred_flexible_stock_lead_mm=21.8,reference_35mm_overall_cable_route_accepted=False,required_pack_lead='24mm usable flexible lead outside housing/shrink; unselected pack must match fixture, reference35mm cable is not confirmed compatible',pack_exit_pair_axis='Assumed20degree axis; confirm actual receiving geometry'),'scope':'Complete conditional body-to-prewired-mate/stock-pack power geometry and two separated lap joints. Wire exits/OD, bendable length, shrink and bend limits are assumptions to confirm against the eventual pack, not controlled Bitcraze maxima or battery adoption. No connector/joint restraint or connected loading/actual process/electrical/thermal/physical acceptance. Body anchor retained; boards/exterior/motor unchanged; humanBOMunchanged.'};(OUT/'geometry-report.json').write_text(json.dumps(result,indent=2)+'\n');A.closeDocument(D.Name);assert sha(source)==before;print('SAVED conditional power clear',result['all_static_screens_clear'],'retention witness',result['all_named_retention_regions_conserved'],'hits',hits,flush=True)
