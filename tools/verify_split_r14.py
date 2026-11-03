"""Compare exported native full-system and board circuits to preserved R0."""
from pathlib import Path
import argparse,hashlib,json,xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ap=argparse.ArgumentParser();ap.add_argument('directory',type=Path);ap.add_argument('source_xml',type=Path);args=ap.parse_args();P=args.directory.resolve()
def read(p):
 r=E.parse(p).getroot();comps={c.get('ref'):{'value':c.findtext('value'),'footprint':c.findtext('footprint'),'libsource':c.find('libsource').attrib}for c in r.findall('components/comp')}
 nets={(n.get('ref'),n.get('pin')):net.get('name')for net in r.findall('nets/net')for n in net.findall('node')}
 libs={(l.get('lib'),l.get('part')):{p.get('num'):(p.get('name'),p.get('type'))for p in l.findall('pins/pin')}for l in r.findall('libparts/libpart')}
 sheets=[{'number':s.get('number'),'name':s.get('name'),'path':s.get('tstamps')}for s in r.findall('design/sheet')]
 return comps,nets,libs,sheets
source_comp,source_nets,source_libs,_=read(args.source_xml)
comp,nets,libs,sheets=read(P/'system-native.xml');r=json.loads((P/'partition-source.json').read_text());pinmap=r['connector_pinmap']
assert set(comp)==set(source_comp)|{'J6','J7'}
for ref,c in source_comp.items():assert comp[ref]==c,(ref,comp[ref],c)
assert {k:v for k,v in nets.items()if k[0]not in ['J6','J7']}==source_nets
for header in ['J6','J7']:assert {pin:nets[(header,pin)]for pin in pinmap}==pinmap
for lib,spec in libs.items():
 if lib[1]=='Conn10':assert len(spec)==10 and all(v[1]=='passive'for v in spec.values())
 else:assert source_libs[lib]==spec,lib
boards={}
for domain,count in [('body',67),('flange',22)]:
 bc,bn,bl,bs=read(P/domain/(domain+'-native.xml'));wanted={ref for ref,record in r['board_instances'].items()if record['domain']==domain}
 assert len(bc)==count and set(bc)==wanted
 assert bn=={k:v for k,v in nets.items()if k[0]in wanted},domain
 for ref in wanted:assert bc[ref]==comp[ref],ref
 boards[domain]={'physical_components':len(bc),'exported_pin_net_nodes':len(bn),'native_xml_sha256':sha(P/domain/(domain+'-native.xml')),'schematic_sha256':{str(p.relative_to(P)):sha(p)for p in(P/domain).glob('*.kicad_sch')},'pin_net_parity':True,'component_value_footprint_parity':True,'sheet_pages':bs}
out={'date':'2026-11-01','verifier_sha256':sha(Path(__file__)),'baseline_native_xml_sha256':sha(args.source_xml),'system_native_xml_sha256':sha(P/'system-native.xml'),'partition_record_sha256':sha(P/'partition-source.json'),
 'source_components':len(source_comp),'system_components':len(comp),'preserved_source_net_nodes':len(source_nets),'new_header_pin_net_nodes':20,'system_net_nodes':len(nets),'original_symbol_pin_numbers_names_types_preserved':True,
 'boards':boards,'system_sheet_pages':sheets,'scope':'Actual KiCad7 native XML exports, all original refs/values/footprints, connected pin nets and symbol pin identities/types. Separate from ERC, PCB routing, wire/current/fault/RF/process or physical operation. PWR_FLAG annotations are absent from netlist component exports.'}
(P/'native-netlist-parity.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'source_nodes':len(source_nets),'new_nodes':len(nets),'boards':{k:{'components':v['physical_components'],'nodes':v['exported_pin_net_nodes']}for k,v in boards.items()},'issues':[]},indent=2))
