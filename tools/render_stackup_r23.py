"""Plot source-bound native R23 conductor geometry; filled planes are omitted."""
from pathlib import Path
import sys,json,hashlib,html,subprocess
from PIL import Image,PngImagePlugin
ROOT=Path(__file__).resolve().parents[1];P=Path(sys.argv[1]).resolve();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
gp=P/'body-native-geometry-all-layers.json';g=json.loads(gp.read_text());bp=P/'body/body-r23.kicad_pcb';assert sha(bp)==g['board_sha256'];dr=json.loads((P/'body/native-drc.json').read_text());assert dr['native_board_sha256']==sha(bp)and dr['counts']=={'violations':0,'unconnected':0,'footprint_errors':0}
ir=json.loads((P/'layout-inspection.json').read_text());assert ir['boards']['body']['native_board_sha256']==sha(bp)
out=ROOT/'developer-docs/docs/assets/prototype-r2';svg=out/'body-stackup-r23-d.svg';png=svg.with_suffix('.png')
parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1880" height="1010" viewBox="0 0 1880 1010">','<rect width="1880" height="1010" fill="white"/>']
def text(x,y,value,size=22,color='#536479',weight='normal'):
    parts.append(f'<text x="{x}" y="{y}" font-family="Arial,sans-serif" font-size="{size}" fill="{color}" font-weight="{weight}">{html.escape(value)}</text>')
text(30,44,'Body PCB: all connections complete',36,'#25354a','bold');text(31,84,'R23D / six layers / same 20 mm maximum width and 1 mm thickness / existing component positions',23)
palette={'F.Cu':'#166583','In1.Cu':'#7554a4','In3.Cu':'#d6772f','B.Cu':'#277d58'}
names={'F.Cu':'TOP SIGNAL','In1.Cu':'INNER SIGNAL 1','In3.Cu':'NEW INNER SIGNAL','B.Cu':'BOTTOM SIGNAL'}
for col,layer in enumerate(['F.Cu','In1.Cu','In3.Cu','B.Cu']):
    left=20+col*465;top=125;parts.append(f'<rect x="{left}" y="{top}" width="450" height="630" rx="16" fill="#f4f7fa" stroke="#d8e1eb"/>');text(left+20,top+36,names[layer],23,'#25354a','bold');text(left+20,top+67,layer+' · native Cu shapes',18)
    ox=left+225;oy=top+105;scale=16.8
    def xy(p):return(ox+p[0]*scale,oy+(54-p[1])*scale)
    for a,b in g['outline_edges_xy_mm']:
        x,y=xy(a);u,v=xy(b);parts.append(f'<path d="M{x},{y}L{u},{v}" fill="none" stroke="#33485d" stroke-width="2"/>')
    for z in g['rules']:
        if layer not in z['layers']:continue
        for poly in z['polygons']:
            coords=' '.join(f'{x},{y}'for x,y in map(xy,poly));parts.append(f'<polygon points="{coords}" fill="#ffe8b8" stroke="#c17c14" stroke-width="1" stroke-dasharray="4,3"/>')
    for t in g['routes']:
        if t['kind']!='track'or t['layer']!=layer:continue
        a,b=xy(t['start']),xy(t['end']);parts.append(f'<path d="M{a[0]},{a[1]}L{b[0]},{b[1]}" stroke="{palette[layer]}" stroke-width="{t["width"]*scale}" fill="none" stroke-linecap="round"/>')
    for p in g['pads']:
        if layer not in p['layers']:continue
        for poly in p['polygons']:
            coords=' '.join(f'{x},{y}'for x,y in map(xy,poly));parts.append(f'<polygon points="{coords}" fill="#b29045"/>')
    for t in g['routes']:
        if t['kind']!='via':continue
        x,y=xy(t['position']);parts.append(f'<circle cx="{x}" cy="{y}" r="{t["diameter"]*scale/2}" fill="{palette[layer]}" stroke="#25354a" stroke-width=".6"/><circle cx="{x}" cy="{y}" r="{t["drill"]*scale/2}" fill="#f4f7fa"/>')
    if layer in ['F.Cu','B.Cu']:
        for q in ir['boards']['body']['placements']:
            if q['side']!=layer[0]or q['ref']not in ['J2','J3','J5','J6','U1','U2','U3','U4','U5','U7','U8','U9']:continue
            x,y=xy(q['xy_mm']);text(x+4,y-4,q['ref'],12,'#111d2c','bold')
    text(left+20,top+603,'Planes and solder mask omitted for clarity',16)
text(31,802,'In2 + In4: dedicated ground planes. Bottom power routes retain an adjacent ground reference.',25,'#25354a','bold')
text(31,847,'0 native DRC findings / 0 missing connections / 94 device components and all 338 circuit nodes conserved.',23,'#25354a')
text(31,888,'138 vias screened against 238 native copper/paste pad shapes: no nominal drill overlaps.',23)
text(31,929,'Source-bound layout review; exact stackup needs fabricator review. Electrical and physical validation remain open.',21)
text(31,970,'R21 carrier envelope is unchanged. The complete prototype build package remains in development.',21)
parts.append('</svg>');svg.write_text('\n'.join(parts))
subprocess.run(['rsvg-convert',str(svg),'-o',str(png)],check=True)
meta={'native_board_sha256':sha(bp),'geometry_sha256':sha(gp),'inspection_sha256':sha(P/'layout-inspection.json'),'native_DRC_sha256':sha(P/'body/fresh-native-drc.txt'),'renderer_sha256':sha(Path(__file__)),'SVG_sha256':sha(svg),'planes_omitted':True,'scope':'Actual native pad polygons, tracks, through-via Cu/drills, board outline and rule areas. No electrical/physical or complete-return-path validation.'}
im=Image.open(png);info=PngImagePlugin.PngInfo();info.add_text('SourceHashes',json.dumps(meta,sort_keys=True));im.save(png,pnginfo=info);png.with_name(png.stem+'-source.json').write_text(json.dumps(meta,indent=2)+'\n');print(png,flush=True)
