"""Move the dock pull-up out of a closed routing pocket, preserving its circuit."""
from pathlib import Path
import sys,json
from collections import Counter
import pcb_r2_route as R
import pcb_split_r12 as G
K=R.k;ROOT=Path(__file__).resolve().parents[1];source=ROOT/'hardware/pcb/route-r17/candidate-y';P=Path(sys.argv[1]).resolve();P.mkdir(parents=True,exist_ok=True);assert not any(P.iterdir());records=['fp-lib-table','sym-lib-table','body-seed.json','local-power.json','power-refinement.json','local-interfaces.json','compact-driver.json','signal-first-seed.json','ground-rework.json','fresh-fill.json','ground-plan.json','ground-application.json','signal-ports.json','signal-application.json','local-seed-final.json','dock-port-rework.json']
for p in source.rglob('*'):
 if p.is_file()and((p.suffix in ['.kicad_pro','.kicad_sch','.kicad_sym','.kicad_mod']or p.suffix=='.kicad_pcb'and p.name!='source-seed.kicad_pcb')or p.name in records):
  q=P/p.relative_to(source);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
def point(p):return tuple(round(float(v),5)for v in p)
def sig(t):
 if t['kind']=='via':return('via',t['net'],point(t['position']),t['diameter'],t['drill'])
 return('track',t['net'],t['layer'],tuple(sorted([point(t['start']),point(t['end'])])),t['width'])
parent=ROOT/'hardware/pcb/route-r17/candidate-n/signal-ports.json';target=next(t for t in json.loads(parent.read_text())['targets']if(t['ref'],t['pad'])==('R4','1'));assert target['new_via'];old=[{'kind':'via','net':target['net'],'position':target['via'],'diameter':.6,'drill':.3}]+[{'kind':'track','net':target['net'],'layer':target['side'],'width':target['neck_width_mm'],'start':a,'end':c}for a,c in zip(target['path'],target['path'][1:])];wanted=Counter(map(sig,old));bp=P/'body/body-r17.kicad_pcb';b=K.LoadBoard(str(bp));before=R.sha(bp);removed=[]
for t,r in zip(list(b.GetTracks()),R.route_records(b)):
 key=sig(r)
 if wanted[key]>0:wanted[key]-=1;removed.append(r);b.Delete(t)
assert not any(wanted.values());f=next(f for f in b.GetFootprints()if f.GetReference()=='R4');oldpose=R.mech(f.GetPosition())+[f.GetOrientationDegrees(),'B'if f.IsFlipped()else'F'];oldfields={'value':f.GetValue(),'footprint':str(f.GetFPID().GetLibNickname())+':'+str(f.GetFPID().GetLibItemName()),'pad_nets':{p.GetNumber():p.GetNetname()for p in f.Pads()}};newpose=[7.5,30.75,90,'F'];G.pose(f,*newpose);assert oldfields=={'value':f.GetValue(),'footprint':str(f.GetFPID().GetLibNickname())+':'+str(f.GetFPID().GetLibItemName()),'pad_nets':{p.GetNumber():p.GetNetname()for p in f.Pads()}}
rc=G.rect(f,[K.F_CrtYd,K.B_CrtYd]);clashes=[q.GetReference()for q in b.GetFootprints()if q.GetReference()!='R4'and not q.IsFlipped()and G.overlap(rc,G.rect(q,[K.F_CrtYd,K.B_CrtYd]))];assert not clashes,clashes
K.SaveBoard(str(bp),b);R.fill_save(bp);R.write(P/'signal-repack.json',{'date':'2026-11-01','builder_sha256':R.sha(Path(__file__)),'source_Y_body_sha256':before,'source_N_ports_sha256':R.sha(parent),'R4_old_pose':oldpose,'R4_new_pose':newpose,'unchanged_R4_fields':oldfields,'removed_old_R4_3V3_escape':removed,'native_body_sha256':R.sha(bp),'scope':'Move only R4 beside the interboard header, outside its native courtyard. Same component/value/pad nets; old pull-up branch escape removed for replanning. No substrate, power-stage placement, circuit or native rule changes. Native DRC, new escapes and actual CAD fit/integration still required.'});print(P,flush=True)
