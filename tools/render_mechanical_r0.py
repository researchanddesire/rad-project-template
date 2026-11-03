"""Render native CAD mesh exports as a labeled assembly/section review image.

Uses the actual exported triangles, with an orthographic camera and flat
shading. This is an engineering review render, not a physical-fit test.
"""
from pathlib import Path
import json
import struct
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
CAD=ROOT/'hardware/cad/prototype-r0'
ASSETS=ROOT/'developer-docs/docs/assets/prototype-r0'
ASSETS.mkdir(parents=True,exist_ok=True)
FONT='/System/Library/Fonts/Supplemental/Arial.ttf'
BOLD='/System/Library/Fonts/Supplemental/Arial Bold.ttf'
canvas=Image.new('RGB',(1600,1130),'white')
draw=ImageDraw.Draw(canvas)


def text(x,y,s,size=22,bold=False,color='#243449'):
    font=ImageFont.truetype(BOLD if bold else FONT,size)
    draw.multiline_text((x,y),s,font=font,fill=color,spacing=8)


def triangles(name):
    data=(CAD/(name+'.stl')).read_bytes()
    count=struct.unpack_from('<I',data,80)[0]
    if len(data)!=84+50*count:
        raise ValueError(f'{name}: expected native binary STL')
    a=np.frombuffer(data,dtype=np.dtype([('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')]),offset=84)
    return a['v'].astype(float)


camera=np.array([1.05,.20,1.75]);camera/=np.linalg.norm(camera)
right=np.cross([0,1,0],camera);right/=np.linalg.norm(right)
up=np.cross(camera,right)
light=np.array([-.4,.7,1.0]);light/=np.linalg.norm(light)
colors={'MetalBody':(181,192,205),'FlangeWithBosses':(65,91,121),'ServiceCover':(82,108,139),
        'FrontRetainer':(188,147,90),'RearRetainer':(188,147,90),'FaceSealReservation':(47,141,113),
        'TBoardReservation':(54,139,93),'MotorReservation':(211,153,64),'PackReservation':(84,155,192),
        'CarrierGuideStudy':(211,209,186)}


def panel(x,section=False):
    draw.rounded_rectangle((x,160,x+748,918),radius=20,fill='#f5f7fa',outline='#dbe3ec',width=2)
    text(x+24,182,'SECTION / component reservations' if section else 'ASSEMBLED / selected Plan A',25,True)
    text(x+24,224,'One side removed to inspect the cavity.' if section else 'Hollow metal body and whole polymer flange.',19,color='#5b6c7e')
    names=list(colors) if section else ['MetalBody','FlangeWithBosses','ServiceCover']
    meshes=[]
    for name in names:
        fn=name+'-section' if section and name in ['MetalBody','FlangeWithBosses','ServiceCover'] else name
        meshes.append((name,triangles(fn)))
    allv=np.concatenate([v.reshape(-1,3) for _,v in meshes])
    pu,pv=allv@right,allv@up
    scale=min(620/(pu.max()-pu.min()),550/(pv.max()-pv.min()))
    cx=x+374-(pu.max()+pu.min())/2*scale
    cy=555+(pv.max()+pv.min())/2*scale
    faces=[]
    for name,vs in meshes:
        normals=np.cross(vs[:,1]-vs[:,0],vs[:,2]-vs[:,0])
        lengths=np.linalg.norm(normals,axis=1)
        normals/=np.maximum(lengths[:,None],1e-12)
        shade=.58+.42*np.maximum(normals@light,0)
        projected=np.stack((cx+vs@right*scale,cy-vs@up*scale),axis=-1)
        for i in np.flatnonzero(normals@camera>0):
            color=tuple(int(min(255,c*shade[i])) for c in colors[name])
            faces.append((float(vs[i].mean(axis=0)@camera),projected[i],color))
    for _,points,color in sorted(faces,key=lambda v:v[0]):
        draw.polygon([tuple(p) for p in points],fill=color)
    text(x+24,850,'No final wall, seal or fastening specification.' if not section else 'Green PCB · gold motor · blue battery study volume',18,color='#5b6c7e')
    text(x+24,880,'Body and flange dimensions are editable study inputs.',18,color='#5b6c7e')


text(36,32,'R0 / native prototype packaging',36,True)
text(38,86,'Assembly geometry developed around the T-shaped board insertion path.',23,color='#5b6c7e')
panel(32);panel(820,True)
report=json.loads((CAD/'geometry-report.json').read_text())
collision_count=len(report['collisions'])
passed=report['assembly_insertion']['passes_nominal_continuous_envelope']
text(38,954,f'CAD checks: {collision_count} intersecting reservation pairs · continuous insertion envelope '+('clear' if passed else 'needs revision'),24,True,color='#27745f' if collision_count==0 and passed else '#975d15')
text(38,1000,'These checks cover nominal dummy solids. Actual parts, wiring, tolerances, supports and seals still need fitting.',20,color='#5b6c7e')
text(38,1044,'Supplier feedback remains open on casting process, alloy, wall refinement, finish and joint design.',20,color='#5b6c7e')
text(38,1090,'DEVELOPMENT MODEL / not a fabrication release or body-contact validation',20,True,color='#975d15')
canvas.save(ASSETS/'mechanical-r0.png')
print(ASSETS/'mechanical-r0.png')
