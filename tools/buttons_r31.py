"""Adjustable two-button prototype cassette on current R30 geometry.

The nominal stop is a study setting, not published switch overtravel. Silicone
response, unit calibration, PCB seating and actual thread/process need bench
work. No circuit/BOM or exterior-envelope expansion.
"""
from pathlib import Path
import sys,json,hashlib,itertools
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part
from tip_wire_native_r26 import edges_from_plan
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'hardware/cad/harness-support-r30/candidate-b';OUT=Path(sys.argv[1]).resolve();OUT.mkdir(parents=True,exist_ok=True);assert not any(OUT.iterdir());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text());r=read(SRC/'geometry-report.json');nf=SRC/'HarnessSupportR30.FCStd';assert sha(nf)==r['native_sha256'];D=A.openDocument(str(nf));old={n:D.getObject(n).Shape.copy()for n in dict(r['parts'],**r['mates'],**r['allowances'])}
def box(n,b):
 x,y,z,u,v,w=b;o=D.addObject('Part::Box',n);o.Length=u-x;o.Width=v-y;o.Height=w-z;o.Placement.Base=A.Vector(x,y,z);return o
def cyl(n,R,x,y,z,L,axis=(0,1,0)):
 o=D.addObject('Part::Cylinder',n);o.Radius=R;o.Height=L;o.Placement=A.Placement(A.Vector(x,y,z),A.Rotation(A.Vector(0,0,1),A.Vector(*axis)));return o
def cone(n,R,S,x,y,z,L):
 o=D.addObject('Part::Cone',n);o.Radius1=R;o.Radius2=S;o.Height=L;o.Placement=A.Placement(A.Vector(x,y,z),A.Rotation(A.Vector(0,0,1),A.Vector(0,1,0)));return o
def fuse(n,ls):
 o=D.addObject('Part::MultiFuse',n);o.Shapes=ls;o.Refine=True;return o
def cut(n,a,b):
 o=D.addObject('Part::Cut',n);o.Base=a;o.Tool=b;o.Refine=True;return o
def rounded(n,b,R):
 a=box(n+'Blank',b);D.recompute();f=D.addObject('Part::Fillet',n);f.Base=a;f.Edges=[(i,R,R)for i in range(1,13)];return f
modified_existing=set();updated_plan=None
if len(sys.argv)>2:
 updated_path=Path(sys.argv[2]).resolve();updated_plan=read(updated_path);assert updated_plan['source_R30_native_sha256']==sha(nf)
 for q in updated_plan['wires']:
  assert q['guarded_minimum_centerline_radius_mm']>=4
  D.getObject('InterboardPathR29_'+str(q['pin'])).Shape=Part.Wire(edges_from_plan(q));modified_existing.add('InterboardWireR29_'+str(q['pin']))
 modified_existing.add('FlangeAnchorPadR30');D.recompute()
centres=[]
for ref in ['SW1','SW2']:
 q=r['parts']['R17_'+ref]['bounds_xyz_mm'];centres.append((ref,(q[0]+q[3])/2,(q[2]+q[5])/2))
Zstop=8.;study=.58;bosses=[];covertools=[];plungers=[];pins=[];stops=[];dynamic=[];spec=[]
# Recessed rigid retainer and continuous silicone lid. Rearward exposed
# envelope stays within the original service-cover surfaceY=-30.
bezelbase=rounded('ButtonBezelBlankR31',[-29.,-30.,0.,-7.,-28.,11.],.6)
bezeltools=[box('ButtonBezelBootCavityR31',[-24.8,-29.85,1.1,-11.8,-27.9,10.1])]
for k,(ref,x,z)in enumerate(centres):
 bezeltools.append(box('ButtonBezelWindowR31_'+ref,[x-2.7,-30.1,1.8,x+2.7,-29.84,9.4]))
