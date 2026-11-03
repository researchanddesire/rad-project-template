"""Source-bound view of the saved R21 motor/PCB keeper proposal."""
from pathlib import Path
import sys,json,hashlib
from PIL import Image,ImageDraw,PngImagePlugin
import render_mechanical_r2 as draw
ROOT=Path(__file__).resolve().parents[1];P=Path(sys.argv[1]).resolve()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((P/'geometry-report.json').read_text())
assert sha(P/'MotorRetentionR21.FCStd')==r['native_sha256']
m=draw.NativeMeshes(P);m.expected=r['review_meshes_sha256'];old=draw.part_color
colors={'MotorKeeperR21':(185,145,63),'PortedCarrierR20':(67,151,159),'MotorMaxEnvelope':(105,135,162),'MotorLeadFlareAllowanceR21':(204,100,105),'BodyPCB_R17':(54,139,93),'KeyedOnePieceBody':(181,192,205),'FullerClosingCap':(153,170,189)}
draw.part_color=lambda n:colors.get(n,(180,148,65)if n.startswith('R17Mate_')else(86,107,90)if n.startswith('R17_')else old(n))
def geom(names,section=False):
    return[(n,m.load(n,section and n in ['KeyedOnePieceBody','FullerClosingCap'],require_section=section and n in ['KeyedOnePieceBody','FullerClosingCap']),None)for n in names]
im=Image.new('RGB',(1720,1080),'white');d=ImageDraw.Draw(im)
draw.label(d,(32,22),'One keeper for the PCB and motor',36,True)
draw.label(d,(33,76),'R21C conditional capture study / fuller nose and 15 mm neck preserved',23,fill=draw.MUTED)
names=[n for n in r['parts']if n not in ['FlangeCoverUpper','ServiceCoverReference']]+list(r['allowances'])
draw.panel(im,(25,125,760,635),'INTEGRATED CUTAWAY','Actual saved native part boxes and declared allowance',geom(names,True),camera=(.35,.04,1.8))
close=['MotorKeeperR21','PortedCarrierR20','MotorMaxEnvelope','MotorLeadFlareAllowanceR21','KeeperScrew_1','KeeperScrew1','R17_J3','R17_J5','R17Mate_J3','R17Mate_J5','BodyPCB_R17']
draw.panel(im,(810,125,885,635),'SAME TWO KEEPER SCREWS','Blue motor; gold keeper; lower saddles on carrier',geom(close),camera=(.6,.25,1.8))
d=ImageDraw.Draw(im)
draw.label(d,(33,795),'Motor shifted 6.5 mm toward the tip; modeled lead flare now has its own space.',25,True)
draw.label(d,(33,842),'One removable keeper joins the board guides, upper motor hoops and axial stops.',24,True)
draw.label(d,(33,889),'Flare radii are inferred design allowances: supplier dimensions and received fit must confirm them.',22,fill=draw.AMBER)
draw.label(d,(33,935),'Liner, preload, wires, screw details and retention strength remain unqualified.',23,fill=draw.MUTED)
draw.label(d,(33,979),'Battery OPEN. Body routing, flange flex, controls, tip support and seals remain unfinished.',22,fill=draw.MUTED)
draw.label(d,(33,1023),'This is a conditional assembly proposal, not a build release or physical validation.',22,fill=draw.MUTED)
m.verify();meta={'native_sha256':r['native_sha256'],'geometry_report_sha256':sha(P/'geometry-report.json'),'renderer_sha256':sha(Path(__file__)),'render_library_sha256':sha(ROOT/'tools/render_mechanical_r2.py'),'native_meshes_sha256':m.used,'display_translations':{},'scope':'Saved native meshes; component height boxes and inferred lead flare allowance, not controlled physical part maxima.'}
info=PngImagePlugin.PngInfo();info.add_text('SourceHashes',json.dumps(meta,sort_keys=True))
out=ROOT/'developer-docs/docs/assets/prototype-r2/motor-retention-r21-c.png'
im.save(out,pnginfo=info);out.with_name(out.stem+'-source.json').write_text(json.dumps(meta,indent=2)+'\n')
print(out,flush=True)
