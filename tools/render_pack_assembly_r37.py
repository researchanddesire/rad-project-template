"""Render source-bound R37 assembly development figure."""
from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image,ImageDraw,PngImagePlugin
import render_mechanical_r2 as draw
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'hardware/cad/pack-assembly-r37';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();r=json.loads((P/'saved-review.json').read_text());c=json.loads((P/'display/display-context.json').read_text());assert r['all_saved_checks_pass']and r['power_F_sha256']==c['native_sha256']==sha(P/'power-f/ConditionalPackPowerR37.FCStd')
a=draw.NativeMeshes(P/'display');a.expected={f:h for q in c['panels'].values()for f,h in q['meshes_sha256'].items()};rot=np.array([[1,0,0],[0,0,1],[0,-1,0]])
def colour(n):
 if n.startswith('PackAnchored'):return(147,158,168)
 if n.startswith('PackTie'):return(213,155,60)
 if n.startswith('PackWireSoft'):return(109,184,160)
 if n.startswith('PackPublished'):return(135,178,196)
 if n.startswith('PackMate'):return(101,111,130)
 if n.startswith('PackPowerJoint'):return(182,134,68)
 if n.startswith('PackNTCHead'):return(158,105,155)
 if n.startswith('FactoryNTC'):return(184,146,92)
 if n.startswith(('StockPackLead','SpareMateLead')):return(204,106,88)
 return(60,119,176)
draw.part_color=colour
def geometry(label):return[(f.removesuffix('.stl'),a.load(f.removesuffix('.stl'))@rot.T,None)for f in c['panels'][label]['meshes_sha256']]
im=Image.new('RGB',(1800,1110),'white');d=ImageDraw.Draw(im)
draw.label(d,(32,25),'Separate wire support; shell-coupled motor stays independent',34,True)
draw.label(d,(32,80),'R37 / no added anchor screw / unchanged 15 mm neck and upright flange / battery choice OPEN',23,fill=draw.MUTED)
draw.panel(im,(25,125,745,610),'ANCHOR SECTION / Y36 mm','Thin native section; gray carrier, amber tie, green soft pad.',geometry('anchor'),camera=(0,0,-2.5))
draw.panel(im,(800,125,975,610),'CONDITIONAL PACK POWER ROUTE','Hubs/covers/boards omitted; blue block is a pack-size reference.',geometry('power'),camera=(.2,.4,-2.5))
d=ImageDraw.Draw(im)
for y,t in [(775,'Five wire jackets touch the pad and formed-band allowance; no nominal interference.'),(820,'The anchor reuses the empty body tray. Both power wires dip below the carrier before turning left.'),(865,'Power laps have separate bare cores, 0.10 mm nominal gap and touching solder-process targets.'),(910,'Saved native checks: source geometry conserved; 3,135 conditional power comparisons clear.'),(955,'Lead exit, shrink, connector size and bend limits still need the eventual pack and actual parts.'),(1000,'Connector/joint retention, connected loading, seals and first-build testing remain unfinished.')]:
 draw.label(d,(33,y),t,23,fill=draw.AMBER if y>=955 else draw.INK)
draw.label(d,(33,1050),'Editable geometry checkpoint. No purchase, battery selection, energized test or physical fit claim.',23,fill=draw.MUTED)
a.verify();meta={'native_sha256':c['native_sha256'],'saved_review_sha256':sha(P/'saved-review.json'),'display_context_sha256':sha(P/'display/display-context.json'),'renderer_sha256':sha(Path(__file__)),'render_library_sha256':sha(ROOT/'tools/render_mechanical_r2.py'),'meshes_sha256':a.used,'display_transform':'(x,y,z)->(x,z,-y); no relative transforms','scope':c['scope']};out=ROOT/'developer-docs/docs/assets/prototype-r2/pack-assembly-r37-f.png';info=PngImagePlugin.PngInfo();info.add_text('SourceHashes',json.dumps(meta,sort_keys=True));im.save(out,pnginfo=info);out.with_name(out.stem+'-source.json').write_text(json.dumps(meta,indent=2)+'\n');print(out,flush=True)
