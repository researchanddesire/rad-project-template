"""Offline R15 flange DSN exchange; retain immutable manual seed copper.

Uses local native KiCad and an explicitly configured local router. Native
DRC, ground-reference, pad/net parity and process review remain separate.
"""
from pathlib import Path
import argparse, hashlib, json, re, shutil
import pcb_r2_route as R
K=R.k
ROOT=Path(__file__).resolve().parents[1]
SEED=ROOT/'hardware/pcb/route-r15/candidate-e'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ap=argparse.ArgumentParser();ap.add_argument('action',choices=['export','import']);ap.add_argument('directory',type=Path);ap.add_argument('--seed',type=Path,default=SEED);a=ap.parse_args();P=a.directory.resolve();SEED=a.seed.resolve()
board=P/'flange/flange-r15.kicad_pcb';dsn=P/'flange/flange-r15.dsn';ses=P/'flange/flange-r15.ses'
def sig(r):
 if r['kind']=='via':return('via',r['net'],tuple(r['position']),r['diameter'],r['drill'])
 return('track',r['net'],r['layer'],tuple(sorted((tuple(r['start']),tuple(r['end'])))),r['width'])
if a.action=='export':
 P.mkdir(parents=True,exist_ok=True);assert not any(P.rglob('*.kicad_pcb')),'Preserve executed candidates'
 for f in SEED.rglob('*'):
  if f.is_file()and(f.suffix in ['.kicad_pcb','.kicad_pro','.kicad_sch','.kicad_sym','.kicad_mod']or f.name in ['fp-lib-table','sym-lib-table']):
   q=P/f.relative_to(SEED);q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,q)
 shutil.copyfile(board,P/'flange/source-seed.kicad_pcb')
 b=K.LoadBoard(str(board))
 for z in list(b.Zones()):
  if not z.GetIsRuleArea()and not z.GetLayerSet().Contains(K.In1_Cu):b.Delete(z)
 assert K.ExportSpecctraDSN(b,str(dsn))
 txt=dsn.read_text();begin=txt.index('(class kicad_default');end=txt.index('(circuit',begin);header=txt[begin:end]
 for net in ['DOCK_5V','3V3']:header=re.sub(r'(?<!\S)'+net+r'(?=\s)','',header)
 txt=txt[:begin]+header+txt[end:];insert=txt.rfind('\n  )',0,txt.index('\n  (wiring'))
 extra=''
 for name,net,width in [('DockFeed','DOCK_5V',600),('RadioSupply','3V3',300)]:
  extra+='\n    (class '+name+' '+net+'\n      (circuit (use_via Via[0-3]_600:300_um))\n      (rule (width '+str(width)+') (clearance 100.1))\n    )'
 dsn.write_text(txt[:insert]+extra+txt[insert:])
 (P/'router-exchange.json').write_text(json.dumps({'seed_board_sha256':sha(board),'seed_directory':str(SEED.relative_to(ROOT)),'export_dsn_sha256':sha(dsn),'exchange_tool_sha256':sha(Path(__file__)),'rule_note':'Actual KiCad project rules unchanged. In1 reserved for GND, DOCK_5V width .6, 3V3 pullup branches .3, other .2 mm candidates. Locked .65mm radio feed remains. PACK_P only feeds high-impedance telemetry on flange; these widths do not qualify current, thermal, RF or impedance.'},indent=2)+'\n')
 print(json.dumps({'dsn':str(dsn),'sha256':sha(dsn)},indent=2),flush=True)
else:
 r=json.loads((P/'router-exchange.json').read_text());assert sha(board)==r['seed_board_sha256'];assert sha(dsn)==r['export_dsn_sha256']
 b=K.LoadBoard(str(board));before=R.route_records(b);assert all(t.IsLocked()for t in b.GetTracks())
 incoming=R.parse_ses(ses);frozen={sig(t)for t in before};duplicates=[t for t in incoming if sig(t)in frozen]
 # The Specctra output can include protected seed wires. Exclude exact
 # signatures only; changed/missing USB paths are a hard failure.
 usb=[t for t in incoming if t['net']in ['USB_DM','USB_DP']]
 assert all(sig(t)in frozen for t in usb),'Router altered protected USB'
 added=[t for t in incoming if sig(t)not in frozen]
 assert not any(t['net']in ['USB_DM','USB_DP']for t in added)
 R.apply_routes(b,added,locked=False);K.SaveBoard(str(board),b);saved=R.fill_save(board)
 current={sig(t)for t in R.route_records(saved)};assert frozen<=current
 r.update({'import_session_sha256':sha(ses),'session_records':len(incoming),'exact_seed_duplicates_skipped':len(duplicates),'added_records':len(added),'preserved_manual_records':len(before),'native_board_sha256':sha(board),'scope':'Partial manual plus local router exchange, not accepted until fresh native DRC and independent saved copper checks.'})
 (P/'router-exchange.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2),flush=True)
