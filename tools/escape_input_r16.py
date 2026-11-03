"""Explicit final J7 charging-power escape; preserve N as a failed route."""
from pathlib import Path
import sys,json
import pcb_r2_route as R
K=R.k;ROOT=Path(__file__).resolve().parents[1];source=ROOT/'hardware/pcb/route-r16/candidate-n';P=Path(sys.argv[1]).resolve();P.mkdir(parents=True,exist_ok=True);assert not any(P.iterdir())
for p in source.rglob('*'):
 if p.is_file()and(p.suffix in ['.kicad_pcb','.kicad_pro','.kicad_sch','.kicad_sym','.kicad_mod']or p.name in ['fp-lib-table','sym-lib-table','input-partition.json','input-net-repair.json','flange-seed.json','route-preparation.json','component-proposals.json']):
  q=P/p.relative_to(source);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
bp=P/'flange/flange-r16.kicad_pcb';b=K.LoadBoard(str(bp));before=R.sha(bp);removed=[]
for t in list(b.GetTracks()):
 if not isinstance(t,K.PCB_VIA)and t.GetNetname()=='POWER_N'and t.GetLayer()==K.F_Cu and all(-24.6<=p[0]<=-24.5 and -17.98<=p[1]<=-14 for p in [R.mech(t.GetStart()),R.mech(t.GetEnd())]):
  removed.append(str(t.m_Uuid.AsString()));b.Delete(t)
assert len(removed)==3
routes=[]
for net,layer,width,pts in [('POWER_N','F.Cu',.2,[[-24.55,-14],[-24.375,-14.175],[-24.375,-17.7748],[-24.5754,-17.9752]]),('VBUS_CHG','B.Cu',.6,[[-26.5,-12.8],[-26.5,-13.7],[-24.94,-15.32]])]:
 for p,q in zip(pts,pts[1:]):routes.append({'kind':'track','net':net,'layer':layer,'width':width,'start':p,'end':q})
routes.append({'kind':'via','net':'VBUS_CHG','position':[-24.94,-15.32],'diameter':.6,'drill':.3});R.apply_routes(b,routes);K.SaveBoard(str(bp),b);R.fill_save(bp);R.write(P/'input-escape.json',{'builder_sha256':R.sha(Path(__file__)),'source_N_flange_sha256':before,'native_flange_sha256':R.sha(bp),'removed_POWER_segment_UUIDs':removed,'added_manual_routes':routes,'scope':'Charging header escape beside F-side module lands and small local POWER control detour only. MODE routing unchanged. One remaining interlayer power route still required; fresh DRC required.'});print(P,flush=True)
