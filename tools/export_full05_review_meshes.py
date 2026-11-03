"""Read-only saved-world mesh/section export for the Full05 review figure."""
from pathlib import Path
import argparse, hashlib, json, re, sys
sys.path.insert(0, '/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as App
import Part, Mesh

root = Path(__file__).resolve().parents[1]
cad = root/'hardware/cad/prototype-r2/full-05'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--expected-sha', required=True)
args = parser.parse_args()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
native = cad/'ButtplugPrototypeR2Full05.FCStd'
rp = cad/'geometry-report.json'
report = json.loads(rp.read_text())
assert sha(native) == args.expected_sha == report['native_sha256']
assert len(report['parts']) == 103 and not report['unintended_intersections']
before = sha(rp)
out = cad/'review-meshes'
out.mkdir(exist_ok=True)
doc = App.openDocument(str(native))
sections = {'NewMetalLower', 'FemaleNoseCap', 'Full04PolymerFlangeCore',
            'MotorNut1ForwardPortApplied'}
clip = Part.makeBox(200, 250, 100, App.Vector(-100, -100, -100))
records = {}
for name, expected in report['parts'].items():
    assert re.fullmatch(r'[A-Za-z0-9_]+', name)
    shape = doc.getObject(name).Shape
    assert not shape.isNull() and shape.isValid()
    assert abs(shape.Volume-expected['volume_mm3']) < 1e-4
    entry = {'native_role': name, 'volume_mm3': shape.Volume}
    targets = [(name+'.stl', shape)]
    if name in sections:
        section = shape.common(clip)
        assert not section.isNull() and section.isValid() and section.Volume > 1e-8
        entry['section_volume_mm3'] = section.Volume
        targets.append((name+'-section.stl', section))
    entry['exports'] = {}
    for filename, value in targets:
        target = out/filename
        Mesh.Mesh(value.tessellate(.18)).write(str(target))
        entry['exports'][filename] = sha(target)
    records[name] = entry
App.closeDocument(doc.Name)
assert sha(native) == args.expected_sha and sha(rp) == before
index = {'native_sha256': args.expected_sha, 'geometry_report_sha256': before,
         'exporter_sha256': sha(Path(__file__)), 'roles': records,
         'scope': 'Actual saved world Shapes, tessellation0.18mm; four exact native negative-Z sections. No native save, triangle clipping, inferred clearances or physical acceptance.'}
(out/'mesh-index.json').write_text(json.dumps(index, indent=2)+'\n')
print(json.dumps({'roles': len(records), 'mesh_files': sum(len(x['exports']) for x in records.values())}))
