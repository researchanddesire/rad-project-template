"""Verify current native/report identities and freeze scoped artifact indexes."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
PCB=ROOT/'hardware/pcb/split-r12';CAD=ROOT/'hardware/cad/simple-assembly-r13';I=PCB/'candidate-i';F=CAD/'candidate-f'
source_checks={
 'hardware/bom.csv':'d5424d0536840bd3b555c439a129c0271b19b1cfbb3b94f1e1709e57cd63f05c',
 'hardware/pcb/prototype-r2/buttplug-r2.kicad_pcb':'5ba844fad77f58a8a5dfcb67f50e9070cf021048c29ed45a2751a9b8067f0bd4',
 'hardware/pcb/tip-r1/buttplug-tip-r1.kicad_pcb':'7d6d069e0daf16936299bdd99dfb08b9a416b0b5e6e5d2b5d44eaf717e7ed6ea',
 'hardware/cad/front-load-r10/candidate-c/FrontLoadR10.FCStd':'b77ac8e14adba236f2824a9ad762ef02373632114d694178f8db3f3011430841',
 'hardware/cad/front-load-retention-r11/candidate-c/FrontLoadRetentionR11.FCStd':'2fdbc43a5dc58b0fb55874a33dc9c08fd9364c826c2c1118d70558731d64499c',
 'hardware/cad/prototype-r2/full-05/ButtplugPrototypeR2Full05.FCStd':'8987e095e5ff4bfcfd32b8ce53f114c68cf2ebc33e751ac59a7692651fa543a6'}
for p,h in source_checks.items():assert sha(ROOT/p)==h,p
manifest=json.loads((ROOT/'hardware/pcb/prototype-r2/candidate-pin-manifest.json').read_text());original={p['ref']for p in manifest['parts']if p.get('on_main_board')}
refs=[];generation=json.loads((I/'placement-report.json').read_text())
for domain,want,unconnected in [('body',67,165),('flange',22,81)]:
    r=json.loads((I/(domain+'-native-inspection.json')).read_text());g=generation['boards'][domain]
    assert r['board_sha256']==g['board_sha256']==sha(I/(domain+'-r12.kicad_pcb'))
    assert g['project_sha256']==sha(I/(domain+'-r12.kicad_pro'))
    assert r['footprints']==want and not r['pad_net_mismatches']and not r['same_face_courtyard_bbox_overlaps']
    assert r['native_DRC_counts']=={'violations':0,'unconnected':unconnected,'footprint_errors':0}
    assert not g['unplaced_or_fixed_conflicts'];refs.extend(p['ref']for p in r['placements'])
assert len(refs)==len(set(refs))==89 and set(refs)-{'J6','J7'}==original and len(original)==87
fit=json.loads((I/'mechanical-fit.json').read_text());assert not fit['body_intersections']and not fit['mate_intersections']
r=json.loads((F/'geometry-report.json').read_text());s=json.loads((F/'saved-review.json').read_text())
assert sha(F/'SimpleAssemblyR13.FCStd')==r['native_sha256']==s['native_sha256']
assert sha(F/'geometry-report.json')==s['geometry_report_sha256']
assert len(r['parts'])==110 and len(r['mates'])==7 and len(s['saved_roles'])==117
assert not r['unexpected_intersections']and not r['nominal_mate_intersections']
assert all(not p['hits']for k in ['board_drop_listed_poses','keeper_lowering_listed_poses']for p in r[k])
assert all(p['body_hit_mm3']<1e-5 for p in r['cartridge_listed_poses'])
assert not s['external_document_links']
for v in s['fixed_source_roles_material_comparison'].values():assert v['removed_mm3']<1e-4 and v['added_mm3']<1e-4
for folder,revision,figure in [(PCB,'R12 candidate I','split-pcb-r12'),(CAD,'R13 candidate F','simple-assembly-r13')]:
    files={str(p.relative_to(folder)):sha(p)for p in sorted(folder.rglob('*'))if p.is_file()and p.name not in ['artifact-index.json','.DS_Store']and '__pycache__'not in p.parts}
    assets=ROOT/'developer-docs/docs/assets/prototype-r2';bindings={str((assets/(figure+suffix)).relative_to(ROOT)):sha(assets/(figure+suffix))for suffix in ['.png','-source.json']}
    doc=ROOT/'developer-docs/docs'/('split-pcb-r12.md'if folder==PCB else'simple-assembly-r13.md');bindings[str(doc.relative_to(ROOT))]=sha(doc)
    out={'date':'2026-11-01','current':revision,'artifact_files_sha256':files,'source_invariants_sha256':source_checks,'figure_and_doc_bindings_sha256':bindings,'freezer_sha256':sha(Path(__file__)),
         'scope':'Frozen development records and review meshes. Not fabrication, purchase, complete build proposal, physical assembly, current/thermal/strength or wear acceptance.'}
    (folder/'artifact-index.json').write_text(json.dumps(out,indent=2)+'\n')
    assert all(sha(folder/p)==h for p,h in files.items())
    print(revision,len(files),'indexed artifacts;',len(source_checks),'unchanged source files;',len(bindings),'figure/doc bindings')
