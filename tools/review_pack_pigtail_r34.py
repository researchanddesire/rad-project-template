"""Fresh native pigtail/source conservation and context meshes; no fabrication claim."""
from pathlib import Path
import hashlib
import json
import sys
sys.path.insert(0, '/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part
import MeshPart

ROOT = Path(__file__).resolve().parents[1]
P = Path(sys.argv[1]).resolve()
SOURCE = ROOT / 'hardware/cad/pack-harness-r34/passage-c'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
report = json.loads((P / 'geometry-report.json').read_text())
path = P / 'PackPigtailTransitR34.FCStd'
before = sha(path)
assert before == report['native_sha256']
source_path = SOURCE / 'PackTailPassageR34.FCStd'
source_hash = sha(source_path)
assert source_hash == report['source_passage_trial_native_sha256']
D = A.openDocument(str(path))
S = A.openDocument(str(source_path))
for obj in D.Objects:
    if hasattr(obj, 'Shape'):
        obj.touch()
D.recompute()
conserved = []
for name in report['fixed_roles']:
    obj = D.getObject(name)
    assert obj and obj.Shape.isValid() and obj.Shape.Volume > 0, name
    if name == 'PackWireCarrierR34':
        continue
    old = S.getObject(name)
    assert old and old.Shape.isValid(), name
    a, b = obj.Shape.copy(), old.Shape.copy()
    assert len(a.Solids) == len(b.Solids), name
    assert abs(a.Volume - b.Volume) < 1e-4, name
    removed = b.copy().cut(a.copy()).Volume
    added = a.copy().cut(b.copy()).Volume
    assert abs(removed) < 1e-4 and abs(added) < 1e-4, (name, removed, added)
    conserved.append(name)
    if len(conserved) % 25 == 0:
        print('source roles conserved', len(conserved), flush=True)

new = {}
for plan in report['wire_plan']:
    i = plan['wire_index']
    for prefix in ['PackPigtailWireR34_', 'PackBareLeadR34_']:
        name = prefix + str(i)
        shape = D.getObject(name).Shape.copy()
        assert shape.isValid() and len(shape.Solids) == 1, name
        new[name] = shape
    path_shape = D.getObject('PackWirePathR34_' + str(i)).Shape
    assert abs(path_shape.Length - plan['exact_path_length_mm']) < 1e-5

hits = []
for name, shape in new.items():
    for fixed in report['fixed_roles']:
        other = D.getObject(fixed).Shape.copy()
        a, b = shape.BoundBox, other.BoundBox
        if any(min(getattr(a, k + 'Max'), getattr(b, k + 'Max')) <=
               max(getattr(a, k + 'Min'), getattr(b, k + 'Min')) + 1e-7 for k in 'XYZ'):
            continue
        v = shape.copy().common(other).Volume
        if v > 1e-5:
            hits.append({'wire': name, 'fixed': fixed, 'volume_mm3': v})
assert not hits, hits

meshes = {}
body_clip = Part.makeBox(40, 33, 16, A.Vector(-20, 24, -8))
neck_clip = Part.makeBox(30, 44, 12, A.Vector(-15, -20, -8))
contexts = {
    'body': ['BodyPCB_R17', 'PCBOnlyKeeperR25', 'PackWireCarrierR34'] + list(new),
    'neck': ['PackTailLeftHubR34', 'PackTailRightHubR34', 'BodyPCB_R17'] + list(new),
}
for label, names in contexts.items():
    clip = body_clip if label == 'body' else neck_clip
    for name in names:
        shape = D.getObject(name).Shape.copy().common(clip.copy())
        if shape.Volume < 1e-7:
            continue
        assert shape.isValid(), name
        out = P / (name + '-' + label + '.stl')
        MeshPart.meshFromShape(Shape=shape, LinearDeflection=.025,
                               AngularDeflection=.10, Relative=False).write(str(out))
        meshes[out.name] = sha(out)
A.closeDocument(D.Name)
A.closeDocument(S.Name)
assert sha(path) == before and sha(source_path) == source_hash
result = {'native_sha256': before, 'source_sha256': source_hash,
          'reviewer_sha256': sha(Path(__file__)),
          'conserved_fixed_roles': conserved, 'conserved_fixed_role_count': len(conserved),
          'changed_carrier': report['changed_carrier'],
          'fresh_new_to_fixed_comparisons': len(new) * len(report['fixed_roles']),
          'unexpected_intersections': hits,
          'all_reported_native_wire_lengths_equal': True,
          'context_meshes_sha256': meshes,
          'body_clip_xyz_mm': [-20, 24, -8, 20, 57, 8],
          'neck_clip_xyz_mm': [-15, -20, -8, 15, 24, 4],
          'scope': 'Fresh recompute, exact native source material comparison, wire/path validity and finite installed intersections. Source header/mate intentionally absent for native R35 solder-land variant. No complete pack/sensor harness, solder joint, strain relief, connected assembly, fatigue/current/thermal or physical acceptance.'}
(P / 'saved-review.json').write_text(json.dumps(result, indent=2) + '\n')
print('Fresh pigtail review:', len(conserved), 'source roles conserved;', len(new) * len(report['fixed_roles']), 'static comparisons clear.', flush=True)
