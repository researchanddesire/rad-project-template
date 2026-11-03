"""Plot native-derived orientation envelopes; no invented surface geometry."""
from pathlib import Path
import json,hashlib,html,subprocess
from PIL import Image,PngImagePlugin
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'hardware/cad/flange-orientation-r24/candidate-b'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((P/'orientation-screen.json').read_text())
for c in r['cases']:assert sha(P/c['native_file'])==c['native_sha256']
out=ROOT/'developer-docs/docs/assets/prototype-r2/flange-orientation-r24.svg'
s=['<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="860" viewBox="0 0 1600 860">','<rect width="1600" height="860" fill="white"/>']
def text(x,y,t,size=20,color='#56677b',bold=False):
    s.append(f'<text x="{x}" y="{y}" font-family="Arial,sans-serif" font-size="{size}" fill="{color}" font-weight="{"bold"if bold else"normal"}">{html.escape(t)}</text>')
text(28,45,'A flange board can stand upright',34,'#24364a',True)
text(29,84,'R24B: complete populated envelopes, including radio overhang and nominal connector mates',22)
labels=['Flat reference','90° about X','90° about Y','90° in XY plane']
for i,c in enumerate(r['cases']):
    x=20+395*i;b=c['populated_bounds_xyz_mm'];a=c['populated_spans_xyz_mm'];hits=len(c['fixed_context_intersections'])
    s.append(f'<rect x="{x}" y="117" width="375" height="613" rx="14" fill="#f4f7fa" stroke="#d6e0e8"/>')
    text(x+18,151,labels[i],24,'#24364a',True)
    text(x+18,185,' × '.join(f'{v:.2f}'for v in a)+' mm',20)
    for row,(axis,title,lo,hi)in enumerate([(1,'TOP · X / Y',-35,-3),(2,'FRONT · X / Z',-19,19)]):
        top=225+row*228
        text(x+18,top,title,18)
        ox=x+25;oy=top+24;scale=5.3
        # Fixed wing bounding window only, not a reconstructed surface.
        s.append(f'<rect x="{ox}" y="{oy}" width="{33*scale}" height="{(hi-lo)*scale}" fill="none" stroke="#adbaca" stroke-dasharray="5,4"/>')
        u=ox+(b[0]+45)*scale;v=oy+(b[axis]-lo)*scale
        s.append(f'<rect x="{u}" y="{v}" width="{a[0]*scale}" height="{a[axis]*scale}" fill="#399b8760" stroke="#207b69" stroke-width="2"/>')
    text(x+18,710,f'{hits} fixed-context intersection'+('s'if hits!=1 else''),19,'#936125'if hits else'#207b69',True)
text(29,751,'Green: populated bounding envelope. Dashed: fixed outer wing bounding window; not its surface.',21)
text(29,792,'Y-rotation clears the saved fixed context. Antenna, buttons, flex, assembly route and physical fit remain open.',21)
text(29,831,'All exterior shapes unchanged. Dimensions alone do not qualify comfort or flange motion.',21)
s.append('</svg>');out.write_text('\n'.join(s))
subprocess.run(['rsvg-convert',str(out),'-o',str(out.with_suffix('.png'))],check=True)
meta={'report_sha256':sha(P/'orientation-screen.json'),'renderer_sha256':sha(Path(__file__)),'SVG_sha256':sha(out),'native_files_sha256':{c['native_file']:c['native_sha256']for c in r['cases']},'scope':'Projections of complete populated native bounding envelopes only; dashed rectangles are fixed outer wing bounding windows, not surfaces or clearance proofs.'}
png=out.with_suffix('.png');im=Image.open(png);info=PngImagePlugin.PngInfo();info.add_text('SourceHashes',json.dumps(meta,sort_keys=True));im.save(png,pnginfo=info)
out.with_name(out.stem+'-source.json').write_text(json.dumps(meta,indent=2)+'\n')
print(png)
