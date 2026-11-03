"""Move the flange wire rise outboard4mm, preserving body/neck and pin maps."""
from pathlib import Path
import sys,json,hashlib
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'hardware/cad/interboard-r29/review-e/wire-plan.json';P=Path(sys.argv[1]);P.mkdir(parents=True,exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();r=json.loads(SRC.read_text())
for w in r['wires']:
 c=w['curves'];c[3]['poles_xyz_mm']=[[float(-8+( -14+8)*i/5),p[1],p[2]]for i,p in enumerate(c[3]['poles_xyz_mm'])]
 for k in ['start_xyz_mm','mid_xyz_mm','end_xyz_mm']:c[4][k][0]-=4
 for p in c[5]['poles_xyz_mm']:p[0]-=4
 for p in c[6]['poles_xyz_mm'][:3]:p[0]-=4
r['loop_search_seed_parameters']=r['loop_search']['parameters'];r['source_R30_native_sha256']=sha(ROOT/'hardware/cad/harness-support-r30/candidate-b/HarnessSupportR30.FCStd');r['R31_preparer_sha256']=sha(Path(__file__));r['source_R29_plan_sha256']=sha(SRC);r['scope']='Seed only: body fanout/neck and XY turn unchanged; horizontal span extends4mm and both concentric risers shiftX-4. Loops require new search, complete guard and native fit. No radius/separation acceptance transfers.'
(P/'wire-plan.json').write_text(json.dumps(r,indent=2)+'\n')
