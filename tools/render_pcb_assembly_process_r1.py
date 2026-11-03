"""Draw four source-bound PCB assembly details as editable SVG and PNG."""
from pathlib import Path
import hashlib
import html
import json
from PIL import Image, ImageDraw, ImageFont, PngImagePlugin

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / 'hardware/pcb/prototype-r2/assembly-review'
OUT = ROOT / 'developer-docs/docs/assets/prototype-r2'
SOURCE = FOLDER / 'native-pad-details.json'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
r = json.loads(SOURCE.read_text())
assert sha(ROOT / r['board']) == r['board_sha256']
image = Image.new('RGB', (1800, 1340), 'white')
draw = ImageDraw.Draw(image)
svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="1340" viewBox="0 0 1800 1340">', '<rect width="1800" height="1340" fill="white"/>']


def text(x, y, value, size=23, color='#263746'):
    font = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', size)
    draw.text((x, y), value, fill=color, font=font)
    svg.append(f'<text x="{x}" y="{y+size*.91}" fill="{color}" font-family="Arial,sans-serif" font-size="{size}">{html.escape(value)}</text>')


def rect(x, y, w, h, fill, outline=None):
    draw.rectangle((x, y, x+w, y+h), fill=fill, outline=outline, width=2)
    svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{outline or "none"}" stroke-width="2"/>')


def polygon(points, fill, outline):
    draw.polygon(points, fill=fill, outline=outline, width=1)
    data = ' '.join(f'{x:.4f},{y:.4f}' for x,y in points)
    svg.append(f'<polygon points="{data}" fill="{fill}" stroke="{outline}" stroke-width="1"/>')


def circle(x, y, radius, fill, outline):
    draw.ellipse((x-radius,y-radius,x+radius,y+radius),fill=fill,outline=outline,width=2)
    svg.append(f'<circle cx="{x:.4f}" cy="{y:.4f}" r="{radius:.4f}" fill="{fill}" stroke="{outline}" stroke-width="2"/>')


text(35, 24, 'Main PCB / assembly-process details', 39)
text(37, 80, 'Actual R2 pad and paste geometry · decisions for assembler review · board unchanged', 25, '#5b6c7e')
specs = [
    ('U1', 'Charger / B side', 1.9, [
        'Ground pad 17: 1.68 × 1.68 mm',
        'Paste aperture: 1.55 × 1.55 mm',
        'Ø0.30 mm drill crosses the paste.',
        '',
        'Review via treatment and print/voids.',
        'TI’s example uses Ø0.20 mm vias;',
        'current via is a different size/layout.',
        'No fill, plug or tent process accepted.']),
    ('U5', 'Motor driver / F side', 1.45, [
        'Ground pad 9: 0.90 × 1.60 mm',
        'Two 0.75 × 0.65 mm paste windows',
        'Nominal paste/copper area: 67.7%',
        'Ø0.30 mm drill crosses both edges.',
        '',
        'TI’s example windows: 0.90 × 0.70 mm',
        'Review paste volume, via treatment',
        'and resulting solder/void acceptance.']),
    ('U6', 'Radio module / central pad 49 only', 3.3, [
        'Nine ground-copper islands',
        'No pad-49 paste in the current native',
        'Ø0.30 mm drill in the center island',
        '',
        'Manufacturer permits unsoldered EPAD.',
        'Confirm this assembly route; do not',
        'add center paste without review.',
        'Peripheral lands/paste omitted here.']),
    ('U7', 'Accelerometer / F side', 1.0, [
        'Ten nominal 0.30 × 0.20 mm lands',
        'Copper and paste are coextensive.',
        'No drill-in-pad in this detail',
        '',
        'Package contacts are not a complete',
        'land/stencil-process approval.',
        'Review device-specific assembly and',
        'reflow/handling with the assembler.']),
]
for index,(ref,title,extent,lines) in enumerate(specs):
    x,y = 30+890*(index%2), 145+535*(index//2)
    rect(x,y,860,505,'#f5f7fa','#d5dee8')
    detail=r['details'][ref]
    text(x+20,y+18,f'{ref}  {title}',27)
    cx,cy=detail['center_xy_mm']
    text(x+20,y+61,f'Center X {cx:g}, Y {cy:g} mm · shared top coordinates',20,'#617486')
    px,py=x+25,y+110
    width,height=365,350
    rect(px,py,width,height,'white','#e4e9ef')
    scale=min((width-36)/(2*extent),(height-36)/(2*extent))
    def project(point):
        return px+width/2+(point[0]-cx)*scale,py+height/2-(point[1]-cy)*scale
    pads=[p for p in detail['pads'] if ref!='U6' or p['number']=='49']
    for layer,fill,outline in [('copper_polygons_xy_mm','#80aec9','#32607a'),('paste_polygons_xy_mm','#e8ba68','#a16e1d')]:
        for p in pads:
            for poly in p[layer]: polygon([project(point) for point in poly],fill,outline)
    for via in detail['drill_in_pad']:
        vx,vy=project(via['center_xy_mm'])
        circle(vx,vy,via['drill_mm']*scale/2,'#152b3e','#152b3e')
    for pad in pads:
        if not pad['number'] or not pad['copper_polygons_xy_mm'] or (ref=='U6' and pad['center_xy_mm']!=detail['center_xy_mm']):continue
        tx,ty=project(pad['center_xy_mm'])
        if detail['drill_in_pad'] and pad['number']=={'U1':'17','U5':'9','U6':'49','U7':None}[ref]:tx-=30;ty-=25
        text(tx-6,ty-8,pad['number'],15,'#263746')
    for j,line in enumerate(lines):text(x+415,y+113+35*j,line,21)
    text(x+25,y+468,'Detail scales differ; dimensions are millimetres.',18,'#617486')

rect(36,1235,24,24,'#80aec9')
text(72,1232,'Copper',22)
rect(210,1235,24,24,'#e8ba68')
text(246,1232,'Paste aperture',22)
circle(468,1247,9,'#152b3e','#152b3e')
text(490,1232,'Drill',22)
text(630,1232,'Back copper uses top coordinates, not a mirrored bottom view.',22,'#617486')
text(36,1282,'Native 5ba844fa… · source-bound review only; mask, via process, stencil, assembly yield and thermal behavior remain unqualified.',21,'#8e5a16')
svg.append('</svg>')
OUT.mkdir(exist_ok=True)
base=OUT/'pcb-assembly-process-r1'
base.with_suffix('.svg').write_text('\n'.join(svg)+'\n')
metadata={'board_sha256':r['board_sha256'],'native_details_sha256':sha(SOURCE),'renderer_sha256':sha(Path(__file__)),
          'scope':'Four native pad/paste detail plots. U6 shows only actual pad49 islands; other footprints show all source pads. No mask/fill/etch/volume/yield acceptance. Nominal U5 area ratio excludes drill subtraction and paste transfer effects.'}
png=PngImagePlugin.PngInfo();png.add_text('SourceHashes',json.dumps(metadata,sort_keys=True))
image.save(base.with_suffix('.png'),pnginfo=png)
metadata.update({'image_sha256':sha(base.with_suffix('.png')),'svg_sha256':sha(base.with_suffix('.svg'))})
base.with_name(base.name+'-source.json').write_text(json.dumps(metadata,indent=2)+'\n')
print(base.with_suffix('.png'))
