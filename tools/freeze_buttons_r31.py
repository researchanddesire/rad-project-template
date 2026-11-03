"""Freeze the checked R31 prototype control checkpoint and its limits."""
from pathlib import Path
import json,hashlib,shutil,zipfile,datetime
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'hardware/cad/buttons-r31';D=P/'candidate-d';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
r=read(D/'geometry-report.json');v=read(D/'saved-review.json');s=read(D/'assembly-screen.json');access=read(D/'calibration-access-review.json');g=read(P/'wire-review-d/plan-review.json');plan=read(P/'wire-review-d/wire-plan.json');lands=read(P/'board-land-review.json');ui=read(D/'ButtonsR31-review.json')
assert sha(D/'ButtonsR31.FCStd')==r['native_sha256']==v['native_sha256']==s['native_sha256']==access['native_sha256']==ui['source_native_sha256']
assert sha(D/'geometry-report.json')==v['geometry_report_sha256']==access['geometry_report_sha256']and sha(D/'saved-review.json')==s['saved_review_sha256']==access['saved_review_sha256']
assert len(v['saved_roles'])==163 and len(v['source_roles_conserved'])==139 and not v['external_document_links']and not v['unexpected_intersections']and not r['unexpected_intersections']and v['forced_new_pairs_tested']==3612
assert s['all_listed_screens_clear']and len(s['rigid_press_study'])==14 and [len(q)for q in s['assembly_stages'].values()]==[8,8,9,11]
assert access['all_listed_shafts_clear_to_stop_face']and len(access['full_face_access_probes'])==6
assert sha(P/'wire-review-d/wire-plan.json')==r['updated_wire_plan_sha256']==v['wire_plan_sha256']==g['reviewed_plan_sha256']and g['all_curves_R_at_least_4mm_and_separated']and len(v['stored_wire_curves'])==10
assert lands['all_contact_projections_clear']and lands['contact_projection_count']==14 and not lands['unexpected_intersections']and sha(P/'native-board-geometry.json')==lands['extracted_geometry_sha256']
assert sha(ROOT/'hardware/pcb/flange-access-r28/candidate-s/flange/flange-r28.kicad_pcb')==lands['board_sha256']=='521bbffad5ad2ea960973a6650904ff64e906639b86408db8227b640d531e542'
assert sha(ROOT/'hardware/pcb/flange-access-r28/candidate-s/body/body-r28.kicad_pcb')=='19f0c9b20d4b6e6c43636076531297af3eab12effb196b8ce46c807de477491b'
assert sha(ROOT/'hardware/cad/harness-support-r30/candidate-b/HarnessSupportR30.FCStd')==r['source_R30_native_sha256']==v['source_R30_native_sha256']
sourceplan=read(ROOT/'hardware/cad/interboard-r29/review-e/wire-plan.json')
for a,b in zip(sourceplan['wires'],plan['wires']):
 assert all(a[k]==b[k]for k in ['pin','net','start_xyz_mm','end_xyz_mm'])and a['curves'][:2]==b['curves'][:2]
for q in r['button_spec']:assert q['approved_overtravel_mm']is None and q['study_stop_stroke_mm']==.58
assert read(P/'interface-requirements.json')['switch']['allowable_overtravel_mm']is None
assert sha(ROOT/'hardware/bom.csv')=='d5424d0536840bd3b555c439a129c0271b19b1cfbb3b94f1e1709e57cd63f05c'
assert sha(D/'ButtonsR31-review.FCStd')==ui['review_copy_sha256']and ui['all_non_GUI_archive_members_unchanged']
with zipfile.ZipFile(D/'ButtonsR31.FCStd')as a,zipfile.ZipFile(D/'ButtonsR31-review.FCStd')as b:
 for n,h in ui['geometry_archive_entries_sha256'].items():assert hashlib.sha256(a.read(n)).hexdigest()==hashlib.sha256(b.read(n)).hexdigest()==h
for folder in ['candidate-a','candidate-b','candidate-c','candidate-d']:
 row=read(P/folder/'geometry-report.json');assert sha(P/folder/'executed-tools/buttons_r31.py')==row['builder_sha256']
