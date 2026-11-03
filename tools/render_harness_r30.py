"""Source-bound internal anchor geometry; one stated display displacement."""
from pathlib import Path
import sys,json,hashlib
import numpy as np
from PIL import Image,ImageDraw,PngImagePlugin
import render_mechanical_r2 as draw
ROOT=Path(__file__).resolve().parents[1];P=Path(sys.argv[1]).resolve();SRC=ROOT/'hardware/cad/interboard-r29/candidate-e';BASE=ROOT/'hardware/cad/flange-controls-r27/candidate-d';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();r=json.loads((P/'geometry-report.json').read_text());v=json.loads((P/'saved-review.json').read_text());old=json.loads((SRC/'saved-review.json').read_text());base=json.loads((BASE/'geometry-report.json').read_text());assert sha(P/'HarnessSupportR30.FCStd')==r['native_sha256']==v['native_sha256']and v['all_new_static_keeper_capture_tool_screens_clear']
a=draw.NativeMeshes(P);a.expected=v['changed_role_meshes_sha256'];b=draw.NativeMeshes(SRC);b.expected=old['wire_review_meshes_sha256'];c=draw.NativeMeshes(BASE);c.expected=base['review_meshes_sha256'];original=draw.part_color

def colour(n):
 if n.endswith('AnchorPadR30'):return(173,105,170)
 if n=='HarnessKeeperR30':return(189,146,64)
 if n in ['HarnessLeftHubR30','HarnessRightHubR30']:return(91,146,157)
 if n.startswith('InterboardWireR29_'):return(180,122,60)
 if n in ['FlangePCB_R17','R17_J7']:return(59,139,93)
 if n.startswith('R17Mate_'):return(154,175,191)
 return original(n)
draw.part_color=colour
wire_names=['InterboardWireR29_'+str(i)for i in range(1,11)]
central=[];mesh=a.load('HarnessLeftHubR30');central.append(('HarnessLeftHubR30',mesh[(mesh[:,:,0]>-8).all(axis=1)],None));central.append(('CentralAnchorPadR30',a.load('CentralAnchorPadR30'),None))
for n in wire_names:
 mesh=b.load(n);central.append((n,mesh[((mesh[:,:,1]>-17)&(mesh[:,:,1]<-10)&(abs(mesh[:,:,0])<5)).all(axis=1)],None))
flange=[('HarnessKeeperR30',a.load('HarnessKeeperR30')+np.array([0,-6,0]),None),('FlangeAnchorPadR30',a.load('FlangeAnchorPadR30'),None),('R17Mate_J7',c.load('R17Mate_J7'),None)]
for n in wire_names:
 mesh=b.load(n);flange.append((n,mesh[((mesh[:,:,2]>7)&(mesh[:,:,1]<-14)&(mesh[:,:,0]<-20)).all(axis=1)],None))
im=Image.new('RGB',(1740,1100),'white');d=ImageDraw.Draw(im);draw.label(d,(33,25),'Harness anchors captured by the existing joints',35,True);draw.label(d,(33,81),'R30B / no extra screws / unchanged exterior, boards, wire paths and independent motor mount',23,fill=draw.MUTED)
draw.panel(im,(25,125,820,640),'CENTRAL ANCHOR','Right hub omitted; outboard cradle and long wires cropped',central,camera=(1.7,-1.0,.7))
draw.panel(im,(870,125,845,640),'FLANGE ANCHOR AND KEEPER','Wires cropped; keeper displaced 6 mm rearward',flange,camera=(.55,-1.2,1.3))
d=ImageDraw.Draw(im);draw.label(d,(33,799),'Purple: compliant pads molded around the wires. Teal: hub pocket. Gold: the extended one-screw keeper.',23,True);draw.label(d,(33,845),'Fresh saved review: 153 roles / 750 changed-part comparisons / zero unintended intersections.',23);draw.label(d,(33,889),'The keeper clears the fixed formed wires and pads at all 11 listed approach positions.',23);draw.label(d,(33,933),'Close the hubs with loose flange ends parked straight; form and terminate the flange loop afterward.',22,fill=draw.AMBER);draw.label(d,(33,977),'Pad capture is geometry only. External cure, insulation adhesion, pull/creep tests and actual fit remain open.',22,fill=draw.MUTED);draw.label(d,(33,1021),'No physical prototype, full connected service-motion result or completed build proposal is claimed. Battery stays open.',22,fill=draw.MUTED)
a.verify();b.verify();c.verify();meta={'native_sha256':r['native_sha256'],'geometry_report_sha256':sha(P/'geometry-report.json'),'saved_review_sha256':sha(P/'saved-review.json'),'source_R29_native_sha256':r['source_R29_native_sha256'],'changed_meshes_sha256':a.used,'R29_wire_meshes_sha256':b.used,'R27_context_meshes_sha256':c.used,'display_translations':{'HarnessKeeperR30':[0,-6,0]},'mesh_triangle_crops':{'central':'Left hub all triangle verticesX>-8; wires-17<Y<-10 and|X|<5.','flange_wires':'All triangle verticesZ>7,Y<-14,X<-20. Open crops without invented cap surfaces.'},'renderer_sha256':sha(Path(__file__)),'render_library_sha256':sha(ROOT/'tools/render_mechanical_r2.py'),'scope':'Saved native mesh geometry. Right hub/covers/body omitted; keeper display displacement stated. No material/bond, actual fixture/connected motion or physical acceptance.'};out=ROOT/'developer-docs/docs/assets/prototype-r2/harness-support-r30-b.png';info=PngImagePlugin.PngInfo();info.add_text('SourceHashes',json.dumps(meta,sort_keys=True));im.save(out,pnginfo=info);out.with_name(out.stem+'-source.json').write_text(json.dumps(meta,indent=2)+'\n');print(out,flush=True)
