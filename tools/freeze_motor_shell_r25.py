"""Freeze scoped R25D review evidence, retaining failed antecedents/exports."""
from pathlib import Path
import json,hashlib,shutil,math
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'hardware/cad/motor-shell-mount-r25';P=BASE/'candidate-d'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
r=read(P/'geometry-report.json');v=read(P/'saved-review.json');a=read(P/'adaptive-volume-diagnostic.json')
nf=P/'ShellMotorMountR25.FCStd';native=sha(nf)
assert native==r['native_sha256']==v['native_sha256']==a['native_sha256']
assert sha(P/'geometry-report.json')==v['geometry_report_sha256']
assert len(r['parts'])==113 and r['static_pairs_tested']==6328
assert not r['unexpected_intersections']and not r['nominal_mate_intersections']and not r['conditional_flare_intersections']
assert len(r['named_unqualified_screw_pilot_interfaces'])==2
assert len(v['saved_roles'])==121 and not v['external_document_links']
assert all(x>=.5 for x in v['motor_mount_clearances_mm'].values())
assert abs(r['parts']['MotorSeatCapR25']['bounds_xyz_mm'][4]-98.1)<1e-5
assert r['GUI_only_configuration']['all_geometry_archive_entries_unchanged']
for key,count in [('motor_module_listed_loading_poses',12),('cap_to_motor_tip_listed_poses',36),('motor_into_clamp_listed_poses',12),('board_drop_listed_poses',8),('PCB_keeper_drop_listed_poses',8)]:
 assert len(r[key])==count and not any(row['hits']for row in r[key]),key
source=ROOT/'hardware/cad/motor-retention-r21/candidate-c/MotorRetentionR21.FCStd'
assert sha(source)==r['source_native_sha256']==v['source_native_sha256']==a['source_native_sha256']
assert a['runtime']['OCCT']=='7.8.1'and a['runtime']['PythonOCC'].startswith('7.8.1')
assert a['mass_diagnostic_screen']['all_row_convergence_below_0_0001_mm3']and a['mass_diagnostic_screen']['all_partition_residuals_below_0_001_mm3']
assert all(a['mass_diagnostic_screen']['STEP_adaptive_mass_below_0_001_mm3'].values())
for row in a['rows'].values():
 assert all(math.isfinite(t['volume_mm3'])and math.isfinite(t['estimated_relative_error'])and t['estimated_relative_error']>=0 for t in row['adaptive'])
export=read(P/'step-review-r1/export-review.json');controls=read(P/'step-review-r1/comparison-controls.json')
assert export['native_sha256']==native
assert not export['parts']['KeyedBodyR25']['numeric_screen_pass']and not export['parts']['MotorSeatCapR25']['numeric_screen_pass']
assert not controls['rows']['MotorSeatCapR25']['comparison_boolean_volume_bound_valid']
for name,row in export['parts'].items():assert sha(P/'step-review-r1'/(name+'.step'))==row['STEP_sha256']
for name,h in dict(r['review_meshes_sha256'],**v['side_section_meshes_sha256']).items():assert sha(P/name)==h,name
binder=ROOT/'hardware/design/motor-shell-mount-r25/r23d-pcb-envelopes.json';b=read(binder)
assert b['native_CAD_sha256']==native and b['saved_review_sha256']==sha(P/'saved-review.json')
assert len(b['actual_Fab_height_boxes'])==88 and sum(x['parts']for x in b['boards'].values())==89
pcb=ROOT/'hardware/pcb/stackup-r23/candidate-d'
assert b['PCB_inspection_sha256']==sha(pcb/'layout-inspection.json')
for domain,row in b['boards'].items():assert row['native_board_sha256']==sha(pcb/domain/(domain+'-r23.kicad_pcb'))
bom=ROOT/'hardware/bom.csv';assert sha(bom)=='d5424d0536840bd3b555c439a129c0271b19b1cfbb3b94f1e1709e57cd63f05c'
bindings={'mount_motor_to_shell_r25.py':r['builder_sha256'],'configure_shell_motor_r25_view.py':r['GUI_only_configuration']['script_sha256'],'review_shell_motor_r25.py':v['reviewer_sha256'],'export_shell_motor_r25.py':export['exporter_sha256'],'review_motor_mass_r25.py':a['reviewer_sha256'],'bind_pcb_shell_motor_r25.py':b['comparator_sha256']}
asset=ROOT/'developer-docs/docs/assets/prototype-r2/motor-shell-r25-d.png';render=read(asset.with_name(asset.stem+'-source.json'))
assert render['native_sha256']==native and render['geometry_report_sha256']==sha(P/'geometry-report.json')and render['saved_review_sha256']==sha(P/'saved-review.json')
bindings.update({'render_shell_motor_r25.py':render['renderer_sha256'],'render_mechanical_r2.py':render['render_library_sha256']})
ex=P/'executed-tools';ex.mkdir(exist_ok=True)
for name,h in bindings.items():
 src=ROOT/'tools'/name;assert sha(src)==h,name
 dest=ex/name
 if dest.exists():assert sha(dest)==h
 else:shutil.copyfile(src,dest)
for srcname,destname in [('motor-r25-d.log','build.log'),('motor-r25-d-review.log','review.log'),('motor-r25-d-step.log','step-export.log'),('motor-r25-d-mass.log','adaptive-mass.log'),('motor-r25-d-pcb-binding.log','pcb-binding.log'),('motor-r25-d-render.log','render.log'),('buttplug-r25-docs-final.log','docs-build.log')]:
 src=Path('/private/tmp')/srcname
 assert src.is_file(),src
 dest=P/destname
 if dest.exists():assert dest.read_bytes()==src.read_bytes()
 else:shutil.copyfile(src,dest)
external=[ROOT/'developer-docs/docs/motor-shell-mount-r25.md',ROOT/'assembly-docs/motor-shell-mount-r25.md',asset,asset.with_name(asset.stem+'-source.json'),source,bom,binder,pcb/'layout-inspection.json',pcb/'circuit-conservation.json']
external+=list((ROOT/'hardware/design/motor-shell-mount-r25').rglob('*'))
external=[p for p in external if p.is_file()]
self_source=Path(__file__);self_copy=ex/self_source.name
if self_copy.exists():assert sha(self_copy)==sha(self_source)
else:shutil.copyfile(self_source,self_copy)
files={str(p.relative_to(BASE)):sha(p)for p in sorted(BASE.rglob('*'))if p.is_file()and p.name!='artifact-index.json'and '__pycache__'not in p.parts and p.suffix not in ['.lck']and not p.name.startswith('~')}
out={'date':'2026-11-01','current':'R25D conditional independent shell motor mount; separate PCB support; no complete build release','freezer_sha256':sha(Path(__file__)),'native_sha256':native,'files_sha256':files,'external_bindings_sha256':{str(p.relative_to(ROOT)):sha(p)for p in external},'scope':'Saved native/material and static/listed-rigid-pose review, current PCB envelope binding and read-only numerical export diagnostics. Earlier failed/tight candidates and original STEP failures remain explicit. Adaptive mass/partition screens pass but cap Boolean is invalid; no full surface/supplier import, real wires, clamp force/stress/preload, seal/thread/material/process or physical acceptance. BatteryOPEN/BOMunchanged; no purchases/fabrication/commit.'}
(BASE/'artifact-index.json').write_text(json.dumps(out,indent=2)+'\n')
assert all(sha(BASE/n)==h for n,h in files.items())
print(len(files),'R25 files;',len(out['external_bindings_sha256']),'external bindings; current native/PCB/BOM verified',flush=True)
