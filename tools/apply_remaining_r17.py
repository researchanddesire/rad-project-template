"""Apply a geometry plan to a separate R17 native candidate; retain parent."""
from pathlib import Path
import sys,json
import pcb_r2_route as R
R.LAYERS['In1.Cu']=R.k.In1_Cu
ROOT=Path(__file__).resolve().parents[1];source=Path(sys.argv[1]).resolve();planpath=Path(sys.argv[2]).resolve();P=Path(sys.argv[3]).resolve();plan=json.loads(planpath.read_text());bp=next((source/'body').glob('body-r*.kicad_pcb'));board_name=bp.name
assert R.sha(bp)==plan['source_board_sha256'];assert R.sha(source/'body-native-geometry-all-layers.json')==plan['source_geometry_sha256'];assert R.sha(source/'body/fresh-native-drc.txt')==plan['source_native_DRC_sha256']
P.mkdir(parents=True,exist_ok=True);assert not any(P.iterdir())
records=['unused-copper-r23.json','stackup-r23.json','global-release-r19.json','local-ground-rework-r19.json','fp-lib-table','sym-lib-table','body-seed.json','local-power.json','power-refinement.json','local-interfaces.json','compact-driver.json','signal-first-seed.json','signal-ports.json','signal-application.json','ground-plan.json','ground-application.json','router-exchange.json','ground-rework.json','fresh-fill.json','local-seed-final.json','dock-port-rework.json','signal-repack.json','local-seed-conservation.json','board-width.json','via-process.json']
for p in source.rglob('*'):
 if p.is_file()and(p.suffix in ['.kicad_pro','.kicad_sch','.kicad_sym','.kicad_mod','.kicad_pcb']or p.name in records):
  q=P/p.relative_to(source);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
bp=P/'body'/board_name
if not(P/'body/source-seed.kicad_pcb').exists():(P/'body/source-seed.kicad_pcb').write_bytes(bp.read_bytes())
b=R.k.LoadBoard(str(bp));active={b.GetLayerName(i):i for i in range(32)if b.GetEnabledLayers().Contains(i)};R.LAYERS.update(active);reserved=json.loads((P/'stackup-r23.json').read_text())['reserved_ground_layers']if(P/'stackup-r23.json').exists()else['In2.Cu'];assert all(t['kind']=='via'or t['layer']in active and(t['layer']not in reserved or t['net']=='GND')for t in plan['routes']);parent_records=R.route_records(b);R.apply_routes(b,plan['routes'],locked=False);R.k.SaveBoard(str(bp),b);saved=R.fill_save(bp)
from collections import Counter
canon=lambda t:json.dumps(t,sort_keys=True)
assert not Counter(map(canon,parent_records))-Counter(map(canon,R.route_records(saved)))
(P/'remaining-plan.json').write_bytes(planpath.read_bytes())
R.write(P/'remaining-application.json',{'builder_sha256':R.sha(Path(__file__)),'source_directory':str(source.relative_to(ROOT)),'source_board_sha256':plan['source_board_sha256'],'plan_sha256':R.sha(planpath),'native_board_sha256':R.sha(bp),'new_records':len(plan['routes']),'new_global_routes_locked':False,'all_parent_copper_records_preserved':len(parent_records),'scope':'Separate native candidate with conservative geometry-planned remaining tracks. Parent unchanged. Fresh DRC/drill/pad/reference checks required; unfinished paths remain explicit.'});print(P,flush=True)
