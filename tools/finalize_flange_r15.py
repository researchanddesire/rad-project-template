"""Label R15Q routed flange clearly without changing electrical geometry."""
from pathlib import Path
import sys,shutil,json,re
import pcb_r2_route as R
K=R.k;ROOT=Path(__file__).resolve().parents[1];S=ROOT/'hardware/pcb/route-r15/candidate-q';P=Path(sys.argv[1]).resolve();P.mkdir(parents=True,exist_ok=True);assert not any(P.iterdir())
for f in S.rglob('*'):
 if f.is_file()and(f.suffix in ['.kicad_pcb','.kicad_pro','.kicad_sch','.kicad_sym','.kicad_mod']or f.name in ['fp-lib-table','sym-lib-table']):
  q=P/f.relative_to(S);q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,q)
  if f.suffix=='.kicad_sch':
   txt=q.read_text();txt=re.sub(r'\((title|rev) "([^"\n]*)"\)',lambda m:'('+m[1]+' "'+m[2].replace('R14','R15')+'")',txt)
   txt=txt.replace('"UNROUTED / REVIEW ONLY"','"REVIEW ONLY / BODY UNROUTED / FLANGE ROUTE R15"');q.write_text(txt)
bpath=P/'flange/flange-r15.kicad_pcb';b=K.LoadBoard(str(bpath));before=R.route_records(b)
for fp in b.GetFootprints():fp.SetProperty('PlacementStatus','R15 routed flange candidate / NOT FABRICATION')
K.SaveBoard(str(bpath),b);assert R.route_records(K.LoadBoard(str(bpath)))==before
(P/'final-labels.json').write_text(json.dumps({'source_Q_board_sha256':R.sha(S/'flange/flange-r15.kicad_pcb'),'native_board_sha256':R.sha(bpath),'tool_sha256':R.sha(Path(__file__)),'entire_saved_route_records_unchanged':True,'body_board_byte_identical_to_Q':R.sha(P/'body/body-r15.kicad_pcb')==R.sha(S/'body/body-r15.kicad_pcb'),'scope':'Clarify candidate labels and schematic title blocks only. No electrical connections, symbols, pad placements, copper, project rules or geometry changed. Fresh native DRC and XML bind final files.'},indent=2)+'\n')
print(P)
