"""Source-bound native mesh views of the R26 stationary tip and wire routing."""
from pathlib import Path
import sys,json,hashlib
from PIL import Image,ImageDraw,PngImagePlugin
import render_mechanical_r2 as draw
ROOT=Path(__file__).resolve().parents[1];P=Path(sys.argv[1]).resolve()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((P/'geometry-report.json').read_text());v=json.loads((P/'saved-review.json').read_text())
assert sha(P/'StationaryTipR26.FCStd')==r['native_sha256']==v['native_sha256']
assert sha(P/'geometry-report.json')==v['geometry_report_sha256']
assert v['all_new_listed_screens_clear']
m=draw.NativeMeshes(P);m.expected=r['review_meshes_sha256'];old=draw.part_color
colors={'TipReadyCarrierR26':(43,143,153),'StationaryTipCarrierR26':(43,143,153),'StationaryPickupShoeR26':(180,192,204),'TipClipFittedEnvelopeR26':(100,111,126),'TipDielectricBondR26':(164,113,167),'TipCapThermalGelR26':(199,169,203),'ShellMotorMountR25':(191,146,54),'PCBOnlyKeeperR25':(43,143,153),'MotorMaxEnvelope':(83,127,177),'KeyedBodyR25':(180,192,204),'MotorSeatCapR25':(180,192,204)}
def color(n):
 if n.startswith('TipWireR26_'):return (192,128,46)
 if n.startswith(('TipBareWireR26_','TipSolderAllowanceR26_')):return (196,157,125)
 for key,value in colors.items():
  if n.startswith(key):return value
 return (58,130,89)if n.startswith('R17_')or n.endswith('PCB_R17')else old(n)
draw.part_color=color
sectioned=['KeyedBodyR25','MotorSeatCapR25','ShellMotorMountR25','StationaryTipCarrierR26']
def geom(names,section=False):
 return [(n,m.load(n+'-side-section'if section and n in sectioned else n),None)for n in names]
im=Image.new('RGB',(1720,1120),'white');d=ImageDraw.Draw(im)
draw.label(d,(32,22),'Stationary tip sensor; separate motor load path',35,True)
draw.label(d,(33,76),'R26F / one-piece body, fuller nose and 15 mm neck / battery choice open',23,fill=draw.MUTED)
omit=['HubLeft','HubRight','HubBolt_1','HubBolt1','HubNut_1','HubNut1','FlangeCoverLower','FlangeCoverUpper','ServiceCoverReference','FlangePCB_R17']
flangerefs=['SW1','D1','SW2','U6','J4','F1','SW3','R37','R35','C32','SW4','R32','J7','C33','R33','R40','C31','R39','J1','R38','R31','R36','C34','R34']
names=[n for n in r['parts']if n not in omit and n not in ['R17_'+ref for ref in flangerefs]]
draw.panel(im,(25,125,800,650),'BODY INTERNALS','Native side sections; flange omitted for clarity',geom(names,True),camera=(1.8,.02,.6))
close=['StationaryTipCarrierR26','TipPCB','TipComponentEnvelope','StationaryPickupShoeR26','TipClipFittedEnvelopeR26','TipDielectricBondR26','TipCapThermalGelR26']+[n for n in r['parts']if n.startswith(('TipWireR26_','TipBareWireR26_','TipSolderAllowanceR26_'))]
draw.panel(im,(850,125,845,650),'TIP DETAIL','Cup section; shell and cap omitted',geom(close,True),camera=(1.8,.14,.5),focus_bounds=([-4.6,90.5,-6.3],[4.6,97,4.6]))
d=ImageDraw.Draw(im)
draw.label(d,(33,800),'Gold: independent shell motor clamp. Teal: electronics tray and detachable tip support.',23,True)
draw.label(d,(33,842),'Amber: four individual wire allowances. Purple: thermal bond / cap gel reservations.',23,True)
draw.label(d,(33,892),'Proposed heat path: metal cap -> gel -> stationary pickup -> dielectric bond -> thin sensor PCB.',23)
draw.label(d,(33,938),'Cap force is intended to bypass the PCB through the clip and cup; contact/load needs verification.',22,fill=draw.MUTED)
draw.label(d,(33,980),'Clip shown as fitted envelope. Wire exits, crimping, cure, sealing and physical assembly remain open.',22,fill=draw.AMBER)
draw.label(d,(33,1022),'Native geometry and finite assembly/tool screens only; complete prototype proposal still in development.',22,fill=draw.MUTED)
draw.label(d,(33,1064),'Semi-flex and a 90-degree flange board remain permitted; this checkpoint retains the existing flange pose.',21,fill=draw.MUTED)
m.verify();out=ROOT/'developer-docs/docs/assets/prototype-r2/tip-support-r26-f.png'
meta={'native_sha256':r['native_sha256'],'geometry_report_sha256':sha(P/'geometry-report.json'),'saved_review_sha256':sha(P/'saved-review.json'),'renderer_sha256':sha(Path(__file__)),'render_library_sha256':sha(ROOT/'tools/render_mechanical_r2.py'),'review_meshes_sha256':m.used,'display_translations':{},'scope':'Saved native meshes, owner-exported side sections and image viewport crop. Components, materials and interfaces are allowances/candidates. No actual wire, clip, adhesive/cure, installed thermal/electrical, assembly/load or physical validation.'}
info=PngImagePlugin.PngInfo();info.add_text('SourceHashes',json.dumps(meta,sort_keys=True));im.save(out,pnginfo=info);out.with_name(out.stem+'-source.json').write_text(json.dumps(meta,indent=2)+'\n');print(out,flush=True)
