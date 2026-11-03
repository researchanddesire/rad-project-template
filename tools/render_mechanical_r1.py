"""Render actual R1 mesh exports for assembly and close-view inspection.

The engineering image uses native exported triangles. Colored component and
wire solids are packaging reservations, not a photographed prototype.
"""
from pathlib import Path
import json
import struct
import numpy as np
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[1]
CAD=ROOT/'hardware/cad/prototype-r1'
OUT=ROOT/'developer-docs/docs/assets/prototype-r1'
OUT.mkdir(parents=True,exist_ok=True)
report=json.loads((CAD/'geometry-report.json').read_text())
names=report['native_view_state']['visible_final_objects']
FONT='/System/Library/Fonts/Supplemental/Arial.ttf'
BOLD='/System/Library/Fonts/Supplemental/Arial Bold.ttf'
LIGHT=np.array([-.4,.7,1.0]);LIGHT/=np.linalg.norm(LIGHT)

def mesh(name,section=False):
 p=CAD/(name+('-section' if section and (CAD/(name+'-section.stl')).exists() else '')+'.stl')
 data=p.read_bytes();n=struct.unpack_from('<I',data,80)[0]
 assert len(data)==84+50*n,p
 return np.frombuffer(data,dtype=np.dtype([('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')]),offset=84)['v'].astype(float)

def color(name):
 if name=='MetalBody':return(181,192,205)
 if any(w in name for w in ['Flange','CoverWith']):return(65,91,121)
 if any(w in name for w in ['Retainer','CaptureShim']):return(188,147,90)
 if any(w in name for w in ['Seal','Gasket','Tape','Liner']):return(47,141,113)
 if any(w in name for w in ['TBoard','TipPCB','PlacedComponent']):return(54,139,93)
 if 'Motor' in name:return(211,153,64)
 if 'Pack' in name:return(84,155,192)
 if 'Carrier' in name:return(211,209,186)
 if any(w in name for w in ['Corridor','Lead','Splice']):return(85,145,155)
 if any(w in name for w in ['Tip','Temperature']):return(153,109,157)
 return(115,126,140)

def label(d,x,y,s,size=22,bold=False,fill='#243449'):
 d.multiline_text((x,y),s,font=ImageFont.truetype(BOLD if bold else FONT,size),fill=fill,spacing=8)

def panel(canvas,box,title,selected,section=False,y_window=None,camera=(1.05,.2,1.75)):
 d=ImageDraw.Draw(canvas);x,y,w,h=box
 d.rounded_rectangle((x,y,x+w,y+h),radius=18,fill='#f5f7fa',outline='#dbe3ec',width=2)
 label(d,x+22,y+20,title,24,True)
 cam=np.array(camera);cam/=np.linalg.norm(cam)
 right=np.cross([0,1,0],cam);right/=np.linalg.norm(right);up=np.cross(cam,right)
 geometry=[]
 for name in selected:
  a=mesh(name,section)
  if y_window is not None:
   a=a[(a[:,:,1].max(axis=1)>=y_window[0])&(a[:,:,1].min(axis=1)<=y_window[1])]
   a=a.copy();a[:,:,1]=np.clip(a[:,:,1],*y_window)
  if len(a):geometry.append((name,a))
 allv=np.concatenate([a.reshape(-1,3) for _,a in geometry])
 u,v=allv@right,allv@up
 scale=min((w-80)/(u.max()-u.min()),(h-105)/(v.max()-v.min()))
 cx=x+w/2-(u.max()+u.min())/2*scale
 cy=y+55+(h-70)/2+(v.max()+v.min())/2*scale
 faces=[]
 for name,a in geometry:
  normals=np.cross(a[:,1]-a[:,0],a[:,2]-a[:,0]);n=np.linalg.norm(normals,axis=1)
  normals/=np.maximum(n[:,None],1e-12)
  shade=.58+.42*np.maximum(normals@LIGHT,0)
  pts=np.stack((cx+a@right*scale,cy-a@up*scale),axis=-1)
  for i in np.flatnonzero(normals@cam>0):
   faces.append((float(a[i].mean(axis=0)@cam),pts[i],tuple(int(c*shade[i])for c in color(name))))
 for _,p,c in sorted(faces,key=lambda v:v[0]):d.polygon([tuple(q)for q in p],fill=c)

canvas=Image.new('RGB',(1600,1120),'white');d=ImageDraw.Draw(canvas)
label(d,35,26,'R1 / complete assembly integration study',35,True)
label(d,36,83,'Actual native CAD meshes · body-mounted pack · single T-shaped XY board',23,fill='#5b6c7e')
panel(canvas,(30,140,755,735),'ASSEMBLED / exterior remains unapproved',
      [n for n in names if n in ['MetalBody','FlangeControlPorts','ServiceCoverWithDockPorts','SiliconeButtonBootReservations','DockContactReservations'] or n.startswith('CoverBolt')])
panel(canvas,(815,140,755,735),'SECTION / components, carrier and wire space',names,True)
d=ImageDraw.Draw(canvas)
label(d,36,903,'R0 → R1: neck Ø25 → Ø28 mm · base depth 31 → 27.5 mm + 2.5 mm cover',26,True)
label(d,36,952,'Flange profile: 38 mm / local 40 mm; control peak: 40.3 mm. Depth reduction is not a fit result.',21)
label(d,36,995,'Green PCB · blue battery reference · gold motor · beige carrier · teal wire corridors / seals',21,fill='#5b6c7e')
label(d,36,1042,'Engineering candidate: actual parts, tolerances, retention loads, sealing and body contact remain unqualified.',21,True,fill='#975d15')
canvas.save(OUT/'mechanical-r1.png')

close=Image.new('RGB',(1600,1030),'white');d=ImageDraw.Draw(close)
label(d,35,25,'R1 / joint, neck and tip inspection',35,True)
label(d,36,80,'Native exported meshes · close views are clipped visual inspections, not new geometry checks',22,fill='#5b6c7e')
panel(close,(30,135,755,735),'JOINT / retaining ring, fasteners and carrier',names,True,(-32,10))
panel(close,(815,135,755,735),'TIP / sensor, dielectric bond and wire route',names,True,(81,98))
d=ImageDraw.Draw(close)
label(d,36,903,'The geometry report records intersections, insertion bounds and source hashes independently.',23)
label(d,36,948,'No finished seal, thermal accuracy, screw load or physical assembly result follows from these views.',22,True,fill='#975d15')
close.save(OUT/'mechanical-r1-close.png')
print(OUT/'mechanical-r1.png');print(OUT/'mechanical-r1-close.png')
