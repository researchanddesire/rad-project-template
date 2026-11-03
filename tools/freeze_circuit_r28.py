"""Bind the R28S review checkpoint without rewriting earlier native evidence."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'hardware/pcb/flange-access-r28'
S = BASE / 'candidate-s'
HISTORY = BASE / 'source-history'
R27 = ROOT / 'hardware/cad/flange-controls-r27/artifact-index.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def verify(index, base):
    for name, digest in index['files_sha256'].items():
        assert sha(base / name) == digest, name
    for name, digest in index.get('external_bindings_sha256', {}).items():
        assert sha(ROOT / name) == digest, name


HISTORY.mkdir(exist_ok=True)
old28 = HISTORY / 'R28A-artifact-index.json'
old27 = HISTORY / 'R27D-before-R28S-index.json'
if not old28.exists():
    assert json.loads((BASE / 'artifact-index.json').read_text())['state'].startswith('R28A')
    shutil.copyfile(BASE / 'artifact-index.json', old28)
if not old27.exists():
    shutil.copyfile(R27, old27)
previous = json.loads(old27.read_text())
readme_key = 'hardware/pcb/flange-access-r28/README.md'
original_readme = '# Flange plug-access correction R28\n\n' + (
    (BASE / 'README.md').read_text().split('## Preserved placement correction A\n\n', 1)[1]
)
readme_snapshot = HISTORY / 'README-before-r28s.md'
readme_snapshot.write_text(original_readme)
assert sha(readme_snapshot) == previous['external_bindings_sha256'][readme_key]
# Preserve R27's existing frozen file inventory verbatim. Do not rehydrate and
# rehash historical rejected geometry for a README-only metadata refresh.
for name, digest in previous['external_bindings_sha256'].items():
    if name != readme_key:
        assert sha(ROOT / name) == digest, name
refreshed = dict(previous)
refreshed['external_bindings_sha256'] = dict(previous['external_bindings_sha256'])
refreshed['external_bindings_sha256'][readme_key] = sha(BASE / 'README.md')
refreshed['metadata_refresh_R28S'] = {
    'scope': 'Only the mutable R28 README binding is refreshed. Original R27 geometry, native checks and historical R28A failure scope remain as recorded.',
    'previous_index': str(old27.relative_to(ROOT)),
    'previous_index_sha256': sha(old27),
    'previous_README': str(readme_snapshot.relative_to(ROOT)),
    'refresher_sha256': sha(Path(__file__)),
}
write(R27, refreshed)
assert refreshed['files_sha256'] == previous['files_sha256']

review = json.loads((S / 'saved-circuit-review.json').read_text())
assert review['components'] == 94 and review['pin_net_function_type_nodes'] == 338
assert review['all_source_components_and_nodes_equal'] and review['source_body_byte_identical']
for domain in ['body', 'flange']:
    d = review['domains'][domain]
    assert d['DRC'] == dict(drc_violations=0, unconnected_items=0, footprint_errors=0)
    assert sha(S / domain / (domain + '-r28.kicad_pcb')) == d['native_board_sha256']
    assert sha(S / domain / (domain + '-r28.kicad_pro')) == d['native_project_sha256']
    assert sha(S / domain / 'routed-native-drc.txt') == d['native_DRC_report_sha256']
assert sha(ROOT / 'hardware/bom.csv') == 'd5424d0536840bd3b555c439a129c0271b19b1cfbb3b94f1e1709e57cd63f05c'
assert sha(ROOT / 'tools/audit_circuit_r28.py') == review['auditor_sha256']
shutil.copyfile(Path(__file__), S / 'executed-tools/freeze_circuit_r28.py')
externals = [
    'hardware/bom.csv',
    'hardware/pcb/stackup-r23/artifact-index.json',
    'hardware/pcb/stackup-r23/candidate-d/system-native.xml',
    'hardware/pcb/stackup-r23/candidate-d/layout-inspection.json',
    'hardware/pcb/stackup-r23/candidate-d/body/body-r23.kicad_pcb',
    'hardware/pcb/stackup-r23/candidate-d/flange/flange-r23.kicad_pcb',
    'hardware/cad/flange-controls-r27/artifact-index.json',
    'hardware/cad/flange-controls-r27/candidate-d/FlangeCradleR27.FCStd',
    'hardware/cad/flange-controls-r27/candidate-d/saved-review.json',
    'developer-docs/docs/flange-routing-r28.md',
    'developer-docs/docs/assets/prototype-r2/flange-routing-r28-s.svg',
    'developer-docs/docs/assets/prototype-r2/flange-routing-r28-s.png',
    'developer-docs/docs/assets/prototype-r2/flange-routing-r28-s-source.json',
]
# Footprint libraries are repository-relative dependencies of all three projects.
for f in (ROOT / 'hardware/pcb/stackup-r23/candidate-d').rglob('*'):
    if f.is_file() and (f.suffix == '.kicad_mod' or f.name in ['fp-lib-table', 'sym-lib-table']):
        externals.append(str(f.relative_to(ROOT)))
files = {}
for f in sorted(BASE.rglob('*')):
    if not f.is_file() or f == BASE / 'artifact-index.json':
        continue
    if f.name == '.DS_Store' or f.suffix in ['.kicad_prl', '.lck', '.pyc'] or '__pycache__' in f.parts:
        continue
    files[str(f.relative_to(BASE))] = sha(f)
index = {
    'date': '2026-11-01',
    'state': 'R28S complete circuit review checkpoint; prototype build proposal unfinished',
    'current': 'candidate-s',
    'freezer_sha256': sha(Path(__file__)),
    'files_sha256': files,
    'external_bindings_sha256': {name: sha(ROOT / name) for name in sorted(set(externals))},
    'native_board_sha256': {k: review['domains'][k]['native_board_sha256'] for k in ['body', 'flange']},
    'native_DRC_counts': {k: review['domains'][k]['DRC'] for k in ['body', 'flange']},
    'history': 'A-R are placement, seed, failed/incomplete search or intermediate route stages. Only S is current. Partial search plans are not fabrication input. Original R28A and pre-refresh R27 indices are preserved in source-history.',
    'router_settings': 'Q log records invalid requested settings and fallback to defaults. Post-run defaults are retained accurately; no disabled-telemetry or applied requested-scoring claim.',
    'scope': 'Saved circuit/pad/net/rule/pose conservation and geometry checks only. No fresh GUI ERC, actual harness/flex/buttons, supplier CAM/stackup/impedance, RF/current/thermal/runtime or physical acceptance. Battery OPEN; human BOM unchanged.',
}
write(BASE / 'artifact-index.json', index)
verify(index, BASE)
print(f"R28S frozen: {len(files)} files / {len(index['external_bindings_sha256'])} external bindings; body/flange 0/0/0. Original R27 evidence preserved.")
