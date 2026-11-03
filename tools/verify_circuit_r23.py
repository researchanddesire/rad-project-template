"""Whole R23 source conservation and fresh native full-device node comparison."""
from pathlib import Path
import sys,json,hashlib,copy,xml.etree.ElementTree as E
import kicad_sexp as S
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'hardware/pcb/route-r16/candidate-u';P=Path(sys.argv[1]).resolve();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();canon=lambda n:tuple(canon(x)for x in n)if isinstance(n,list)else n.raw;compact=json.loads((P/'compact-driver.json').read_text());fields={};files={};url='https://www.murata.com/en-global/api/pdfdownloadapi?cate=luCeramicCapacitorsSMD&partno=GRM155R71C104KA88%23'
actual={str(p.relative_to(P)).replace('-r23','-r16'):p for p in P.rglob('*.kicad_sch')};original={str(p.relative_to(BASE)):p for p in BASE.rglob('*.kicad_sch')};assert set(actual)==set(original)and len(actual)==13
for name,path in original.items():
 old=S.parse(path.read_text());new=S.parse(actual[name].read_text().replace('-r23','-r16'));expected=copy.deepcopy(old)
 for n in S.children(expected,'symbol'):
  ref=S.prop(n,'Reference')
  if ref not in ['C28','C29']:continue
  note=S.prop(n,'ReviewNote');changes={'Footprint':'PrototypeR0:C_0402_1005Metric','Datasheet':url,'ReviewNote':(note+'; 'if note else'')+'GRM155R71C104KA88D 0402 candidate; same100nF/16V/X7R/10percent nominal; installed bias/assembly/availability review pending'};assert changes==compact['component_changes'][ref]['schematic_field_changes'];fields[ref]=changes
  for prop in S.children(n,'property'):
   if prop[1].value in changes:prop[2]=S.string(changes[prop[1].value])
 assert canon(expected)==canon(new),name;files[name]={'source_R16_sha256':sha(path),'R23_sha256':sha(actual[name]),'R23_relative_path':str(actual[name].relative_to(P))}
assert set(fields)=={'C28','C29'};projects={}
for f in BASE.rglob('*.kicad_pro'):
 name=str(f.relative_to(BASE));new=P/name.replace('-r16','-r23');old=json.loads(f.read_text());current=json.loads(new.read_text());old['meta']['filename']=new.name
 if(P/'via-process.json').exists()and name.startswith('body/'):
  for c in json.loads((P/'via-process.json').read_text())['project_delta']:
   d=old
   for key in c['path'][:-1]:d=d[key]
   assert d[c['path'][-1]]==c['old']
   live=current
   for key in c['path']:live=live[key]
   assert isinstance(live,(int,float))and abs(live-c['new'])<1e-14,(c,live)
   d[c['path'][-1]]=live # only declared dimension paths: native nm-to-mm float round-trip

 assert old==current,name;projects[str(new.relative_to(P))]={'source_sha256':sha(f),'new_sha256':sha(new),'only_filename_and_declared_via_process_changes':True}
libs={}
for f in BASE.rglob('*.kicad_sym'):
 new=P/f.relative_to(BASE);assert sha(f)==sha(new);libs[str(new.relative_to(P))]=sha(new)
def xml(p):
 root=E.parse(p).getroot();comps={c.get('ref'):(c.findtext('value'),c.findtext('footprint'),c.find('libsource').attrib)for c in root.findall('components/comp')};nodes={(n.get('ref'),n.get('pin')):(net.get('name'),n.get('pinfunction'),n.get('pintype'))for net in root.findall('nets/net')for n in net.findall('node')};return comps,nodes
oc,on=xml(BASE/'system-native.xml');nc,nn=xml(P/'system-native.xml');assert set(oc)==set(nc)and on==nn and len(nn)==338 and len(nc)==94
for ref,old in oc.items():
 wanted=(old[0],fields[ref]['Footprint'],old[2])if ref in fields else old;assert nc[ref]==wanted,ref
assert sha(P/'flange/flange-r23.kicad_pcb')==sha(BASE/'flange/flange-r16.kicad_pcb')
out={'date':'2026-11-01','verifier_sha256':sha(Path(__file__)),'whole_source_sheets':files,'project_rule_ERC_setting_conservation':projects,'symbol_library_sha256':libs,'two_declared_component_field_changes':fields,'source_native_XML_sha256':sha(BASE/'system-native.xml'),'new_native_XML_sha256':sha(P/'system-native.xml'),'components':94,'pin_net_function_type_nodes':338,'all_338_nodes_equal_R16U':True,'all_schematic_nominal_values_equal_R16U':True,'declared_six_layer_stackup_sha256':sha(P/'stackup-r23.json'),'declared_via_process_sha256':sha(P/'via-process.json')if(P/'via-process.json').exists()else None,'flange_board_byte_identical_to_R16U':True,'flange_board_sha256':sha(P/'flange/flange-r23.kicad_pcb'),'scope':'Whole13schematic atom equality after only project/file name changes and two declared capacitor footprint/datasheet/review-note updates. All project settings and symbol libraries retained except the explicitly recorded optional four via-process minimum/default changes; no ERC/spacing/edge/hole-spacing/annular changes. Fresh native XML conserves all338nodes and nominal values. No fresh GUIERC, analog/thermal/RF/current/harness/process/physical acceptance.'};(P/'circuit-conservation.json').write_text(json.dumps(out,indent=2)+'\n');print('94components / all338nodes /13whole source sheets conserved; two capacitor packages declared',flush=True)
