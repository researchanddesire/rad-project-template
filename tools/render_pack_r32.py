"""Source-bound pack retention view and actual native X<=0 section."""
from pathlib import Path
import sys,json,hashlib
import numpy as np
from PIL import Image,ImageDraw,PngImagePlugin
import render_mechanical_r2 as draw
ROOT=Path(__file__).resolve().parents[1];P=Path(sys.argv[1]).resolve();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();r=json.loads((P/'geometry-report.json').read_text());v=json.loads((P/'saved-review.json').read_text());s=json.loads((P/'assembly-screen.json').read_text());f=json.loads((P/'freeplay-review.json').read_text());assert sha(P/'PackRetentionR32.FCStd')==r['native_sha256']==v['native_sha256']==s['native_sha256']==f['native_sha256']and s['all_listed_screens_clear']and f['all_six_translation_probes_keep_sensors_out_of_first_contact']
close=json.loads((P/'close-view-meshes.json').read_text());assert close['native_sha256']==r['native_sha256']and close['saved_review_sha256']==sha(P/'saved-review.json')
a=draw.NativeMeshes(P);a.expected=dict(v['new_meshes_sha256'],**v['native_X_nonpositive_section_meshes_sha256'],**close['meshes_sha256']);old=draw.part_color
def colour(n):
 if n=='PackRetainingCarrierR32':return(78,145,153)
 if n=='PackLidR32':return(181,145,73)
 if n=='PackSizeGaugeR32':return(98,159,194)
 if n.startswith('PackNTCHead'):return(154,99,159)
 if n.startswith('PackNTCLead'):return(174,118,75)
 if n.startswith('PackNTCContact'):return(209,145,176)
 if 'Screw' in n:return(137,148,160)
 return old(n)
draw.part_color=colour
exploded=[];offsets={};rotation=np.array([[1,0,0],[0,0,1],[0,-1,0]])
for n in r['new_roles']:
 d=[0,0,0]
 if n in s['module_roles']:d=[0,0,6]
 if n in ['PackLidR32','PackLidScrewEnvelopeR32']:d=[0,0,12]
 offsets[n]=d;mesh=a.load(n+'-close'if n=='PackRetainingCarrierR32'else n);exploded.append((n,(mesh+np.array(d))@rotation.T,None))
section=[]
for name in v['native_X_nonpositive_section_meshes_sha256']:
 n=name.removesuffix('-section.stl');mesh=a.load(n+'-close'if n=='PackRetainingCarrierR32'else n,section=True,require_section=True);section.append((n,mesh@rotation.T,None))
im=Image.new('RGB',(1800,1180),'white');d=ImageDraw.Draw(im);draw.label(d,(33,25),'A separate pack lid; clearance around both sensors',35,True);draw.label(d,(33,80),'R32E / one pack-lid screw / PCB keeper and shell-mounted motor unchanged / battery choice OPEN',23,fill=draw.MUTED)
draw.panel(im,(25,125,850,640),'PACK MODULE AND ONE-SCREW LID','Frame cropped; pack +6 mm Z, lid/screw +12 mm Z',exploded,camera=(1.1,1.5,.8))
draw.panel(im,(925,125,850,640),'INSTALLED / NATIVE X <= 0 SECTION','PCB omitted. Blue: size gauge. Purple: sensor-head envelope.',section,camera=(1.8,.15,-.05))
d=ImageDraw.Draw(im);draw.label(d,(33,804),'Load the pack module, lower and slide its lid into the rear tongues, then fit one screw.',24,True);draw.label(d,(33,850),'The PCB and its original keeper load afterward. Lid preload is intended to react through the outboard post.',24);draw.label(d,(33,896),'The 18 x 33 x 6 mm block is a size gauge. Match the holder to the chosen protected pack and its limits.',23,fill=draw.AMBER);draw.label(d,(33,942),'Six sampled freeplay probes reach the frame before the head/lead allowances; actual soft-pack loads need test.',23);draw.label(d,(33,988),'Only the first 4.5 mm of sensor leads is shown. Full pack/NTC wiring, tape/bond and thermal response remain open.',22,fill=draw.MUTED);draw.label(d,(33,1034),'No battery was selected or purchased. Digital geometry does not establish swelling, vibration or physical retention.',22,fill=draw.MUTED);draw.label(d,(33,1080),'The complete prototype proposal is still being finished, including remaining harnesses, flange loads and seals.',22,fill=draw.MUTED)
a.verify();meta={'native_sha256':r['native_sha256'],'geometry_report_sha256':sha(P/'geometry-report.json'),'saved_review_sha256':sha(P/'saved-review.json'),'assembly_screen_sha256':sha(P/'assembly-screen.json'),'freeplay_review_sha256':sha(P/'freeplay-review.json'),'native_meshes_sha256':a.used,'close_view_meshes_sha256':sha(P/'close-view-meshes.json'),'display_translations_xyz_mm':offsets,'display_rotation_after_translations':'All vertices Rx(-90deg): (x,y,z)->(x,z,-y), to put the native long axis horizontally. No relative rotation of parts.','section':'Exact source-native Boolean X<=0 mesh exports and Y33.8..71 carrier crop, no triangle clipping or invented cut faces','renderer_sha256':sha(Path(__file__)),'render_library_sha256':sha(ROOT/'tools/render_mechanical_r2.py'),'scope':'CAD/gauge and sensor-envelope geometry only. Contact-film box is a process reservation, not a formed bond or proven thermal contact. No pack/supplier/material/process/physical acceptance.'};out=ROOT/'developer-docs/docs/assets/prototype-r2/pack-retention-r32-e.png';info=PngImagePlugin.PngInfo();info.add_text('SourceHashes',json.dumps(meta,sort_keys=True));im.save(out,pnginfo=info);out.with_name(out.stem+'-source.json').write_text(json.dumps(meta,indent=2)+'\n');print(out,flush=True)
