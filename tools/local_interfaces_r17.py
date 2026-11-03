"""Place charger/driver bypasses by actual pins; add local same-face paths."""
from pathlib import Path
import sys,json
import pcb_r2_route as R
K=R.k;ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/'hardware/pcb/route-r17/candidate-c';P=Path(sys.argv[1]).resolve();P.mkdir(parents=True,exist_ok=True);assert not any(P.iterdir())
for p in SOURCE.rglob('*'):
 if p.is_file()and((p.suffix in ['.kicad_pro','.kicad_sch','.kicad_sym','.kicad_mod']or p.suffix=='.kicad_pcb'and p.name!='source-seed.kicad_pcb')or p.name in ['fp-lib-table','sym-lib-table','body-seed.json','local-power.json','power-refinement.json']):
  q=P/p.relative_to(SOURCE);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
bp=P/'body/body-r17.kicad_pcb';b=K.LoadBoard(str(bp));before=R.sha(bp);fps={f.GetReference():f for f in b.GetFootprints()};poses={'C1':[4.5,42.4,180,'F'],'C2':[.8,39.45,180,'F'],'C3':[7.725,39.4,90,'F'],'C28':[7.975,44.8,90,'F'],'C29':[3.8,45.3,270,'F'],'R41':[6.4,35.85,90,'F'],'R43':[3.05,31.75,0,'B'],'C27':[5.1,30.1,0,'B'],'R25':[7.95,35.645,90,'F'],'R48':[7.69,37.32,0,'F']};old={}
for ref,(x,y,angle,side)in poses.items():
 f=fps[ref];old[ref]={'xy':R.mech(f.GetPosition()),'angle':f.GetOrientationDegrees(),'side':'B'if f.IsFlipped()else'F'}
 if(f.GetLayer()==K.B_Cu)!=(side=='B'):f.Flip(f.GetPosition(),True)
 f.SetOrientationDegrees(angle);f.SetPosition(R.xy(x,y));f.SetLocked(False)
def rect(f):
 ss=[s.GetBoundingBox()for s in f.GraphicalItems()if isinstance(s,K.PCB_SHAPE)and s.GetLayer()in [K.F_CrtYd,K.B_CrtYd]]
 return[min(s.GetLeft()for s in ss),min(s.GetTop()for s in ss),max(s.GetRight()for s in ss),max(s.GetBottom()for s in ss)]if ss else None
conflicts=[];ff=list(fps.values())
for i,f in enumerate(ff):
 for g in ff[i+1:]:
  a,c=rect(f),rect(g)
  if f.IsFlipped()==g.IsFlipped()and a and c and min(a[2],c[2])-max(a[0],c[0])>1000 and min(a[3],c[3])-max(a[1],c[1])>1000:conflicts.append([f.GetReference(),g.GetReference()])
assert not conflicts,conflicts
routes=[]
def line(net,pts,width):
 for p,q in zip(pts,pts[1:]):routes.append({'kind':'track','net':net,'layer':'F.Cu','width':width,'start':p,'end':q})
line('VBUS_CHG',[[5.45,40.8],[5.45,41.4]],.3);line('VBUS_CHG',[[5.45,41.4],[5.45,42.4]],.6)
line('PACK_P',[[3.3,39.15],[3.3,39.65]],.3);line('PACK_P',[[3.3,39.15],[2.6,39.15],[1.75,39.45]],.3)
line('SYS',[[6.1,39.15],[6.1,39.65]],.3);line('SYS',[[6.1,39.15],[6.8,39.15],[7.725,38.45]],.3)
line('MOTOR_3V7',[[5.25,44.35],[5.25,43.45],[7.3,43.45],[7.975,44.125]],.25)
line('3V3',[[5.25,46.25],[4.55,46.25],[3.8,45.975]],.25)
line('GND',[[4.7,39.4],[3.95,38.65],[3.95,38]],.2);line('GND',[[4.7,39.4],[5.45,38.65],[5.45,38]],.2)
line('GND',[[6,45.3],[6.75,45],[6.75,44.35]],.2);line('GND',[[6.75,45],[6.75,46.25]],.2);line('GND',[[6,45.3],[5.75,45.8],[5.75,46.25]],.2)
R.apply_routes(b,routes);K.SaveBoard(str(bp),b);R.fill_save(bp);R.write(P/'local-interfaces.json',{'date':'2026-11-01','builder_sha256':R.sha(Path(__file__)),'source_C_body_sha256':before,'native_body_sha256':R.sha(bp),'old_poses':old,'new_poses':poses,'same_face_courtyard_conflicts':conflicts,'new_local_routes':routes,'scope':'Actual IN13 bypass C1, BAT C2, OUT C3 and separate driver VM/VCC bypasses placed by pins. Ten explicit pose changes; all values, pads/nets and outline retained. Ground necks join exposed pads to discrete grounds. Carrier fit and remaining routes require fresh checks; no loop/thermal/current/process acceptance.'});print(P,flush=True)
