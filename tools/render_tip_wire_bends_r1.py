"""Editable SVG review of native-derived routing arithmetic, no CAD edits."""
from pathlib import Path
import hashlib
import json
from html import escape

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / 'hardware/design/tip-wire-bend-r1-references/native-bend-review.json'
OUT = ROOT / 'developer-docs/docs/assets/prototype-r2'
d = json.loads(REF.read_text())
critical = min(d['segments'], key=lambda s: s['uniform_radius_upper_bound_mm'])
assert critical['segment_index'] == 2
parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="900" viewBox="0 0 1400 900">',
         '<rect width="1400" height="900" fill="white"/>',
         '<style>text{font-family:Arial,sans-serif;fill:#24354b} .muted{fill:#61758c}</style>']
def text(x,y,t,size=24,weight='normal',color=None):
    parts.append(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}"'+(f' fill="{color}"' if color else '')+'>'+escape(t)+'</text>')
def line(a,b,color='#526f86',width=5):
    parts.append(f'<path d="M {a[0]:.3f} {a[1]:.3f} L {b[0]:.3f} {b[1]:.3f}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round"/>')
text(35,58,'Tip wire / bend space needs a new route',37,'bold')
text(36,102,'Read-only Full05 reservation review · existing wire example remains unselected',24)
for x in [30,715]:
    parts.append(f'<rect x="{x}" y="140" width="655" height="580" rx="18" fill="#f3f6fa" stroke="#cfdbe7"/>')
text(52,184,'SAVED FLANGE ROUTE',25,'bold')
text(52,220,'First five native vertices, projected in X/Y/Z',21)
def project(p):
    return 105+(p[0]+24)*20+(p[1]+15.5)*10, 615-p[2]*20-(p[1]+15.5)*5
points=[project(p) for p in d['points_xyz_mm'][:5]]
for i,(a,b) in enumerate(zip(points,points[1:])):
    line(a,b,'#bf4e38' if i==2 else '#526f86',8)
for i,(x,y) in enumerate(points):
    parts.append(f'<circle cx="{x:.3f}" cy="{y:.3f}" r="7" fill="#24354b"/>')
    text(x-(40 if i in [0,3] else 18),y-17,f'P{i}',19)
a,b=points[2],points[3];xx=a[0]+38
line((xx,a[1]),(xx,b[1]),'#bf4e38',2)
for yy in [a[1],b[1]]:line((xx-8,yy),(xx+8,yy),'#bf4e38',2)
text(xx+12,(a[1]+b[1])/2-3,'8.3 mm',24,'bold')
text(52,658,'Both ends of this leg turn through 90°.',22)
text(52,693,'Corner spheres reserve space; they are not wire bends.',21)
text(740,184,'FIXED-VERTEX CIRCULAR FILLETS',25,'bold')
text(740,232,'Explicit 10× OD centerline scenario',22)
rows=[('Available straight leg','8.300 mm'),
      ('Needed at example’s minimum OD',f"{critical['required_setback_sum_at_OD_min_max_mm'][0]:.3f} mm"),
      ('Needed at example’s maximum OD',f"{critical['required_setback_sum_at_OD_min_max_mm'][1]:.3f} mm"),
      ('Largest uniform fillet radius here',f"{d['maximum_uniform_fillet_radius_with_fixed_vertices_mm']:.3f} mm")]
for i,(label,value)in enumerate(rows):
    y=294+i*81
    text(740,y,label,21)
    text(740,y+34,value,29,'bold')
text(740,663,'All three radius interpretations fail at minimum OD.',21,'bold')
text(740,696,'This does not rule out a different smooth route.',21)
text(35,765,'Next: route actual individual wires with bends, fanouts, slack and strain relief; recheck neighboring parts.',23,'bold')
text(35,808,f"Current polyline length: {d['polyline_center_length_mm']:.3f} mm. This is not an accepted cut length or a lower bound.",22)
text(35,847,'Center / inside / outside radius interpretations screened separately; four-wire routing remains open.',21)
text(35,881,'No CAD recompute/save, wire selection, crimp/current qualification or physical fit result.',21)
parts.append('</svg>')
OUT.mkdir(parents=True,exist_ok=True)
target=OUT/'tip-wire-bend-r1.svg';target.write_text('\n'.join(parts)+'\n')
meta={'native_sha256':d['inputs_sha256']['hardware/cad/prototype-r2/full-05/ButtplugPrototypeR2Full05.FCStd'],
      'review_sha256':hashlib.sha256(REF.read_bytes()).hexdigest(),
      'renderer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
      'svg_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
      'scope':'Actual saved points projected; arithmetic-only annotations. Not a smooth route or manufactured wire.'}
(OUT/'tip-wire-bend-r1-source.json').write_text(json.dumps(meta,indent=2)+'\n')
print(target)
