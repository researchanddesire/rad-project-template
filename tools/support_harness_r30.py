"""Two molded harness anchors captured by existing hub and keeper joints.

Native prototype geometry only. Actual overmold adhesion/creep and supported
connected-harness assembly need test; no new screws or exterior change.
"""
from pathlib import Path
import sys,json,hashlib,itertools
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'hardware/cad/interboard-r29/candidate-e';OUT=Path(sys.argv[1]).resolve();OUT.mkdir(parents=True,exist_ok=True);assert not any(OUT.iterdir());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text());r=read(SRC/'geometry-report.json');review=read(SRC/'saved-review.json');nf=SRC/'InterboardR29.FCStd';assert sha(nf)==r['native_sha256']==review['native_sha256']and not review['unexpected_intersections']
D=A.openDocument(str(nf));old={n:D.getObject(n).Shape.copy()for n in dict(r['parts'],**r['mates'],**r['allowances'])}
def box(n,b):
 x,y,z,u,v,w=b;o=D.addObject('Part::Box',n);o.Length=u-x;o.Width=v-y;o.Height=w-z;o.Placement.Base=A.Vector(x,y,z);return o
def fuse(n,ls):
 o=D.addObject('Part::MultiFuse',n);o.Shapes=ls;o.Refine=True;return o
def cut(n,a,b):
 o=D.addObject('Part::Cut',n);o.Base=a;o.Tool=b;o.Refine=True;return o
def rounded(n,b):
 a=box(n+'Blank',b);D.recompute();f=D.addObject('Part::Fillet',n+'Rounded');f.Base=a;f.Edges=[(i,.25,.25)for i in range(1,13)];D.recompute();assert f.Shape.isValid()and len(f.Shape.Solids)==1;return f
wires=D.addObject('Part::Compound','HarnessWireCutToolsR30');wires.Links=[D.getObject('InterboardWireR29_'+str(i))for i in range(1,11)]
central=cut('CentralAnchorPadR30',rounded('CentralAnchorR30',[-3.5,-15.1,-.5,3.5,-13.,2.5]),wires)
flange=cut('FlangeAnchorPadR30',rounded('FlangeAnchorR30',[-33.9,-18.6,9.4,-23.1,-15.,11.4]),wires)
central.Label='Mold around actual wires / compliant anchor / grade and bond unqualified'
flange.Label='Mold around actual wires / keeper-captured anchor / grade and bond unqualified'
cp=box('CentralAnchorPocketR30',[-3.6,-15.2,-.6,3.6,-12.9,2.6]);throat=box('CentralAnchorWireThroatR30',[-2.2,-16.3,-.05,2.2,-11.9,1.75])
# Cup is carried by the same removable keeper, open toward +Y. Different top
# and bottom slots follow the existing wire departures without threading.
outer=box('FlangeAnchorCupBlankR30',[-34.7,-20.,8.7,-22.4,-14.4,12.1]);cavity=box('FlangeAnchorCupPocketR30',[-34.,-18.7,9.3,-23.,-13.9,11.5]);bottom=box('FlangeAnchorBottomWireSlotR30',[-33.6,-17.5,8.6,-23.5,-13.9,9.31]);top=box('FlangeAnchorTopWireSlotR30',[-33.6,-19.,11.49,-23.5,-13.9,12.3]);stopnotch=box('FlangeAnchorStopNotchR30',[-30.1,-14.8,8.6,-26.9,-13.3,12.3])
cup=cut('FlangeAnchorCupR30',outer,fuse('FlangeAnchorCupCutToolsR30',[cavity,bottom,top,stopnotch]));keeper=fuse('HarnessKeeperR30',[D.getObject('FlangeEndKeeperR27'),cup]);keeper.Label='Existing one-screw PCB keeper with open-front harness cup'
# The old rail top has local relief for the cup's approach. Its PCB groove,
# screw boss, body capture and all other source interfaces remain in place.
relief=box('FlangeCupApproachReliefR30',[-34.8,-20.1,8.6,-22.3,-14.3,12.2]);tab=box('FlangeAnchorFrontStopR30',[-30.,-14.7,8.0,-27.,-13.5,11.6])
leftblank=fuse('HarnessLeftHubBlankR30',[D.getObject('FlangeSupportHubR27'),box('CentralAnchorLeftBodyR30',[-4.3,-15.9,-1.2,0,-12.2,3.2]),box('CentralAnchorLeftBridgeR30',[-8.,-13.8,3.1,0,-12.2,4.2])]);leftcut=cut('HarnessLeftHubPocketR30',leftblank,fuse('HarnessLeftHubCutToolsR30',[cp,throat,relief]));left=fuse('HarnessLeftHubR30',[leftcut,tab])
rightblank=fuse('HarnessRightHubBlankR30',[D.getObject('HubRight'),box('CentralAnchorRightBodyR30',[0,-15.9,-1.2,4.3,-12.2,3.2]),box('CentralAnchorRightBridgeR30',[0,-13.8,3.1,8.,-12.2,4.2])]);right=cut('HarnessRightHubR30',rightblank,fuse('HarnessRightHubCutToolsR30',[cp,throat]));left.Label='Left capture hub / central wire anchor pocket / local keeper-cup relief';right.Label='Right capture hub / central wire anchor pocket'
D.recompute();replaced={'FlangeSupportHubR27':left.Name,'HubRight':right.Name,'FlangeEndKeeperR27':keeper.Name};parts={n:D.getObject(n)for n in r['parts']if n not in replaced};parts.update({o.Name:o for o in [left,right,keeper,central,flange]});mates={n:D.getObject(n)for n in r['mates']};allowances={n:D.getObject(n)for n in r['allowances']};new={o.Name:o for o in [left,right,keeper,central,flange]}
def inv(s):
 b=s.optimalBoundingBox(False,False);return {'valid':s.isValid(),'solids':len(s.Solids),'volume_mm3':s.Volume,'bounds_xyz_mm':[getattr(b,k)for k in ['XMin','YMin','ZMin','XMax','YMax','ZMax']]}
