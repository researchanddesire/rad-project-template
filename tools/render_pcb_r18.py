"""Render saved R18 native meshes, including the fuller exterior and keeper."""
from pathlib import Path
import sys,json,hashlib
from PIL import Image,ImageDraw,PngImagePlugin
import render_mechanical_r2 as draw
ROOT=Path(__file__).resolve().parents[1];P=Path(sys.argv[1]).resolve();OUT=ROOT/'developer-docs/docs/assets/prototype-r2';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();r=json.loads((P/'geometry-report.json').read_text());assert sha(P/'PCBIntegrationR18.FCStd')==r['native_sha256'];m=draw.NativeMeshes(P);m.expected=r['review_meshes_sha256'];old=draw.part_color
colors={'KeyedOnePieceBody':(181,192,205),'FullerClosingCap':(153,170,189),'PortedCarrierR18':(67,151,159),'PortedKeeperR18':(187,151,76),'BodyPCB_R17':(54,139,93),'FlangePCB_R17':(54,139,93),'FlangeCoverLower':(62,82,107),'FlangeCoverUpper':(62,82,107)}
draw.part_color=lambda n:colors.get(n,(180,148,65)if n.startswith('R17Mate_')else(86,107,90)if n.startswith('R17_')else old(n))
def geom(names,section=False):return[(n,m.load(n,section and n in ['KeyedOnePieceBody','FullerClosingCap'],require_section=section and n in ['KeyedOnePieceBody','FullerClosingCap']),None)for n in names]
im=Image.new('RGB',(1760,1120),'white');d=ImageDraw.Draw(im)
draw.label(d,(34,24),'Fuller nose / one keeper / accessible plugs',36,True)
draw.label(d,(35,78),f"R18 candidate {P.name.rsplit('-',1)[-1].upper()} · actual native geometry · 15 mm neck · same exterior and two keeper screws",23,fill=draw.MUTED)
draw.panel(im,(25,130,430,640),'FULLER EXTERIOR','No inward scoop',geom(['KeyedOnePieceBody','FullerClosingCap','FlangeCoverLower','FlangeCoverUpper']),camera=(0,0,1))
names=[n for n in r['parts']if n not in ['FlangeCoverUpper','ServiceCoverReference']]
draw.panel(im,(475,130,760,640),'INTEGRATED PCB POSES / SECTION','Metal cut away; part boxes are height budgets',geom(names,True),camera=(.45,.04,1.8))
close=['PortedKeeperR18','R17_J2','R17_J3','R17_J5','R17Mate_J2','R17Mate_J3','R17Mate_J5']
draw.panel(im,(1255,130,480,640),'ONE KEEPER','Outside bridge clears battery plug',geom(close),camera=(.3,.35,1.8))
d=ImageDraw.Draw(im)
draw.label(d,(35,804),'Three connector ports; the left bridge keeps the keeper in one piece. No extra screws.',25,True)
draw.label(d,(35,850),'5,995 static pairs: no unexpected hits. All seven nominal mating allowances clear.',24,True)
draw.label(d,(35,896),'8 board-drop / 8 keeper / 21 cartridge positions clear their stated rigid contexts.',23,True)
draw.label(d,(35,942),'Nominal ports include 0.3 mm allowance. These checks do not establish real connector, wire or load fit.',22,fill=draw.MUTED)
draw.label(d,(35,986),'PCB routing, supported wires, flange compliance, controls, tip support, seals and parts remain in development.',21,fill=draw.AMBER)
draw.label(d,(35,1030),'Battery OPEN. Source exterior preserved; no runtime, wear, manufacturing or physical assembly validation.',22,fill=draw.MUTED)
draw.label(d,(35,1074),'All views use saved native meshes at their model coordinates; mates are allowances, not received parts.',21,fill=draw.MUTED)
m.verify();meta={'native_sha256':r['native_sha256'],'geometry_report_sha256':sha(P/'geometry-report.json'),'renderer_sha256':sha(Path(__file__)),'render_library_sha256':sha(ROOT/'tools/render_mechanical_r2.py'),'native_meshes_sha256':m.used,'display_translations':{},'scope':'Actual saved native meshes; PCB Fab/height and nominal mate boxes, not controlled physical part maxima.'};info=PngImagePlugin.PngInfo();info.add_text('SourceHashes',json.dumps(meta,sort_keys=True));tag='pcb-integration-r18'if P.name=='candidate-a'else'pcb-integration-r18-'+P.name.rsplit('-',1)[-1];f=OUT/(tag+'.png');im.save(f,pnginfo=info);(OUT/(tag+'-source.json')).write_text(json.dumps(meta,indent=2)+'\n');print(f,flush=True)
