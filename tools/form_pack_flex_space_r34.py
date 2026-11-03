"""Develop formed pack-tail SPACE CLAIM on the channel trial, before copper.

J2 header/mate omitted only for this DNP/pigtail comparison. No native PCB DNP
variant, chosen flex stackup, copper/developed board or functional harness yet.
"""
from pathlib import Path
import sys,json,hashlib,math
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'hardware/cad/pack-harness-r34/passage-c';OUT=Path(sys.argv[1]).resolve();OUT.mkdir(parents=True,exist_ok=True);assert not any(OUT.iterdir());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();r=json.loads((P/'geometry-report.json').read_text());f=P/'PackTailPassageR34.FCStd';before=sha(f);assert before==r['native_sha256'];D=A.openDocument(str(f));TH=.25;R=1.925;S=2.125;U=3.145
pieces=[];descriptions=[]
def box(n,b):
 x,y,z,u,v,w=b;o=D.addObject('Part::Box',n);o.Length=u-x;o.Width=v-y;o.Height=w-z;o.Placement.Base=A.Vector(x,y,z);pieces.append(o);descriptions.append({'role':n,'kind':'flat_region','bounds_xyz_mm':b});return o
def sector(n,plane,center,radius,start,end,lo,width):
 def v(rad,a):
  a=math.radians(a);u=center[0]+rad*math.cos(a);v=center[1]+rad*math.sin(a)
  return A.Vector(lo,u,v)if plane=='YZ'else A.Vector(u,lo,v)if plane=='XZ'else A.Vector(u,v,lo)
 ro=radius+TH/2;ri=radius-TH/2;mid=(start+end)/2;edges=[Part.Arc(v(ro,start),v(ro,mid),v(ro,end)).toShape(),Part.makeLine(v(ro,end),v(ri,end)),Part.Arc(v(ri,end),v(ri,mid),v(ri,start)).toShape(),Part.makeLine(v(ri,start),v(ro,start))];face=Part.Face(Part.Wire(edges));s=face.extrude(A.Vector(width,0,0)if plane=='YZ'else A.Vector(0,width,0)if plane=='XZ'else A.Vector(0,0,width));assert s.isValid()and len(s.Solids)==1;o=D.addObject('PartDesign::Feature',n);o.Shape=s;o.addProperty('App::PropertyString','SourceSection','Geometry');o.SourceSection=json.dumps({'plane':plane,'center':center,'centre_radius_mm':radius,'inside_radius_mm':ri,'angles_deg':[start,end],'extrusion_low_width_mm':[lo,width]});pieces.append(o);descriptions.append({'role':n,'kind':'cylindrical_bend','plane':plane,'centre_radius_mm':radius,'inside_radius_mm':ri,'angles_deg':[start,end],'centreline_arc_length_mm':radius*abs(math.radians(end-start)),'extrusion_width_mm':width});return o
box('PackFlexUpperLapSpaceR34',[-3.2,37.65,.535,-1.485,43.35,.785])
rise=2.5-.66;rise_angle=math.degrees(math.acos(1-rise/(2*S)));rise_dx=S*math.sin(math.radians(rise_angle));rise_end=-3.2-2*rise_dx
sector('PackFlexUpperRiseFirstSpaceR34','XZ',[-3.2,.66+S],S,270,270-rise_angle,37.65,5.7)
sector('PackFlexUpperRiseSecondSpaceR34','XZ',[rise_end,2.5-S],S,90-rise_angle,90,37.65,5.7)
box('PackFlexUpperExitSpaceR34',[-11.4,37.65,2.375,rise_end,43.35,2.625])
sector('PackFlexBodyUTurnSpaceR34','XZ',[-11.4,2.5-U],U,90,270,37.65,5.7)
lower=2.5-2*U;theta=math.degrees(math.acos(1-(-4.2-lower)*-1/(2*S)));dy=S*math.sin(math.radians(theta));endy=5-2*dy
box('PackFlexLowerLapSpaceR34',[-11.4,37.65,lower-TH/2,2.25,43.35,lower+TH/2])
box('PackFlexBodyRunSpaceR34',[-2.25,5,lower-TH/2,2.25,40.5,lower+TH/2])
sector('PackFlexNeckSFirstSpaceR34','YZ',[5,lower-S],S,90,90+theta,-2.25,4.5)
sector('PackFlexNeckSSecondSpaceR34','YZ',[endy,-4.2+S],S,270+theta,270,-2.25,4.5)
box('PackFlexNeckRunSpaceR34',[-2.25,-24.475,-4.325,2.25,endy,-4.075])
sector('PackFlexFlangeTurnSpaceR34','YZ',[-24.475,-4.2+R],R,270,180,-2.25,4.5)
zc=-4.2+R;lowz=zc;highz=zc+4.5
box('PackFlexRearCrossbarSpaceR34',[-2.25,-26.525,lowz,39.775,-26.275,highz])
sector('PackFlexOuterRearTurnSpaceR34','XY',[39.775,-24.475],R,270,360,lowz,4.5)
box('PackFlexOuterRunSpaceR34',[41.575,-24.475,lowz,41.825,-11.625,highz])
sector('PackFlexOuterFrontTurnSpaceR34','XY',[39.775,-11.625],R,0,90,lowz,4.5)
box('PackFlexFrontIslandSpaceR34',[24,-9.825,-9,39.775,-9.575,9])
formed=D.addObject('Part::MultiFuse','PackFormedFlexSpaceR34');formed.Shapes=pieces;formed.Refine=True;formed.Label='FORMED SPACE CLAIM / not finished stack, copper, developed board or harness';D.recompute();s=formed.Shape;assert s.isValid()and len(s.Solids)==1,(s.isValid(),len(s.Solids))
tool=D.addObject('Part::Box','PackTailUnusedTrayReliefToolR34');tool.Length=.7;tool.Width=6.5;tool.Height=.7;tool.Placement.Base=A.Vector(-10.35,37.25,-4.1);carrier=D.addObject('Part::Cut','PackTailCarrierR34');carrier.Base=D.getObject('TipReadyCarrierR26');carrier.Tool=tool;carrier.Refine=True;D.recompute();oldcarrier=D.getObject('TipReadyCarrierR26').Shape.copy();newcarrier=carrier.Shape.copy();removed=oldcarrier.copy().cut(newcarrier.copy());outside=removed.copy().cut(tool.Shape.copy()).Volume;added=newcarrier.copy().cut(oldcarrier.copy()).Volume;assert newcarrier.isValid()and len(newcarrier.Solids)==len(oldcarrier.Solids)and abs(outside)<1e-5 and abs(added)<1e-5
witnesses={}
for n in ['TipReceiverR26','SupportedWireCombR26']:
 a=D.getObject(n).Shape.copy();lost=a.copy().cut(newcarrier.copy()).Volume;assert abs(lost)<1e-5;witnesses[n]={'source_volume_mm3':a.Volume,'lost_mm3':lost}
