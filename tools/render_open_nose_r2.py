"""Explain the open-ended shell using source-hashed native mesh exports."""
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw, PngImagePlugin
from render_mechanical_r2 import NativeMeshes, panel, label, INK, MUTED, AMBER

ROOT = Path(__file__).resolve().parents[1]
CAD = ROOT/'hardware/cad/prototype-r2'
OUT = ROOT/'developer-docs/docs/assets/prototype-r2'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
report_path = CAD/'open-mouth-evidence.json'
report = json.loads(report_path.read_text())
native = CAD/'ButtplugPrototypeR2.FCStd'
assert sha(native) == report['native_sha256']
full = json.loads((CAD/'geometry-report.json').read_text())
assert sha(CAD/'geometry-report.json') == report['geometry_report_sha256']
assert report['central_open_path']['shell_intersection_volume_mm3'] == 0
extra = NativeMeshes(CAD/'open-mouth-evidence')
extra.expected = {name+'.stl': e['stl_sha256'] for name,e in report['exports'].items()}
main = NativeMeshes(CAD, report=full)
tube = extra.load('OpenPipeShellNoseSegment')
support = extra.load('InternalMotorSupportNoseSegment')
ring = extra.load('InternalMotorLinerCapsTapeSegment')
cap = main.load('FemaleNoseCap')
cap_display = cap.copy()
cap_display[:, :, 1] += 18

im = Image.new('RGB', (1800, 1150), 'white')
d = ImageDraw.Draw(im)
label(d, (36, 25), 'Open-ended shell / closing nose cap', 38, True)
label(d, (37, 85), 'Actual full-02 native geometry · the green ring is an internal motor retainer', 24, fill=MUTED)
panel(im, (30, 145, 855, 755), 'OPEN MOUTH / cap and contents removed',
      'Two shell halves · Ø21 mm nose bore',
      [('MetalShellLower', tube, None)], camera=(.45, 1.25, .65))
panel(im, (915, 145, 855, 755), 'CAP / sole external nose closure',
      'Cap raised 18 mm for illustration; supports remain fixed',
      [('MetalShellLower', tube, None), ('RemovableMotorTipCarrier', support, None),
       ('MotorLiners', ring, None), ('FemaleNoseCap', cap_display, None)],
      camera=(.75, .20, 1.5))
d = ImageDraw.Draw(im)
label(d, (37, 936), 'The cap closes the open tube and retains the front. The neck stays Ø15 mm.', 27, True)
label(d, (37, 988), 'Green: separate motor caps / liners / tape. These retain the motor inside the open tube.', 24, fill=MUTED)
label(d, (37, 1040), 'Clipped native nose segments shown. Display offsets do not prove an assembly path.', 23, fill=MUTED)
label(d, (37, 1090), 'Thread fit, continuous seals and physical assembly remain unqualified.', 23, True, fill=AMBER)
extra.verify()
main.verify()
assert sha(native) == report['native_sha256']
metadata = {'native_sha256': sha(native), 'open_mouth_evidence_sha256': sha(report_path),
            'geometry_report_sha256': sha(CAD/'geometry-report.json'),
            'renderer_sha256': sha(Path(__file__)),
            'mesh_sha256': {'open-mouth-evidence/'+k: v for k,v in extra.used.items()} | main.used,
            'cap_display_translation_xyz_mm': [0, 18, 0]}
png = PngImagePlugin.PngInfo()
png.add_text('SourceHashes', json.dumps(metadata, sort_keys=True))
png.add_text('Scope', 'Actual owner-exported clipped native geometry. Cap display offset only. No physical, continuous-motion, seal or thread-strength result.')
target = OUT/'open-nose-r2.png'
im.save(target, pnginfo=png)
(OUT/'open-nose-r2-source.json').write_text(json.dumps(metadata, indent=2)+'\n')
print(target)
