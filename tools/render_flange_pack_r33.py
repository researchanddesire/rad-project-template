"""Source-bound R33 layout and sensor-section figure, no fabricated geometry."""
from pathlib import Path
import sys,json,hashlib
import numpy as np
from PIL import Image,ImageDraw,PngImagePlugin
import render_mechanical_r2 as draw
ROOT=Path(__file__).resolve().parents[1];P=Path(sys.argv[1]).resolve();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();r=json.loads((P/'geometry-report.json').read_text());v=json.loads((P/'saved-review.json').read_text());c=json.loads((P/'display-context.json').read_text());f=json.loads((P/'freeplay-review.json').read_text());assert sha(P/'FlangePackR33.FCStd')==r['native_sha256']==v['native_sha256']==c['native_sha256']==f['native_sha256'];assert v['all_listed_screens_clear']and f['all_six_probes_frame_before_sensors_and_cover'];a=draw.NativeMeshes(P);a.expected=dict(v['meshes_sha256'],**v['native_Y_at_least_minus18_section_meshes_sha256'],**c['meshes_sha256'],**c['sensor_section_meshes_sha256']);rotation=np.array([[1,0,0],[0,0,1],[0,-1,0]]);original=draw.part_color
def colour(n):
 if n=='PackSupportHubR33'or n=='ButtonSupportHubR31':return(83,143,151)
 if n=='PackLidR33':return(181,145,73)
 if n=='PackPublishedGaugeR33':return(98,159,194)
 if n.startswith('PackNTCHead'):return(154,99,159)
 if n.startswith('PackNTCLead'):return(174,118,75)
 if n.startswith('PackNTCContact'):return(209,145,176)
 if n=='FlangePCB_R17':return(59,139,93)
 if n.startswith('R17_'):return(92,103,118)
 if 'Screw'in n:return(137,148,160)
 return original(n)
draw.part_color=colour
overview=[]
names=['PackSupportHubR33','PackPublishedGaugeR33','PackLidR33','PackLidScrewR33_1','PackLidScrewR33_2','FlangePCB_R17','ButtonSupportHubR31']+[n.removesuffix('.stl')for n in c['meshes_sha256']]
for n in names:overview.append((n,a.load(n)@rotation.T,None))
section=[]
for filename in c['sensor_section_meshes_sha256']:
 n=filename.removesuffix('-sensor-section.stl');section.append((n,a.load(n+'-sensor-section')@rotation.T,None))
im=Image.new('RGB',(1800,1130),'white');d=ImageDraw.Draw(im);draw.label(d,(33,25),'A real pack-size option fits opposite the flange PCB',35,True);draw.label(d,(33,80),'R33F / unchanged 90 mm flange, 15 mm neck, body PCB and shell-mounted motor / battery choice OPEN',23,fill=draw.MUTED)
draw.panel(im,(25,125,1000,590),'OPEN FLANGE / INSTALLED NATIVE GEOMETRY','Left: existing upright PCB. Right: pack-size reference and two-screw lid.',overview,camera=(.12,.38,2.5))
draw.panel(im,(1050,125,725,590),'ONE SENSOR / NATIVE SECTION','Cut through the lower sensor and front-floor window.',section,camera=(.35,2.5,.85))
d=ImageDraw.Draw(im);draw.label(d,(33,750),'The right hub gains an integral tray. Its original capture material is preserved; the tray is one solid.',24,True);draw.label(d,(33,796),'Load the pack module from the rear, fit the separate lid, then close the covers. The PCB stays independent.',23);draw.label(d,(33,842),'Blue: published 33 x 8 x 20 mm protected-pack body reference; leads and connector are not included.',23,fill=draw.AMBER);draw.label(d,(33,888),'Both sensors sit on the front face. Only their first 4.5 mm lead stubs and contact-film space are shown.',23);draw.label(d,(33,934),'Static, listed loading/cover positions and six rigid freeplay probes pass their recorded digital scopes.',23);draw.label(d,(33,980),'Pack choice, finished maxima/growth, full wiring, process/load, thermal and physical checks remain open.',23,fill=draw.MUTED);draw.label(d,(33,1026),'This is a geometry checkpoint toward the full prototype proposal. No pack was selected or purchased.',23,fill=draw.MUTED)
a.verify();meta={'native_sha256':r['native_sha256'],'geometry_report_sha256':sha(P/'geometry-report.json'),'saved_review_sha256':sha(P/'saved-review.json'),'freeplay_review_sha256':sha(P/'freeplay-review.json'),'context_report_sha256':sha(P/'display-context.json'),'native_meshes_sha256':a.used,'display_rotation':'All vertices Rx(-90deg): (x,y,z)->(x,z,-y). No relative transforms.','display_translations':{},'section':'Actual native Boolean clip X[14,32],Y[-28,-11],Z[-7,-3], no triangle clipping or fabricated faces. Overview body crop Y[-10,12], exterior/skins and remote parts omitted.','renderer_sha256':sha(Path(__file__)),'render_library_sha256':sha(ROOT/'tools/render_mechanical_r2.py'),'scope':'Published body-size gauge and physical/process envelopes, not selected/received/fitted pack or completed harness.'};out=ROOT/'developer-docs/docs/assets/prototype-r2/flange-pack-r33-f.png';info=PngImagePlugin.PngInfo();info.add_text('SourceHashes',json.dumps(meta,sort_keys=True));im.save(out,pnginfo=info);out.with_name(out.stem+'-source.json').write_text(json.dumps(meta,indent=2)+'\n');print(out,flush=True)
