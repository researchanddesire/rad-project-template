"""R34 trial: dedicated thin-pack-tail passage below existing wire anchor.

The transit block is a reservation, not a finished flex circuit. No J2/PCB
variant or real harness changes here; keep R33 current until complete review.
"""
from pathlib import Path
import sys,json,hashlib,itertools
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'hardware/cad/battery-fit-r33/candidate-f';OUT=Path(sys.argv[1]).resolve();OUT.mkdir(parents=True,exist_ok=True);assert not any(OUT.iterdir());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();r=json.loads((P/'geometry-report.json').read_text());f=P/'FlangePackR33.FCStd';before=sha(f);assert before==r['native_sha256'];D=A.openDocument(str(f))
def box(n,b):
 x,y,z,u,v,w=b;o=D.addObject('Part::Box',n);o.Length=u-x;o.Width=v-y;o.Height=w-z;o.Placement.Base=A.Vector(x,y,z);return o
def inv(s):
 b=s.optimalBoundingBox(False,False);return {'valid':s.isValid(),'solids':len(s.Solids),'volume_mm3':s.Volume,'bounds_xyz_mm':[getattr(b,k)for k in ['XMin','YMin','ZMin','XMax','YMax','ZMax']]}
def vol(a,b):
 u,v=a.BoundBox,b.BoundBox
 if any(min(getattr(u,k+'Max'),getattr(v,k+'Max'))<=max(getattr(u,k+'Min'),getattr(v,k+'Min'))+1e-7 for k in 'XYZ'):return 0.
 return a.copy().common(b.copy()).Volume
slot=box('PackTailChannelToolR34',[-2.65,-14,-4.7,2.65,-8,-3.7]);gauge=box('PackFlexTransitGaugeR34',[-2.25,-18,-4.325,2.25,24.9,-4.075]);gauge.Label='4.5x0.25 STRAIGHT SPACE CLAIM ONLY / not selected stackup, formed flex or harness'
replaced={};changes={};old={n:D.getObject(n).Shape.copy()for n in dict(r['parts'],**r['mates'],**r['allowances'])}
for source,target in [('ButtonSupportHubR31','PackTailLeftHubR34'),('PackSupportHubR33','PackTailRightHubR34')]:
 o=D.addObject('Part::Cut',target);o.Base=D.getObject(source);o.Tool=slot;o.Refine=True;replaced[source]=target
D.recompute();outer=Part.makeCylinder(100,150,A.Vector(0,-40,0),A.Vector(0,1,0)).cut(Part.makeCylinder(7,150,A.Vector(0,-40,0),A.Vector(0,1,0)))
for source,target in replaced.items():
 a=old[source];b=D.getObject(target).Shape.copy();lost=a.copy().cut(b.copy());added=b.copy().cut(a.copy()).Volume;outside=lost.copy().cut(slot.Shape.copy()).Volume;witness=a.copy().common(outer);lostwitness=witness.copy().cut(b.copy()).Volume;assert b.isValid()and len(b.Solids)==1 and abs(added)<1e-5 and abs(outside)<1e-5 and abs(lostwitness)<1e-5,(source,inv(b),added,outside,lostwitness);changes[source]={'replacement':target,'removed_mm3':lost.Volume,'added_mm3':added,'removed_outside_declared_tool_mm3':outside,'source_material_at_radius_at_least7mm_mm3':witness.Volume,'outer_witness_lost_mm3':lostwitness}
parts={replaced.get(n,n):D.getObject(replaced.get(n,n))for n in r['parts']};mates={n:D.getObject(n)for n in r['mates']};allowances={n:D.getObject(n)for n in r['allowances']};physical=dict(parts,**mates,**allowances);conserved={}
for n,s in old.items():
 if n in replaced:continue
 q=D.getObject(n).Shape;exact=s.exportBrepToString()==q.exportBrepToString();removed,added=(0.,0.)if exact else(s.copy().cut(q.copy()).Volume,q.copy().cut(s.copy()).Volume);assert abs(removed)<1e-4 and abs(added)<1e-4,(n,removed,added);conserved[n]={'exact_BRep_equal':exact,'removed_mm3':removed,'added_mm3':added}
poses=[]
for dx,dz in [(0,0),(-.2,0),(.2,0),(0,-.2),(0,.2)]:
 s=gauge.Shape.copy();s.translate(A.Vector(dx,0,dz));hits=[]
 for n,o in physical.items():
  v=vol(s,o.Shape)
  if v>1e-5:hits.append({'fixed':n,'intersection_mm3':v})
 poses.append({'offset_XZ_mm':[dx,dz],'hits':hits});print('transit pose',dx,dz,hits,flush=True)
gaps={n:slot.Shape.distToShape(D.getObject(n).Shape)[0]for n in ['HubBolt_1','HubBolt1','HubNut_1','HubNut1','CentralAnchorPadR30']}
reservations={n:D.getObject(n)for n in r['co_moving_reservations']};reservedhits=[]
for target in replaced.values():
 for n,q in reservations.items():
  v=vol(D.getObject(target).Shape,q.Shape)
  if v>1e-5:reservedhits.append({'hub':target,'reservation':n,'intersection_mm3':v})
out=OUT/'PackTailPassageR34.FCStd';D.Label='R34 trial / dedicated pack-tail transit / NOT COMPLETE HARNESS';D.saveAs(str(out));report={'native_sha256':sha(out),'source_R33_native_sha256':before,'source_R33_report_sha256':sha(P/'geometry-report.json'),'builder_sha256':sha(Path(__file__)),'parts':{n:inv(o.Shape)for n,o in parts.items()},'mates':r['mates'],'allowances':r['allowances'],'source_co_moving_reservations':r['co_moving_reservations'],'new_fixed_transit_reservation':{gauge.Name:inv(gauge.Shape)},'channel_tool_bounds_xyz_mm':[-2.65,-14,-4.7,2.65,-8,-3.7],'changed_hubs':changes,'source_roles_conserved':conserved,'listed_straight_transit_position_studies':poses,'channel_tool_to_existing_fastener_and_anchor_gap_mm':gaps,'unexpected_hub_vs_source_reservations':reservedhits,'all_listed_transit_poses_clear':not any(q['hits']for q in poses)and not reservedhits,'scope':'Dedicated5.3x1.0mm channel below old anchor through two existing hubs, Y[-14,-8]. Changed hubs each one solid; all removal within declared tool, source radial>=7mm witness conserved. No new hub material, so inherited contacts cannot increase. Straight4.5x0.25mm transit claim and four0.2mm placement probes only. Does not establish load/compliance, entry bend/abrasion, actual stackup/copper, full developed shape/terminations/restraints, J2 DNP variant, assembly/service/dynamic flex, electrical/thermal or physical acceptance. R33 remains current checkpoint; batteryOPEN/BOMunchanged.'};(OUT/'geometry-report.json').write_text(json.dumps(report,indent=2)+'\n');A.closeDocument(D.Name);assert sha(f)==before;print('saved trial',report['all_listed_transit_poses_clear'],'changes',changes,'gaps',gaps,flush=True)
