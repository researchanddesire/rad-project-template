"""Source-bound saved native view of the independent shell motor mount."""
from pathlib import Path
import sys,json,hashlib
from PIL import Image,ImageDraw,PngImagePlugin
import render_mechanical_r2 as draw
ROOT=Path(__file__).resolve().parents[1];P=Path(sys.argv[1]).resolve()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((P/'geometry-report.json').read_text());v=json.loads((P/'saved-review.json').read_text())
assert sha(P/'ShellMotorMountR25.FCStd')==r['native_sha256']==v['native_sha256']
assert sha(P/'geometry-report.json')==v['geometry_report_sha256']
assert not r['unexpected_intersections']
m=draw.NativeMeshes(P);m.expected=dict(r['review_meshes_sha256'],**v['side_section_meshes_sha256'])
old=draw.part_color
colors={'ShellMotorMountR25':(191,146,54),'PortedCarrierR20':(56,153,163),'PCBOnlyKeeperR25':(56,153,163),'MotorMaxEnvelope':(83,127,177),'MotorClampScrewR25':(134,145,157),'MotorClampNutR25':(134,145,157),'KeyedBodyR25':(180,192,204),'MotorSeatCapR25':(180,192,204),'MotorLeadFlareAllowanceR21':(204,109,113)}
def color(n):
 for key,value in colors.items():
  if n.startswith(key):return value
 return (71,128,87)if n.startswith('R17_')or n.endswith('PCB_R17')else old(n)
draw.part_color=color
def geom(names,section=False):
 return [(n,m.load(n+'-side-section'if section and n in ['KeyedBodyR25','MotorSeatCapR25','ShellMotorMountR25']else n),None)for n in names]
im=Image.new('RGB',(1720,1090),'white');d=ImageDraw.Draw(im)
draw.label(d,(32,22),'Motor to metal shell; separate PCB support',36,True)
draw.label(d,(33,77),'R25 independent mount / one-piece body, fuller nose and 15 mm neck retained',23,fill=draw.MUTED)
names=[n for n in r['parts']if n not in ['FlangeCoverUpper','ServiceCoverReference']]+list(r['allowances'])
draw.panel(im,(25,125,760,630),'INTEGRATED SIDE SECTION','Native X <= 0 cuts in shell, cap and motor clamp',geom(names,True),camera=(1.8,.02,.6))
close=['ShellMotorMountR25','MotorClampScrewR25','MotorClampNutR25','MotorMaxEnvelope','MotorLeadFlareAllowanceR21']
draw.panel(im,(810,125,885,630),'KEYED MOTOR MODULE','Full clamp; one M2 screw/nut budget',geom(close,False),camera=(1.8,.1,.6))
d=ImageDraw.Draw(im)
draw.label(d,(33,790),'Gold: metal motor mount. Teal: independent PCB carrier and keeper. Blue: motor envelope.',24,True)
draw.label(d,(33,836),'Proposed vibration path: motor clamp -> keyed flange -> metal body rim.',25,True)
draw.label(d,(33,882),'One motor-clamp screw/nut budget; nose-cap shoulder captures the mount independently.',23,fill=draw.MUTED)
draw.label(d,(33,928),'Nominal geometry and listed poses only. Clamp preload, cap stack and actual wires remain open.',22,fill=draw.AMBER)
draw.label(d,(33,974),'Battery OPEN. Material, process, physical fit and vibration transfer still need verification.',22,fill=draw.MUTED)
draw.label(d,(33,1020),'The complete prototype build proposal remains in development.',23,fill=draw.MUTED)
m.verify();out=ROOT/'developer-docs/docs/assets/prototype-r2'/('motor-shell-r25-'+P.name.removeprefix('candidate-')+'.png')
meta={'native_sha256':r['native_sha256'],'geometry_report_sha256':sha(P/'geometry-report.json'),'saved_review_sha256':sha(P/'saved-review.json'),'renderer_sha256':sha(Path(__file__)),'render_library_sha256':sha(ROOT/'tools/render_mechanical_r2.py'),'review_meshes_sha256':m.used,'display_translations':{},'scope':'Native source-bound meshes and owner-exported side sections. Motor/part envelopes and assembly proposal, not actual parts, contact/preload, loads or vibration validation.'}
info=PngImagePlugin.PngInfo();info.add_text('SourceHashes',json.dumps(meta,sort_keys=True));im.save(out,pnginfo=info);out.with_name(out.stem+'-source.json').write_text(json.dumps(meta,indent=2)+'\n');print(out,flush=True)
