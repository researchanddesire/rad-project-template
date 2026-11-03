"""Compact local driver bypasses and create actual motor-output escapes."""
from pathlib import Path
import sys,json
import pcb_r2_route as R
import kicad_sexp as S
K=R.k;ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/'hardware/pcb/route-r17/candidate-e';P=Path(sys.argv[1]).resolve();P.mkdir(parents=True,exist_ok=True);assert not any(P.iterdir())
for p in SOURCE.rglob('*'):
 if p.is_file()and((p.suffix in ['.kicad_pro','.kicad_sch','.kicad_sym','.kicad_mod']or p.suffix=='.kicad_pcb'and p.name!='source-seed.kicad_pcb')or p.name in ['fp-lib-table','sym-lib-table','body-seed.json','local-power.json','power-refinement.json','local-interfaces.json']):
  q=P/p.relative_to(SOURCE);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
bp=P/'body/body-r17.kicad_pcb';b=K.LoadBoard(str(bp));before=R.sha(bp);fps={f.GetReference():f for f in b.GetFootprints()};removed=[]
for t in list(b.GetTracks()):
 if not isinstance(t,K.PCB_VIA)and t.GetLayer()==K.F_Cu and t.GetNetname()in ['MOTOR_3V7','3V3']:removed.append(str(t.m_Uuid.AsString()));b.Delete(t)
assert len(removed)==5
name='C_0402_1005Metric';stock=Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/Capacitor_SMD.pretty')/(name+'.kicad_mod');(P/'body/PrototypeR0.pretty'/(name+'.kicad_mod')).write_bytes(stock.read_bytes());changes={};url='https://www.murata.com/en-global/api/pdfdownloadapi?cate=luCeramicCapacitorsSMD&partno=GRM155R71C104KA88%23'
for ref,y in [('C28',44.5),('C29',45.54)]:
 old=fps[ref];nets={p.GetNumber():p.GetNetname()for p in old.Pads()};context=old.GetPath();props=dict(old.GetProperties());changes[ref]={'old_PCB_value':old.GetValue(),'new_PCB_value':'GRM155R71C104KA88D candidate','old_footprint':str(old.GetFPID().GetLibNickname())+':'+str(old.GetFPID().GetLibItemName()),'new_footprint':'PrototypeR0:'+name,'old_xy':R.mech(old.GetPosition()),'new_pose':[3.65,y,180,'F'],'height_budget_mm':.6,'datasheet':url};b.Delete(old);f=K.FootprintLoad(str(P/'body/PrototypeR0.pretty'),name);f.SetReference(ref);f.SetValue('GRM155R71C104KA88D candidate');f.SetPath(context);f.SetFPID(K.LIB_ID('PrototypeR0',name));f.SetOrientationDegrees(180);f.SetPosition(R.xy(3.65,y));f.Reference().SetVisible(False);f.Value().SetVisible(False)
 for k,v in props.items():f.SetProperty(k,v)
 f.SetProperty('MPN','GRM155R71C104KA88D candidate');b.Add(f);fps[ref]=f
 for p in f.Pads():p.SetNet(b.FindNet(nets[p.GetNumber()]));p.SetZoneConnection(K.ZONE_CONNECTION_FULL)if p.GetNetname()=='GND'else None
old_R4=R.mech(fps['R4'].GetPosition());fps['R4'].SetPosition(R.xy(1.93,46.54))
for ref in ['U8','U9','R48']:
 for p in fps[ref].Pads():
  if p.GetNumber()=='2':assert p.GetNetname()=='GND';p.SetZoneConnection(K.ZONE_CONNECTION_FULL)
for sheet in(P/'body').glob('*.kicad_sch'):
 root=S.parse(sheet.read_text())
 for symbol in S.children(root,'symbol'):
  ref=S.prop(symbol,'Reference')
  if ref not in changes:continue
  note=S.prop(symbol,'ReviewNote');fields={'Footprint':'PrototypeR0:'+name,'Datasheet':url,'ReviewNote':(note+'; 'if note else'')+'GRM155R71C104KA88D 0402 candidate; same100nF/16V/X7R/10percent nominal; installed bias/assembly/availability review pending'};changes[ref]['schematic_field_changes']=fields
  for prop in S.children(symbol,'property'):
   if prop[1].value in fields:prop[2]=S.string(fields[prop[1].value])
 S.write(sheet,root)
routes=[]
def line(net,pts,width,layer='F.Cu'):
 for p,q in zip(pts,pts[1:]):routes.append({'kind':'track','net':net,'layer':layer,'width':width,'start':p,'end':q})
line('MOTOR_3V7',[[5.25,44.35],[4.65,44.35],[4.16,44.5]],.25);line('3V3',[[5.25,46.25],[4.65,46.25],[4.16,45.54]],.25)
line('MOTOR_P',[[5.75,44.35],[5.75,43.8],[5.7,43.75],[5.7,43.55]],.25);line('MOTOR_N',[[6.25,44.35],[6.25,43.7],[6.4,43.55],[6.4,43.15]],.25)
for net,p in [('MOTOR_P',[5.7,43.55]),('MOTOR_N',[6.4,43.15])]:routes.append({'kind':'via','net':net,'position':p,'diameter':.6,'drill':.3})
R.apply_routes(b,routes)
edges=[[R.mech(s.GetStart()),R.mech(s.GetEnd())]for s in b.GetDrawings()if isinstance(s,K.PCB_SHAPE)and s.GetLayer()==K.Edge_Cuts];a,c=edges.pop();outline=[a,c]
while edges:
 i,a,c=next((i,a,c)for i,(a,c)in enumerate(edges)if a==outline[-1]or c==outline[-1]);edges.pop(i);outline.append(c if a==outline[-1]else a)
assert outline[0]==outline[-1];assert not[z for z in b.Zones()if not z.GetIsRuleArea()];R.ground_planes(b,outline[:-1]);K.SaveBoard(str(bp),b);R.fill_save(bp)
R.write(P/'compact-driver.json',{'date':'2026-11-01','builder_sha256':R.sha(Path(__file__)),'source_E_body_sha256':before,'native_body_sha256':R.sha(bp),'component_changes':changes,'R4_old_xy':old_R4,'R4_new_pose':[1.93,46.54,0,'F'],'removed_old_driver_bypass_track_UUIDs':removed,'new_routes':routes,'direct_GND_plane_pads':['U8.2','U9.2','R48.2','C28.2','C29.2'],'scope':'Two100nF16VX7R10percent0402candidates and three further poses. Nominal schematic values/net topology unchanged. Direct ground-plane pads follow existing project pattern; solder/rework process still needs review. Actual four-layer ground pours added, In2 reserved for GND. Motor fanout and ground-plan completion need fresh DRC/drill/fit checks; no part approval or physical acceptance.'});print(P,flush=True)
