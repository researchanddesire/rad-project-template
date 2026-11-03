"""Bind the scoped R15T routing review and preserve predecessor sources."""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'hardware/pcb/route-r15';P=OUT/'candidate-t';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
bp=P/'flange/flange-r15.kicad_pcb';a=json.loads((P/'saved-copper-audit.json').read_text());inv=json.loads((P/'drill-paste-inventory.json').read_text());fit=json.loads((P/'flange-mechanical-fit.json').read_text());parity=json.loads((P/'native-netlist-parity.json').read_text());source=json.loads((P/'source-conservation.json').read_text())
assert sha(bp)==a['native_board_sha256']==inv['native_board_sha256']==fit['new_board_sha256']
assert a['DRC']=={'violations':0,'unconnected':0,'footprint_errors':0}and not a['pin_net_mismatches']
assert inv['counts']=={'all_through_vias':40,'all_native_copper_or_paste_pad_shapes':121,'vias_drilling_SMD_copper':0,'vias_drilling_paste':0}
assert fit['component_intersections']==fit['nominal_mate_intersections']==[]and fit['primary_fixed_pairs_tested']==2093
assert all(u['samples_without_In1_GND']==0 and u['signal_vias']==0 for u in a['USB'].values())
assert a['USB_saved_copper_identical_to_E_seed']and len(a['explicit_native_NC_pins_kept_copper_netless'])==14
assert sha(bp.with_suffix('.kicad_pro'))==a['project_sha256']and sha(P/'flange/routed-native-drc.txt')==a['drc_sha256']
old=ROOT/'hardware/pcb/split-r14/candidate-b'
for f,r in source['schematics'].items():assert sha(P/f)==r['R15_sha256']and sha(old/f.replace('-r15','-r14'))==r['R14_sha256']
for f,h in source['symbol_libraries_equal_sha256'].items():assert sha(P/f)==h
for f,r in source['projects'].items():assert sha(P/f)==r['R15_sha256']and sha(old/f.replace('-r15','-r14'))==r['R14_sha256']
for domain,r in parity['domain_native_XML_parity'].items():
 f=P/(domain+'-native.xml')if domain=='system'else P/domain/(domain+'-native.xml');assert sha(f)==r['new_xml_sha256']and r['all_nodes_match_R14']
bodydrc=(P/'body/unrouted-native-drc.txt').read_text();assert '** Found 0 DRC violations **'in bodydrc and'** Found 165 unconnected pads **'in bodydrc and'** Found 0 Footprint errors **'in bodydrc
invariants={
 'hardware/bom.csv':'d5424d0536840bd3b555c439a129c0271b19b1cfbb3b94f1e1709e57cd63f05c',
 'hardware/pcb/prototype-r2/buttplug-r2.kicad_pcb':'5ba844fad77f58a8a5dfcb67f50e9070cf021048c29ed45a2751a9b8067f0bd4',
 'hardware/pcb/tip-r1/buttplug-tip-r1.kicad_pcb':'7d6d069e0daf16936299bdd99dfb08b9a416b0b5e6e5d2b5d44eaf717e7ed6ea',
 'hardware/pcb/split-r14/candidate-b/flange/flange-r14.kicad_pcb':'cc71cc8a57447ce3009ef1fb4df46ff7f4cb976065282e0f92fc728a6b62f17d',
 'hardware/pcb/split-r14/candidate-b/body/body-r14.kicad_pcb':parity['body_board_sha256'],
 'hardware/cad/simple-assembly-r13/candidate-f/SimpleAssemblyR13.FCStd':fit['source_R13_native_sha256']}
assert sha(P/'body/body-r15.kicad_pcb')==parity['body_board_sha256']
for f,h in invariants.items():assert sha(ROOT/f)==h,f
assets=ROOT/'developer-docs/docs/assets/prototype-r2';docs=[ROOT/'developer-docs/docs/flange-routing-r15.md']+[assets/('flange-routing-r15'+s)for s in ['.svg','.png','-source.json']]
files={str(f.relative_to(OUT)):sha(f)for f in sorted(OUT.rglob('*'))if f.is_file()and f.name!='artifact-index.json'and not(f.name.startswith('~')or f.suffix in ['.lck','.kicad_prl'])and'__pycache__'not in f.parts}
r={'date':'2026-11-01','current':'R15 candidate T flange routed; body unrouted165','freezer_sha256':sha(Path(__file__)),'artifact_files_sha256':files,'preserved_sources_sha256':invariants,'figure_and_doc_bindings_sha256':{str(f.relative_to(ROOT)):sha(f)for f in docs},'scope':'Native flange0/0/0, saved copper/pin parity, discreteUSBreference, nominal all-via process geometry and read-onlyCADcontext only. Fresh R15 GUI ERC pending; R14 saved report is source evidence, not a transferred new pass. Body routing, supported harness/flange/controls/tip, actualparts/process/materials and complete build proposal remain open. Failed developmental candidates preserved; no fabrication release.'}
(OUT/'artifact-index.json').write_text(json.dumps(r,indent=2)+'\n');assert all(sha(OUT/f)==h for f,h in files.items());print(len(files),'R15artifacts frozen;',len(invariants),'preserved source bindings;',len(docs),'figure/doc bindings')