for n,o in new.items():print('new role',n,inv(o.Shape),flush=True)
# Save all evidence before deciding whether this candidate is usable.
output=OUT/'HarnessSupportR30.FCStd';D.Label='R30 / captured compliant harness anchors / DEVELOPMENT';D.saveAs(str(output));out={'builder_sha256':sha(Path(__file__)),'source_R29_native_sha256':sha(nf),'source_R29_report_sha256':sha(SRC/'geometry-report.json'),'source_R29_saved_review_sha256':sha(SRC/'saved-review.json'),'parts':{n:inv(o.Shape)for n,o in parts.items()},'mates':r['mates'],'allowances':r['allowances'],'replaced_roles':replaced,'new_roles':list(new),'native_sha256':sha(output),'scope':'Two molded-in-place compliant wire pads, captured by modified existing hubs/keeper. No new screws. Candidate geometry only; grade/bond/cure/strength/strain-relief, connected loading/service motion and physical/electrical acceptance remain open. R29 wires, source boards/exterior/motor/tip and battery OPEN retained.'}
conserved={}
for n,s in old.items():
 if n in replaced:continue
 now=D.getObject(n).Shape;equal=s.exportBrepToString()==now.exportBrepToString();a,b=(0.,0.)if equal else(s.copy().cut(now.copy()).Volume,now.copy().cut(s.copy()).Volume);bd=max(abs(x-y)for x,y in zip(inv(s)['bounds_xyz_mm'],inv(now)['bounds_xyz_mm']));assert abs(a)<1e-4 and abs(b)<1e-4 and bd<1e-5,(n,a,b,bd);conserved[n]={'exact_BRep_equal':equal,'removed_mm3':a,'added_mm3':b,'maximum_bounds_delta_mm':bd}
 if not equal:print('source serialization delta',n,a,b,bd,flush=True)
out['all_unmodified_source_roles_conserved']=conserved
changes={}
for oldname,newname in replaced.items():
 a,b=old[oldname],D.getObject(newname).Shape;changes[oldname]={'replacement':newname,'removed_mm3':a.copy().cut(b.copy()).Volume,'added_mm3':b.copy().cut(a.copy()).Volume}
out['changed_material']=changes
r27=read(ROOT/'hardware/cad/flange-controls-r27/candidate-d/geometry-report.json');named={tuple(sorted(replaced.get(n,n)for n in [q['a'],q['b']]))for q in r27['named_unqualified_screw_pilot_interfaces']}
def vol(a,b):
 u,v=a.BoundBox,b.BoundBox
 if any(min(getattr(u,k+'Max'),getattr(v,k+'Max'))<=max(getattr(u,k+'Min'),getattr(v,k+'Min'))+1e-7 for k in 'XYZ'):return 0.
 return a.copy().common(b.copy()).Volume
hits=[];pilots=[];seen=set();pairs=0
for n,o in new.items():
 local=[]
 for m,p in dict(parts,**mates,**allowances).items():
  if n==m:continue
  key=tuple(sorted([n,m]))
  if key in seen:continue
  seen.add(key);pairs+=1;v=vol(o.Shape,p.Shape)
  if v<=1e-5:continue
  row={'a':n,'b':m,'intersection_mm3':v}
  if key in named:pilots.append(row)
  else:local.append(row)
 hits+=local;print('static',n,local,flush=True)
out['new_role_pairs_tested']=pairs;out['unexpected_intersections']=hits;out['named_unqualified_screw_pilot_interfaces']=pilots
(OUT/'geometry-report.json').write_text(json.dumps(out,indent=2)+'\n');A.closeDocument(D.Name);assert sha(nf)==r['native_sha256'];print('saved',output,'hits',len(hits),flush=True)
