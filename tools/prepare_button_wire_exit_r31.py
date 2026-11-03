"""Shift flange risers .6mm toward the button clearance, away from keeper."""
from pathlib import Path
import sys,json,hashlib
P=Path(sys.argv[1]);O=Path(sys.argv[2]);O.mkdir(parents=True,exist_ok=True);assert not any(O.iterdir());r=json.loads(P.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for w in r['wires']:
 c=w['curves']
 for i,p in enumerate(c[3]['poles_xyz_mm']):p[0]+=.6*i/5
 for key in ['start_xyz_mm','mid_xyz_mm','end_xyz_mm']:c[4][key][0]+=.6
 for p in c[5]['poles_xyz_mm']:p[0]+=.6
 for p in c[6]['poles_xyz_mm'][:3]:p[0]+=.6
r['loop_search_seed_parameters']=r['loop_search']['parameters'];r['R31_exit_preparer_sha256']=sha(Path(__file__));r['source_R31B_plan_sha256']=sha(P);r['scope']='New seed only. Riser X shifts+.6; body/neck prefixes and header ends retained. Search, full guards and new native check required.'
(O/'wire-plan.json').write_text(json.dumps(r,indent=2)+'\n')