covertools.extend([box('ButtonBezelSeatR31',[-29.1,-30.1,-.1,-6.9,-28.,11.1]),box('ButtonBootSealSeatR31',[-25.2,-28.01,.7,-11.4,-27.5,10.5]),box('ButtonDryCavityR31',[-24.05,-28.1,1.85,-12.55,-26.6,9.35])])
boots=[box('ButtonSkinR31',[-24.7,-29.8,1.2,-11.9,-29.35,10.]),cut('ButtonPerimeterWallR31',box('ButtonWallBlankR31',[-24.7,-29.8,1.2,-11.9,-27.5,10.]),box('ButtonWallVoidR31',[-24.,-29.9,1.9,-12.6,-27.4,9.3])),cut('ButtonInstalledRimR31',box('ButtonRimBlankR31',[-25.1,-28.,.8,-11.5,-27.5,10.4]),box('ButtonRimVoidR31',[-24.,-28.1,1.9,-12.6,-27.4,9.3])),box('ButtonDividerR31',[-18.6,-29.8,1.9,-18.1,-27.5,9.3])];boottools=[]
for ref,x,z in centres:
 # Plunger has an insulating narrow tip and a rigid stop arm. A separate
 # cross-pin sets the home datum without needing membrane adhesion.
 head=cyl('ButtonHeadR31_'+ref,1.7,x,-28.8,z,.7);stem=cyl('ButtonStemR31_'+ref,.9,x,-28.1,z,6.3);tip=cyl('ButtonTipR31_'+ref,.4,x,-21.8,z,.5);arm=box('ButtonArmR31_'+ref,[x-1.6,-28.3,z,x+1.6,-27.7,9.1]);blank=fuse('ButtonPlungerBlankR31_'+ref,[head,stem,tip,arm]);pinbore=cyl('ButtonPinBoreR31_'+ref,.39,x-2.,-23.1,z,4.,(1,0,0));access=cyl('ButtonCalibrationAccessR31_'+ref,.7,x,-28.5,Zstop,.9);plunger=cut('ButtonPlungerR31_'+ref,blank,fuse('ButtonPlungerToolsR31_'+ref,[pinbore,access]));pin=cyl('ButtonHomePinR31_'+ref,.4,x-1.5,-23.1,z,3.,(1,0,0));plungers.append(plunger);pins.append(pin);dynamic.extend([plunger,pin])
 bosses.extend([cyl('ButtonGuideBossR31_'+ref,1.5 if ref=='SW2'else 1.9,x,-25.52,z,2.02),cyl('ButtonStopBossR31_'+ref,1.6 if ref=='SW2'else 2.,x,-25.52,Zstop,2.82)])
 covertools.extend([cyl('ButtonGuideBoreR31_'+ref,1.,x,-28.2,z,5.),cyl('ButtonStopPilotR31_'+ref,.8,x,-28.2,Zstop,5.8)])
 rear=-27.7+study;stop=cyl('ButtonStopScrewR31_'+ref,1.,x,rear,Zstop,4.);stops.append(stop)
 boots.append(cyl('ButtonBootBossR31_'+ref,2.2,x,-29.8,z,2.))
 boottools.extend([cyl('ButtonHeadPocketR31_'+ref,1.8,x,-28.85,z,.85),cyl('ButtonBootStemPortR31_'+ref,1.1,x,-28.01,z,.4),box('ButtonBootArmChannelR31_'+ref,[x-1.7,-28.41,z-.1,x+1.7,-27.6,9.2])])
 spec.append({'switch':ref,'center_XZ_mm':[x,z],'press_direction_xyz':[0,1,0],'tip_home_Y_mm':-21.3,'actuator_top_Y_nominal_mm':-20.9125,'actuator_top_Y_range_from_height_only_mm':[-21.0625,-20.8125],'height_only_free_gap_mm':[.2375,.4875],'height_and_pretravel_operation_range_mm':[.2875,.8375],'study_stop_stroke_mm':study,'adjustment_capacity_mm':[.05,.95],'approved_overtravel_mm':None,'operational_stop_setting':'Per-unit bench calibration and qualification required; .58mm is CAD study only.'})
