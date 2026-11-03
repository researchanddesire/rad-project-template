"""Show the matching cable and installed dock wires from native P1 meshes."""
from pathlib import Path
import hashlib
import json
from PIL import Image, ImageDraw, PngImagePlugin
import render_mechanical_r2 as draw

ROOT = Path(__file__).resolve().parents[1]
CAD = ROOT / 'hardware/cad/prototype-p1'
OUT = ROOT / 'developer-docs/docs/assets/prototype-p1-charging.png'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
product = json.loads((CAD / 'review.json').read_text())
cable = json.loads((CAD / 'charging-cable/review.json').read_text())
assert sha(CAD / 'PrototypeP1.FCStd') == product['native_sha256']
assert sha(CAD / 'charging-cable/P1ChargingCable.FCStd') == cable['native_sha256']
assert cable['product_native_sha256'] == product['native_sha256']
meshes = draw.NativeMeshes(CAD / 'display')
meshes.expected = {n+'.stl': h for n, h in product['meshes_sha256'].items()}
case_meshes = draw.NativeMeshes(Path(cable['mesh_cache']))
case_meshes.expected = {n+'.stl': q['mesh_sha256'] for n, q in cable['parts'].items()}


def color(name):
    if name == 'P1DockWire1':
        return (205, 76, 63)
    if name == 'P1DockWire2':
        return (62, 66, 72)
    if 'Contact' in name or 'Spring' in name or 'Plunger' in name:
        return (211, 166, 58)
    if 'Magnet' in name:
        return (141, 120, 168)
    if name == 'PackMateProcessSpaceR37':
        return (190, 179, 166)
    if name == 'FlangePCB_R17':
        return (62, 137, 94)
    if name.startswith('R17'):
        return (93, 104, 112)
    if name == 'P1CableHousing':
        return (133, 177, 193)
    return (117, 154, 151)


draw.part_color = color
assembled = [(n, meshes.load(n), None) for n in
             ('P1FlangeCover', 'P1GroundContact', 'P1PositiveContact',
              'ButtonBezelR31', 'ButtonBootR31')]
assembled += [(n, case_meshes.load(n), None) for n in cable['parts']]
wiring_names = ['FlangePCB_R17', 'R17_U6', 'R17_J1', 'R17Mate_J1',
                'R17_J4', 'P1PackMateSpace', 'P1DockWire1',
                'P1DockWire2', 'P1GroundContact', 'P1PositiveContact']
wiring = [(n, meshes.load(n), None) for n in wiring_names]
im = Image.new('RGB', (1800, 1020), 'white')
d = ImageDraw.Draw(im)
draw.label(d, (32, 24), 'P1 charging / one housing, hand-dressed wires', 35, True)
draw.label(d, (32, 77), 'Native CAD; contacts and wires shown in the installed toy coordinates', 23, fill=draw.MUTED)
draw.panel(im, (25, 125, 850, 590), 'MATCHING EXTERNAL CABLE',
           'One insulating housing, two spring contacts and two magnets.',
           assembled, camera=(.55, -3., .55))
draw.panel(im, (925, 125, 850, 590), 'INTERNAL WIRES / COVER AND SKINS HIDDEN',
           'Red: J1.1 to upper target. Dark: J1.2 to lower target.',
           wiring, camera=(-.25, -3., .25))
d = ImageDraw.Draw(im)
draw.label(d, (35, 750), 'No new internal retainer, screw or PCB change. Both wires pass behind the radio to the contact tails.', 23)
draw.label(d, (35, 797), 'Nominal OD0.60 routes: 56.35 mm positive / 49.35 mm ground; not finished cut or strip dimensions.', 23)
draw.label(d, (35, 844), 'Equal-length wire shapes clear at 0, 1, 2 and 3 mm cover opening; real wire motion still needs a dry trial.', 23)
draw.label(d, (35, 891), 'First bend radius 2.0 mm; other bends 1.5 mm; pack-mate gap about 0.51 mm. Confirm the actual lead.', 22, fill=draw.AMBER)
draw.label(d, (35, 938), 'Candidate geometry only. Bonding, magnetic holding, strain relief, electrical commissioning and seals remain unqualified.', 21, fill=draw.MUTED)
meshes.verify()
case_meshes.verify()
meta = {'product_native_sha256': product['native_sha256'],
        'cable_native_sha256': cable['native_sha256'], 'renderer_sha256': sha(Path(__file__)),
        'product_meshes_sha256': meshes.used, 'cable_meshes_sha256': case_meshes.used,
        'scope': 'Native installed meshes. Right panel hides cover/skins/supports to expose the two conditional wire routes. No physical fit/holding/sealing result.'}
info = PngImagePlugin.PngInfo()
info.add_text('Source', json.dumps(meta, sort_keys=True))
im.save(OUT, pnginfo=info)
OUT.with_suffix('.json').write_text(json.dumps(meta, indent=2)+'\n')
print(OUT)
