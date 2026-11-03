"""Local R16 flange exchange, preserving existing seed geometry and rules."""
from pathlib import Path
import argparse,json,re
import pcb_r2_route as R
K=R.k
ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('action',choices=['export','import']);ap.add_argument('directory',type=Path);ap.add_argument('--seed',type=Path);ap.add_argument('--keep-input-escape',action='store_true');a=ap.parse_args();P=a.directory.resolve()
board=P/'flange/flange-r16.kicad_pcb';dsn=board.with_suffix('.dsn');ses=board.with_suffix('.ses')
def sig(r):
 if r['kind']=='via':return('via',r['net'],tuple(r['position']),r['diameter'],r['drill'])
 return('track',r['net'],r['layer'],tuple(sorted((tuple(r['start']),tuple(r['end'])))),r['width'])
if a.action=='export':
 assert a.seed;source=a.seed.resolve();P.mkdir(parents=True,exist_ok=True);assert not any(P.iterdir()),'Preserve executed candidates'
 for p in source.rglob('*'):
  if p.is_file()and(p.suffix in ['.kicad_pcb','.kicad_pro','.kicad_sch','.kicad_sym','.kicad_mod']or p.name in ['fp-lib-table','sym-lib-table','input-partition.json','input-net-repair.json','flange-seed.json','route-preparation.json','component-proposals.json','input-escape.json']):
   q=P/p.relative_to(source);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
 b=K.LoadBoard(str(board));rejected=json.loads((P/'route-preparation.json').read_text())['new_manual_routes'];reject={sig(t)for t in rejected};removed=[]
 for t,r in zip(list(b.GetTracks()),R.route_records(b)):
  if sig(r)in reject:removed.append(r);b.Delete(t)
 assert not removed if a.keep_input_escape else len(removed)==len(rejected)
 # All surviving existing paths are fixed for this exchange. The failed L
 # VBUS escape is removed explicitly; no clearance rules are relaxed.
 for t in b.GetTracks():t.SetLocked(True)
 K.SaveBoard(str(board),b);R.fill_save(board);(P/'flange/source-seed.kicad_pcb').write_bytes(board.read_bytes());b=K.LoadBoard(str(board))
 for z in list(b.Zones()):
  if not z.GetIsRuleArea()and not z.GetLayerSet().Contains(K.In1_Cu):b.Delete(z)
 assert K.ExportSpecctraDSN(b,str(dsn));txt=dsn.read_text();begin=txt.index('(class kicad_default');end=txt.index('(circuit',begin);header=txt[begin:end]
 classes=[('DockFeed','DOCK_5V',600),('FusedInput','DOCK_FUSED',600),('ChargerFeed','VBUS_CHG',600),('RadioSupply','3V3',300)]
 for _,net,_ in classes:header=re.sub(r'(?<!\S)'+net+r'(?=\s)','',header)
 txt=txt[:begin]+header+txt[end:];insert=txt.rfind('\n  )',0,txt.index('\n  (wiring'));extra=''
 for name,net,width in classes:extra+='\n    (class '+name+' '+net+'\n      (circuit (use_via Via[0-3]_600:300_um))\n      (rule (width '+str(width)+') (clearance 100.1))\n    )'
 dsn.write_text(txt[:insert]+extra+txt[insert:]);R.write(P/'router-exchange.json',{'seed_directory':str(source.relative_to(ROOT)),'source_seed_sha256':R.sha(source/'flange/flange-r16.kicad_pcb'),'seed_board_sha256':R.sha(board),'export_dsn_sha256':R.sha(dsn),'exchange_tool_sha256':R.sha(Path(__file__)),'rejected_L_manual_escape':removed,'rule_note':'Existing native rules unchanged. In1 GND only; input power .6mm,3V3 new branches .3mm, other .2mm; locked .65mm radio feed/USB retained. Current, thermal, installed harness and impedance not qualified.'});print(dsn,flush=True)
else:
 r=json.loads((P/'router-exchange.json').read_text());assert R.sha(board)==r['seed_board_sha256']and R.sha(dsn)==r['export_dsn_sha256'];b=K.LoadBoard(str(board));before=R.route_records(b);assert all(t.IsLocked()for t in b.GetTracks());frozen={sig(t)for t in before};incoming=R.parse_ses(ses);assert all(sig(t)in frozen for t in incoming if t['net']in ['USB_DM','USB_DP']);added=[t for t in incoming if sig(t)not in frozen];R.apply_routes(b,added,locked=False);K.SaveBoard(str(board),b);saved=R.fill_save(board);assert frozen<={sig(t)for t in R.route_records(saved)};r.update({'import_session_sha256':R.sha(ses),'session_records':len(incoming),'added_records':len(added),'preserved_seed_records':len(before),'native_board_sha256':R.sha(board),'scope':'Offline candidate exchange only; fresh native DRC, source parity and independent copper/process/MCAD reviews still required.'});R.write(P/'router-exchange.json',r);print(json.dumps(r,indent=2),flush=True)
