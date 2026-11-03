"""Freeze conditional R26F evidence without changing geometry or the product BOM."""
from pathlib import Path
import json,hashlib,shutil
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'hardware/cad/tip-support-r26';P=BASE/'candidate-f';E=BASE/'candidate-e';DESIGN=ROOT/'hardware/design/tip-support-r26'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
r=read(P/'geometry-report.json');v=read(P/'saved-review.json');e=read(E/'geometry-report.json');plan=read(DESIGN/'wire-plan-c.json');curvature=read(DESIGN/'wire-plan-c-curvature.json')
nf=P/'StationaryTipR26.FCStd';native=sha(nf)
assert native==r['native_sha256']==v['native_sha256']
assert sha(P/'geometry-report.json')==v['geometry_report_sha256']
assert sha(E/'StationaryTipR26.FCStd')==r['source_R26_native_sha256']==v['source_R26E_native_sha256']
assert sha(E/'geometry-report.json')==r['source_R26_report_sha256']
assert len(r['parts'])==130 and len(r['mates'])==7 and len(r['allowances'])==2
assert r['static_pairs_tested']==6903 and r['new_wire_pairs_tested']==1482
for key in ['unexpected_intersections','nominal_mate_intersections','new_wire_unexpected_intersections','new_wire_nominal_mate_intersections','new_wire_conditional_flare_intersections']:assert not r[key]
assert len(r['named_unqualified_screw_pilot_interfaces'])==3
assert len(v['saved_roles'])==139 and len(v['source_R26E_conservation'])==118 and len(v['source_R25_conservation'])==109
assert not v['external_document_links']and v['all_new_listed_screens_clear']
for key,count in [('electronics_into_body_listed_poses',21),('motor_module_with_new_tray_listed_poses',12),('cap_to_final_tip_and_wires_listed_poses',20),('generic_solder_tools_at_plus7Y',4)]:
 assert len(v[key])==count and not any(q['hits']for q in v[key]),key
assert not v['tip_module_at_plus7Y_hits']
assert r['GUI_only_configuration']['all_geometry_archive_entries_unchanged']
assert sha(DESIGN/'wire-plan-c.json')==r['wire_plan_sha256']==e['wire_guide_plan_sha256']==v['wire_plan_sha256']==curvature['plan_sha256']
assert sha(DESIGN/'wire-plan-c-curvature.json')==v['curvature_report_sha256']
assert all(q['minimum_polynomial_radius_lower_bound_mm']>=2.5 and q['analytic_arc_radius_mm']==2.5 for q in curvature['rows'])
assert min(q['native_insulation_surface_distance_mm']for q in r['wire_pair_surface_gaps'])>=.084
assert all(q>0 for q in r['strain_relief_wire_overlap_mm3'].values())
for name,h in r['review_meshes_sha256'].items():assert sha(P/name)==h,name
source=ROOT/'hardware/cad/motor-shell-mount-r25/candidate-d';assert sha(source/'ShellMotorMountR25.FCStd')==r['source_R25_native_sha256']==v['source_R25_native_sha256']
assert sha(source/'geometry-report.json')==r['source_R25_report_sha256']
pcb=ROOT/'hardware/pcb/stackup-r23/candidate-d';tip=ROOT/'hardware/pcb/tip-r1'
assert sha(pcb/'layout-inspection.json')==plan['source_body_inspection_sha256']
assert sha(tip/'buttplug-tip-r1.kicad_pcb')==plan['source_native_tip_board_sha256']
assert sha(tip/'validation-tip-r1.json')==plan['source_tip_validation_sha256']
bom=ROOT/'hardware/bom.csv';assert sha(bom)=='d5424d0536840bd3b555c439a129c0271b19b1cfbb3b94f1e1709e57cd63f05c'
harness=read(DESIGN/'harness-review.json');hsource=ROOT/'hardware/cables/tip-r26/tip-sensor-r26.yml'
assert sha(hsource)==harness['source_sha256']and harness['WireViz_version']=='0.4.1'
for name,h in harness['generated_external_outputs_sha256'].items():assert sha(Path(name))==h
refs=read(DESIGN/'references-and-assumptions.json')
for key in ['thermal_adhesive','main_tip_mate']:assert sha(DESIGN/refs[key]['local_PDF'])==refs[key]['PDF_sha256']
asset=ROOT/'developer-docs/docs/assets/prototype-r2/tip-support-r26-f.png';render=read(asset.with_name(asset.stem+'-source.json'))
assert render['native_sha256']==native and render['geometry_report_sha256']==sha(P/'geometry-report.json')and render['saved_review_sha256']==sha(P/'saved-review.json')
bindings={'apply_tip_wires_r26.py':r['builder_sha256'],'tip_wire_native_r26.py':r['native_wire_library_sha256'],'configure_tip_r26_view.py':r['GUI_only_configuration']['script_sha256'],'review_tip_r26.py':v['reviewer_sha256'],'plan_tip_wires_r26.py':plan['planner_sha256'],'review_tip_wire_curvature_r26.py':curvature['reviewer_sha256'],'render_tip_r26.py':render['renderer_sha256'],'render_mechanical_r2.py':render['render_library_sha256']}
ex=P/'executed-tools';ex.mkdir(exist_ok=True)
for name,h in bindings.items():
 src=ROOT/'tools'/name;assert sha(src)==h,name;dest=ex/name
 if dest.exists():assert sha(dest)==h
 else:shutil.copyfile(src,dest)
