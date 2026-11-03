"""Source-bound native overview of the printable P1 dry-fit kit."""
from pathlib import Path
import hashlib
import json
import sys
from PIL import Image, ImageDraw, PngImagePlugin
import render_mechanical_r2 as draw

ROOT = Path(__file__).resolve().parents[1]
folder = Path(sys.argv[1]).resolve()
out = ROOT / 'developer-docs/docs/assets/prototype-p1-dry-fit.png'
r = json.loads((folder / 'kit-manifest.json').read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(folder / 'P1DryFitKit.FCStd') == r['native_sha256']
meshes = draw.NativeMeshes(folder / 'view-meshes')
meshes.expected = {n+'.stl': h for n, h in r['view_meshes_sha256'].items()}


def color(name):
    if name == 'P1DockWire1':
        return (207, 76, 63)
    if name == 'P1DockWire2':
        return (57, 65, 71)
    if name.startswith('P1Pack'):
        return (186, 130, 63)
    if 'Gauge' in name:
        return (88, 155, 194)
    if name.startswith(('Body-half', 'Body', 'NoseCap', 'MotorMount')) and 'Carrier' not in name and 'Keeper' not in name:
        return (187, 195, 201)
    return (107, 155, 146)


draw.part_color = color
def geometry(names):
    return [(n, meshes.load(n), None) for n in names]

outside = geometry(['Body', 'NoseCap', 'LowerFlangeSkin', 'UpperFlangeSkin', 'ChargingCover'])
inside = geometry(['Body-half', 'NoseCap-half', 'LowerFlangeSkin-half', 'BodyCarrier',
                   'BodyBoardKeeper', 'BodyBoardGauge', 'MotorMount', 'MotorGauge',
                   'TipCarrier', 'TipBoardGauge', 'LeftHub', 'RightHub', 'FlangeBoardGauge',
                   'BatteryGauge', 'PackConnectorGauge', 'P1DockWire1', 'P1DockWire2'])
close = geometry(['FlangeBoardGauge', 'PlugGauge_J1', 'PackConnectorGauge',
                  'P1DockWire1', 'P1DockWire2', 'P1PackMateWire1', 'P1PackMateWire2'])
im = Image.new('RGB', (1860, 1070), 'white')
d = ImageDraw.Draw(im)
draw.label(d, (32, 23), 'P1 / one dry-fit kit, with removable gauges', 35, True)
draw.label(d, (32, 77), 'Native geometry; separate body/flange boards; independent motor mount; battery choice open', 23, fill=draw.MUTED)
draw.panel(im, (20, 125, 600, 680), 'OUTER FIT PARTS',
           'Rigid shape trial; silicone and buttons not fitted.',
           outside, camera=(1., -.6, 1.4))
draw.panel(im, (630, 125, 600, 680), 'INSIDE / REAL NATIVE HALF SECTIONS',
           'Blue parts are board, pack and motor gauges.',
           inside, camera=(1.2, -.55, 1.4))
draw.panel(im, (1240, 125, 600, 680), 'FLANGE WIRING / COVER HIDDEN',
           'Red = dock5V; dark = ground; gold = pack leads.',
           close, camera=(.15, -3., .45))
d = ImageDraw.Draw(im)
draw.label(d, (35, 845), 'Charging wires: first bend radius 2.0 mm; about 0.51 mm nominal clearance to the repositioned pack-mate allowance.', 22)
draw.label(d, (35, 891), 'No added product keeper or fastener. Board gauges load unplugged; removable plug gauges attach afterwards.', 22)
draw.label(d, (35, 937), 'The kit includes 26 closed STL files (27 printed pieces), native CAD, quantities and a complete assembly/service worksheet.', 22)
draw.label(d, (35, 986), 'Unpowered bench fit only. Actual wire/connector fit, materials, seals, electronics and wear remain unvalidated.', 21, fill=draw.AMBER)
meshes.verify()
meta = {'native_kit_sha256': r['native_sha256'], 'source_assembly_sha256': r['source_assembly_sha256'],
        'renderer_sha256': sha(Path(__file__)), 'meshes_sha256': meshes.used,
        'scope': 'Actual native kit meshes and half sections; no exploded transforms or functional/physical acceptance.'}
info = PngImagePlugin.PngInfo()
info.add_text('Source', json.dumps(meta, sort_keys=True))
im.save(out, pnginfo=info)
out.with_suffix('.json').write_text(json.dumps(meta, indent=2)+'\n')
print(out)
