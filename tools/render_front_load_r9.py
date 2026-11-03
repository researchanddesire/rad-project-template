"""Render the actual R9 native meshes; offsets illustrate the assembly idea."""
from pathlib import Path
import hashlib
import json
from PIL import Image,ImageDraw,PngImagePlugin
import render_mechanical_r2 as draw
ROOT=Path(__file__).resolve().parents[1]
CAD=ROOT/'hardware/cad/front-load-r9'
OUT=ROOT/'developer-docs/docs/assets/prototype-r2'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((CAD/'geometry-report.json').read_text())
assert sha(CAD/'FrontLoadR9.FCStd')==r['native_sha256']
meshes=draw.NativeMeshes(CAD);meshes.expected=r['review_meshes_sha256']
colors={'OnePieceBody':(181,192,205),'ClosingNoseCap':(153,170,189),
 'FlangePCBStudy':(54,139,93),'BodyPCBStudy':(54,139,93),
 'BodyComponentAllowance':(68,108,75),'BatteryAllowance':(84,155,192),
 'MotorMaxEnvelope':(211,153,64),'FlexibleLinkSpace':(203,160,56)}
oldcolor=draw.part_color
draw.part_color=lambda n:colors.get(n,oldcolor(n))
flangecad=ROOT/'hardware/cad/prototype-r2/full-05/review-meshes'
fi=json.loads((flangecad/'mesh-index.json').read_text())
flange=draw.NativeMeshes(flangecad)
flange.expected={n:h for role in fi['roles'].values() for n,h in role['exports'].items()}
flange_shape=flange.load('ElastomerFlangeCoverLower')
def shapes(section=False,exploded=False):
    out=[('ElastomerFlangeCoverLower',flange_shape,None)]
    for n in r['parts']:
        use_section=section and n in ['OnePieceBody','ClosingNoseCap']
        m=meshes.load(n,use_section,require_section=use_section).copy()
        if exploded and n=='ClosingNoseCap':m[:,:,1]+=22
        if exploded and n in ['BodyPCBStudy','BodyComponentAllowance','BatteryAllowance','MotorMaxEnvelope']:
            m[:,:,0]+=35
        out.append((n,m,None))
    return out
im=Image.new('RGB',(1800,1230),'white');d=ImageDraw.Draw(im)
draw.label(d,(36,25),'One-piece body / front-loaded electronics',38,True)
draw.label(d,(37,86),'R9 native packaging study · 15 mm neck · larger cap · separate body and flange PCB budgets',24,fill=draw.MUTED)
draw.panel(im,(30,145,855,800),'SECTION / proposed seated spaces',
           'Original outer contour; new cap mouth at Y66',shapes(section=True),camera=(.2,.04,1.8))
draw.panel(im,(915,145,855,800),'ASSEMBLY IDEA / cap off, cartridge beside body',
           'Display offsets: cap +22Y; internal budgets +35X',shapes(exploded=True),camera=(.5,.1,1.8))
d=ImageDraw.Draw(im)
draw.label(d,(37,976),'Green: two main PCB budgets · blue: battery allowance · amber: motor and flexible-link space',23,True)
draw.label(d,(37,1025),'26 mm clear mouth · 21 listed axial loading poses clear against the one-piece body only',24,True)
draw.label(d,(37,1074),'No connected carrier, finished flange attachment, real flex construction or circuit placement yet.',23,fill=draw.MUTED)
draw.label(d,(37,1122),'Motor-carrier outer allowance hits the cap by 1.266 mm³; that local support still needs redesign.',23,fill=draw.AMBER)
draw.label(d,(37,1170),'Flange contour is a preserved reference. Packaging evidence does not establish physical fit or wear.',23,fill=draw.MUTED)
meshes.verify();flange.verify()
meta={'native_sha256':r['native_sha256'],'geometry_report_sha256':sha(CAD/'geometry-report.json'),
 'renderer_sha256':sha(Path(__file__)),'render_library_sha256':sha(ROOT/'tools/render_mechanical_r2.py'),
 'R9_meshes_sha256':meshes.used,'preserved_flange_meshes_sha256':flange.used,
 'scope':'Actual native meshes and actual native half-sections. Explicit exploded offsets only. Envelopes/unrouted boards, no connected cartridge or actual flange retention.'}
png=PngImagePlugin.PngInfo();png.add_text('SourceHashes',json.dumps(meta,sort_keys=True))
target=OUT/'front-load-r9.png';im.save(target,pnginfo=png)
(OUT/'front-load-r9-source.json').write_text(json.dumps(meta,indent=2)+'\n')
print(target)
