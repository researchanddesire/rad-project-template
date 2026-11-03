"""Render saved native R13D meshes beside the preserved R11 cap."""
from pathlib import Path
import hashlib,json
from PIL import Image,ImageDraw,PngImagePlugin
import render_mechanical_r2 as draw
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'hardware/cad/simple-assembly-r13/candidate-f';OLD=ROOT/'hardware/cad/front-load-retention-r11/candidate-c';OUT=ROOT/'developer-docs/docs/assets/prototype-r2';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((P/'geometry-report.json').read_text());old=json.loads((OLD/'geometry-report.json').read_text());assert sha(P/'SimpleAssemblyR13.FCStd')==r['native_sha256'];assert sha(OLD/'FrontLoadRetentionR11.FCStd')==old['native_sha256']
m=draw.NativeMeshes(P);m.expected=r['review_meshes_sha256'];previous=draw.NativeMeshes(OLD);previous.expected=old['review_meshes_sha256']
colors={'KeyedOnePieceBody':(181,192,205),'FullerClosingCap':(153,170,189),'ClosingNoseCap':(153,170,189),
        'DropInCarrier':(67,151,159),'DropInPCBKeeper':(187,151,76),'BodyPCB_R12':(54,139,93),'FlangePCB_R12':(54,139,93),
        'FlangeCoverLower':(62,82,107)}
oldcolor=draw.part_color
draw.part_color=lambda n:colors.get(n,(180,148,65)if n.startswith('Mate_')else(86,107,90)if n.startswith('Placed_')else oldcolor(n))
def geom(names):return[(n,m.load(n,n in ['KeyedOnePieceBody','FullerClosingCap'],require_section=n in ['KeyedOnePieceBody','FullerClosingCap']),None)for n in names]
im=Image.new('RGB',(1700,1140),'white');d=ImageDraw.Draw(im)
draw.label(d,(34,24),'Fuller nose / simpler PCB assembly',36,True)
draw.label(d,(35,78),'R13 candidate F · actual native geometry · 37.338 mm body diameter / 98 mm length / 15 mm neck',22,fill=draw.MUTED)
draw.panel(im,(25,133,400,650),'PREVIOUS NOSE','Preserved R11 cap', [('ClosingNoseCap',previous.load('ClosingNoseCap'),None)],camera=(0,0,1))
draw.panel(im,(445,133,400,650),'FULLER NOSE','Elliptical taper; same bounds', [('FullerClosingCap',m.load('FullerClosingCap'),None)],camera=(0,0,1))
names=[n for n in r['parts']if n not in ['FlangeCoverUpper','ServiceCoverReference']]
draw.panel(im,(865,133,810,650),'CURRENT PACKAGING / SECTION','Metal cut away; actual placed part envelopes',geom(names),camera=(.55,.04,1.8))
d=ImageDraw.Draw(im)
draw.label(d,(35,815),'The nose no longer scoops inward. The body, neck, hub and three cover shapes are preserved.',23,True)
draw.label(d,(35,860),'PCB drops from above; one U-shaped keeper captures it using the existing two screw positions.',23,True)
draw.label(d,(35,905),'5,995 static pairs: no unexpected hits · 8 board-drop / 8 keeper / 21 cartridge poses clear.',23,True)
draw.label(d,(35,950),'Part boxes and plugs are study envelopes. Clear listed poses do not establish continuous or physical assembly.',22,fill=draw.MUTED)
draw.label(d,(35,994),'Boards remain unrouted. Wires, wing retention/compliance, controls, tip thermal support and battery stay open.',22,fill=draw.AMBER)
draw.label(d,(35,1038),'Fuller inner nose changes the tip thermal interface. No material, seal, load, runtime or wear acceptance.',22,fill=draw.MUTED)
draw.label(d,(35,1082),'All views use saved native meshes; no display translations. Previous revisions remain unchanged.',21,fill=draw.MUTED)
m.verify();previous.verify()
meta={'native_sha256':r['native_sha256'],'previous_native_sha256':old['native_sha256'],'geometry_report_sha256':sha(P/'geometry-report.json'),'renderer_sha256':sha(Path(__file__)),'render_library_sha256':sha(ROOT/'tools/render_mechanical_r2.py'),'native_meshes_sha256':m.used,'previous_meshes_sha256':previous.used,'display_translations':{},'scope':'Actual native comparison and negativeZsections; boxes are component-height budgets, not received parts.'}
info=PngImagePlugin.PngInfo();info.add_text('SourceHashes',json.dumps(meta,sort_keys=True));out=OUT/'simple-assembly-r13.png';im.save(out,pnginfo=info)
(OUT/'simple-assembly-r13-source.json').write_text(json.dumps(meta,indent=2)+'\n');print(out)
