"""Source-bound flange cradle/connector access geometry; no build release."""
from pathlib import Path
import sys,json,hashlib
from PIL import Image,ImageDraw,PngImagePlugin
import render_mechanical_r2 as draw
ROOT=Path(__file__).resolve().parents[1];P=Path(sys.argv[1]).resolve();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((P/'geometry-report.json').read_text());v=json.loads((P/'saved-review.json').read_text())
assert sha(P/'FlangeCradleR27.FCStd')==r['native_sha256']==v['native_sha256']and sha(P/'geometry-report.json')==v['geometry_report_sha256']
assert v['all_new_listed_screens_clear'];m=draw.NativeMeshes(P);m.expected=r['review_meshes_sha256'];old=draw.part_color
def color(n):
 if n.startswith('R17Mate_'):return (132,157,183)
 if n=='R17_U6':return (101,114,131)
 if n.startswith('R17_')or n=='FlangePCB_R17':return (56,134,91)
 if n in ['FlangeSupportHubR27','FlangeEndKeeperR27']:return (43,143,153)
 if n=='FlangeKeeperScrewEnvelopeR27':return (191,146,54)
 return old(n)
draw.part_color=color
def geom(names):return [(n,m.load(n),None)for n in names]
im=Image.new('RGB',(1720,1040),'white');d=ImageDraw.Draw(im)
draw.label(d,(32,22),'Rotated flange board with a retained loading path',35,True)
draw.label(d,(33,77),'R27D / two edge-facing header poses from R28A / exterior retained',23,fill=draw.MUTED)
flange=list(r['inverse_transformed_flange_roles'])
bb=[r['parts'].get(n,r['mates'].get(n))['bounds_xyz_mm']for n in flange]
spans=[max(q[i+3]for q in bb)-min(q[i]for q in bb)for i in range(3)]
support=['FlangeSupportHubR27','HubRight','HubBolt_1','HubBolt1','HubNut_1','HubNut1','FlangeEndKeeperR27','FlangeKeeperScrewEnvelopeR27']
draw.panel(im,(25,125,800,620),'POPULATED FLANGE','Covers/body omitted; radio still faces outboard',geom(flange+support),camera=(.45,-1.8,.8))
draw.panel(im,(850,125,845,620),'CRADLE AND END KEEPER','Board omitted to show the open rails and plug notches',geom(support),camera=(.8,-1.8,1.0))
d=ImageDraw.Draw(im)
draw.label(d,(33,775),'Teal: cradle integrated into the left capture hub, plus one removable end keeper.',23,True)
draw.label(d,(33,817),'Gold: one M1.6 x 6 screw allowance. Blue-grey: nominal plug bodies, directed toward board edges.',23)
draw.label(d,(33,861),f'Populated island: {spans[0]:.2f} mm X width / {spans[1]:.2f} mm Y / {spans[2]:.2f} mm Z, including new plug poses.',22)
draw.label(d,(33,905),'Native geometry and listed assembly/tool screens only. Actual fits, loads, RF and seals remain open.',22,fill=draw.MUTED)
draw.label(d,(33,949),'R28A is a placement correction: its PCB routing needs repair and DRC. This is not a build-ready circuit.',22,fill=draw.AMBER)
draw.label(d,(33,991),'Buttons, interboard flex/wires and flange compliance remain in development. Battery choice stays open.',21,fill=draw.MUTED)
m.verify();out=ROOT/'developer-docs/docs/assets/prototype-r2/flange-cradle-r27-d.png'
meta={'native_sha256':r['native_sha256'],'geometry_report_sha256':sha(P/'geometry-report.json'),'saved_review_sha256':sha(P/'saved-review.json'),'placement_R28_native_sha256':r['placement_R28_native_sha256'],'renderer_sha256':sha(Path(__file__)),'render_library_sha256':sha(ROOT/'tools/render_mechanical_r2.py'),'review_meshes_sha256':m.used,'display_translations':{},'scope':'Saved native meshes. Covers/body omitted; no false section surfaces or display translations. Geometry candidate only: source PCB routing incomplete, no working button/flex/material/load/seal/RF or physical acceptance.'}
info=PngImagePlugin.PngInfo();info.add_text('SourceHashes',json.dumps(meta,sort_keys=True));im.save(out,pnginfo=info);out.with_name(out.stem+'-source.json').write_text(json.dumps(meta,indent=2)+'\n');print(out,flush=True)
