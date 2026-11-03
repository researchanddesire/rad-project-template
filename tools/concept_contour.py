"""Render the non-dimensional Concept 03 contour study; this is not a CAD solid."""
from pathlib import Path
import html
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'hardware/cad/concepts/contour-v3.json'
OUTPUT = SOURCE.with_suffix('.svg')
ASSETS = ROOT / 'developer-docs/docs/assets/concept-v3'
data = json.loads(SOURCE.read_text())
INK, MUTED, GREEN, BLUE, AMBER = '#243449', '#5a6b7d', '#27745f', '#35679d', '#975d15'
bits = [
    '<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1136" viewBox="0 0 1600 1136">',
    '<title>Concept 03 — pelvic contour and tailbone relief study</title>',
    '<desc>Non-dimensional side and rear contour intentions, not a 3D anatomical fit model. '
    'Awake wear with breaks is the primary use goal. Continuous and sleep wear remain unvalidated.</desc>',
    '<defs><marker id="arrow" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto-start-reverse">'
    '<path d="M0 0 L7 3.5 L0 7" fill="#5a6b7d"/></marker></defs>',
    '<rect width="1600" height="1136" fill="#ffffff"/>'
]


def text(x, y, value, size=19, color=INK, weight='normal', anchor='start'):
    for i, line in enumerate(value.split('\n')):
        bits.append(f'<text x="{x}" y="{y+i*size*1.38}" font-family="Arial, sans-serif" '
                    f'font-size="{size}" fill="{color}" font-weight="{weight}" '
                    f'text-anchor="{anchor}">{html.escape(line)}</text>')


def rect(x, y, w, h, fill='#f7f9fb', stroke='#dce4ec', radius=18):
    bits.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" '
                f'fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')


def line(points, color=MUTED, dash=False, arrow=False, both=False):
    bits.append('<polyline points="' + ' '.join(f'{x},{y}' for x, y in points) +
                f'" fill="none" stroke="{color}" stroke-width="1.8" stroke-linejoin="round"' +
                (' stroke-dasharray="6 5"' if dash else '') +
                (' marker-end="url(#arrow)"' if arrow else '') +
                (' marker-start="url(#arrow)"' if both else '') + '/>')


def shape(key, x, y, scale):
    path = data['geometry'][key]['path']
    if not path.startswith('M ') or not path.endswith(' Z'):
        raise ValueError(f'{key}: expected a closed illustration path')
    bits.append(f'<path id="{key}-contour" d="{html.escape(path, quote=True)}" '
                f'transform="translate({x} {y}) scale({scale})" '
                'fill="#d9eee6" stroke="#27745f" stroke-width="2.3" '
                'stroke-linejoin="round"/>')


text(40, 54, 'Concept 03 / let the body contour lead', 36, weight='bold')
text(42, 92, 'Pelvic fit study: a low-profile base along the cleft, with clearance at the tailbone and perineum.', 22, MUTED)
text(42, 131, 'PRIMARY: awake wear with removal breaks     •     CONTINUOUS / SLEEP WEAR: unvalidated goal', 18, AMBER, 'bold')
rect(32, 164, 974, 698)
rect(1032, 164, 536, 698)
text(56, 204, 'SIDE / front-to-back contour', 26, GREEN, 'bold')
text(56, 236, 'Proposed orientation: base long axis follows the cleft.', 19, MUTED)
text(1056, 204, 'REAR / base and neck', 26, GREEN, 'bold')
text(1056, 236, 'Looking from the tailbone side.', 19, MUTED)

# The silhouettes are independent illustration studies, not orthographic CAD projections.
shape('side', 490, 732, 1.65)
shape('rear', 1300, 536, 1.4)
line([(264, 293), (732, 293)], arrow=True, both=True)
text(244, 286, 'FRONT', 17, MUTED, 'bold', 'end')
text(753, 286, 'TAILBONE SIDE', 17, MUTED, 'bold')
text(1300, 292, 'Across the cleft', 18, MUTED, anchor='middle')
line([(1144, 312), (1456, 312)], arrow=True, both=True)
text(1129, 318, 'L', 18, MUTED, 'bold', 'end')
text(1471, 318, 'R', 18, MUTED, 'bold')

text(68, 383, 'Rounded body', 21, GREEN, 'bold')
text(68, 410, 'Size and angle stay open.', 17, MUTED)
line([(280, 399), (347, 399), (419, 438)], GREEN)
text(68, 554, 'Long neck blend', 21, GREEN, 'bold')
text(68, 581, 'No abrupt shoulder.', 17, MUTED)
line([(253, 565), (358, 565), (458, 684)], GREEN)
text(778, 433, 'Posterior relief', 21, GREEN, 'bold')
text(778, 460, 'Rear end falls away;', 17, MUTED)
text(778, 484, 'no upward hook.', 17, MUTED)
line([(792, 505), (792, 683), (729, 766)], GREEN)
text(68, 713, 'Anterior relief', 21, GREEN, 'bold')
text(68, 740, 'Clear the perineum.', 17, MUTED)
line([(247, 721), (318, 712), (365, 712)], GREEN)
text(778, 745, 'Removal access', 21, GREEN, 'bold')
text(778, 773, 'Preserve an exposed', 17, MUTED)
text(778, 797, 'rounded end to grip.', 17, MUTED)
line([(766, 783), (735, 783)], GREEN)
text(500, 836, 'Smooth external stop • retention under flex is still to verify', 18, MUTED, anchor='middle')

text(1300, 387, 'Neck continues toward body', 18, MUTED, anchor='middle')
line([(1279, 435), (1321, 435)], GREEN, dash=True)
text(1058, 651, 'Round the lateral edges', 21, GREEN, 'bold')
text(1058, 680, 'A shallow base instead of a flat slab.', 18, MUTED)
line([(1157, 621), (1167, 575)], GREEN)
text(1058, 746, 'Preserve the stop', 21, GREEN, 'bold')
text(1058, 775, 'The base must remain outside and', 18, MUTED)
text(1058, 800, 'grippable when it bends or twists.', 18, MUTED)

rect(32, 888, 1536, 172, '#eff4fa', '#d8e3f0')
text(56, 926, 'Fit the electronics inside this contour', 25, BLUE, 'bold')
text(56, 970, '01  Outer form + fit range', 21, BLUE, 'bold')
text(56, 1000, 'Resolve clearance, base profile', 18, MUTED)
text(56, 1025, 'and body-to-base alignment.', 18, MUTED)
text(565, 970, '02  Carrier + component space', 21, BLUE, 'bold')
text(565, 1000, 'Protect soft contact areas from', 18, MUTED)
text(565, 1025, 'rigid edges, cell loads and heat.', 18, MUTED)
text(1090, 970, '03  One T-shaped PCB', 21, BLUE, 'bold')
text(1090, 1000, 'Resize the XY outline to the cavity.', 18, MUTED)
text(1090, 1025, 'Rigid FR4 stays flat inside.', 18, MUTED)
text(42, 1094, 'Editable contour study • no anatomical scale, finished dimensions or proven wear duration', 18, AMBER, 'bold')
text(42, 1120, 'Side and rear views express contour intentions; they are not projections of a common 3D solid.', 17, MUTED)
bits.append('</svg>')
OUTPUT.write_text('\n'.join(bits) + '\n')
ASSETS.mkdir(parents=True, exist_ok=True)
shutil.copyfile(OUTPUT, ASSETS / OUTPUT.name)
print(f'Wrote {OUTPUT.relative_to(ROOT)} and documentation copy')
