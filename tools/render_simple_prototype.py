"""Readable exterior and cutaway of the source-bound P1 review assembly."""
from pathlib import Path
import hashlib
import json
import numpy as np
from PIL import Image, ImageDraw, PngImagePlugin
import render_mechanical_r2 as draw

ROOT = Path(__file__).resolve().parents[1]
CAD = ROOT / 'hardware/cad/prototype-p1'
OUT = ROOT / 'developer-docs/docs/assets/prototype-p1.png'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
r = json.loads((CAD / 'review.json').read_text())
assert sha(CAD / 'PrototypeP1.FCStd') == r['native_sha256']
meshes = draw.NativeMeshes(CAD / 'display')
meshes.expected = {n + '.stl': h for n, h in r['meshes_sha256'].items()}
meshes.expected.update({n + '-half.stl': h
                       for n, h in r['native_half_sections_sha256'].items()})


def colour(name):
    if name.startswith(('FlangeCover', 'ButtonServiceCover', 'ButtonBoot', 'P1FlangeCover')):
        return (48, 111, 110)
    if name in ('KeyedBodyR25', 'MotorSeatCapR25'):
        return (197, 207, 214)
    group = r['roles'][name]['group']
    return {'Electronics': (52, 143, 91), 'BatteryReference': (69, 149, 190),
            'Motor': (215, 157, 67), 'Controls': (103, 130, 147),
            'Supports': (175, 176, 164),
            'WiringAndProcessAllowances': (184, 122, 62),
            'FastenerAllowances': (101, 110, 120),
            'Charging': (205, 166, 73)}.get(group, (130, 140, 150))


draw.part_color = colour
outside = []
inside = []
exterior = ['KeyedBodyR25', 'MotorSeatCapR25', 'FlangeCoverLower',
            'FlangeCoverUpper', 'P1FlangeCover', 'ButtonBezelR31',
            'ButtonBootR31', 'P1GroundContact', 'P1PositiveContact']
for name in exterior:
    outside.append((name, meshes.load(name), None))
for name, q in r['roles'].items():
    group = q['group']
    if name in ('KeyedBodyR25', 'MotorSeatCapR25', 'FlangeCoverLower'):
        # Native half sections use an explicit suffix rather than the shared
        # renderer's legacy '-section' convention.
        inside.append((name, meshes.load(name + '-half'), None))
    elif group in ('Electronics', 'Motor', 'BatteryReference'):
        if not name.startswith('R17Mate_'):
            inside.append((name, meshes.load(name), None))
    elif group == 'Supports' and name not in ('PackLidR33',):
        inside.append((name, meshes.load(name), None))
    elif group == 'WiringAndProcessAllowances':
        # Jackets only; bare-core and overlapping process/solder budgets are
        # kept in native CAD and deliberately omitted from the overview.
        if name.startswith(('InterboardWireR29_', 'TipWireR26_',
                            'BodyPackPowerWireR37_', 'PackConnectedWireR36_',
                            'FactoryNTCWireR36_', 'StockPackLeadR37_',
                            'SpareMateLeadR37_', 'PackMateProcessSpaceR37', 'P1MotorWire')):
            inside.append((name, meshes.load(name), None))

im = Image.new('RGB', (1800, 1180), 'white')
d = ImageDraw.Draw(im)
draw.label(d, (32, 24), 'P1 / bring it back to the product', 36, True)
draw.label(d, (32, 80), 'One-piece metal body + front cap / 15 mm neck / independent motor / flexible wiring', 24,
           fill=draw.MUTED)
draw.panel(im, (25, 128, 825, 770), 'EXTERIOR',
           'Existing body and flange contours retained.', outside,
           camera=(.40, .18, 2.5))
draw.panel(im, (900, 128, 875, 770), 'INSIDE / NATIVE HALF SECTION',
           'Front skin, service cover and pack lid omitted.', inside,
           camera=(.40, .18, 2.5))
d = ImageDraw.Draw(im)
draw.label(d, (40, 925), 'Silver: body + cap     Gold: shell-coupled motor     Green: boards     Blue: battery size reference', 23)
draw.label(d, (40, 970), 'Assembly: body electronics → rear hub + flange boards → hand-dress wires → motor + tip → cap + cover', 23)
draw.label(d, (40, 1015), 'No separate joint comb, return plug or connector cage. Insulate joints; tack jackets in accessible recesses.', 23)
draw.label(d, (40, 1060), 'Battery open. Integral contact seats and motor leads added; dock wiring, connected loading and seals remain.', 22,
           fill=draw.AMBER)
draw.label(d, (40, 1105), 'Native CAD overview; component boxes and wire paths are space allowances. No physical fit or wear result.', 22,
           fill=draw.MUTED)
meshes.verify()
meta = {'native_sha256': r['native_sha256'], 'meshes_sha256': meshes.used,
        'renderer_sha256': sha(Path(__file__)), 'section': 'Native Z <= 0 solids',
        'omissions': 'Front skins, service cover/contacts/magnets, pack lid, most fasteners, mates and overlapping process/core budgets omitted from interior view.'}
info = PngImagePlugin.PngInfo()
info.add_text('Source', json.dumps(meta, sort_keys=True))
OUT.parent.mkdir(parents=True, exist_ok=True)
im.save(OUT, pnginfo=info)
OUT.with_suffix('.json').write_text(json.dumps(meta, indent=2) + '\n')
print(OUT)
