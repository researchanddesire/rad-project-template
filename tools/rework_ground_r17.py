"""Preserve local circuitry, reopen two pin exits, discard unfinished globals."""
from pathlib import Path
import sys,json
from collections import Counter
import pcb_r2_route as R
K=R.k;R.LAYERS['In1.Cu']=K.In1_Cu;ROOT=Path(__file__).resolve().parents[1];source=ROOT/'hardware/pcb/route-r17/candidate-q';P=Path(sys.argv[1]).resolve();P.mkdir(parents=True,exist_ok=True);assert not any(P.iterdir())
records=['fp-lib-table','sym-lib-table','body-seed.json','local-power.json','power-refinement.json','local-interfaces.json','compact-driver.json','signal-first-seed.json','ground-plan.json','ground-application.json','signal-ports.json','signal-application.json']
for p in source.rglob('*'):
 if p.is_file()and((p.suffix in ['.kicad_pro','.kicad_sch','.kicad_sym','.kicad_mod']or p.suffix=='.kicad_pcb'and p.name!='source-seed.kicad_pcb')or p.name in records):
  q=P/p.relative_to(source);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
def point(p):return tuple(round(float(v),5)for v in p)
def sig(t):
 if t['kind']=='via':return('via',t['net'],point(t['position']),t['diameter'],t['drill'])
 return('track',t['net'],t['layer'],tuple(sorted([point(t['start']),point(t['end'])])),t['width'])
bp=P/'body/body-r17.kicad_pcb';b=K.LoadBoard(str(bp));before=R.sha(bp);seed_geometry=json.loads((source/'source-seed-geometry.json').read_text());assert seed_geometry['board_sha256']==R.sha(source/'body/source-seed.kicad_pcb');original=seed_geometry['routes'];ports=json.loads((source/'signal-ports.json').read_text())['routes'];keep=Counter(map(sig,original+ports));removed_global=[]
for t,r in zip(list(b.GetTracks()),R.route_records(b)):
 key=sig(r)
 if keep[key]>0:keep[key]-=1
 else:removed_global.append(r);b.Delete(t)
assert not any(keep.values())
plan=json.loads((source/'ground-plan.json').read_text());selected=[t for t in plan['target_results']if(t['ref'],t['pad'])in {('U7','1'),('U7','4'),('U3','15')}];old=[];vias=set()
for t in selected:
 vias.add(tuple(t['via_xy']))
 old.extend({'kind':'track','net':'GND','layer':t['side'],'width':.25,'start':a,'end':c}for a,c in zip(t['path_xy'],t['path_xy'][1:]))
old.extend({'kind':'via','net':'GND','position':list(v),'diameter':.6,'drill':.3}for v in vias);remove=Counter(map(sig,old));removed_ground=[]
for t,r in zip(list(b.GetTracks()),R.route_records(b)):
 key=sig(r)
 if remove[key]>0:remove[key]-=1;removed_ground.append(r);b.Delete(t)
assert not any(remove.values())
new=[]
for pos,path in [([5.7,26.75],[[5.35,27.4],[5.7,26.75]]),([6.9,28.7],[[5.35,28.6],[5.95,28.8],[6.9,28.7]])]:
 new.append({'kind':'via','net':'GND','position':pos,'diameter':.6,'drill':.3});new.extend({'kind':'track','net':'GND','layer':'B.Cu','width':.25,'start':a,'end':c}for a,c in zip(path,path[1:]))
R.apply_routes(b,new);K.SaveBoard(str(bp),b);R.write(P/'ground-rework.json',{'date':'2026-11-01','builder_sha256':R.sha(Path(__file__)),'source_Q_body_sha256':before,'source_N_seed_sha256':R.sha(source/'body/source-seed.kicad_pcb'),'source_Q_port_plan_sha256':R.sha(source/'signal-ports.json'),'original_seed_records':len(original),'retained_extra_port_records':len(ports),'discarded_unfinished_global_routes':removed_global,'removed_ground_routes':removed_ground,'new_ground_routes':new,'native_body_sha256':R.sha(bp),'scope':'Preserve source local switching/AUX/feedback/supply/IC necks, all other ground stitches and Q port records. Split accelerometer ground stitch into top/bottom exits; leave U3 ground15 stitch to be planned after the motor-arm escape. Rebuild unfinished global routes after actual pin escapes. No poses, circuit or native rule changes. Fresh one-board-process fill and native DRC/drill/reference review required. Source state is saved before zone refill.'});print(len(removed_global),'unfinished global records removed;',len(removed_ground),'ground records replaced by',len(new),flush=True)
