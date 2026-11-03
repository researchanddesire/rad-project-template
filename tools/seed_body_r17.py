"""Begin R17 body routing from exact R16U poses and unchanged circuit."""
from pathlib import Path
import sys,json,math,copy
import pcb_r2_route as R
import kicad_sexp as S
K=R.k;ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/'hardware/pcb/route-r16/candidate-u';P=Path(sys.argv[1]).resolve();P.mkdir(parents=True,exist_ok=True);assert not any(P.iterdir())
for p in SOURCE.rglob('*'):
 if p.is_file()and(p.suffix in ['.kicad_pcb','.kicad_pro','.kicad_sch','.kicad_sym','.kicad_mod']or p.name in ['fp-lib-table','sym-lib-table']):
  q=P/str(p.relative_to(SOURCE)).replace('-r16','-r17');q.parent.mkdir(parents=True,exist_ok=True)
  if p.suffix=='.kicad_sch':q.write_text(p.read_text().replace('-r16','-r17'))
  elif p.suffix=='.kicad_pro':j=json.loads(p.read_text());j['meta']['filename']=q.name;q.write_text(json.dumps(j,indent=2)+'\n')
  else:q.write_bytes(p.read_bytes())
bp=P/'body/body-r17.kicad_pcb';before=R.sha(bp);b=K.LoadBoard(str(bp));assert not list(b.GetTracks());source=Path('/private/tmp/r16-regulator-source/buttplug-r2.kicad_pcb');assert R.sha(source)=='5ba844fad77f58a8a5dfcb67f50e9070cf021048c29ed45a2751a9b8067f0bd4';old=K.LoadBoard(str(source));routes=[];copied=[]
for dy in [56.5,67.5]:
 for r in R.route_records(old):
  if r['kind']!='track'or r['net']not in ['REG1_L1','REG1_L2','REG1_AUX','REG1_FB']:continue
  if math.dist(r['start'],r['end'])<.001:continue
  assert r['layer']=='B.Cu';q=copy.deepcopy(r)
  for k in ['start','end']:q[k]=[round(q[k][0]-7.4875,6),round(q[k][1]+dy,6)]
  if dy==67.5:q['net']=q['net'].replace('REG1_','REG2_')
  routes.append(q);copied.append(q)
def line(net,points,width,dy=0):
 for p,q in zip(points,points[1:]):routes.append({'kind':'track','net':net,'layer':'B.Cu','width':width,'start':[p[0],round(p[1]+dy,6)],'end':[q[0],round(q[1]+dy,6)]})
for dy,net in [(0,'3V3'),(11,'MOTOR_3V7')]:
 line('SYS',[[3.65,36.125],[3.65,36.625]],.4248,dy)
 line('SYS',[[3.65,36.125],[4.45,36.125]],.3,dy)
 line('SYS',[[4.45,36.125],[5.15,35.625]],.25,dy)
 line(net,[[.85,36.125],[.85,36.625]],.3,dy)
 line(net,[[.85,36.125],[.15,36.125]],.3,dy)
 line(net,[[.15,36.125],[-.45,35.625]],.25,dy)
# REG2 pin14 is MOTOR_ARM, not REG2_PS. Only REG1 ties pin14 to PS.
line('REG1_PS',[[3.65,35.625],[3.4685,35.625],[3,35.1565],[3,34.7]],.2)
R.apply_routes(b,routes);K.SaveBoard(str(bp),b);R.fill_save(bp)
report={'date':'2026-11-01','builder_sha256':R.sha(Path(__file__)),'source_R16_body_sha256':before,'native_body_sha256':R.sha(bp),'source_R2_body_sha256':R.sha(source),'flange_byte_identical_to_R16U':R.sha(P/'flange/flange-r17.kicad_pcb')==R.sha(SOURCE/'flange/flange-r16.kicad_pcb'),'copied_local_back_routes':copied,'all_seed_routes':routes,'ground_reference_plan':'B-side regulators use In2 GND reference; later signals may use F/In1/B. Split source starts with no copper zones; add actual ground zones in the later explicit step. No signal may occupy In2. No stackup/thermal/current/loop qualification inferred.','scope':'Explicit same-face local switching/AUX/feedback and VIN/VOUT escapes only; no whole-board route or fresh DRC/ERC/physical acceptance. Footprint poses and electrical circuit remain unchanged.'};R.write(P/'body-seed.json',report);print(len(routes),'manual tracks;',report['flange_byte_identical_to_R16U'],'flange source equality',flush=True)
