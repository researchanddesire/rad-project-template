"""Apply source-bound local signal escapes, before planning ground stitches."""
from pathlib import Path
import sys,json
import pcb_r2_route as R
K=R.k;R.LAYERS['In1.Cu']=K.In1_Cu;ROOT=Path(__file__).resolve().parents[1]
source=Path(sys.argv[1]).resolve();planpath=Path(sys.argv[2]).resolve();P=Path(sys.argv[3]).resolve()
plan=json.loads(planpath.read_text());bp=next((source/'body').glob('body-r*.kicad_pcb'));board_name=bp.name
assert R.sha(bp)==plan['source_board_sha256']
assert R.sha(source/'body-native-geometry-all-layers.json')==plan['source_geometry_sha256']
assert all(t['status']=='planned'for t in plan['targets'])or'--allow-partial'in sys.argv[4:]
P.mkdir(parents=True,exist_ok=True);assert not any(P.iterdir())
records=['unused-copper-r23.json','stackup-r23.json','global-release-r19.json','local-ground-rework-r19.json','fp-lib-table','sym-lib-table','body-seed.json','local-power.json','power-refinement.json','local-interfaces.json','compact-driver.json','signal-first-seed.json','ground-rework.json','fresh-fill.json','ground-plan.json','ground-application.json','ground-rework.json','fresh-fill.json','local-seed-final.json','dock-port-rework.json','signal-repack.json','router-exchange.json','remaining-plan.json','remaining-application.json','board-width.json','via-process.json','local-seed-conservation.json']
for p in source.rglob('*'):
 if p.is_file()and(p.suffix in ['.kicad_pro','.kicad_sch','.kicad_sym','.kicad_mod','.kicad_pcb']or p.name in records):
  q=P/p.relative_to(source);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
bp=P/'body'/board_name;b=K.LoadBoard(str(bp));parent_records=R.route_records(b);R.apply_routes(b,plan['routes']);K.SaveBoard(str(bp),b);saved=R.fill_save(bp)
from collections import Counter
canon=lambda t:json.dumps(t,sort_keys=True)
assert not Counter(map(canon,parent_records))-Counter(map(canon,R.route_records(saved)))
(P/'signal-ports.json').write_bytes(planpath.read_bytes())
R.write(P/'signal-application.json',{'builder_sha256':R.sha(Path(__file__)),'source_directory':str(source.relative_to(ROOT)),'source_body_sha256':plan['source_board_sha256'],'plan_sha256':R.sha(planpath),'native_body_sha256':R.sha(bp),'target_count':len(plan['targets']),'planned_targets':sum(t['status']=='planned'for t in plan['targets']),'unplanned_targets':[t for t in plan['targets']if t['status']!='planned'],'new_records':len(plan['routes']),'all_parent_copper_records_preserved':len(parent_records),'scope':'Locked local signal escapes added; no poses or circuit changes. Partial planning remains explicit when requested. Source parent preserves earlier plans. Fresh native DRC required.'})
print(P,flush=True)
