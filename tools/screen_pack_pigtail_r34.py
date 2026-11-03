"""Five thin-wire body/neck pigtail comparison against the formed flex option.

J2 header/mate omitted for a proposed soldered-land variant; native PCB and
complete pack/sensor terminations are NOT implemented by this transit trial.
"""
from pathlib import Path
import sys,json,hashlib,math,itertools
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part,Sketcher
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'hardware/cad/pack-harness-r34/passage-c';OUT=Path(sys.argv[1]).resolve();OUT.mkdir(parents=True,exist_ok=True);assert not any(OUT.iterdir());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();r=json.loads((P/'geometry-report.json').read_text());f=P/'PackTailPassageR34.FCStd';before=sha(f);assert before==r['native_sha256'];D=A.openDocument(str(f));R=4.;upper=2.8;z0=.8;lower=upper-2*R;rise=math.acos(1-(upper-z0)/(2*R));neck=math.acos(1-(-4.2-lower)/(2*R));neck_end=26-2*R*math.sin(neck);xu=-10.35
def point(plane,c,rad,a,fixed):
 u=c[0]+rad*math.cos(a);v=c[1]+rad*math.sin(a)
 return A.Vector(u,fixed,v)if plane=='XZ'else A.Vector(fixed,u,v)if plane=='YZ'else A.Vector(u,v,fixed)
def line(edges,records,a,b):
 a=A.Vector(*a)if not isinstance(a,A.Vector)else a;b=A.Vector(*b)if not isinstance(b,A.Vector)else b
 if(a-b).Length<1e-8:return
 edges.append(Part.makeLine(a,b));records.append({'kind':'line','start_xyz_mm':list(a),'end_xyz_mm':list(b),'length_mm':(a-b).Length})
def arc(edges,records,plane,c,rad,a,b,fixed):
 p=point(plane,c,rad,a,fixed);m=point(plane,c,rad,(a+b)/2,fixed);q=point(plane,c,rad,b,fixed);edges.append(Part.Arc(p,m,q).toShape());records.append({'kind':'circle_segment','plane':plane,'centre_in_plane_mm':c,'radius_mm':rad,'angles_rad':[a,b],'fixed_coordinate_mm':fixed,'start_xyz_mm':list(p),'end_xyz_mm':list(q),'length_mm':rad*abs(b-a)});return q
tool=D.addObject('Part::Box','PackWireTrayReliefToolR34');tool.Length=1.3;tool.Width=5.4;tool.Height=1.;tool.Placement.Base=A.Vector(-10.8,37.8,-5.7);carrier=D.addObject('Part::Cut','PackWireCarrierR34');carrier.Base=D.getObject('TipReadyCarrierR26');carrier.Tool=tool;carrier.Refine=True;D.recompute();oldcarrier=D.getObject('TipReadyCarrierR26').Shape.copy();removed=oldcarrier.copy().cut(carrier.Shape.copy());assert carrier.Shape.isValid()and len(carrier.Shape.Solids)==len(oldcarrier.Solids)and removed.copy().cut(tool.Shape.copy()).Volume<1e-5
protected={}
for n,shape in [('TipReceiverR26',D.getObject('TipReceiverR26').Shape.copy()),('SupportedWireCombR26',D.getObject('SupportedWireCombR26').Shape.copy()),('rear_capture_Y_below26',oldcarrier.copy().common(Part.makeBox(100,66,100,A.Vector(-50,-40,-50)))),('PCB_guides_Z_above_minus1_2',oldcarrier.copy().common(Part.makeBox(100,100,51.2,A.Vector(-50,-20,-1.2))))]:
 lost=shape.copy().cut(carrier.Shape.copy()).Volume;assert abs(lost)<1e-5;protected[n]={'source_volume_mm3':shape.Volume,'lost_mm3':lost}
