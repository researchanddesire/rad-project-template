"""Render source-bound native R31 meshes with a true Boolean section."""
from pathlib import Path
import sys,json,hashlib
import numpy as np
from PIL import Image,ImageDraw,PngImagePlugin
import render_mechanical_r2 as draw
ROOT=Path(__file__).resolve().parents[1];P=Path(sys.argv[1]).resolve();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();r=json.loads((P/'geometry-report.json').read_text());v=json.loads((P/'saved-review.json').read_text());screen=json.loads((P/'assembly-screen.json').read_text());assert sha(P/'ButtonsR31.FCStd')==r['native_sha256']==v['native_sha256']==screen['native_sha256']and not v['unexpected_intersections']and screen['all_listed_screens_clear']
a=draw.NativeMeshes(P);a.expected=dict(v['meshes_sha256'],**v['section_meshes_sha256']);original=draw.part_color
def colour(n):
 if n=='ButtonBootR31':return(176,113,161)
 if 'Plunger' in n:return(207,161,73)
 if 'Pin' in n or 'Screw' in n:return(161,172,184)
 if 'Keeper' in n:return(164,135,77)
 if n in ['ButtonServiceCoverR31','ButtonBezelR31','ButtonSupportHubR31']:return(93,142,155)
 if n.startswith('InterboardWire'):return(178,117,65)
 if n=='FlangePCB_R17':return(59,139,93)
 return original(n)
draw.part_color=colour
names=['ButtonSupportHubR31','ButtonKeeperR31','FlangeAnchorPadR30','FlangePCB_R17','R17_SW1','R17_SW2','R17Mate_J7','ButtonPlungerR31_SW1','ButtonPlungerR31_SW2','ButtonHomePinR31_SW1','ButtonHomePinR31_SW2','ButtonStopScrewR31_SW1','ButtonStopScrewR31_SW2']+['InterboardWireR29_'+str(i)for i in range(1,11)]
overview=[]
for n in names:
 m=a.load(n)
 if n=='ButtonSupportHubR31':m=m[((m[:,:,0]<-11)&(m[:,:,1]<-12)).all(axis=1)]
 if n.startswith('InterboardWire'):m=m[((m[:,:,1]<-14)&(m[:,:,0]<-10)&(m[:,:,2]>0)).all(axis=1)]
 overview.append((n,m,None))
section=[(n.removesuffix('-section.stl'),a.load(n.removesuffix('-section.stl'),section=True,require_section=True),None)for n in v['section_meshes_sha256']]
im=Image.new('RGB',(1800,1200),'white');d=ImageDraw.Draw(im);draw.label(d,(33,25),'Silicone buttons on the upright flange board',36,True);draw.label(d,(33,82),'R31D / separate body and flange boards / unchanged flange width and independent shell-mounted motor',23,fill=draw.MUTED)
draw.panel(im,(25,125,850,660),'INSIDE THE FLANGE','Cover and skin omitted; hub and long wires cropped',overview,camera=(.65,-1.3,.8))
draw.panel(im,(925,125,850,660),'ONE BUTTON / NATIVE SECTION','Gold: plunger. Purple: silicone. Teal: cover and guide.',section,camera=(-1,-.08,.05))
d=ImageDraw.Draw(im);draw.label(d,(33,822),'The wire rise passes between the buttons. Integral locating lands support the PCB without loose shims.',24,True);draw.label(d,(33,867),'A cross-pin sets the free position; a separate adjustable stop routes excess push into the cover.',24);draw.label(d,(33,913),'The 0.58 mm position is a CAD study. Set operating travel only after switch and assembled-button tests.',23,fill=draw.AMBER);draw.label(d,(33,959),'Retainer, boot and two plungers form one removable cover module. The keeper still uses its existing screw.',23);draw.label(d,(33,1005),'Silicone return/sealing, actual stop faces/threads, board fit and wire handling remain first-build checks.',23,fill=draw.MUTED);draw.label(d,(33,1051),'Geometry is digitally checked; the design has not been physically assembled. Battery selection stays open.',23,fill=draw.MUTED);draw.label(d,(33,1102),'The complete prototype proposal is still being finished: remaining harnesses, pack retention, flange loads and seals.',22,fill=draw.MUTED)
a.verify();meta={'native_sha256':r['native_sha256'],'geometry_report_sha256':sha(P/'geometry-report.json'),'saved_review_sha256':sha(P/'saved-review.json'),'assembly_screen_sha256':sha(P/'assembly-screen.json'),'native_meshes_sha256':a.used,'native_section_bounds_xyz_mm':v['section_crop_bounds_xyz_mm'],'triangle_crops':{'hub':'All triangle verticesX<-11,Y<-12','wires':'All verticesY<-14,X<-10,Z>0. Open crops without new cap faces.'},'display_translations':{},'renderer_sha256':sha(Path(__file__)),'render_library_sha256':sha(ROOT/'tools/render_mechanical_r2.py'),'scope':'Native mesh/Boolean section figure, no image generation or physical test. Covers/remote parts omitted only as labelled.'};out=ROOT/'developer-docs/docs/assets/prototype-r2/buttons-r31-d.png';info=PngImagePlugin.PngInfo();info.add_text('SourceHashes',json.dumps(meta,sort_keys=True));im.save(out,pnginfo=info);out.with_name(out.stem+'-source.json').write_text(json.dumps(meta,indent=2)+'\n');print(out,flush=True)
