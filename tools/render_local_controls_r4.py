"""Draw source-bound native R4 button sections, including assembly clearance."""
from pathlib import Path
import hashlib
import json
from PIL import Image, ImageDraw, ImageFont, PngImagePlugin

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / 'hardware/cad/local-controls-r4'
OUT = ROOT / 'developer-docs/docs/assets/prototype-r2'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
source = FOLDER / 'preview-geometry.json'
r = json.loads(source.read_text())
assert sha(FOLDER / 'LocalControlsR4.FCStd') == r['native_sha256']
assert sha(FOLDER / 'geometry-report.json') == r['geometry_report_sha256']
assert sha(FOLDER / 'review.json') == r['review_sha256']
im = Image.new('RGB', (1800, 1050), '#f5f7fa')
d = ImageDraw.Draw(im)


def font(size):
    return ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', size)


def text(x, y, value, size=23, color='#263746'):
    d.text((x, y), value, fill=color, font=font(size))


def color(name):
    if 'Blocking' in name:
        return '#cf473c'
    if 'Plunger' in name:
        return '#af7b00'
    if 'AxialLockKey' in name:
        return '#a341a0'
    if 'Guide' in name:
        return '#008b8a'
    return '#28699b'


text(36, 24, 'Button cartridges R4 / assembly clearance', 39)
text(38, 82, 'Separate native candidate · 0.15 mm sampled loading window · full blocking rings remain fitted', 24)
titles = ['Guide below home / key absent', 'Home / key catches guide roof', 'Plan / key enters from the side']
for i, v in enumerate(r['views']):
    left, top, width, height = 30 + 590 * i, 150, 560, 590
    d.rounded_rectangle((left, top, left + width, top + height), radius=12,
                        fill='white', outline='#ced7e1', width=2)
    text(left + 18, top + 18, titles[i], 25)
    text(left + 18, top + 59, v['plane'], 19, '#627486')
    x0, y0, x1, y1 = v['suggested_bounds_xy']
    pad = 25
    area_left, area_top = left + pad, top + 125
    area_width, area_height = width - 2 * pad, height - 185
    scale = min(area_width / (x1 - x0), area_height / (y1 - y0))
    ox = (area_width - (x1 - x0) * scale) / 2
    oy = (area_height - (y1 - y0) * scale) / 2
    detail = Image.new('RGB', (area_width, area_height), 'white')
    detail_draw = ImageDraw.Draw(detail)
    for part in v['parts']:
        for path in part['paths']:
            pts = [(ox + (x - x0) * scale, oy + (y1 - y) * scale) for x, y in path]
            if len(pts) > 1:
                detail_draw.line(pts, fill=color(part['name']), width=3)
    im.paste(detail, (area_left, area_top))
    caption = ['Rigid guide offset −0.125 mm; loading pose',
               'No accepted operating stroke or preload',
               'Tongue 0.30 mm; pocket height 0.40 mm'][i]
    text(left + 18, top + height - 43, caption, 20, '#627486')

text(38, 775, 'Blue: cartridge   ·   Teal: guide   ·   Purple: side key   ·   Gold: plunger   ·   Red: blocking ring', 24)
text(38, 824, 'Both guides: 76 turn samples each; corner gap ≥0.05 mm. Four driver entries and receiver-wall checks clear.', 23)
text(38, 868, 'These are finite poses and nominal geometry. Assembly handling, manufactured fit and strength remain unqualified.', 23)
text(38, 912, 'Track floor 0.35 mm; key tongue and guide roof 0.30 mm. Working spring, membrane and travel remain open.', 23, '#975b15')
text(38, 978, 'Source-bound 0.001 mm native sections · current main assembly is unchanged · no physical assembly acceptance', 21, '#627486')
meta = {'native_sha256': r['native_sha256'],
        'geometry_report_sha256': r['geometry_report_sha256'],
        'review_sha256': r['review_sha256'],
        'preview_geometry_sha256': sha(source),
        'renderer_sha256': sha(Path(__file__)), 'scope': r['scope']}
png = PngImagePlugin.PngInfo()
png.add_text('SourceHashes', json.dumps(meta, sort_keys=True))
target = OUT / 'local-controls-r4-review.png'
im.save(target, pnginfo=png)
(OUT / 'local-controls-r4-review-source.json').write_text(json.dumps(meta, indent=2) + '\n')
print(target)