definitions=[('PACK_P',1,42.75,1.6,-3.,-1.5),('GND_SENSE',2,41.9,.8,-3.,-2.),('GND_POWER',2,41.25,0.,-3.,-1.5),('PACK_NTC',3,39.75,-.8,-3.,-1.5),('PACK_GUARD',4,38.25,-1.6,-3.,-1.5)];wires={};plans=[];bare={}
for index,(net,pin,y,lane,xstart,xbareend)in enumerate(definitions,1):
 edges=[];records=[];endx=xstart-2*R*math.sin(rise)
 arc(edges,records,'XZ',[xstart,z0+R],R,3*math.pi/2,3*math.pi/2-rise,y)
 end=arc(edges,records,'XZ',[endx,upper-R],R,math.pi/2-rise,math.pi/2,y)
 line(edges,records,end,[xu,y,upper]);arc(edges,records,'XZ',[xu,upper-R],R,math.pi/2,3*math.pi/2,y)
 rr=y-32.;arcx=lane-rr;assert arcx>=xu
 line(edges,records,[xu,y,lower],[arcx,y,lower]);arc(edges,records,'XY',[arcx,32.],rr,math.pi/2,0,lower)
 line(edges,records,[lane,32,lower],[lane,26,lower]);arc(edges,records,'YZ',[26,lower+R],R,3*math.pi/2,3*math.pi/2-neck,lane);arc(edges,records,'YZ',[neck_end,-4.2-R],R,math.pi/2-neck,math.pi/2,lane)
 line(edges,records,[lane,neck_end,-4.2],[lane,-18,-4.2]);path=D.addObject('PartDesign::Feature','PackWirePathR34_'+str(index));path.Shape=Part.Wire(edges);profile=D.addObject('Sketcher::SketchObject','PackWireProfileR34_'+str(index));profile.Placement=A.Placement(A.Vector(xstart,y,z0),A.Rotation(A.Vector(0,0,1),A.Vector(-1,0,0)));profile.addGeometry(Part.Circle(A.Vector(),A.Vector(0,0,1),.3),False);wire=D.addObject('Part::Sweep','PackPigtailWireR34_'+str(index));wire.Sections=[profile];wire.Spine=path;wire.Solid=True;wire.Frenet=True;wire.Label=net+' / OD0.60 allowance / proposed28AWG / unfinished harness';D.recompute();assert wire.Shape.isValid()and len(wire.Shape.Solids)==1
 b=D.addObject('PartDesign::Feature','PackBareLeadR34_'+str(index));b.Shape=Part.makeCylinder(.2,xbareend-xstart,A.Vector(xstart,y,z0),A.Vector(1,0,0));b.Label=net+' / barecoreD0.4 PROCESS allowance / not supplier maximum';bare[b.Name]=b.Shape.copy();wires[wire.Name]=wire.Shape.copy();joins=[]
 for a,c in zip(edges,edges[1:]):
  aend=a.Vertexes[-1].Point;cstart=c.Vertexes[0].Point;ta=a.tangentAt(a.LastParameter);tc=c.tangentAt(c.FirstParameter);cos=ta.dot(tc)/(ta.Length*tc.Length);gap=(aend-cstart).Length;assert gap<1e-7 and cos>1-1e-7,(net,gap,cos);joins.append({'gap_mm':gap,'tangent_dot':cos})
 length=sum(e.Length for e in edges);assert abs(length-sum(q['length_mm']for q in records))<1e-5;plans.append({'wire_index':index,'body_logical_J2_pin':pin,'net_function':net,'start_xyz_mm':[xstart,y,z0],'end_xyz_mm':[lane,-18,-4.2],'coated_OD_allowance_mm':.6,'bare_OD_process_allowance_mm':.4,'bare_end_X_mm':xbareend,'body_landing_is_new_for_GND_SENSE':net=='GND_SENSE','exact_path_length_mm':length,'minimum_circle_radius_mm':min(q['radius_mm']for q in records if q['kind']=='circle_segment'),'segments':records,'tangent_joins':joins});print('wire',index,net,'length',length,flush=True)
native_root=ROOT/'hardware/pcb/pack-pigtail-r35/candidate-f';native_review=json.loads((native_root/'saved-circuit-review.json').read_text());native_change=json.loads((native_root/'interface-change.json').read_text());assert sha(native_root/'body/body-r35.kicad_pcb')==native_review['boards']['body']['sha256'];assert native_review['all_source_nodes_equal'];land_bindings=[]
for plan in plans:
 candidates=[q for q in native_change['current_J2_pad_rows']if q['number']==str(plan['body_logical_J2_pin'])and abs(q['xy_mm'][1]-plan['start_xyz_mm'][1])<1e-6];assert len(candidates)==1;pad=candidates[0];assert plan['bare_end_X_mm']>pad['xy_mm'][0]-.25;land_bindings.append({'wire_index':plan['wire_index'],'function':plan['net_function'],'native_pad':pad})
