"""Independently compare saved R35 solder-land circuit/board against R28S."""
from pathlib import Path
import collections
import json
import sys
import xml.etree.ElementTree as ET
import pcb_r2_route as R

K = R.k
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'hardware/pcb/flange-access-r28/candidate-s'
OUT = Path(sys.argv[1]).resolve()

def circuit(path):
    root = ET.parse(path).getroot()
    components = {c.get('ref'): (c.findtext('value'), c.findtext('footprint'),
                  c.find('libsource').attrib) for c in root.findall('components/comp')}
    nodes = {(n.get('ref'), n.get('pin')):
             (net.get('name'), n.get('pinfunction'), n.get('pintype'))
             for net in root.findall('nets/net') for n in net.findall('node')}
    return components, nodes

def pad_row(p):
    return {'number': p.GetNumber(), 'net': p.GetNetname(),
            'xy_mm': R.mech(p.GetPosition()),
            'size_mm': [K.ToMM(p.GetSize().x), K.ToMM(p.GetSize().y)],
            'drill_mm': [K.ToMM(p.GetDrillSize().x), K.ToMM(p.GetDrillSize().y)],
            'angle_deg': p.GetOrientationDegrees(), 'shape': int(p.GetShape()),
            'layers': p.GetLayerSet().FmtHex()}

def footprint(f):
    return {'ref': f.GetReference(), 'value': f.GetValue(), 'id': str(f.GetFPID().GetLibNickname()) + ':' + str(f.GetFPID().GetLibItemName()),
            'xy_mm': R.mech(f.GetPosition()), 'angle_deg': f.GetOrientationDegrees(),
            'side': f.GetLayer(), 'pads': sorted((pad_row(p) for p in f.Pads()),
                                               key=lambda p: json.dumps(p, sort_keys=True))}

oldc, oldn = circuit(SRC / 'system-native.xml')
newc, newn = circuit(OUT / 'system-native.xml')
assert len(newc) == 94 and len(newn) == 338 and oldn == newn
assert oldc.keys() == newc.keys()
assert {k: v for k, v in oldc.items() if k != 'J2'} == {k: v for k, v in newc.items() if k != 'J2'}
assert newc['J2'][0:2] == ('PACK_PIGTAIL_4NET_5LAND', 'PackPigtailR35:Pack_Pigtail_4Net_5Land')
assert oldc['J2'][2] == newc['J2'][2]
boards = {}
for domain in ['body', 'flange']:
    path = OUT / domain / (domain + '-r35.kicad_pcb')
    source = SRC / domain / (domain + '-r28.kicad_pcb')
    before = R.sha(path)
    b, old = K.LoadBoard(str(path)), K.LoadBoard(str(source))
    current = {f.GetReference(): f for f in b.GetFootprints()}
    previous = {f.GetReference(): f for f in old.GetFootprints()}
    assert current.keys() == previous.keys()
    _, nodes = circuit(OUT / domain / (domain + '-native.xml'))
    checked = 0
    for ref, f in current.items():
        if domain != 'body' or ref != 'J2':
            assert footprint(f) == footprint(previous[ref]), (domain, ref)
        for p in f.Pads():
            if p.GetNumber() in ['', 'MP']:
                continue
            target = nodes[(ref, p.GetNumber())]
            expected = '' if 'no_connect' in target[2].split('+') else target[0]
            assert p.GetNetname() == expected, (domain, ref, p.GetNumber())
            checked += 1
    pro = json.loads(path.with_suffix('.kicad_pro').read_text())
    prior = json.loads(source.with_suffix('.kicad_pro').read_text())
    for section in ['board', 'erc', 'net_settings']:
        assert pro[section] == prior[section], (domain, section)
    counter = lambda rows: collections.Counter(json.dumps(q, sort_keys=True) for q in rows)
    newroutes, oldroutes = counter(R.route_records(b)), counter(R.route_records(old))
    assert not oldroutes - newroutes
    added = list((newroutes - oldroutes).elements())
    if domain == 'flange':
        assert before == R.sha(source) and not added
    else:
        assert len(added) == 1 and json.loads(added[0])['net'] == 'GND'
        status = json.loads((OUT / 'body/native-drc.json').read_text())
        assert status['native_board_sha256'] == before
        assert status['counts'] == {'violations': 0, 'unconnected': 0, 'footprint_errors': 0}
        j = current['J2']
        jpads = [pad_row(p) for p in j.Pads()]
        assert len(jpads) == 5 and all(not p.GetLayerSet().Contains(K.F_Paste) for p in j.Pads())
        for p in previous['J2'].Pads():
            if p.GetNumber() in ['', 'MP']:
                continue
            row = pad_row(p)
            assert any(all(q[k] == row[k] for k in ['number', 'net', 'xy_mm', 'size_mm', 'shape', 'angle_deg']) for q in jpads)
        extra = next(p for p in j.Pads() if R.mech(p.GetPosition()) == [-2.2, 41.9])
        assert extra.GetNumber() == '2' and extra.GetNetname() == 'GND'
        assert extra.GetZoneConnection() == K.ZONE_CONNECTION_FULL
        assert j.GetProperty('CandidateHeight_mm') == '0'
    assert R.sha(path) == before
    boards[domain] = {'sha256': before, 'source_sha256': R.sha(source),
                      'footprints': len(current), 'electrical_pad_entries_checked': checked,
                      'original_routes_conserved': sum(oldroutes.values()),
                      'added_routes': [json.loads(q) for q in added],
                      'board_erc_net_rules_equal': True,
                      'copper_layers': b.GetCopperLayerCount()}

result = {'reviewer_sha256': R.sha(Path(__file__)), 'system_xml_sha256': R.sha(OUT / 'system-native.xml'),
          'components': 94, 'logical_nodes': 338, 'all_source_nodes_equal': True,
          'only_component_value_footprint_change': 'J2', 'boards': boards,
          'new_sensor_return_land': {'xy_mm': [-2.2, 41.9], 'world_size_mm': [.5, .5],
          'net': 'GND', 'number': '2', 'zone_connection': 'solid locally; original ground land retains thermal relief'},
          'scope': 'Saved circuit topology, native pad assignments, all other footprint poses/pads, source routes and rules conserved. Fresh body DRC 0/0/0; flange byte-identical to R28S. Native fabrication output, fresh GUI ERC, wire soldering/strain relief, current, thermal and physical qualification remain open. Battery OPEN; human BOM unchanged.'}
R.write(OUT / 'saved-circuit-review.json', result)
print('R35: 94 components / 338 nodes; source routes and other footprint poses/pads conserved; body native DRC 0/0/0; flange identical.', flush=True)
