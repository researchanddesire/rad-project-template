"""Render the actual R10 native meshes; offsets illustrate the assembly idea."""
from pathlib import Path
import hashlib
import json
from PIL import Image,ImageDraw,PngImagePlugin
import render_mechanical_r2 as draw
ROOT=Path(__file__).resolve().parents[1]
CAD=ROOT/'hardware/cad/front-load-r10/candidate-c'
OUT=ROOT/'developer-docs/docs/assets/prototype-r2'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((CAD/'geometry-report.json').read_text())
assert sha(CAD/'FrontLoadR10.FCStd')==r['native_sha256']
meshes=draw.NativeMeshes(CAD);meshes.expected=r['review_meshes_sha256']
colors={'OnePieceBody':(181,192,205),'ClosingNoseCap':(153,170,189),
 'FlangePCBStudy':(54,139,93),'BodyPCBStudy':(54,139,93),
 'FrontComponentAllowance':(68,108,75),'BackComponentAllowance':(76,122,83),
 'ConnectedCarrier':(67,151,159),'RemovablePCBKeeper':(190,152,84),
 'KeeperScrew_1':(164,153,133),'KeeperScrew1':(164,153,133),'NarrowPackAllowance':(84,155,192),
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
        if exploded and n in ['ConnectedCarrier','RemovablePCBKeeper','KeeperScrew_1','KeeperScrew1','BodyPCBStudy','FrontComponentAllowance','BackComponentAllowance','NarrowPackAllowance','MotorMaxEnvelope']:
            m[:,:,0]+=35
        out.append((n,m,None))
    return out
im=Image.new('RGB',(1800,1230),'white');d=ImageDraw.Draw(im)
draw.label(d,(36,25),'Connected carrier / front-loaded body',38,True)
draw.label(d,(37,86),'R10 candidate C · one-piece body · larger cap · separate body and flange PCB budgets',24,fill=draw.MUTED)
draw.panel(im,(30,145,855,800),'SECTION / stacked body cartridge',
           'Original outer contour; cap mouth at Y51',shapes(section=True),camera=(.55,.04,1.8))
draw.panel(im,(915,145,855,800),'ASSEMBLY IDEA / cartridge beside body',
           'Display offsets: cap +22Y; carrier group +35X',shapes(exploded=True),camera=(.5,.1,1.8))
d=ImageDraw.Draw(im)
draw.label(d,(37,976),'Teal: connected carrier · green: board budgets · blue: battery allowance · amber: motor',23,True)
draw.label(d,(37,1025),'30 mm clear mouth · 15 mm neck · 21 listed cartridge-loading poses clear against the body',24,True)
draw.label(d,(37,1074),'120 static pairs: zero unexpected intersections; three named process/connection spaces remain unqualified.',23,fill=draw.MUTED)
draw.label(d,(37,1122),'Actual PCB layouts, cartridge/flange retention, tip support/wires and a selected battery remain open.',23,fill=draw.AMBER)
draw.label(d,(37,1170),'Flange contour is a preserved reference. No physical fit, strength, assembly or wear acceptance.',23,fill=draw.MUTED)
meshes.verify();flange.verify()
meta={'native_sha256':r['native_sha256'],'geometry_report_sha256':sha(CAD/'geometry-report.json'),
 'renderer_sha256':sha(Path(__file__)),'render_library_sha256':sha(ROOT/'tools/render_mechanical_r2.py'),
 'R10_meshes_sha256':meshes.used,'preserved_flange_meshes_sha256':flange.used,
 'display_translation_mm':{'ClosingNoseCap':[0,22,0],
   'carrier_group':[35,0,0]},
 'carrier_group':['ConnectedCarrier','RemovablePCBKeeper','KeeperScrew_1','KeeperScrew1','BodyPCBStudy','FrontComponentAllowance','BackComponentAllowance','NarrowPackAllowance','MotorMaxEnvelope'],
 'scope':'Actual native carrier/metal meshes and half-sections, explicit display offsets. PCB/component/pack budgets only; no actual flange retention, tip load path or physical assembly acceptance.'}
png=PngImagePlugin.PngInfo();png.add_text('SourceHashes',json.dumps(meta,sort_keys=True))
target=OUT/'front-load-r10.png';im.save(target,pnginfo=png)
(OUT/'front-load-r10-source.json').write_text(json.dumps(meta,indent=2)+'\n')
print(target)