for name,record,key in [('review_buttons_r31.py',v,'reviewer_sha256'),('review_button_access_r31.py',access,'reviewer_sha256'),('button_board_review_r31.py',lands,'reviewer_sha256'),('button_board_extract_r31.py',read(P/'native-board-geometry.json'),'extractor_sha256'),('configure_buttons_r31_view.py',ui,'configurator_sha256')]:assert sha(D/'executed-tools'/name)==record[key]
assert len(read(P/'candidate-a/geometry-report.json')['unexpected_intersections'])==33
assert len(read(P/'candidate-b/geometry-report.json')['unexpected_intersections'])==1
assert not read(P/'candidate-c/assembly-screen.json')['all_listed_screens_clear']
for name,h in dict(v['meshes_sha256'],**v['section_meshes_sha256']).items():assert sha(D/name)==h
figure=read(ROOT/'developer-docs/docs/assets/prototype-r2/buttons-r31-d-source.json');assert figure['native_sha256']==r['native_sha256']and figure['saved_review_sha256']==sha(D/'saved-review.json')and figure['assembly_screen_sha256']==sha(D/'assembly-screen.json')
assert sha(D/'executed-tools/render_buttons_r31.py')==figure['renderer_sha256']
for name,h in figure['native_meshes_sha256'].items():assert sha(D/name)==h
for ref in P.glob('references/*.pdf'):assert ref.read_bytes().startswith(b'%PDF')
status={'current_candidate':'candidate-d','native_sha256':r['native_sha256'],'geometry_ready_for_review':True,'full_prototype_proposal_ready':False,'scope':'Editable prototype control mechanism on current upright flange board; no widened exterior or motor-to-PCB support. Calibration and first-build commissioning remain unperformed.','counts':{'saved_roles':163,'conserved_source_roles':139,'new_or_changed_role_comparisons':3612,'rigid_press_poses':14,'rear_module_poses':8,'keeper_poses':8,'parked_left_hub_poses':9,'populated_board_poses':11,'full_calibration_access_shafts':6,'PCB_contact_projections':14},'wire_guard_minimum_surface_separation_lower_mm':min(q['guarded_continuous_surface_gap_lower_mm']for q in g['pair_gaps']),'PCB_land_minimum_conductor_gap_mm':min(q['minimum_conductor_paste_gap_mm']for q in lands['rows']),'button_stop_study_mm':.58,'approved_switch_overtravel_mm':None,'remaining_proposal_work':['Remaining harnesses and their restraint/loading','Pack and NTC retention with battery choice OPEN','Flange attachment/removal loads and compliance','Seal/material/process interfaces','Consolidated complete prototype build/test package'],'first_build_control_work':['Controlled switch data or sacrificial switch/boot characterization','Matched-board registration and deflection','Per-unit stop and make/release calibration','Inspected/custom stop socket-end annulus and actual threads/drives','Home-pin retention and stop locking/drift','Silicone return, perimeter/diaphragm leakage and cleaning'],'purchases_or_physical_build':False}
(P/'review-status.json').write_text(json.dumps(status,indent=2)+'\n');shutil.copyfile(Path(__file__),D/'executed-tools/freeze_buttons_r31.py')
external=['hardware/bom.csv','hardware/cad/harness-support-r30/artifact-index.json','hardware/cad/harness-support-r30/candidate-b/HarnessSupportR30.FCStd','hardware/cad/harness-support-r30/candidate-b/geometry-report.json','hardware/cad/harness-support-r30/candidate-b/saved-review.json','hardware/cad/harness-support-r30/parked-d/ParkedHarnessR30.FCStd','hardware/cad/harness-support-r30/parked-d/parking-review.json','hardware/cad/interboard-r29/review-e/wire-plan.json','hardware/cad/flange-controls-r27/candidate-d/geometry-report.json','hardware/pcb/flange-access-r28/artifact-index.json','hardware/pcb/flange-access-r28/candidate-s/system-native.xml','hardware/pcb/flange-access-r28/candidate-s/body/body-r28.kicad_pcb','hardware/pcb/flange-access-r28/candidate-s/flange/flange-r28.kicad_pcb','hardware/cables/interboard-r29/interboard-r29.yml','hardware/cables/interboard-r29/logical-review.json','hardware/design/local-controls-interface-r2.json','hardware/design/local-controls-operating-screen-r1.json','developer-docs/docs/buttons-r31.md','assembly-docs/buttons-r31.md','developer-docs/docs/assets/prototype-r2/buttons-r31-d.png','developer-docs/docs/assets/prototype-r2/buttons-r31-d-source.json','tools/render_mechanical_r2.py']
files={str(f.relative_to(P)):sha(f)for f in sorted(P.rglob('*'))if f.is_file()and f!=P/'artifact-index.json'and f.suffix not in ['.pyc','.lck']and f.name!='.DS_Store'and '__pycache__'not in f.parts}
index={'frozen_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'current':'candidate-d','freezer_sha256':sha(Path(__file__)),'files_sha256':files,'external_bindings_sha256':{n:sha(ROOT/n)for n in external},'state':'Prototype control geometry and finite assembly checkpoint, not complete product build proposal or physical acceptance','scope':status['scope']};(P/'artifact-index.json').write_text(json.dumps(index,indent=2)+'\n')
for n,h in index['files_sha256'].items():assert sha(P/n)==h,n
for n,h in index['external_bindings_sha256'].items():assert sha(ROOT/n)==h,n
print('R31 frozen',len(files),'files /',len(external),'bindings;163roles/3612comparisons and listed stages pass. Full proposal remains unfinished.',flush=True)