for n,region in [('rear_capture_Y_below26',Part.makeBox(100,66,100,A.Vector(-50,-40,-50))),('PCB_guides_Z_above_minus1_2',Part.makeBox(100,100,51.2,A.Vector(-50,-20,-1.2)))]:
 a=oldcarrier.copy().common(region);lost=a.copy().cut(newcarrier.copy()).Volume;assert abs(lost)<1e-5;witnesses[n]={'source_volume_mm3':a.Volume,'lost_mm3':lost}
relief={'source':'TipReadyCarrierR26','replacement':carrier.Name,'tool_bounds_xyz_mm':[-10.35,37.25,-4.1,-9.65,43.75,-3.4],'removed_mm3':removed.Volume,'added_mm3':added,'removal_outside_tool_mm3':outside,'source_and_new_solids':[len(oldcarrier.Solids),len(newcarrier.Solids)],'protected_source_material':witnesses}
physical={n:D.getObject(n).Shape.copy()for n in dict(r['parts'],**r['mates'],**r['allowances'])if n not in ['R17_J2','R17Mate_J2','TipReadyCarrierR26']};physical[carrier.Name]=newcarrier
def vol(a,b):
 u,v=a.BoundBox,b.BoundBox
 if any(min(getattr(u,k+'Max'),getattr(v,k+'Max'))<=max(getattr(u,k+'Min'),getattr(v,k+'Min'))+1e-7 for k in 'XYZ'):return 0.
 return a.copy().common(b.copy()).Volume
hits=[]
for n,b in physical.items():
 v=vol(s,b)
 if v>1e-5:
  intersection=s.copy().common(b.copy());bb=intersection.optimalBoundingBox(False,False);local=[]
  for o in pieces:
   w=vol(o.Shape,b)
   if w>1e-5:local.append({'region':o.Name,'intersection_mm3':w})
  hits.append({'fixed':n,'intersection_mm3':v,'intersection_bounds_xyz_mm':[getattr(bb,k)for k in ['XMin','YMin','ZMin','XMax','YMax','ZMax']],'regions':local});print('hit',n,v,local,flush=True)
out=OUT/'FormedFlexSpaceR34.FCStd';D.Label='R34 formed pack-tail space comparison / NOT FUNCTIONAL HARNESS';D.saveAs(str(out));report={'native_sha256':sha(out),'source_passage_trial_native_sha256':before,'source_passage_report_sha256':sha(P/'geometry-report.json'),'builder_sha256':sha(Path(__file__)),'space_claim_thickness_mm':TH,'space_claim_valid_solids':[s.isValid(),len(s.Solids)],'space_claim_volume_mm3':s.Volume,'parts_of_space_claim':descriptions,'neck_run_Z_mm':-4.2,'underbody_run_Z_mm':lower,'S_transition_angular_span_deg':theta,'S_transition_end_Y_mm':endy,'body_upper_rise_angular_span_deg':rise_angle,'body_upper_rise_end_X_mm':rise_end,'body_header_and_mate_omitted_for_comparison':['R17_J2','R17Mate_J2'],'unused_tray_wall_relief':relief,'fixed_roles':list(physical),'unexpected_space_claim_intersections':hits,'all_static_space_claim_screens_clear':not hits,'scope':'Native formed flex reservation with cylindrical folds and flat islands, thickness.25mm space claim. Single solid only; not developed-area/neutral-axis/flat-copper proof, selected stackup/material/supplier, actual PCB or J2DNP variant. Body J2 header and mate omitted ONLY as explicit comparison. Small declared unused-tray-wall relief preserves source carrier solids, capture, PCB guides, tip receiver and comb witnesses; keeper unchanged. Minimum reserved inside radius1.8mm is an installation-study value, never repeated-flex approval. No solder-pad/process/anchors, full sensor/pack leads, strain relief, assembly, current/thermal/runtime or physical acceptance. R33 remains current checkpoint.'};(OUT/'geometry-report.json').write_text(json.dumps(report,indent=2)+'\n');A.closeDocument(D.Name);assert sha(f)==before;print('saved formed trial, hits',len(hits),flush=True)
