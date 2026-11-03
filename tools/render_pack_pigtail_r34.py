"""Source-bound body/neck pigtail figure from native context meshes."""
from pathlib import Path
import hashlib
import json
import sys
import numpy as np
from PIL import Image, ImageDraw, PngImagePlugin
import render_mechanical_r2 as draw

ROOT = Path(__file__).resolve().parents[1]
P = Path(sys.argv[1]).resolve()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
r = json.loads((P / 'geometry-report.json').read_text())
v = json.loads((P / 'saved-review.json').read_text())
assert sha(P / 'PackPigtailTransitR34.FCStd') == r['native_sha256'] == v['native_sha256']
assert r['all_transit_static_screens_clear'] and not v['unexpected_intersections']
meshes = draw.NativeMeshes(P)
meshes.expected = v['context_meshes_sha256']
rotation = np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]])
colors = [(205, 83, 64), (60, 113, 176), (91, 103, 120), (182, 140, 43), (145, 91, 164)]
def color(name):
    if name.startswith('PackPigtailWire') or name.startswith('PackBareLead'):
        return colors[int(name.rsplit('_', 1)[1].split('-')[0]) - 1]
    if name.startswith('BodyPCB'):
        return (75, 150, 104)
    if name.startswith('PackWireCarrier'):
        return (197, 205, 213)
    if name.startswith('PackTail'):
        return (119, 173, 178)
    return (170, 180, 192)
draw.part_color = color
panels = {}
for label in ['body', 'neck']:
    panels[label] = [(f.removesuffix('.stl'), meshes.load(f.removesuffix('.stl')) @ rotation.T, None)
                     for f in v['context_meshes_sha256'] if f.endswith('-' + label + '.stl')]
im = Image.new('RGB', (1800, 1130), 'white')
d = ImageDraw.Draw(im)
draw.label(d, (32, 25), 'A loose-end pigtail keeps the neck assembly simple', 35, True)
draw.label(d, (32, 80), 'R34J route + R35F native solder lands / rotated flange unchanged / motor stays coupled to the shell', 23, fill=draw.MUTED)
draw.panel(im, (25, 125, 860, 650), 'BODY BOARD / FIVE INDIVIDUAL WIRES',
           'Board, separate keeper and locally relieved carrier; component boxes omitted.',
           panels['body'], camera=(-1.9, -1.4, 2.0))
draw.panel(im, (915, 125, 860, 650), 'NECK / CROPPED NATIVE HUB CONTEXT',
           'Dedicated lower channel; battery-side ends remain unfinished.',
           panels['neck'], camera=(-.35, -.75, 2.4))
d = ImageDraw.Draw(im)
draw.label(d, (33, 810), 'Five functions: pack positive, power return, sensor return, charge NTC and independent guard NTC.', 23, True)
draw.label(d, (33, 855), '0.60 mm wire diameter allowance; R4 mm minimum centerline bends; solder/process fit remains to be tested.', 23)
draw.label(d, (33, 900), 'Fresh native review: 171 source roles conserved and 1,720 wire-to-fixed comparisons clear.', 23)
draw.label(d, (33, 945), 'Smallest coated-wire gap is 0.05 mm. That is a nominal geometry result, not a production tolerance.', 23, fill=draw.AMBER)
draw.label(d, (33, 990), 'The protected pack mate, full sensor leads, strain relief and connected loading still need finishing.', 23)
draw.label(d, (33, 1035), 'Semi-flex remains a saved alternative. Battery choice is OPEN; this is not the completed build package.', 23, fill=draw.MUTED)
meshes.verify()
meta = {'native_sha256': r['native_sha256'], 'geometry_report_sha256': sha(P / 'geometry-report.json'),
        'saved_review_sha256': sha(P / 'saved-review.json'), 'renderer_sha256': sha(Path(__file__)),
        'render_library_sha256': sha(ROOT / 'tools/render_mechanical_r2.py'),
        'mesh_sha256': meshes.used, 'display_transform': '(x,y,z)->(x,z,-y); no relative transforms',
        'scope': 'Actual native context clips. Component boxes and exterior omitted; wire swept allowances and bare-tail process envelopes only. Full harness and physical qualification unfinished.'}
out = ROOT / 'developer-docs/docs/assets/prototype-r2/pack-pigtail-r34-j.png'
png = PngImagePlugin.PngInfo()
png.add_text('SourceHashes', json.dumps(meta, sort_keys=True))
im.save(out, pnginfo=png)
out.with_name(out.stem + '-source.json').write_text(json.dumps(meta, indent=2) + '\n')
print(out, flush=True)
