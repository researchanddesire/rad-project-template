"""Keep original difficult MCU escapes while reopening the header-side trunks."""
from pathlib import Path
import sys,json,shutil
import pcb_r2_route as R
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'hardware/pcb/flange-access-r28/candidate-d';OUT=Path(sys.argv[1]).resolve();OUT.mkdir(parents=True,exist_ok=True);assert not any(OUT.iterdir())
for name in ['flange-r28.kicad_pcb','flange-r28.kicad_pro','fp-lib-table','routing-seed.json']:
 if(SRC/name).is_file():shutil.copyfile(SRC/name,OUT/name)
r=json.loads((SRC/'routing-seed.json').read_text());new=[q['record']for q in r['removed_routes']if q['record']['net']in ['DOCK_PRESENT_N','STRAP8']and(q['record']['kind']=='via'or q['record'].get('layer')=='F.Cu')];assert len(new)==9
bp=OUT/'flange-r28.kicad_pcb';before=R.sha(bp);b=R.k.LoadBoard(str(bp));R.apply_routes(b,new,locked=True);R.k.SaveBoard(str(bp),b);R.fill_save(bp)
R.write(OUT/'reserved-ports.json',{'source_D_board_sha256':before,'native_board_sha256':R.sha(bp),'builder_sha256':R.sha(Path(__file__)),'restored_original_MCU_escape_records':new,'scope':'Restore nine original F/through-via records for hard-access DOCK_PRESENT_N/STRAP8. Their old B routes to moved pads remain removed. Native rules/poses/USB/radio remain; route completion and actual native review required.'});print('reserved9 native escape records',flush=True)
