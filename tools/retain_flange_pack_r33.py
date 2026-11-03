"""R33: separate right-wing pack tray; body PCB and independent motor preserved.

Published protected-pack body reference only, battery selection OPEN. Source
NTC envelopes/guards are reoriented onto the front face, not load stops.
"""
from pathlib import Path
import sys,json,hashlib,itertools
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'hardware/cad/pack-retention-r32/candidate-e';OUT=Path(sys.argv[1]).resolve();OUT.mkdir(parents=True,exist_ok=True);assert not any(OUT.iterdir())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text());r=read(P/'geometry-report.json');f=P/'PackRetentionR32.FCStd';before=sha(f);assert before==r['native_sha256'];D=A.openDocument(str(f))
def box(n,b):
 x,y,z,u,v,w=b;o=D.addObject('Part::Box',n);o.Length=u-x;o.Width=v-y;o.Height=w-z;o.Placement.Base=A.Vector(x,y+1,z);return o
def cyl(n,rad,x,y,z,L):
 o=D.addObject('Part::Cylinder',n);o.Radius=rad;o.Height=L;o.Placement=A.Placement(A.Vector(x,y+1,z),A.Rotation(A.Vector(0,0,1),A.Vector(0,1,0)));return o
def feature(n,s,label):
 o=D.addObject('PartDesign::Feature',n);o.Shape=s;o.Label=label;return o
def fuse(n,ls):
 o=D.addObject('Part::MultiFuse',n);o.Shapes=ls;o.Refine=True;return o
def cut(n,a,b):
 o=D.addObject('Part::Cut',n);o.Base=a;o.Tool=b;o.Refine=True;return o
def inv(s):
 b=s.optimalBoundingBox(False,False);return {'valid':s.isValid(),'solids':len(s.Solids),'volume_mm3':s.Volume,'bounds_xyz_mm':[getattr(b,k)for k in ['XMin','YMin','ZMin','XMax','YMax','ZMax']]}
def vol(a,b):
 u,v=a.BoundBox,b.BoundBox
 if any(min(getattr(u,k+'Max'),getattr(v,k+'Max'))<=max(getattr(u,k+'Min'),getattr(v,k+'Min'))+1e-7 for k in 'XYZ'):return 0.
 return a.copy().common(b.copy()).Volume
matrix=A.Matrix();matrix.A11=0;matrix.A12=1;matrix.A13=0;matrix.A21=0;matrix.A22=0;matrix.A23=-1;matrix.A31=-1;matrix.A32=0;matrix.A33=0;rot=A.Rotation(matrix)
new=[];heads=[];stubs=[];films=[];reserves=[];guards=[];windows=[];sensorrows=[]
for i,z in [(1,-3.),(2,3.)]:
 source=A.Vector(*r['sensors'][i-1]['head_start_xyz_mm']);target=A.Vector(20.,-14.43,z);placement=A.Placement(target-rot.multVec(source),rot)
 def mapped(name):
  s=D.getObject(name).Shape.copy();s.Placement=placement.multiply(s.Placement);return s
 for prefix,roles in [('PackNTCHeadR32_',heads),('PackNTCContactFilmR32_',films)]:
  n=prefix+str(i);o=feature(n.replace('R32','R33'),mapped(n),'R33 reoriented source envelope / '+n);roles.append(o);new.append(o)
 for j in [1,2]:
  n='PackNTCLeadStubR32_'+str(i)+'_'+str(j);o=feature(n.replace('R32','R33'),mapped(n),'First4.5mm factory lead only / not trim length');stubs.append(o);new.append(o)
 n='PackNTCMotionR32_'+str(i);reserves.append(feature(n.replace('R32','R33'),mapped(n),'NTC clearance reservation / not physical material'))
 windows.append(feature('PackNTCWindowR33_'+str(i),mapped('PackNTCWindowR32_'+str(i)),'Source guard window transformed'))
 guards.append(feature('PackGuardBlankR33_'+str(i),mapped('PackNTCGuardBlankR32_'+str(i)),'Source guard blank transformed'))
 sensorrows.append({'reference':'TH'+str(i),'head_start_xyz_mm':list(target),'head_axis_xyz':[1,0,0],'source_head_start_xyz_mm':list(source),'source_to_current_placement':list(placement.toMatrix().A),'first_straight_factory_lead_mm':4.5,'scope':'Same bounding head/lead/contact-film and clearance shapes, rigidly reoriented. Full factory leads/adapter unmodeled; bond/stress/thermal/vibration need qualification.'})
gauge=box('PackPublishedGaugeR33',[7,-25,-10,40,-17,10]);gauge.Label='Published33x8x20 body-size reference / NOT selected pack / excludes cable';new.append(gauge)
budget=box('PackSizingReservationR33',[6.5,-25.5,-10.5,40.5,-16.5,10.5]);budget.Label='.5mm engineering sizing budget / not controlled maxima or expansion approval';reserves.insert(0,budget)
framebits=[box('PackFrontFloorR33',[6.5,-16.4,-10.5,40.5,-15.6,10.5]),box('PackHubTieR33',[7,-16.4,-4,18,-12.5,4]),box('PackInnerEndStopR33',[5.9,-25.5,-5,6.4,-15.6,5]),box('PackOuterEndStopR33',[40.6,-25.5,-5,41.2,-15.6,5]),box('PackInnerFootR33',[5.9,-16.4,-5,7.2,-15.6,5]),box('PackOuterFootR33',[39.8,-16.4,-5,41.2,-15.6,5])]
for sign in [-1,1]:
 a,b=(10.6,11.2)if sign>0 else(-11.2,-10.6)
 framebits.append(box('PackSideRailR33_'+str(sign),[7,-25.5,a,37,-15.6,b]))
