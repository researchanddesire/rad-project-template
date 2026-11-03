"""Integrity record for R37's scoped checkpoint, not full build readiness."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'hardware/cad/pack-assembly-r37';C=ROOT/'hardware/cables/pack-adapter-r37';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
b=json.loads((P/'body-anchor-b/geometry-report.json').read_text());f=json.loads((P/'power-f/geometry-report.json').read_text());v=json.loads((P/'saved-review.json').read_text());c=json.loads((C/'logical-review.json').read_text())
assert sha(P/'body-anchor-b/PackBodyAnchorR37.FCStd')==b['native_sha256']==f['source_body_anchor_B_sha256']==v['body_anchor_B_sha256']
assert sha(P/'power-f/ConditionalPackPowerR37.FCStd')==f['native_sha256']==v['power_F_sha256']
assert b['all_static_screens_clear']and f['all_static_screens_clear']and f['all_named_retention_regions_conserved']and v['all_saved_checks_pass']
assert sha(C/'pack-adapter-r37.yml')==c['recipe_sha256']and c['separate_external_power_and_sensor_returns']
assert sha(P/'power-f/geometry-report.json')==c['geometry_report_sha256']
for folder,r,tool in [('body-anchor-b',b,'retain_pack_body_wires_r37.py'),('power-f',f,'build_pack_power_r37.py')]:
 assert sha(P/folder/'executed-tools'/tool)==r['builder_sha256']
assert sha(P/'executed-tools/review_pack_assembly_r37.py')==v['reviewer_sha256']
assert sha(ROOT/'hardware/bom.csv')=='d5424d0536840bd3b555c439a129c0271b19b1cfbb3b94f1e1709e57cd63f05c'
files={}
for folder in [P/'body-anchor-b',P/'power-f',P/'display',P/'executed-tools',C,ROOT/'hardware/design/pack-power-r37/references']:
 for p in sorted(folder.rglob('*')):
  if p.is_file()and p.name!='.DS_Store'and p.suffix not in ['.pyc','.FCStd1']:files[str(p.relative_to(ROOT))]=sha(p)
for name in ['README.md','saved-review.json','saved-review.log']:files[str((P/name).relative_to(ROOT))]=sha(P/name)
bindings=['hardware/cad/pack-sensor-r36/access-i/ServiceablePackSensorsR36.FCStd','hardware/cad/pack-sensor-r36/access-i/access-review.json','hardware/design/pack-sensor-r36/current-review.json','hardware/pcb/pack-pigtail-r35/candidate-f/system-native.xml','hardware/pcb/pack-pigtail-r35/candidate-f/body/body-r35.kicad_pcb','hardware/cad/pack-assembly-r37/power-screen-d/placement-screen.json','developer-docs/docs/pack-assembly-r37.md','assembly-docs/pack-assembly-r37.md','developer-docs/docs/assets/prototype-r2/pack-assembly-r37-f.png','developer-docs/docs/assets/prototype-r2/pack-assembly-r37-f-source.json','tools/review_pack_adapter_net_r37.py','hardware/bom.csv']
out={'indexed_at_utc':datetime.now(timezone.utc).isoformat(),'indexer_sha256':sha(Path(__file__)),'files_sha256':files,'external_bindings_sha256':{n:sha(ROOT/n)for n in bindings},'current':{'body_anchor':'R37 B','integrated_conditional_power':'R37 F','electrical_partner':'R35 F','sensor_source':'R36 H / access I','battery_selection':'OPEN'},'checks':{'anchor_source_roles_conserved':v['anchor_source_conservation']['count'],'power_source_roles_conserved':v['power_source_conservation']['count'],'native_anchor_wire_sections':len(v['five_wire_anchor_contacts']),'conditional_power_static_pairs':v['saved_power_static_pairs'],'distinct_power_laps':len(v['power_core_checks']),'recipe_matches_native_nets':True,'source_capture_and_bolt_end_seats_conserved':True},'prototype_build_consideration_ready':False,'remaining_design':['Positive retention of mated power connector, two power laps, four sensor laps and return junction','Loose-end body/hub loading followed by flange forming/termination, tie access, connected cover/service sequence','Actual pack/mate receiving inputs, solder/insulation/attachment process and tolerances','Motor/dock harnesses, flange load/compliance and seals','Consolidated source/exports, fabrication review and practical first-build/commissioning package'],'scope':'Integrity of the nominal body anchor and conditional power route only. Midweb material losses remain explicit, not structural acceptance. Actual pack/connector geometry and lead/shrink/bend inputs conditional. No physical clamp/load/current/thermal/seal/RF/wear acceptance. No purchase, BOM adoption, commit or energized work.'}
target=ROOT/'hardware/design/pack-assembly-r37/current-review.json';target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(out,indent=2)+'\n');print('Indexed R37',len(files),'files and',len(bindings),'external bindings; full proposal remains unfinished.',flush=True)