# Two countersunk retainer screws and matching pilot bosses, all flush.
fasteners=[]
for k,(x,z)in enumerate([(-26.8,1.8),(-9.2,9.)],1):
 bosses.append(cyl('ButtonRetainerBossR31_'+str(k),1.9,x,-25.52,z,1.32));covertools.append(cyl('ButtonRetainerPilotR31_'+str(k),.625,x,-28.1,z,4.1));bezeltools.extend([cyl('ButtonRetainerClearanceR31_'+str(k),.9,x,-30.1,z,2.3),cyl('ButtonRetainerRimClearanceR31_'+str(k),1.7,x,-30.1,z,.3),cone('ButtonRetainerCountersinkR31_'+str(k),1.7,.9,x,-29.8,z,.8)]);screw=fuse('ButtonRetainerScrewR31_'+str(k),[cyl('ButtonRetainerHeadR31_'+str(k),1.6,x,-30.,z,.2),cone('ButtonRetainerConeR31_'+str(k),1.6,.8,x,-29.8,z,.8),cyl('ButtonRetainerShankR31_'+str(k),.8,x,-29.,z,4.)]);fasteners.append(screw)
cover=cut('ButtonServiceCoverR31',fuse('ButtonCoverBlankR31',[D.getObject('ServiceCoverReference')]+bosses),fuse('ButtonCoverCutToolsR31',covertools));bezel=cut('ButtonBezelR31',bezelbase,fuse('ButtonBezelCutToolsR31',bezeltools));boot=cut('ButtonBootR31',fuse('ButtonBootBlankR31',boots),fuse('ButtonBootCutToolsR31',boottools));cover.Label='Service cover with two guides / M2 stop pilots / gasket and bezel seats';bezel.Label='Flush countersunk bezel / silicone strip retainer';boot.Label='Installed compressed silicone lid / material, return and seal unqualified'
# Integrated locating lands reduce nominal board play to0.05mm; finish/fit
# to the received board before button calibration. Contact overlaps only
#0.20mm of the native copper-free FR4 edge band, checked separately.
lands=[]
for name,z0,z1 in [('Upper',7.3125,7.7125),('Lower',-7.6875,-7.2875)]:
 back=[(-22.6,-13.)]if name=='Upper'else[(-22.6,-18.75),(-15.25,-13.)]
 front=[(-22.6,-13.)]if name=='Upper'else[(-22.6,-21.65),(-14.15,-13.)]
 for i,(a,b)in enumerate(back):lands.append(box('ButtonBackLandR31_'+name+str(i),[a,-18.2875,z0,b,-18.10,z1]))
 for i,(a,b)in enumerate(front):lands.append(box('ButtonFrontLandR31_'+name+str(i),[a,-19.525,z0,b,-19.3375,z1]))
lands.extend([box('ButtonUpperEdgeLandR31',[-22.6,-19.3125,7.5375,-13.,-18.3125,7.725]),box('ButtonLowerEdgeLandR31',[-22.6,-19.3125,-7.70,-13.,-18.3125,-7.5125]),box('ButtonInnerEndLandR31',[-12.275,-19.3125,-2.,-12.0875,-18.3125,2.])])
support=fuse('ButtonSupportHubR31',[D.getObject('HarnessLeftHubR30')]+lands)
keeperblank=fuse('ButtonKeeperBlankR31',[D.getObject('HarnessKeeperR30'),box('ButtonOuterEndLandR31',[-36.0125,-19.3125,7.1125,-35.825,-18.3125,7.5125])])
# Widen only the cup's upper wire exit. The complete lower keeper/fastener
# boss and the pad's end wall below Z11.49 remain source material. This is
# a local .40mm roof rim, not a qualified strength or molded-wall claim.
keeper=cut('ButtonKeeperR31',keeperblank,box('ButtonUpperExitReliefR31',[-23.5,-19.,11.49,-22.8,-13.9,12.3]))
D.recompute();replace={'ServiceCoverReference':cover.Name,'HarnessLeftHubR30':support.Name,'HarnessKeeperR30':keeper.Name};parts={n:D.getObject(n)for n in r['parts']if n not in replace};new={o.Name:o for o in [cover,bezel,boot,support,keeper]+plungers+pins+stops+fasteners};parts.update(new);new.update({n:D.getObject(n)for n in modified_existing});mates={n:D.getObject(n)for n in r['mates']};allowances={n:D.getObject(n)for n in r['allowances']}
def inv(s):
 b=s.optimalBoundingBox(False,False);return {'valid':s.isValid(),'solids':len(s.Solids),'volume_mm3':s.Volume,'bounds_xyz_mm':[getattr(b,k)for k in ['XMin','YMin','ZMin','XMax','YMax','ZMax']]}
