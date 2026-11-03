"""Local wide VIN/VOUT paths and regulator ground necks; no placement changes."""
from pathlib import Path
import sys,json,copy,math
import pcb_r2_route as R
K=R.k;ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/'hardware/pcb/route-r17/candidate-a';P=Path(sys.argv[1]).resolve();P.mkdir(parents=True,exist_ok=True);assert not any(P.iterdir())
for p in SOURCE.rglob('*'):
 if p.is_file()and(p.suffix in ['.kicad_pcb','.kicad_pro','.kicad_sch','.kicad_sym','.kicad_mod']or p.name in ['fp-lib-table','sym-lib-table','body-seed.json']):
  q=P/p.relative_to(SOURCE);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
bp=P/'body/body-r17.kicad_pcb';b=K.LoadBoard(str(bp));before=R.sha(bp);oldp=Path('/private/tmp/r16-regulator-source/buttplug-r2.kicad_pcb');assert R.sha(oldp)=='5ba844fad77f58a8a5dfcb67f50e9070cf021048c29ed45a2751a9b8067f0bd4';old=K.LoadBoard(str(oldp));routes=[]
for dy in [56.5,67.5]:
 for r in R.route_records(old):
  if r['kind']!='track'or r['net']!='SYS'or r['layer']!='B.Cu'or math.dist(r['start'],r['end'])<.001:continue
  if not all(-.2<=p[0]<=15.8 and -24<=p[1]<=-14 for p in [r['start'],r['end']]):continue
  q=copy.deepcopy(r)
  for k in ['start','end']:q[k]=[round(q[k][0]-7.4875,6),round(q[k][1]+dy,6)]
  routes.append(q)
def line(net,points,width,dy=0):
 for p,q in zip(points,points[1:]):routes.append({'kind':'track','net':net,'layer':'B.Cu','width':width,'start':[p[0],round(p[1]+dy,6)],'end':[q[0],round(q[1]+dy,6)]})
for dy,net in [(0,'3V3'),(11,'MOTOR_3V7')]:
 line(net,[[.15,36.125],[-1.975,34.000001],[-1.975,34.5]],.3,dy)
 line(net,[[-1.975,34.5],[-1.975,40.5]],.6,dy)
 line('GND',[[1.5,34.7],[2,35.7],[2.25,35.7],[2.25,36.45]],.15,dy)
# Collapse exact coincident duplicates only; retain the widest existing path.
existing=R.route_records(b)
def key(r):return(r['net'],r['layer'],tuple(sorted([tuple(r['start']),tuple(r['end'])])))
combined={}
for r in existing+routes:
 k=key(r)
 if k not in combined or combined[k]['width']<r['width']:combined[k]=r
for t in list(b.GetTracks()):b.Delete(t)
R.apply_routes(b,list(combined.values()));K.SaveBoard(str(bp),b);R.fill_save(bp);R.write(P/'local-power.json',{'date':'2026-11-01','builder_sha256':R.sha(Path(__file__)),'source_A_body_sha256':before,'source_R2_sha256':R.sha(oldp),'native_body_sha256':R.sha(bp),'new_local_routes':routes,'saved_route_count':len(combined),'scope':'Local B-side supply and bulk-capacitor power tracks plus two copied ground necks. Exact duplicate geometry collapsed to widest width. No vias yet; input/ground planes and remaining routes still need completion and fresh DRC.'});print(len(combined),'tracks',flush=True)
