"""Freeze the reviewed R29 wire checkpoint and its source bindings."""
from pathlib import Path
import json,hashlib,shutil
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'hardware/cad/interboard-r29';C=ROOT/'hardware/cables/interboard-r29';E=P/'candidate-e';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
r=read(E/'geometry-report.json');v=read(E/'saved-review.json');p=read(P/'review-e/wire-plan.json');q=read(P/'review-e/plan-review.json');logical=read(C/'logical-review.json');binding=read(C/'native-route-binding.json')
assert sha(E/'InterboardR29.FCStd')==r['native_sha256']==v['native_sha256']
assert sha(E/'geometry-report.json')==v['geometry_report_sha256']and sha(P/'review-e/wire-plan.json')==r['plan_sha256']==v['plan_sha256']==q['reviewed_plan_sha256']==binding['complete_plan_sha256']
assert len(v['saved_roles'])==151 and len(v['source_R27_roles_conserved'])==141 and not v['unexpected_intersections']and not v['external_document_links']and v['forced_new_pairs_tested']==1455
assert q['all_curves_R_at_least_4mm_and_separated']and min(x['guarded_continuous_surface_gap_lower_mm']for x in q['pair_gaps'])>0
assert len(logical['all_10_numbered_nets_equal'])==10 and sha(C/'logical-review.json')==binding['logical_review_sha256']and sha(C/'interboard-r29.yml')==logical['recipe_sha256']
assert sha(ROOT/'hardware/bom.csv')==logical['human_BOM_sha256']=='d5424d0536840bd3b555c439a129c0271b19b1cfbb3b94f1e1709e57cd63f05c'
for filename,key in [('apply_interboard_r29.py','builder_sha256'),('review_interboard_native_r29.py','reviewer_sha256')]:
 record=r if key=='builder_sha256'else v
 assert sha(E/'executed-tools'/filename)==record[key]
for name,digest in v['wire_review_meshes_sha256'].items():assert sha(E/name)==digest
assert sha(ROOT/'tools/review_wire_plan_r29.py')==q['reviewer_sha256']
shutil.copyfile(Path(__file__),E/'executed-tools/freeze_interboard_r29.py')
external=[
 'hardware/cad/flange-controls-r27/artifact-index.json','hardware/cad/flange-controls-r27/candidate-d/FlangeCradleR27.FCStd','hardware/cad/flange-controls-r27/candidate-d/geometry-report.json','hardware/cad/flange-controls-r27/candidate-d/saved-review.json',
 'hardware/pcb/flange-access-r28/artifact-index.json','hardware/pcb/flange-access-r28/candidate-s/system-native.xml','hardware/pcb/flange-access-r28/candidate-s/layout-inspection.json','hardware/pcb/flange-access-r28/candidate-s/saved-circuit-review.json','hardware/pcb/flange-access-r28/candidate-s/body/body-r28.kicad_pcb','hardware/pcb/flange-access-r28/candidate-s/flange/flange-r28.kicad_pcb',
 'hardware/bom.csv','developer-docs/docs/interboard-routing-r29.md','assembly-docs/interboard-r29.md','developer-docs/docs/assets/prototype-r2/interboard-r29-e.png','developer-docs/docs/assets/prototype-r2/interboard-r29-e-source.json']
figure=read(ROOT/'developer-docs/docs/assets/prototype-r2/interboard-r29-e-source.json')
assert figure['native_sha256']==r['native_sha256']and figure['saved_review_sha256']==sha(E/'saved-review.json')
for name,digest in figure['source_meshes_sha256'].items():
 f=ROOT/'hardware/cad/flange-controls-r27/candidate-d'/name;assert sha(f)==digest;external.append(str(f.relative_to(ROOT)))
for f in C.rglob('*'):
 if f.is_file()and f.suffix not in ['.pyc']and '__pycache__'not in f.parts:external.append(str(f.relative_to(ROOT)))
files={str(f.relative_to(P)):sha(f)for f in sorted(P.rglob('*'))if f.is_file()and f!=P/'artifact-index.json'and f.suffix not in ['.pyc','.lck']and f.name!='.DS_Store'and '__pycache__'not in f.parts}
result={'date':'2026-11-01','state':'R29E installed interboard route checkpoint; supports/strain relief and connected movement unfinished, complete prototype proposal not ready','current':'candidate-e','complete_plan':'review-e/wire-plan.json','freezer_sha256':sha(Path(__file__)),'files_sha256':files,'external_bindings_sha256':{name:sha(ROOT/name)for name in sorted(set(external))},'native_sha256':r['native_sha256'],'fresh_saved_roles':151,'source_R27_roles_conserved':141,'new_wire_comparisons':1455,'unexpected_intersections':[],'native_minimum_wire_surface_gap_mm':min(x['native_surface_distance_mm']for x in v['native_wire_surface_gaps']),'guarded_minimum_continuous_separation_mm':min(x['guarded_continuous_surface_gap_lower_mm']for x in q['pair_gaps']),'history':'A native wire crossings; B/C incomplete loop-only trials; D concentric-turn seed; E complete reviewed path. No prior failure is substituted for current checks.','scope':'Guarded floating curvature/separation plus exact stored curves, saved source conservation and native static checks. Assumed wire OD/mated exits, unrestrained route. No actual housing/crimp, assembly/service motion, dynamic-flex/current/RF/physical qualification, procurement or human BOM edit. Battery OPEN.'}
(P/'artifact-index.json').write_text(json.dumps(result,indent=2)+'\n')
for name,digest in result['files_sha256'].items():assert sha(P/name)==digest,name
for name,digest in result['external_bindings_sha256'].items():assert sha(ROOT/name)==digest,name
print('R29E frozen:',len(files),'files /',len(result['external_bindings_sha256']),'external bindings;151roles/1455comparisons/0hits.')