fixed={n:D.getObject(n).Shape.copy()for n in dict(r['parts'],**r['mates'],**r['allowances'])if n not in ['R17_J2','R17Mate_J2','TipReadyCarrierR26']};fixed[carrier.Name]=carrier.Shape.copy()
def vol(a,b):
 u,v=a.BoundBox,b.BoundBox
 if any(min(getattr(u,k+'Max'),getattr(v,k+'Max'))<=max(getattr(u,k+'Min'),getattr(v,k+'Min'))+1e-7 for k in 'XYZ'):return 0.
 return a.copy().common(b.copy()).Volume
new=dict(wires,**bare);hits=[];pairs=0
for n,a in new.items():
 local=[]
 for m,b in fixed.items():
  pairs+=1;v=vol(a,b)
  if v>1e-5:local.append({'moving':n,'fixed':m,'intersection_mm3':v})
 hits+=local;print('static',n,local,flush=True)
wiregaps=[]
for(n,a),(m,b)in itertools.combinations(wires.items(),2):
 v=vol(a,b);gap=a.distToShape(b)[0];wiregaps.append({'a':n,'b':m,'intersection_mm3':v,'native_surface_gap_mm':gap})
out=OUT/'PackPigtailTransitR34.FCStd';D.Label='R34 five-wire soldered pigtail TRANSIT comparison / unfinished harness';D.saveAs(str(out));report={'native_sha256':sha(out),'source_passage_trial_native_sha256':before,'builder_sha256':sha(Path(__file__)),'wire_candidate':'Accu-Glass10069028AWG stranded Kapton, .508mm nominal OD; .6 is engineering allowance, not supplier maximum. R4centre gives3.7mm reserved inside radius, above .13inch(3.302mm) reference if interpreted inside. Actual solder/stripping, received OD and electrical/enclosed rating unqualified.','wire_plan':plans,'native_R35F_bindings':{'PCB_sha256':native_review['boards']['body']['sha256'],'review_sha256':sha(native_root/'saved-circuit-review.json'),'interface_change_sha256':sha(native_root/'interface-change.json'),'land_map':land_bindings},'body_header_and_mate_omitted_for_comparison':['R17_J2','R17Mate_J2'],'proposed_board_landing_change':'R35F replaces J2 with five native solder lands and four original logical nets. Original four lands retained; new GND_SENSE landXY[-2.2,41.9], size0.5x0.5mm, connected locally to body GND. Two external return wires join on body PCB. Native DRC0/0/0 and94components/338nodes reviewed separately. Soldering/current/physical qualification pending.','changed_carrier':{'source':'TipReadyCarrierR26','replacement':carrier.Name,'removed_mm3':removed.Volume,'removal_outside_tool_mm3':removed.copy().cut(tool.Shape.copy()).Volume,'source_and_new_solids':[len(oldcarrier.Solids),len(carrier.Shape.Solids)],'protected_source_material':protected},'fixed_roles':list(fixed),'new_to_fixed_comparisons':pairs,'unexpected_intersections':hits,'native_coated_wire_pair_gaps':wiregaps,'all_transit_static_screens_clear':not hits and all(q['intersection_mm3']<1e-5 and q['native_surface_gap_mm']>.04 for q in wiregaps),'scope':'Five body-to-neck swept OD.6 allowances with exact circular/line paths, native tangency and finite static comparison only; plus first bare solder tails as process bounds. Existing source J2 header/mate omitted for proposed soldered variant, replaced by native R35F five-land interface. Complete OEM pack/mate, thermistor lead extensions/splices/restraints and connected loading remain open. Native R35F solder-land circuit reviewed separately; no current/thermal/physical or full harness/prototype readiness. R33 remains current checkpoint; batteryOPEN/BOMunchanged.'};(OUT/'geometry-report.json').write_text(json.dumps(report,indent=2)+'\n');A.closeDocument(D.Name);assert sha(f)==before;print('saved pigtail trial clear',report['all_transit_static_screens_clear'],'gaps',wiregaps,flush=True)
