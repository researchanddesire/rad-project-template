"""Freeze R27D geometry and R28A's explicit incomplete electrical placement."""
from pathlib import Path
import json,hashlib,shutil
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'hardware/cad/flange-controls-r27';P=BASE/'candidate-d';PCB=ROOT/'hardware/pcb/flange-access-r28';Q=PCB/'candidate-a';SRC=ROOT/'hardware/cad/tip-support-r26'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
r=read(P/'geometry-report.json');v=read(P/'saved-review.json');native=sha(P/'FlangeCradleR27.FCStd')
assert native==r['native_sha256']==v['native_sha256']and sha(P/'geometry-report.json')==v['geometry_report_sha256']
assert sha(SRC/'candidate-f/StationaryTipR26.FCStd')==r['source_native_sha256']==v['source_R26_native_sha256']
assert sha(SRC/'candidate-f/geometry-report.json')==r['source_report_sha256']
assert len(r['parts'])==132 and len(r['mates'])==7 and len(r['allowances'])==2 and r['static_pairs_tested']==8646
assert not r['unexpected_intersections']and not r['nominal_mate_intersections']and len(r['named_unqualified_screw_pilot_interfaces'])==4
assert len(v['saved_roles'])==141 and len(v['preserved_source_roles'])==110 and len(v['inverse_transformed_flange_roles'])==28 and not v['external_document_links']
assert abs(v['source_hub_material_removed_mm3'])<1e-4 and v['all_new_listed_screens_clear']and not v['source_nominal_mate_approach_failures']
for container,key,count in [(r,'island_listed_loading_poses',11),(r,'nominal_mate_listed_approach_poses',24),(v,'hub_listed_side_loading_poses',9),(v,'keeper_listed_approach_poses',8),(v,'screw_listed_approach_poses',8)]:assert len(container[key])==count and not any(x['hits']for x in container[key])
assert not v['generic_2_2mm_tool_shaft_hits']and r['GUI_only_configuration']['all_geometry_archive_entries_unchanged']
pr=read(Q/'placement-inspection.json');dr=read(Q/'placement-drc-status.json');bh=sha(Q/'flange-r28.kicad_pcb')
assert bh==pr['native_board_sha256']==dr['native_board_sha256']==r['placement_R28_native_sha256']==v['native_R28_placement_geometry_binding']['native_board_sha256']
assert sha(Q/'placement-inspection.json')==r['placement_R28_inspection_sha256']==v['native_R28_placement_geometry_binding']['inspection_sha256']
assert len(v['native_R28_placement_geometry_binding']['all_24_Fab_height_boxes'])==24
assert dr['counts']=={'drc_violations':78,'unconnected_items':11,'footprint_errors':0}and sha(Q/'placement-native-drc.txt')==dr['native_drc_report_sha256']
assert len(pr['placements'])==24 and pr['all_24_ref_value_pad_net_maps_and_centres_conserved']and pr['unchanged_22_poses']and pr['all_nominal_mate_Fab_approaches_clear']
assert not pr['component_Fab_box_intersections']and not pr['same_face_courtyard_overlaps']
oldpcb=ROOT/'hardware/pcb/stackup-r23/candidate-d/flange/flange-r23.kicad_pcb';assert sha(oldpcb)==pr['source_native_board_sha256']
lib=read(Q/'library-config-review.json');assert sha(Q/'fp-lib-table')==lib['corrected_fp_lib_table_sha256']and bh==lib['native_board_unchanged_sha256']and(Q/lib['library_relative_path']).resolve().is_dir()
screen=BASE/'placement-screen-a/orientation-screen.json';assert sha(screen)==r['placement_screen_sha256'];sr=read(screen);assert len(sr['cases'])==10
assert sha(ROOT/'tools/screen_flange_r27.py')==sr['screener_sha256']
for n,h in r['review_meshes_sha256'].items():assert sha(P/n)==h,n
asset=ROOT/'developer-docs/docs/assets/prototype-r2/flange-cradle-r27-d.png';render=read(asset.with_name(asset.stem+'-source.json'))
assert render['native_sha256']==native and render['geometry_report_sha256']==sha(P/'geometry-report.json')and render['saved_review_sha256']==sha(P/'saved-review.json')and render['placement_R28_native_sha256']==bh
tools={'retain_flange_r27.py':r['builder_sha256'],'configure_flange_r27_view.py':r['GUI_only_configuration']['script_sha256'],'review_flange_r27.py':v['reviewer_sha256'],'render_flange_r27.py':render['renderer_sha256'],'render_mechanical_r2.py':render['render_library_sha256']}
ex=P/'executed-tools';ex.mkdir(exist_ok=True)
for n,h in tools.items():
 src=ROOT/'tools'/n;assert sha(src)==h,n;dest=ex/n
 if dest.exists():assert sha(dest)==h
 else:shutil.copyfile(src,dest)
