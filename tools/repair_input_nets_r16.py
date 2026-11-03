"""Explicit repair of missing native flange nets in retained I trial."""
from pathlib import Path
import sys,hashlib,json
import pcb_r2_route as R
K=R.k;ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/'hardware/pcb/route-r16/candidate-i';P=Path(sys.argv[1]).resolve();P.mkdir(parents=True,exist_ok=True);assert not any(P.iterdir())
for p in SOURCE.rglob('*'):
 if p.is_file()and(p.suffix in ['.kicad_pcb','.kicad_pro','.kicad_sch','.kicad_sym','.kicad_mod']or p.name in ['fp-lib-table','sym-lib-table','input-partition.json']):
  q=P/p.relative_to(SOURCE);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
bp=P/'flange/flange-r16.kicad_pcb';before=R.sha(bp);b=K.LoadBoard(str(bp));new=[]
for name in ['DOCK_FUSED','VBUS_CHG']:
 if not b.FindNet(name):b.Add(K.NETINFO_ITEM(b,name));new.append(name)
assert len(new)==2
fixed=[]
for ref,pins in [('F1',{'1':'DOCK_5V','2':'DOCK_FUSED'}),('D1',{'1':'DOCK_FUSED','2':'VBUS_CHG'}),('J7',{'2':'VBUS_CHG'})]:
 f=next(f for f in b.GetFootprints()if f.GetReference()==ref)
 for n,name in pins.items():
  p=next(p for p in f.Pads()if p.GetNumber()==n);fixed.append({'ref':ref,'pin':n,'old':p.GetNetname(),'new':name});net=b.FindNet(name);assert net;p.SetNet(net)
K.SaveBoard(str(bp),b);R.fill_save(bp)
(P/'input-net-repair.json').write_text(json.dumps({'date':'2026-11-01','tool_sha256':R.sha(Path(__file__)),'source_I_flange_sha256':before,'new_flange_sha256':R.sha(bp),'new_native_nets':new,'pad_assignments':fixed,'reason':'Saved R15 flange had pruned unused nets. I used FindNet without creating absent VBUS_CHG/DOCK_FUSED, leaving four pads netless. Native pin parity, not its misleading0DRC/1open count, exposed this. J explicitly creates/assigns actual nets; fresh native/XML review required.'},indent=2)+'\n');print(P,flush=True)
