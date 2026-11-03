"""Native rear/outward and inward views of the simple P1 charging cover."""
from pathlib import Path
import hashlib
import json
from PIL import Image, ImageDraw, PngImagePlugin
import render_mechanical_r2 as draw

ROOT = Path(__file__).resolve().parents[1]
CAD = ROOT / 'hardware/cad/prototype-p1'
OUT = ROOT / 'developer-docs/docs/assets/prototype-p1-cover.png'
r = json.loads((CAD / 'review.json').read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(CAD / 'PrototypeP1.FCStd') == r['native_sha256']
meshes = draw.NativeMeshes(CAD / 'display')
meshes.expected = {n + '.stl': h for n, h in r['meshes_sha256'].items()}


def color(name):
    if 'Contact' in name:
        return (215, 172, 71)
    if 'Magnet' in name:
        return (132, 119, 162)
    if 'Boot' in name:
        return (72, 133, 129)
    return (135, 164, 164)


draw.part_color = color
front_names = ['P1FlangeCover', 'P1GroundContact', 'P1PositiveContact',
               'ButtonBezelR31', 'ButtonBootR31']
back_names = ['P1FlangeCover', 'P1GroundContact', 'P1PositiveContact',
              'P1LeftMagnet', 'P1RightMagnet']
front = [(n, meshes.load(n), None) for n in front_names]
back = [(n, meshes.load(n), None) for n in back_names]
im = Image.new('RGB', (1800, 1010), 'white')
d = ImageDraw.Draw(im)
draw.label(d, (32, 24), 'Charging in the cover / no extra keeper screws', 35, True)
draw.label(d, (32, 78), 'Two flat contact references; magnets in blind pockets; rear bond/encapsulation process', 23,
           fill=draw.MUTED)
draw.panel(im, (25, 125, 850, 575), 'OUTWARD FACE',
           'Contacts are flush nominally. Silicone-covered buttons retained.',
           front, camera=(.1, -3., .45))
draw.panel(im, (925, 125, 850, 575), 'INSIDE THE SAME COVER',
           'Integral seats and repaired button supports; bond spaces omitted.',
           back, camera=(-.1, 3., .45))
d = ImageDraw.Draw(im)
draw.label(d, (35, 735), 'One connected cover replaces the old five-solid cover. The contacts move 2 mm left to clear the button bezel.', 23)
draw.label(d, (35, 780), 'Upper target: J1.1 / DOCK_5V. Lower target: J1.2 / GND. The metal body is not a charging conductor.', 23)
draw.label(d, (35, 825), 'Positive contact shoulders carry spring load; rear encapsulation retains/seals the tails and magnets.', 23)
draw.label(d, (35, 870), 'Native installed-part checks clear. Screw/pilot cylinders remain nominal unmodeled thread interfaces.', 22,
           fill=draw.MUTED)
draw.label(d, (35, 915), 'Actual contact fit, bond material, cure, magnetic holding and leakage/cleaning still need bench qualification.', 22,
           fill=draw.AMBER)
meshes.verify()
info = PngImagePlugin.PngInfo()
meta = {'native_sha256': r['native_sha256'], 'meshes_sha256': meshes.used,
        'cover_review': r['cover_integration'], 'renderer_sha256': sha(Path(__file__)),
        'scope': 'Native installed geometry, no exploded transforms. Nominal part references and process spaces are not physically validated.'}
info.add_text('Source', json.dumps(meta, sort_keys=True))
im.save(OUT, pnginfo=info)
OUT.with_suffix('.json').write_text(json.dumps(meta, indent=2) + '\n')
print(OUT)
