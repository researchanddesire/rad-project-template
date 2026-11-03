"""Bind the current R34J/R35F review artifacts without adopting a pack or releasing fabrication."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
CAD = ROOT / 'hardware/cad/pack-harness-r34/pigtail-j'
PCB = ROOT / 'hardware/pcb/pack-pigtail-r35/candidate-f'
r = json.loads((CAD / 'geometry-report.json').read_text())
v = json.loads((CAD / 'saved-review.json').read_text())
c = json.loads((PCB / 'saved-circuit-review.json').read_text())
d = json.loads((PCB / 'body/native-drc.json').read_text())
assert sha(CAD / 'PackPigtailTransitR34.FCStd') == r['native_sha256'] == v['native_sha256']
assert sha(PCB / 'body/body-r35.kicad_pcb') == d['native_board_sha256'] == c['boards']['body']['sha256']
assert d['counts'] == {'violations': 0, 'unconnected': 0, 'footprint_errors': 0}
assert r['all_transit_static_screens_clear'] and not v['unexpected_intersections']
assert r['native_R35F_bindings']['PCB_sha256'] == c['boards']['body']['sha256']
assert r['native_R35F_bindings']['review_sha256'] == sha(PCB / 'saved-circuit-review.json')
assert c['components'] == 94 and c['logical_nodes'] == 338 and c['all_source_nodes_equal']
assert sha(ROOT / 'hardware/bom.csv') == 'd5424d0536840bd3b555c439a129c0271b19b1cfbb3b94f1e1709e57cd63f05c'
files = {}
for directory in [CAD, PCB]:
    for path in sorted(directory.rglob('*')):
        if path.is_file() and path.suffix not in ['.kicad_prl', '.pyc'] and path.name != '.DS_Store':
            files[str(path.relative_to(ROOT))] = sha(path)
bindings = [
    'hardware/cad/pack-harness-r34/README.md',
    'hardware/pcb/pack-pigtail-r35/README.md',
    'hardware/cad/pack-harness-r34/passage-c/PackTailPassageR34.FCStd',
    'hardware/cad/pack-harness-r34/passage-c/geometry-report.json',
    'hardware/cad/pack-harness-r34/formed-f/FormedFlexSpaceR34.FCStd',
    'hardware/cad/pack-harness-r34/formed-f/geometry-report.json',
    'hardware/cad/pack-harness-r34/unfold-h/PackFlexFlatSpaceR34.FCStd',
    'hardware/cad/pack-harness-r34/unfold-h/unfold-review.json',
    'hardware/cad/battery-fit-r33/artifact-index.json',
    'hardware/pcb/flange-access-r28/candidate-s/body/body-r28.kicad_pcb',
    'hardware/pcb/flange-access-r28/candidate-s/flange/flange-r28.kicad_pcb',
    'hardware/pcb/flange-access-r28/candidate-s/system-native.xml',
    'hardware/design/pack-harness-r34/design-basis.json',
    'developer-docs/docs/pack-connection-r34.md',
    'assembly-docs/pack-connection-r34.md',
    'developer-docs/docs/assets/prototype-r2/pack-pigtail-r34-j.png',
    'developer-docs/docs/assets/prototype-r2/pack-pigtail-r34-j-source.json',
    'hardware/bom.csv',
]
external = {p: sha(ROOT / p) for p in bindings}
result = {'indexed_at_utc': datetime.now(timezone.utc).isoformat(),
          'indexer_sha256': sha(Path(__file__)), 'files_sha256': files,
          'external_bindings_sha256': external,
          'current': {'wire_transit': 'R34 pigtail J', 'solder_land_variant': 'R35 candidate F',
                      'pack_retention': 'R33 candidate F', 'battery_selection': 'OPEN'},
          'checks': {'body_DRC': d['counts'], 'components': 94, 'logical_nodes': 338,
                     'source_fixed_roles_conserved': len(v['conserved_fixed_roles']),
                     'fresh_wire_to_fixed_comparisons': v['fresh_new_to_fixed_comparisons'],
                     'minimum_coated_wire_pair_gap_mm': min(q['native_surface_gap_mm'] for q in r['native_coated_wire_pair_gaps'])},
          'prototype_build_consideration_ready': False,
          'remaining_design': ['Full protected-pack mate and leads; full dual-NTC leads/return branch/insulated splices',
                               'Solder geometry/process, force-bypass restraints and connected loading/service',
                               'Flange loads/compliance, seals/material/process and consolidated fabrication/first-build package'],
          'scope': 'Integrity index for the current local wire transit and solder-land variant. Failed trials remain preserved outside this current-file set. Flex is a folded/flat space claim only. No full harness, fabrication, electrical/thermal/physical or wear acceptance; no purchase or human BOM change.'}
out = ROOT / 'hardware/design/pack-harness-r34/current-review.json'
out.write_text(json.dumps(result, indent=2) + '\n')
print('Indexed', len(files), 'current files and', len(external), 'external bindings; prototype proposal remains unfinished.', flush=True)
