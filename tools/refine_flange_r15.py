"""Explicit R15F local repairs; fresh native checks decide acceptance."""
from pathlib import Path
import argparse,hashlib,json,shutil,math
import pcb_r2_route as R
K=R.k;ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/'hardware/pcb/route-r15/candidate-f';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ap=argparse.ArgumentParser();ap.add_argument('directory',type=Path);a=ap.parse_args();P=a.directory.resolve();P.mkdir(parents=True,exist_ok=True);assert not any(P.iterdir())
for f in SOURCE.rglob('*'):
 if f.is_file()and(f.suffix in ['.kicad_pcb','.kicad_pro','.kicad_sch','.kicad_sym','.kicad_mod']or f.name in ['fp-lib-table','sym-lib-table']):
  q=P/f.relative_to(SOURCE);q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,q)
board=P/'flange/flange-r15.kicad_pcb';before=sha(board);b=K.LoadBoard(str(board));changes=[]
for t in list(b.GetTracks()):
 if t.IsLocked():continue
 if isinstance(t,K.PCB_VIA)and t.GetNetname()=='BOOT_N'and math.dist(R.mech(t.GetPosition()),[-22.2019,-11.5814])<.00001:
  changes.append({'remove':{'via_net':t.GetNetname(),'xy':R.mech(t.GetPosition())}});b.Delete(t)
 elif t.GetNetname()=='DOCK_PRESENT_N':
  old=[-30.9064,-11.5716];new=[-30.9064,-11.65]
  if isinstance(t,K.PCB_VIA):
   assert math.dist(R.mech(t.GetPosition()),old)<.00001;t.SetPosition(R.xy(*new));changes.append({'moved_via':{'old':old,'new':new}})
  else:
   for g,s in [(t.GetStart,t.SetStart),(t.GetEnd,t.SetEnd)]:
    if math.dist(R.mech(g()),old)<.00001:s(R.xy(*new))
 elif not isinstance(t,K.PCB_VIA)and t.GetWidth()<K.FromMM(.15):
  changes.append({'widened':{'net':t.GetNetname(),'old':K.ToMM(t.GetWidth()),'new':.15,'start':R.mech(t.GetStart()),'end':R.mech(t.GetEnd())}});t.SetWidth(K.FromMM(.15))
routes=[]
def path(net,points,layer='F.Cu'):
 for p,q in zip(points,points[1:]):routes.append({'kind':'track','net':net,'layer':layer,'start':p,'end':q,'width':.2})
def via(net,p):routes.append({'kind':'via','net':net,'position':p,'diameter':.6,'drill':.3})
path('I2C_SCL',[[-26.8,-17.7],[-27.1,-17.5],[-35.5,-17.5]]);via('I2C_SCL',[-35.5,-17.5]);path('I2C_SCL',[[-35.5,-17.5],[-33.1978,-17.5]],'B.Cu')
path('STRAP8',[[-26.8,-15.3],[-35.5,-15.3]]);via('STRAP8',[-35.5,-15.3]);path('STRAP8',[[-35.5,-15.3],[-35.5,-22.9052],[-33.57,-22.9052]],'In2.Cu')
R.apply_routes(b,routes,locked=True);K.SaveBoard(str(board),b);R.fill_save(board)
(P/'local-repairs.json').write_text(json.dumps({'source_native_board_sha256':before,'native_board_sha256':sha(board),'builder_sha256':sha(Path(__file__)),'changes':changes,'routes':routes,'scope':'Explicit local route trial; no DRC or process acceptance inferred.'},indent=2)+'\n');print(board)
