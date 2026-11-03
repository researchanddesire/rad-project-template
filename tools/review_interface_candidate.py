"""Independent read-only saved-history review of a standalone interface study.

No assembly-motion, tolerance, exchange-precision or physical acceptance.
The source report specifies which final roles are reviewed. All stored native
objects are touched, so the comparison exercises saved feature dependencies.
"""
from pathlib import Path
import argparse
import hashlib
import json
import sys

sys.path.insert(0, '/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as App
import Part

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('directory', type=Path)
parser.add_argument('--native', required=True)
parser.add_argument('--step', required=True)
parser.add_argument('--expected-sha', required=True)
parser.add_argument('--expected-step-solids', required=True, type=int)
args = parser.parse_args()
folder = args.directory.resolve()
native = folder / args.native
stepfile = folder / args.step
reportfile = folder / 'geometry-report.json'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
r = json.loads(reportfile.read_text())
native_sha, report_sha, step_sha = sha(native), sha(reportfile), sha(stepfile)
assert native_sha == args.expected_sha == r['native_sha256']
for key in ['step_sha256', 'STEP_sha256', 'combined_step_sha256']:
    if key in r:
        assert r[key] == step_sha
doc = App.openDocument(str(native))
for obj in doc.Objects:
    obj.touch()
doc.recompute()
rows = {}
for name, expected in r['parts'].items():
    obj = doc.getObject(name)
    assert obj is not None, name
    shape = obj.Shape
    b = shape.BoundBox
    bounds = [b.XMin, b.YMin, b.ZMin, b.XMax, b.YMax, b.ZMax]
    delta = max(abs(a - b) for a, b in zip(bounds, expected['bounds_xyz_mm']))
    vdelta = shape.Volume - expected['volume_mm3']
    assert shape.isValid() and len(shape.Solids) == expected['solids'], name
    assert abs(vdelta) < 1e-4 and delta < 1e-5, (name, vdelta, delta)
    rows[name] = {'valid': True, 'solids': len(shape.Solids),
                  'volume_difference_mm3': vdelta,
                  'maximum_bounds_difference_mm': delta}
step = Part.Shape()
step.read(str(stepfile))
assert step.isValid() and all(s.isValid() for s in step.Solids)
assert len(step.Solids) == args.expected_step_solids
App.closeDocument(doc.Name)
assert sha(native) == native_sha and sha(reportfile) == report_sha and sha(stepfile) == step_sha
out = {
    'status': 'PASS_saved_history_and_STEP_validity_only',
    'native_sha256': native_sha, 'geometry_report_sha256': report_sha,
    'STEP_sha256': step_sha, 'reviewer_sha256': sha(Path(__file__)),
    'method': 'Reopen saved native, touch every object, recompute full saved history without saving. Compare listed final roles to saved report. STEP reopen validity/count only.',
    'parts': rows, 'STEP_valid': True, 'STEP_solids': len(step.Solids),
    'scope': 'No generator replay, continuous loading, classification acceptance, operating controls, geometry exchange precision, tolerances, strength, materials, wire bending, electrical or physical release.',
}
(folder / 'root-independent-native-review.json').write_text(json.dumps(out, indent=2) + '\n')
print(json.dumps({k: v for k, v in out.items() if k != 'parts'}, indent=2))