assert sha(Q/'executed-tools/turn_flange_headers_r28.py')==pr['builder_sha256']
for srcname,destname in [('flange-r27-d-render.log','render.log'),('buttplug-r27-docs-final.log','docs-build.log')]:
 src=Path('/private/tmp')/srcname;dest=P/destname
 if dest.exists():assert dest.read_bytes()==src.read_bytes()
 else:shutil.copyfile(src,dest)
assert 'Documentation built in'in(P/'docs-build.log').read_text()and 'WARNING -'not in(P/'docs-build.log').read_text()
fcopy=ex/Path(__file__).name
if fcopy.exists():assert sha(fcopy)==sha(Path(__file__))
else:shutil.copyfile(Path(__file__),fcopy)
bom=ROOT/'hardware/bom.csv';assert sha(bom)=='d5424d0536840bd3b555c439a129c0271b19b1cfbb3b94f1e1709e57cd63f05c'
external=[ROOT/'developer-docs/docs/flange-cradle-r27.md',ROOT/'assembly-docs/flange-cradle-r27.md',asset,asset.with_name(asset.stem+'-source.json'),SRC/'candidate-f/StationaryTipR26.FCStd',SRC/'candidate-f/geometry-report.json',SRC/'artifact-index.json',oldpcb,ROOT/'hardware/pcb/stackup-r23/artifact-index.json',bom]
external+=[p for p in PCB.rglob('*')if p.is_file()and p.name!='artifact-index.json'and '__pycache__'not in p.parts and p.suffix!='.lck']
files={};omitted=[]
for p in sorted(BASE.rglob('*')):
 if not p.is_file()or p.name=='artifact-index.json'or '__pycache__'in p.parts or p.suffix=='.lck'or p.name.startswith('~'):continue
 if p.suffix=='.stl'and p.parent!=P:omitted.append(str(p.relative_to(BASE)))
 else:files[str(p.relative_to(BASE))]=sha(p)
out={'date':'2026-11-01','current':'R27D mechanical geometry candidate; R28A header placement requires routing repair, complete build proposal unfinished','native_sha256':native,'freezer_sha256':sha(Path(__file__)),'files_sha256':files,'preserved_historical_meshes_not_rehashed':omitted,'external_bindings_sha256':{str(p.relative_to(ROOT)):sha(p)for p in external},'scope':'Current native/source conservation, 24 actual flange Fab boxes and explicitly staged finite rigid/tool screens. R28A has78nativeDRC/11unconnected/0footprint findings: no electrical/fabrication acceptance. Prior failed/corrected probes preserved; unused historical meshes not rehashed. No actual connector/wire/flex/control/load/material/seal/RF or physical qualification. BatteryOPEN/humanBOMunchanged.'}
(BASE/'artifact-index.json').write_text(json.dumps(out,indent=2)+'\n')
qfiles={str(p.relative_to(PCB)):sha(p)for p in sorted(PCB.rglob('*'))if p.is_file()and p.name!='artifact-index.json'and '__pycache__'not in p.parts and p.suffix!='.lck'}
(PCB/'artifact-index.json').write_text(json.dumps({'date':'2026-11-01','state':'R28A incomplete placement correction; copper repair required, not fabrication release','native_board_sha256':bh,'files_sha256':qfiles,'native_DRC_counts':dr['counts'],'source_R23_flange_sha256':sha(oldpcb),'R27_geometry_index_sha256':sha(BASE/'artifact-index.json'),'scope':'Native placement/pad semantics, nominal box/finite approach screens and explicit failing DRC; no current electrical build acceptance. Original executed builder and library-path correction retained.'},indent=2)+'\n')
assert all(sha(BASE/n)==h for n,h in files.items())and all(sha(PCB/n)==h for n,h in qfiles.items())
print(len(files),'R27 hashed files;',len(out['external_bindings_sha256']),'bindings;',len(qfiles),'R28 files; geometry screens pass / electrical placement explicitly incomplete',flush=True)
