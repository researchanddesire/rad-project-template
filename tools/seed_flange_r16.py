"""R16 dock protection seed, outward service port and matched F USB.

Explicit new pin poses/route source; preserve R15 as the prior checkpoint.
Native DRC, pad parity, reference and drill/paste review remain mandatory.
"""
from pathlib import Path
import sys,json,math
import pcb_r2_route as R
import pcb_split_r12 as G
K=R.k;ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/'hardware/pcb/route-r16/candidate-j';P=Path(sys.argv[1]).resolve();P.mkdir(parents=True,exist_ok=True);assert not any(P.iterdir())
for p in SOURCE.rglob('*'):
 if p.is_file()and(p.suffix in ['.kicad_pcb','.kicad_pro','.kicad_sch','.kicad_sym','.kicad_mod']or p.name in ['fp-lib-table','sym-lib-table','input-partition.json','input-net-repair.json']):
  q=P/p.relative_to(SOURCE);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
bp=P/'flange/flange-r16.kicad_pcb';b=K.LoadBoard(str(bp));fps={f.GetReference():f for f in b.GetFootprints()};G.pose(fps['J4'],-19.4,-22,0,'F');G.pose(fps['D1'],-17.18,-17.2,180,'F');removed=[];removed_zones=0
for t in list(b.GetTracks()):
 delete=t.GetNetname()in ['USB_DM','USB_DP']or(t.GetNetname()in ['MCU_EN','BOOT_N','UART_TX']and not t.IsLocked())
 if not isinstance(t,K.PCB_VIA)and t.GetNetname()=='GND'and any(math.dist(R.mech(p),[-16.9,-24])<.00001 for p in [t.GetStart(),t.GetEnd()]):delete=True
 if delete:removed.append(str(t.m_Uuid.AsString()));b.Delete(t)
for z in list(b.Zones()):
 if z.GetIsRuleArea()and z.GetLayerSet().Contains(K.In1_Cu)and z.GetDoNotAllowVias()and not z.GetDoNotAllowTracks():b.Delete(z);removed_zones+=1
assert removed_zones==18
def pad(ref,n):return R.mech(next(p for p in fps[ref].Pads()if p.GetNumber()==str(n)).GetPosition())
assert pad('J4',2)==[-20.9,-20]and pad('J4',3)==[-19.9,-20]
o=.45*math.sqrt(2);rise=.65
dp=[pad('U6',27),[-29.3,-12.6+rise],[-28.15-rise,-11.45],[-26.7+o,-11.45],[-25.5,-12.65+o],[-25.5,-18.8+o],[-25.75+o,-18.55],[-20.95,-18.55],[-19.9,-19.6],pad('J4',3)]
def negative(depth):return[pad('U6',26),[-28.5,-12.3],[-28.1,-11.9],[-26.25,-11.9],[-25.95,-12.2],[-25.95,-18.35],[-25.3,-19],[-24.7,-19],[-24.2,-19.5],[-24.2,-19.5-depth],[-23.7,-20-depth],[-23.3,-20-depth],[-22.8,-19.5-depth],[-22.8,-19.5],[-22.3,-19],[-21.55,-19],[-20.9,-19.65],pad('J4',2)]
length=lambda pts:sum(math.dist(p,q)for p,q in zip(pts,pts[1:]));lo,hi=0,1.5
assert length(negative(lo))<length(dp)<length(negative(hi))
for _ in range(60):
 mid=(lo+hi)/2
 if length(negative(mid))<length(dp):lo=mid
 else:hi=mid
dm=negative((lo+hi)/2);routes=[]
def path(n,pts,w=.2,l='F.Cu'):
 for p,q in zip(pts,pts[1:]):
  if math.dist(p,q)>1e-8:routes.append({'kind':'track','net':n,'start':p,'end':q,'width':w,'layer':l})
def via(n,p):routes.append({'kind':'via','net':n,'position':p,'diameter':.6,'drill':.3})
path('USB_DM',dm);path('USB_DP',dp);path('DOCK_FUSED',[pad('F1',2),pad('D1',1)],.6)
path('DOCK_5V',[pad('F1',1),[-22.4,-17.2],[-22.3,-17.3]],.6);via('DOCK_5V',[-22.3,-17.3]);path('VBUS_CHG',[pad('D1',2),[-16,-17.67],[-16,-18.3]],.6);via('VBUS_CHG',[-16,-18.3]);R.apply_routes(b,routes);R.usb_via_rule_areas(b);K.SaveBoard(str(bp),b);saved=R.fill_save(bp);usb={}
for net in ['USB_DM','USB_DP']:
 tt=[t for t in saved.GetTracks()if t.GetNetname()==net];assert all(not isinstance(t,K.PCB_VIA)and t.GetLayer()==K.F_Cu for t in tt);usb[net]={'length_mm':sum(K.ToMM(t.GetLength())for t in tt),'widths_mm':sorted({K.ToMM(t.GetWidth())for t in tt}),'signal_vias':0}
assert abs(usb['USB_DM']['length_mm']-usb['USB_DP']['length_mm'])<.00001
out={'date':'2026-11-01','builder_sha256':R.sha(Path(__file__)),'source_J_flange_sha256':R.sha(SOURCE/'flange/flange-r16.kicad_pcb'),'native_flange_sha256':R.sha(bp),'deleted_track_via_UUIDs':removed,'deleted_old_USB_via_keepouts':removed_zones,'new_manual_routes':routes,'actual_saved_USB':usb,'DM_single_detour_depth_mm':(lo+hi)/2,'scope':'New USB pair to reversed/outward service connector, one local matched DM detour, local F dock-protection feed/return fanouts. .2width/.25main-gap candidates do not prove impedance; remaining input/control routing and native/return/paste/drill/MCAD checks required.'};(P/'flange-seed.json').write_text(json.dumps(out,indent=2)+'\n');print(usb,flush=True)