for name,h in [('support_tip_r26.py',e['builder_sha256']),('tip_wire_native_r26.py',e['native_wire_library_sha256'])]:assert sha(E/'executed-tools'/name)==h
assert sha(DESIGN/'wire-plan-c-executed.py')==plan['planner_sha256']
for srcname,destname in [('tip-r26-f-review.log','review.log'),('tip-r26-f-render.log','render.log'),('buttplug-r26-docs-final.log','docs-build.log')]:
 src=Path('/private/tmp')/srcname;assert src.is_file();dest=P/destname
 if dest.exists():assert dest.read_bytes()==src.read_bytes()
 else:shutil.copyfile(src,dest)
log=(P/'docs-build.log').read_text();assert 'Documentation built in'in log and 'WARNING -'not in log
fcopy=ex/Path(__file__).name
if fcopy.exists()and sha(fcopy)!=sha(Path(__file__)):
 # An interrupted pre-index freeze may update its own snapshot only. Never
 # rewrite a previously indexed script or any geometry/history evidence.
 assert not(BASE/'artifact-index.json').exists()
 shutil.copyfile(Path(__file__),fcopy)
elif not fcopy.exists():shutil.copyfile(Path(__file__),fcopy)
external=[ROOT/'developer-docs/docs/tip-support-r26.md',ROOT/'assembly-docs/tip-support-r26.md',asset,asset.with_name(asset.stem+'-source.json'),source/'ShellMotorMountR25.FCStd',source/'geometry-report.json',source/'saved-review.json',source.parent/'artifact-index.json',ROOT/'hardware/design/motor-shell-mount-r25/r23d-pcb-envelopes.json',pcb/'layout-inspection.json',tip/'buttplug-tip-r1.kicad_pcb',tip/'validation-tip-r1.json',bom]
external+=[p for folder in [DESIGN,ROOT/'hardware/cables/tip-r26']for p in folder.rglob('*')if p.is_file()and '__pycache__'not in p.parts]
included=[];omitted=[]
for p in sorted(BASE.rglob('*')):
 if not p.is_file()or p.name=='artifact-index.json'or '__pycache__'in p.parts or p.suffix=='.lck'or p.name.startswith('~'):continue
 # Current F meshes were checked above. Earlier native/reports/tools/logs
 # remain indexed; no need to hydrate hundreds of unused historical meshes.
 if p.suffix=='.stl'and p.parent!=P:omitted.append(str(p.relative_to(BASE)))
 else:included.append(p)
files={str(p.relative_to(BASE)):sha(p)for p in included}
out={'date':'2026-11-01','current':'R26F conditional stationary tip and individual wires on support seed E; complete functional build proposal unfinished','native_sha256':native,'freezer_sha256':sha(Path(__file__)),'files_sha256':files,'preserved_historical_meshes_not_rehashed':omitted,'external_bindings_sha256':{str(p.relative_to(ROOT)):sha(p)for p in external},'scope':'Saved native/source conservation and stored wire paths; nominal static pair and explicitly staged finite rigid/tool screens. Current F meshes and historical native/reports/tools/logs bound; unused historical mesh files preserved but not rehashed. Free wire ends during motor loading, no connected-harness motion proof. Fitted clip envelope and candidate adhesive/gel/screw/wire/connector processes, not actual parts, installation/cure/thermal/electrical/load/seal or physical acceptance. Prior failed and follow-up candidates remain preserved. BatteryOPEN/humanBOMunchanged; no build/order release.'}
(BASE/'artifact-index.json').write_text(json.dumps(out,indent=2)+'\n')
assert all(sha(BASE/n)==h for n,h in files.items())
print(len(files),'R26 files;',len(out['external_bindings_sha256']),'external bindings; current native/PCB/wire/harness/BOM verified',flush=True)
