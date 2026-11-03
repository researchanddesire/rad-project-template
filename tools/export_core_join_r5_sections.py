"""Read-only exact source sections for the R5 nut/keeper loading illustration."""
from pathlib import Path
import sys, json, hashlib
sys.path.insert(0, '/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as App
import Part

ROOT = Path(__file__).resolve().parents[1]
F = ROOT / 'hardware/cad/core-join-r5'
OUT = ROOT / 'developer-docs/docs/assets/prototype-r2/core-join-r5-sections.json'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
r = json.loads((F / 'geometry-report.json').read_text())
native = F / 'CoreJoinR5.FCStd'
assert sha(native) == r['native_sha256'] == '717b9dc44a12811551cdfaf0d898bf250fe083bd10cd35626a448a7515e0f0bf'
doc = App.openDocument(str(native))
core = 'R5WithR4PortCut1'
views = []
for title, dy, dz, bolt in [('Pair approaches from +Y', 4, .2, False),
                             ('At port, still lifted', 0, .2, False),
                             ('Seated; bolt after closure', 0, 0, True)]:
    parts = []
    for name in [core, 'R5_NutKeeper0', 'CoreJoinNut0'] + (['R5_CoreJoinBolt0'] if bolt else []):
        shape = doc.getObject(name).Shape.copy()
        if name in ['R5_NutKeeper0', 'CoreJoinNut0']:
            shape.translate(App.Vector(0, dy, dz))
        paths = []
        for wire in shape.slice(App.Vector(1, 0, 0), -25):
            for edge in wire.Edges:
                pts = edge.discretize(Deflection=.005)
                paths.append([[p.y, p.z] for p in pts])
        parts.append({'name': name, 'paths': paths})
    views.append({'title': title, 'pair_offset_YZ_mm': [dy, dz], 'parts': parts})
out = {'native_sha256': sha(native), 'geometry_report_sha256': sha(F / 'geometry-report.json'),
       'exporter_sha256': sha(Path(__file__)), 'plane': 'X=-25 mm, plotted Y/Z',
       'scope': 'Exact native section curves. First two are rigid pair poses from the checked finite sequence. Final bolt shown only after upper-core closure; keeper screw is outside this section. View is cropped to seat detail, not whole assembly.',
       'views': views}
assert sha(native) == r['native_sha256']
OUT.write_text(json.dumps(out, indent=2) + '\n')
App.closeDocument(doc.Name)
print(OUT)
