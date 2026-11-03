"""Render actual saved R11C meshes and native close-view clips."""
from pathlib import Path
import hashlib,json
from PIL import Image,ImageDraw,PngImagePlugin
import render_mechanical_r2 as draw
ROOT=Path(__file__).resolve().parents[1];CAD=ROOT/'hardware/cad/front-load-retention-r11/candidate-c'
OUT=ROOT/'developer-docs/docs/assets/prototype-r2';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((CAD/'geometry-report.json').read_text());c=json.loads((CAD/'close-view-source.json').read_text())
assert sha(CAD/'FrontLoadRetentionR11.FCStd')==r['native_sha256']==c['native_sha256']
m=draw.NativeMeshes(CAD);m.expected=dict(r['review_meshes_sha256'])
m.expected.update({e['file']:e['sha256']for e in c['exports'].values()})
colors={'KeyedOnePieceBody':(181,192,205),'ClosingNoseCap':(153,170,189),
 'CarrierWithRetainingStem':(67,151,159),'CloseCarrierHead':(67,151,159),
 'CloseMetalCollar':(181,192,205),'HubLeft':(107,143,173),'HubRight':(127,163,193),
 'BodyPCBStudy':(54,139,93),'FrontComponentAllowance':(68,108,75),
 'BackComponentAllowance':(76,122,83),'NarrowPackAllowance':(84,155,192),
 'MotorMaxEnvelope':(211,153,64),'FlexibleLinkSpace':(203,160,56),'CloseLinkSpace':(203,160,56),
 'FlangePCBStudy':(54,139,93),'FlangeCoverLower':(62,82,107)}
oldcolor=draw.part_color;draw.part_color=lambda n:colors.get(n,oldcolor(n))
def geom(names,section_roles=()):
    return[(n,m.load(n,n in section_roles,require_section=n in section_roles),None)for n in names]
im=Image.new('RGB',(1800,1270),'white');d=ImageDraw.Draw(im)
draw.label(d,(36,25),'Central hub / body and cartridge capture',38,True)
draw.label(d,(37,86),'R11 candidate C · two side-closing hub halves · separate body/flange PCB budgets · 15 mm neck',23,fill=draw.MUTED)
allnames=[n for n in r['parts']if n not in ['FlangeCoverUpper','ServiceCoverReference']]
draw.panel(im,(30,145,855,800),'ASSEMBLY / upper cover removed',
           'Native metal sections; all parts at their stated poses',
           geom(allnames,['KeyedOnePieceBody','ClosingNoseCap']),camera=(.55,.04,1.8))
draw.panel(im,(915,145,855,800),'CAPTURE DETAIL / right half omitted',
           'Teal carrier head / gold cable space; actual native clips',
           geom(['HubLeft','CloseMetalCollar','CloseCarrierHead','CloseLinkSpace','HubBolt_1','HubBolt1','HubNut_1','HubNut1']),
           camera=(1.7,-.9,.7))
d=ImageDraw.Draw(im)
draw.label(d,(37,978),'Central hub: two screw/nut envelopes · collar carries the body · separate head retains the carrier',23,True)
draw.label(d,(37,1026),'300 static pairs: zero unexpected hits · 21 cartridge / 14 hub / 22 fastener listed poses clear',23,True)
draw.label(d,(37,1074),'Head webs: 1.35 mm front / 1.50 mm rear; material witnesses present. Actual strength is unqualified.',23,fill=draw.MUTED)
draw.label(d,(37,1122),'Cable space clears during side closure. Flange board and covers wait until the hub is clamped.',23,fill=draw.MUTED)
draw.label(d,(37,1170),'Wing attachment/compliance, actual PCBs, tip support/wires and battery choice remain open.',23,fill=draw.AMBER)
draw.label(d,(37,1218),'Native CAD study; no physical assembly, load, sealing, endurance or wear acceptance.',23,fill=draw.MUTED)
m.verify()
meta={'native_sha256':r['native_sha256'],'geometry_report_sha256':sha(CAD/'geometry-report.json'),
      'close_view_source_sha256':sha(CAD/'close-view-source.json'),'renderer_sha256':sha(Path(__file__)),
      'render_library_sha256':sha(ROOT/'tools/render_mechanical_r2.py'),'mesh_sha256':m.used,
      'assembly_visibility_omitted':['FlangeCoverUpper','ServiceCoverReference'],
      'close_view_omitted_hub_half':'HubRight','display_translations':{},
      'scope':'Actual saved native meshes, native negativeZ sections and exact native close clips. No exploded offsets. Boards/components/pack/link remain budgets; nominal capture/material witnesses do not qualify loads or physical build.'}
png=PngImagePlugin.PngInfo();png.add_text('SourceHashes',json.dumps(meta,sort_keys=True))
target=OUT/'front-load-retention-r11.png';im.save(target,pnginfo=png)
(OUT/'front-load-retention-r11-source.json').write_text(json.dumps(meta,indent=2)+'\n')
print(target)
