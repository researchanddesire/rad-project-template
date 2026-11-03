"""Finite hub closure and flange seating with the complete wires held fixed."""
from pathlib import Path
import sys,json,hashlib
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part
ROOT=Path(__file__).resolve().parents[1];P=Path(sys.argv[1]).resolve();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();r=json.loads((P/'geometry-report.json').read_text());nf=P/'HarnessSupportR30.FCStd';before=sha(nf);assert before==r['native_sha256'];D=A.openDocument(str(nf));allparts={n:D.getObject(n).Shape for n in dict(r['parts'],**r['mates'],**r['allowances'])};r27=json.loads((ROOT/'hardware/cad/flange-controls-r27/candidate-d/geometry-report.json').read_text());island=set(r27['inverse_transformed_flange_roles']);covers={'FlangeCoverLower','FlangeCoverUpper','ServiceCoverReference'};hardware={'HubBolt_1','HubBolt1','HubNut_1','HubNut1','FlangeKeeperScrewEnvelopeR27'};hubs={'HarnessLeftHubR30','HarnessRightHubR30'};keeper={'HarnessKeeperR30'}
def volume(a,b):
 u,v=a.BoundBox,b.BoundBox
 if any(min(getattr(u,k+'Max'),getattr(v,k+'Max'))<=max(getattr(u,k+'Min'),getattr(v,k+'Min'))+1e-7 for k in 'XYZ'):return 0.
 return a.copy().common(b.copy()).Volume
def poses(names,fixed,offsets):
 result=[]
 for x in offsets:
  bad=[]
  for n in names:
   s=allparts[n].copy();s.translate(A.Vector(x,0,0))
   for m,p in fixed.items():
    v=volume(s,p)
    if v>1e-5:bad.append({'moving':n,'fixed':m,'intersection_mm3':v})
  result.append({'X_offset_mm':x,'hits':bad});print(names[0],x,bad,flush=True)
 return result
# Fixture holds all10 full paths and both pads at their final positions. The
# flange board/mates and fasteners/covers wait. Other hub is already seated.
basewaiting=island|covers|hardware|keeper
leftfixed={n:s for n,s in allparts.items()if n not in basewaiting|{'HarnessLeftHubR30'}};rightfixed={n:s for n,s in allparts.items()if n not in basewaiting|{'HarnessRightHubR30'}}
left=poses(['HarnessLeftHubR30'],leftfixed,[-30,-20,-10,-5,-2,-1,-.5,-.25,0]);right=poses(['HarnessRightHubR30'],rightfixed,[30,20,10,5,2,1,.5,.25,0])
# Both hubs seated, all wires/pads fixed. Populate flange board through its
# retained +X loading path, with all three mates and keeper/covers waiting.
board=[n for n in island if n in r['parts']];board.sort();waiting=set(board)|covers|keeper|{n for n in r['mates']if n in island}|{'FlangeKeeperScrewEnvelopeR27'};fixed={n:s for n,s in allparts.items()if n not in waiting};flange=poses(board,fixed,[-50,-40,-30,-20,-10,-5,-2,-1,-.5,-.25,0])
out={'native_sha256':before,'geometry_report_sha256':sha(P/'geometry-report.json'),'screener_sha256':sha(Path(__file__)),'left_hub_listed_poses':left,'right_hub_listed_poses':right,'populated_flange_listed_poses':flange,'all_listed_poses_clear':not any(q['hits']for q in left+right+flange),'staging':{'all_10_wires_and_both_pads':'Fixed at complete R29/R30 installed geometry throughout each screen; fixture/hand support assumed.','hub_waiting':sorted(basewaiting),'flange_waiting':sorted(waiting)},'scope':'Finite rigid hub/flange positions against complete fixed wire geometry and cured pad shapes. Not continuous travel or a modeled fixture/hand/tool; does not prove body cartridge/threading, nominal J7 mating stroke, connected service flex, casting/cure/adhesion/physical assembly. Source circuit/exterior unchanged; battery OPEN.'};(P/'assembly-screen.json').write_text(json.dumps(out,indent=2)+'\n');A.closeDocument(D.Name);assert sha(nf)==before;print('listed hub/flange poses clear',out['all_listed_poses_clear'],flush=True)
