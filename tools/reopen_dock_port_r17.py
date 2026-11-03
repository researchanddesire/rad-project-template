"""Move the low-current dock-sense escape out of the VSEL ground path."""
from pathlib import Path
import sys,json
from collections import Counter
import pcb_r2_route as R
K=R.k;ROOT=Path(__file__).resolve().parents[1];source=ROOT/'hardware/pcb/route-r17/candidate-x';P=Path(sys.argv[1]).resolve();P.mkdir(parents=True,exist_ok=True);assert not any(P.iterdir());records=['fp-lib-table','sym-lib-table','body-seed.json','local-power.json','power-refinement.json','local-interfaces.json','compact-driver.json','signal-first-seed.json','ground-rework.json','fresh-fill.json','ground-plan.json','ground-application.json','signal-ports.json','signal-application.json','local-seed-final.json']
for p in source.rglob('*'):
 if p.is_file()and((p.suffix in ['.kicad_pro','.kicad_sch','.kicad_sym','.kicad_mod']or p.suffix=='.kicad_pcb'and p.name!='source-seed.kicad_pcb')or p.name in records):
  q=P/p.relative_to(source);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
def point(p):return tuple(round(float(v),5)for v in p)
def sig(t):
 if t['kind']=='via':return('via',t['net'],point(t['position']),t['diameter'],t['drill'])
 return('track',t['net'],t['layer'],tuple(sorted([point(t['start']),point(t['end'])])),t['width'])
parent=ROOT/'hardware/pcb/route-r17/candidate-q/signal-ports.json';plan=json.loads(parent.read_text());target=next(t for t in plan['targets']if(t['ref'],t['pad'])==('R4','2'));assert target['new_via'];old=[{'kind':'via','net':target['net'],'position':target['via'],'diameter':.6,'drill':.3}]+[{'kind':'track','net':target['net'],'layer':target['side'],'width':target['neck_width_mm'],'start':a,'end':c}for a,c in zip(target['path'],target['path'][1:])];wanted=Counter(map(sig,old));bp=P/'body/body-r17.kicad_pcb';b=K.LoadBoard(str(bp));before=R.sha(bp);removed=[]
for t,r in zip(list(b.GetTracks()),R.route_records(b)):
 key=sig(r)
 if wanted[key]>0:wanted[key]-=1;removed.append(r);b.Delete(t)
assert not any(wanted.values());K.SaveBoard(str(bp),b);R.fill_save(bp);R.write(P/'dock-port-rework.json',{'builder_sha256':R.sha(Path(__file__)),'source_X_body_sha256':before,'Q_port_plan_sha256':R.sha(parent),'removed_routes':removed,'native_body_sha256':R.sha(bp),'scope':'Remove dock-sense R4.2 via and surface tail from inside the regulator control-ground path. Replan that low-current escape around the protected VSEL connection. No poses, circuit or native rule changes; fresh native checks required.'});print(P,flush=True)
