"""Source-bound R5 nut seat section illustration."""
from pathlib import Path
import hashlib, json
from PIL import Image, ImageDraw, ImageFont, PngImagePlugin
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'developer-docs/docs/assets/prototype-r2'
source = OUT / 'core-join-r5-sections.json'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
r = json.loads(source.read_text())
assert sha(ROOT / 'hardware/cad/core-join-r5/CoreJoinR5.FCStd') == r['native_sha256']
im = Image.new('RGB', (1800, 1020), '#f5f7fa')
d = ImageDraw.Draw(im)
font = lambda n: ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', n)
def text(x, y, value, n=23, fill='#263746'):
    d.text((x, y), value, font=font(n), fill=fill)
def color(name):
    if 'NutKeeper' in name: return '#008b8a'
    if name.startswith('CoreJoinNut'): return '#b17d00'
    if 'CoreJoinBolt' in name: return '#a34468'
    return '#71859a'
text(36, 24, 'Core-join nuts R5 / a loading route before closure', 39)
text(38, 82, 'Actual native section at X−25 mm · pair held together during loading · lower parts outside this view', 24)
titles = ['1. Approach / Y offset +4 mm', '2. At port / still lifted 0.2 mm', '3. Seat / bolt after core closure']
for i, v in enumerate(r['views']):
    left, top, w, h = 30 + 590 * i, 150, 560, 580
    d.rounded_rectangle((left, top, left + w, top + h), radius=12,
                        fill='white', outline='#ced7e1', width=2)
    text(left + 18, top + 18, titles[i], 24)
    bounds = (-11, 6, 4, 12)
    x0, y0, x1, y1 = bounds
    aw, ah = w - 40, h - 165
    scale = min(aw / (x1 - x0), ah / (y1 - y0))
    ox, oy = (aw - (x1 - x0) * scale) / 2, (ah - (y1 - y0) * scale) / 2
    detail = Image.new('RGB', (aw, ah), 'white')
    dd = ImageDraw.Draw(detail)
    for part in v['parts']:
        for path in part['paths']:
            pts = [(ox + (x - x0) * scale, oy + (y1 - y) * scale) for x, y in path]
            if len(pts) > 1: dd.line(pts, fill=color(part['name']), width=3)
    im.paste(detail, (left + 20, top + 100))
    text(left + 18, top + h - 42, ['Move toward −Y; pair lifted 0.2 mm',
                                 'Lower pair onto the backed seat',
                                 'Keeper screw is outside this section'][i], 21, '#627486')
text(38, 772, 'Gray: upper core   ·   Teal: keeper with 0.6 mm backed tongue   ·   Gold: M2 nut   ·   Purple: main bolt', 23)
text(38, 821, 'Fit the keeper screws on the removed upper core before the 27-part upper group closes onto the product.', 23)
text(38, 864, 'Both nut routes, keeper tools and stated closure samples clear. Hard seats and nominal stops are not tolerance proof.', 23)
text(38, 907, 'Material, insert process, thin bearing floors, actual sockets, torque and strength remain open.', 23, '#975b15')
text(38, 970, 'Separate source-bound candidate · no main-assembly adoption or physical acceptance', 22, '#627486')
meta = {k: r[k] for k in ['native_sha256', 'geometry_report_sha256', 'exporter_sha256', 'scope']}
meta.update(sections_sha256=sha(source), renderer_sha256=sha(Path(__file__)))
png = PngImagePlugin.PngInfo(); png.add_text('SourceHashes', json.dumps(meta, sort_keys=True))
target = OUT / 'core-join-r5-review.png'; im.save(target, pnginfo=png)
(OUT / 'core-join-r5-review-source.json').write_text(json.dumps(meta, indent=2) + '\n')
print(target)