for n,o in new.items():print('new',n,inv(o.Shape),flush=True)
output=OUT/'ButtonsR31.FCStd';D.Label='R31 / calibrated silicone button cassette / DEVELOPMENT';D.saveAs(str(output));out={'builder_sha256':sha(Path(__file__)),'source_R30_native_sha256':sha(nf),'source_R30_report_sha256':sha(SRC/'geometry-report.json'),'native_sha256':sha(output),'parts':{n:inv(o.Shape)for n,o in parts.items()},'mates':r['mates'],'allowances':r['allowances'],'new_roles':list(new),'replaced_roles':replace,'button_spec':spec,'modified_existing_roles':sorted(modified_existing),'updated_wire_plan_sha256':sha(updated_path)if updated_plan else None,'scope':'Adjustable prototype cassette/rest geometry and nominal study stop. No numeric B3U allowableOT inferred. Material/cure/return/registration/force/seal, actual threads/fasteners and per-unit calibration/test required; no operational acceptance. Source circuit/BOM/battery OPEN preserved.'}
conserved={}
for n,s in old.items():
 if n in replace or n in modified_existing:continue
 now=D.getObject(n).Shape;eq=s.exportBrepToString()==now.exportBrepToString();a,b=(0.,0.)if eq else(s.copy().cut(now.copy()).Volume,now.copy().cut(s.copy()).Volume);assert abs(a)<1e-4 and abs(b)<1e-4,(n,a,b);conserved[n]={'exact_BRep_equal':eq,'removed_mm3':a,'added_mm3':b}
out['source_roles_conserved']=conserved
named={tuple(sorted(replace.get(n,n)for n in [q['a'],q['b']]))for q in read(SRC/'saved-review.json')['named_unqualified_screw_pilot_interfaces']}
for (ref,x,z),plunger,pin,stop in zip(centres,plungers,pins,stops):named.add(tuple(sorted([plunger.Name,pin.Name])));named.add(tuple(sorted([cover.Name,stop.Name])))
for screw in fasteners:named.add(tuple(sorted([cover.Name,screw.Name])))
def vol(a,b):
 u,v=a.BoundBox,b.BoundBox
 if any(min(getattr(u,k+'Max'),getattr(v,k+'Max'))<=max(getattr(u,k+'Min'),getattr(v,k+'Min'))+1e-7 for k in 'XYZ'):return 0.
 return a.copy().common(b.copy()).Volume
hits=[];process=[];seen=set();pairs=0
for n,o in new.items():
 bad=[]
 for m,p in dict(parts,**mates,**allowances).items():
  key=tuple(sorted([n,m]))
  if n==m or key in seen:continue
  seen.add(key);pairs+=1;v=vol(o.Shape,p.Shape)
  if v<=1e-5:continue
  row={'a':n,'b':m,'intersection_mm3':v};(process if key in named else bad).append(row)
 hits+=bad;print('static',n,bad,flush=True)
out['new_pairs_tested']=pairs;out['unexpected_intersections']=hits;out['named_unqualified_pin_pilot_interfaces']=process;(OUT/'geometry-report.json').write_text(json.dumps(out,indent=2)+'\n');A.closeDocument(D.Name);assert sha(nf)==r['native_sha256'];print('saved',output,'unexpected',len(hits),flush=True)