pilots=[];lidholes=[];lidbits=[box('PackLidCrossbarR33',[17,-26.4,-13.5,19,-25.6,13.5])];screws=[]
for i,z in [(1,-12.4),(2,12.4)]:
 framebits.append(cyl('PackLidPostR33_'+str(i),1.4,18,-25.6,z,10.0))
 framebits.append(box('PackPostTieR33_'+str(i),[16.6,-16.4,min(z,0),19.4,-15.6,max(z,0)]))
 pilots.append(cyl('PackLidPilotR33_'+str(i),.625,18,-25.7,z,6.2))
 tab=cyl('PackLidTabR33_'+str(i),2.,18,-26.4,z,.8);hole=cyl('PackLidHoleR33_'+str(i),.9,18,-26.5,z,1.0);lidbits.append(tab);lidholes.append(hole)
 screw=fuse('PackLidScrewR33_'+str(i),[cyl('PackLidShankR33_'+str(i),.8,18,-26.4,z,6.),cyl('PackLidHeadR33_'+str(i),1.6,18,-28.,z,1.6)]);screws.append(screw);new.append(screw)
for sign in [-1,1]:
 a,b=(9.4,10.5)if sign>0 else(-10.5,-9.4)
 lidbits.append(box('PackLidRailR33_'+str(sign),[7,-26.4,a,37,-25.6,b]))
blank=fuse('PackHubTrayBlankR33',[D.getObject('HarnessRightHubR30')]+framebits+guards)
tray=cut('PackSupportHubR33',blank,fuse('PackTrayToolsR33',windows+pilots));tray.Label='Right capture hub with integral pack tray / independent PCB and motor'
lid=cut('PackLidR33',fuse('PackLidBlankR33',lidbits),fuse('PackLidToolsR33',lidholes));lid.Label='Rear pack lid / two M1.6x6 candidates / no pouch preload';new.extend([tray,lid]);D.recompute()
parts={n:D.getObject(n)for n in r['parts']if not n.startswith('Pack')and n!='HarnessRightHubR30'};parts['TipReadyCarrierR26']=D.getObject('TipReadyCarrierR26');parts.update({o.Name:o for o in new});mates={n:D.getObject(n)for n in r['mates']};allowances={n:D.getObject(n)for n in r['allowances']};physical=dict(parts,**mates,**allowances)
for n,o in parts.items():assert o.Shape.isValid()and o.Shape.Volume>0,(n,inv(o.Shape))
known={tuple(sorted([tray.Name,o.Name]))for o in screws};unexpected=[];interfaces=[];seen=set();comparisons=0
for o in new:
 for n,p in physical.items():
  k=tuple(sorted([o.Name,n]))
  if o.Name==n or k in seen:continue
  seen.add(k);comparisons+=1;v=vol(o.Shape,p.Shape)
  if v>1e-5:
   row={'a':o.Name,'b':n,'intersection_mm3':v};(interfaces if k in known else unexpected).append(row)
 print('static',o.Name,flush=True)
module={o.Name for o in [gauge]+heads+stubs+films};rh=[];rc=0
for o in reserves:
 for n,p in physical.items():
  if n in module:continue
  rc+=1;v=vol(o.Shape,p.Shape)
  if v>1e-5:rh.append({'reservation':o.Name,'fixed':n,'intersection_mm3':v})
outpath=OUT/'FlangePackR33.FCStd';D.Label='R33 / right-wing pack / battery OPEN / DEVELOPMENT';D.saveAs(str(outpath))
conserved={}
for n,q in physical.items():
 if n in {o.Name for o in new}:continue
 s=D.getObject(n).Shape.copy();assert s.isValid();conserved[n]=inv(s)
hubold=D.getObject('HarnessRightHubR30').Shape.copy();removed=hubold.cut(tray.Shape.copy()).Volume
report={'native_sha256':sha(outpath),'source_R32_native_sha256':before,'builder_sha256':sha(Path(__file__)),'parts':{n:inv(o.Shape)for n,o in parts.items()},'mates':{n:inv(o.Shape)for n,o in mates.items()},'allowances':{n:inv(o.Shape)for n,o in allowances.items()},'co_moving_reservations':{o.Name:inv(o.Shape)for o in reserves},'new_roles':[o.Name for o in new],'module_roles':sorted(module),'sensors':sensorrows,'source_roles_unchanged':list(conserved),'source_right_hub_removed_mm3':removed,'tray_solids':len(tray.Shape.Solids),'new_physical_pairs':comparisons,'unexpected_intersections':unexpected,'named_candidate_screw_pilot_interfaces':interfaces,'rigid_reservation_pairs':rc,'unexpected_reservation_intersections':rh,'battery_selection':'OPEN','scope':'Native static flange-pack trial. Published reference body excludes lead/connector and lacks controlled maxima. Existing bodyPCB, flangePCB, exterior, 15mm neck, motor and current wires preserved. Old R32 body-pack additions superseded by source R26 carrier. No loading, full adapter/lead, soft pouch/growth, process/load, electrical/thermal/physical or whole-prototype acceptance.'}
(OUT/'geometry-report.json').write_text(json.dumps(report,indent=2)+'\n');print('SAVED',len(new),'unexpected',unexpected,'reservations',rh,'traySolids',len(tray.Shape.Solids),'hubRemoved',removed,flush=True)
A.closeDocument(D.Name);assert sha(f)==before
