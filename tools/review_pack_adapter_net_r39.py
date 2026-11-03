"""Independent WireViz connectivity against full native R35F system XML."""
from pathlib import Path
import csv
import hashlib
import json
import xml.etree.ElementTree as ET
import yaml

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'hardware/cables/pack-adapter-r39'
source=P/'pack-adapter-r39.yml'
native=ROOT/'hardware/pcb/pack-pigtail-r35/candidate-f/system-native.xml'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
data=yaml.safe_load(source.read_text())
xml=ET.parse(native).getroot()
nodes={(n.get('ref'),n.get('pin')):net.get('name') for net in xml.findall('nets/net') for n in net.findall('node')}
components={c.get('ref'):c.findtext('value') for c in xml.findall('components/comp')}
graph={}
def node(kind,name,pin):return (kind,name,str(pin))
def edge(a,b):
    graph.setdefault(a,set()).add(b);graph.setdefault(b,set()).add(a)
for name,connector in data['connectors'].items():
    for loop in connector.get('loops',[]):
        assert len(loop)==2
        edge(node('connector',name,loop[0]),node('connector',name,loop[1]))
for row in data['connections']:
    assert len(row)==3
    ends=[]
    for index,item in enumerate(row):
        assert len(item)==1
        name,pins=next(iter(item.items()))
        kind='cable' if index==1 else 'connector'
        known=data['cables'][name] if kind=='cable' else data['connectors'][name]
        expected=range(1,known['wirecount']+1) if kind=='cable' else known['pins']
        assert all(str(p)in {str(q)for q in expected} for p in pins),(name,pins)
        ends.append([node(kind,name,p)for p in pins])
    assert len(ends[0])==len(ends[1])==len(ends[2])
    for a,b,c in zip(*ends):edge(a,b);edge(b,c)
def reach(start):
    seen={start};queue=[start]
    while queue:
        for q in graph.get(queue.pop(),set())-seen:seen.add(q);queue.append(q)
    return seen
bindings={node('connector','J2-R35',p):nodes['J2',logical] for p,logical in
          [('1','1'),('2S','2'),('2P','2'),('3','3'),('4','4')]}
for ref in ['TH1','TH2']:
    assert data['connectors'][ref]['mpn']==components[ref]
    for pin in ['1','2']:bindings[node('connector',ref,pin)]=nodes[ref,pin]
bindings[node('connector','PACK-REF','P+')]='PACK_P'
bindings[node('connector','PACK-REF','P-')]='GND'
visited=set();groups=[]
for start in graph:
    if start in visited:continue
    group=reach(start);visited|=group
    nets={bindings[q]for q in group if q in bindings}
    assert len(nets)==1, (group,nets)
    groups.append({'native_net':next(iter(nets)),'nodes':[list(q)for q in sorted(group)]})
expected={'1':{('PACK-REF','P+')},'2P':{('PACK-REF','P-')},
          '2S':{('TH1','2'),('TH2','2')},'3':{('TH1','1')},'4':{('TH2','1')}}
for pin,targets in expected.items():
    group=reach(node('connector','J2-R35',pin))
    terminals={(q[1],q[2])for q in group if q[0]=='connector'and q[1]in ['TH1','TH2','PACK-REF']}
    assert terminals==targets,(pin,terminals,targets)
assert reach(node('connector','J2-R35','2P')).isdisjoint(reach(node('connector','J2-R35','2S')))
assert data['cables']['W-BODY']['length']==.150 and data['cables']['W-BODY']['wirecount']==5
assert data['cables']['W-RETURN-LEGS']['length']==.030 and data['cables']['W-RETURN-LEGS']['wirecount']==2
assert all(data['cables'][n]['ignore_in_bom']for n in ['W-TH1-FACTORY','W-TH2-FACTORY'])
bom=Path('/private/tmp/r39-wireviz/pack-adapter-r39.bom.tsv')
with bom.open()as f:rows=list(csv.DictReader(f,delimiter='\t'))
assert sum(float(q['Qty']) for q in rows if q['MPN']=='NTCLE413E2103F524A')==2
assert abs(sum(float(q['Qty'])for q in rows if q['MPN']=='100690')-.81)<1e-7
assert not any('FACTORY'in q['Designators']for q in rows)
assert sum(float(q['Qty'])for q in rows if q['MPN']=='100046015')==1
assert all(data['cables'][n]['ignore_in_bom']for n in ['W-OEM','W-PACK'])
assert not any('W-OEM'in q['Designators']or 'W-PACK'in q['Designators']for q in rows)
geometry=ROOT/'hardware/cad/power-retention-r39/laps-p/geometry-report.json'
r=json.loads(geometry.read_text())
assert r['all_static_screens_clear']
route=ROOT/'hardware/cad/power-retention-r39/power-g/geometry-report.json'
route_data=json.loads(route.read_text())
assert max(q['exact_path_length_mm']for q in route_data['wire_plan']if q['section']=='body')+4+5<150
assert data['connectors']['OEM-MATE']['show_pincount']is False
assert any(q['qty']==2 and 'cuff'in q['description']for q in data['additional_bom_items'])
out={'geometry_report_sha256':sha(geometry),'route_report_sha256':sha(route),'reviewer_sha256':sha(Path(__file__)),'recipe_sha256':sha(source),'native_system_XML_sha256':sha(native),
     'native_binding_count':len(bindings),'electrical_groups':groups,
     'separate_external_power_and_sensor_returns':True,
     'candidate_child_BOM':{'one_prewired_mate_candidate':True,'two_sensors':True,'starting_wire_m':.81,'factory_leads_not_double_counted':True,
                            'generated_tsv_path':str(bom),'generated_tsv_sha256':sha(bom)},
     'scope':'Logical native-net and source recipe verification only. Returns join on body PCB, not in the long harness. Conditional power mate; receiving dimensions, materials/strain relief/assembly and current/thermal/physical qualification remain open. Starting blanks are not finished lengths or procurement approval.'}
(P/'logical-review.json').write_text(json.dumps(out,indent=2)+'\n')
print('R39 recipe matches native J2/TH1/TH2 nets; power and sensor returns separate externally; 2 sensors and0.81m starting wire, factory leads not duplicated; one prewired mate candidate, battery OPEN.')
