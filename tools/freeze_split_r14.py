"""Verify the connected-circuit checkpoint and freeze its review artifacts."""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'hardware/pcb/split-r14/candidate-b';OUT=P.parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=json.loads((P/'partition-source.json').read_text());erc=json.loads((P/'native-erc.json').read_text());parity=json.loads((P/'native-netlist-parity.json').read_text())
for f,h in source['source_schematics_sha256'].items():assert sha(ROOT/'hardware/pcb/prototype-r0'/f)==h,f
assert sha(ROOT/'hardware/pcb/prototype-r0/PrototypeR0.kicad_sym')==source['source_symbol_library_sha256']
for k in ['source_schematics_sha256','source_projects_sha256','source_symbol_libraries_sha256']:
 for f,h in erc[k].items():assert sha(P/f)==h,f
assert erc['errors']==erc['warnings']==erc['violations']==0 and erc['electrical_exclusions']==[]
assert sha(P/erc['native_report'])==erc['native_report_sha256']
assert '** ERC messages: 0  Errors 0  Warnings 0'in(P/erc['native_report']).read_text()
assert parity['preserved_source_net_nodes']==318 and parity['system_net_nodes']==338
assert parity['system_native_xml_sha256']==sha(P/'system-native.xml')
for domain,count,unconnected in [('body',67,165),('flange',22,81)]:
 link=json.loads((P/domain/'instance-link.json').read_text());drc=json.loads((P/domain/'native-drc.json').read_text());f=P/domain/(domain+'-r14.kicad_pcb')
 assert sha(f)==link['native_board_sha256']==drc['native_board_sha256']
 assert len(link['new_schematic_instances'])==count and link['whole_native_text_equal_except_instance_paths']
 assert drc['counts']=={'violations':0,'unconnected':unconnected,'footprint_errors':0}
 assert sha(P/domain/(domain+'-r14.kicad_pro'))==drc['project_sha256']
 assert sha(P/domain/(domain+'-native.xml'))==parity['boards'][domain]['native_xml_sha256']
 old=ROOT/'hardware/pcb/split-r12/candidate-i'/(domain+'-r12.kicad_pcb');assert sha(old)==link['source_R12_board_sha256']
 neutral=lambda p:re.sub(r'(?m)^[ \t]*\(path "[^"\n]*"\)\n','',p.read_text())
 assert neutral(old)==neutral(f)
invariants={
 'hardware/bom.csv':'d5424d0536840bd3b555c439a129c0271b19b1cfbb3b94f1e1709e57cd63f05c',
 'hardware/pcb/prototype-r2/buttplug-r2.kicad_pcb':'5ba844fad77f58a8a5dfcb67f50e9070cf021048c29ed45a2751a9b8067f0bd4',
 'hardware/pcb/tip-r1/buttplug-tip-r1.kicad_pcb':'7d6d069e0daf16936299bdd99dfb08b9a416b0b5e6e5d2b5d44eaf717e7ed6ea'}
cad=ROOT/'hardware/cad/simple-assembly-r13/candidate-f';cr=json.loads((cad/'geometry-report.json').read_text());invariants[str((cad/'SimpleAssemblyR13.FCStd').relative_to(ROOT))]=cr['native_sha256']
for f,h in invariants.items():assert sha(ROOT/f)==h,f
files={str(f.relative_to(OUT)):sha(f)for f in sorted(OUT.rglob('*'))if f.is_file()and f.name!='artifact-index.json'and not(f.name.startswith('~')or f.suffix in ['.lck','.kicad_prl'])and '__pycache__'not in f.parts}
assets=ROOT/'developer-docs/docs/assets/prototype-r2';docs=[ROOT/'developer-docs/docs/split-circuit-r14.md']+[assets/('split-circuit-r14'+suffix)for suffix in ['.png','.svg','-source.json']]
bindings={str(f.relative_to(ROOT)):sha(f)for f in docs}
out={'date':'2026-11-01','current':'R14 candidate B, UNROUTED boards','freezer_sha256':sha(Path(__file__)),'artifact_files_sha256':files,'preserved_sources_sha256':invariants,'figure_and_doc_bindings_sha256':bindings,
     'scope':'Saved full-device ERC/source conservation and instance-linked board checkpoint. Current locks/preferences excluded, not deleted. PCB routing, physical cable/fault/current/RF/process, complete mechanical interfaces and complete build proposal remain unfinished.'}
(OUT/'artifact-index.json').write_text(json.dumps(out,indent=2)+'\n')
assert all(sha(OUT/f)==h for f,h in files.items());print(len(files),'artifacts frozen;',len(invariants),'preserved sources;',len(bindings),'figure/doc bindings')
