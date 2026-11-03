"""Two power laps in one top-loaded comb, captured by the existing local lid."""
from pathlib import Path
import hashlib,itertools,json,sys
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'hardware/cad/power-retention-r39/mate-k';OUT=Path(sys.argv[1]).resolve();OUT.mkdir(parents=True,exist_ok=True);assert not any(OUT.iterdir());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();r=json.loads((P/'geometry-report.json').read_text());source=P/'PackMateCradleR39.FCStd';before=sha(source);assert before==r['native_sha256']and r['all_static_screens_clear']and r['new_single_solids'];D=A.openDocument(str(source));frame=r['local_frame'];rotation=A.Rotation(A.Vector(1,0,0),frame['rotation_X_degrees']);centre=A.Vector(*frame['centre_xyz_mm']);inverse=rotation.inverted()
def feature(n,s,label=None):
 o=D.addObject('PartDesign::Feature',n);o.Shape=s;o.Label=label or n;return o
def box(n,b):
 x,y,z,u,v,w=b;o=D.addObject('Part::Box',n);o.Length=u-x;o.Width=v-y;o.Height=w-z;o.Placement=A.Placement(centre+rotation.multVec(A.Vector(x,y,z)),rotation);return o
def cylinder(n,rad,L,point):
 o=D.addObject('Part::Cylinder',n);o.Radius=rad;o.Height=L;o.Placement=A.Placement(centre+rotation.multVec(A.Vector(*point)),A.Rotation(A.Vector(0,0,1),A.Vector(1,0,0)));return o
def fuse(n,items):
 o=D.addObject('Part::MultiFuse',n);o.Shapes=items;o.Refine=True;return o
def cut(n,base,tool):
 o=D.addObject('Part::Cut',n);o.Base=base;o.Tool=tool;o.Refine=True;return o
def volume(s):return 0. if s.isNull()else s.Volume
def overlap(a,b):
 u,v=a.BoundBox,b.BoundBox
 if any(min(getattr(u,k+'Max'),getattr(v,k+'Max'))<=max(getattr(u,k+'Min'),getattr(v,k+'Min'))+1e-7 for k in 'XYZ'):return 0.
 return volume(a.copy().common(b.copy()))
def inv(s):
 b=s.optimalBoundingBox(False,False);return {'valid':s.isValid(),'solids':len(s.Solids),'volume_mm3':s.Volume,'bounds_xyz_mm':[getattr(b,k)for k in ['XMin','YMin','ZMin','XMax','YMax','ZMax']]}
rows=[]
for i in [1,2]:
 s=D.getObject('PackPowerJointSpaceR39_'+str(i)).Shape.copy();b=s.optimalBoundingBox(False,False);p=inverse.multVec(s.CenterOfMass-centre);rows.append({'pin':i,'centre_local_XWT_mm':list(p),'X_min_mm':b.XMin,'X_max_mm':b.XMax})
assert abs(rows[0]['centre_local_XWT_mm'][2]-rows[1]['centre_local_XWT_mm'][2])<1e-7
t=rows[0]['centre_local_XWT_mm'][2];a=rows[0]['X_min_mm']-.45;b=rows[0]['X_max_mm']+.45;wlo=min(q['centre_local_XWT_mm'][1]for q in rows)-1.7;whi=max(q['centre_local_XWT_mm'][1]for q in rows)+1.7;roof=t+2.8
floor=box('PowerLapFloorR39',[a-1,wlo-.8,t-2.6,b+1,whi+.8,t-1.5]);platform=box('PowerLapPlatformR39',[a,wlo,t-1.8,b,whi,t]);strap=box('PowerLapBackStrapR39',[a+1.3,-1.,t-2.6,b,wlo+.2,t-1.5]);struts=[box('PowerLapCupStrutR39_'+str(i),[x,-1.,2.7,x+1.2,-.2,t-1.5])for i,x in enumerate([a+1.3,b-1.2],1)]
fences=[box('PowerLapEndFenceR39_'+str(i),[x,wlo-.8,t-2.6,u,whi+.8,roof-.2])for i,(x,u)in enumerate([(a-1,a-.2),(b+.2,b+1)],1)]+[box('PowerLapSideFenceR39_'+str(i),[a-1,x,t-2.6,b+1,u,roof-.2])for i,(x,u)in enumerate([(wlo-.8,wlo-.2),(whi+.2,whi+.8)],1)]
seats=[];ports=[];fence_ports=[];pads=[];budgets=[];entries=[]
for row in rows:
 i=row['pin'];w=row['centre_local_XWT_mm'][1];xmin,xmax=row['X_min_mm'],row['X_max_mm'];L=xmax-xmin
 seats.append(cylinder('PowerLapSeatToolR39_'+str(i),1.6,L+.1,[xmin-.05,w,t]));ports.append(cylinder('PowerLapWirePortToolR39_'+str(i),1.2,b-a+.2,[a-.1,w,t]));fence_ports.append(cylinder('PowerLapFencePortToolR39_'+str(i),1.8,b-a+2.2,[a-1.1,w,t]))
 entry=feature('PowerLapEntryConeToolR39_'+str(i),Part.makeCone(1.55,1.2,.4,centre+rotation.multVec(A.Vector(a,w,t)),A.Vector(1,0,0)));entries.append(entry)
 budgets.append(cylinder('RetainedPowerJointSpaceR39_'+str(i),1.4,L,[xmin,w,t]));budgets[-1].Label='D2.8x5.5 insulated power-lap process budget / supersedes sourceD2.5 target'
 outer=Part.makeCylinder(1.6,L-.4,centre+rotation.multVec(A.Vector(xmin+.2,w,t)),A.Vector(1,0,0));inner=Part.makeCylinder(1.4,L-.2,centre+rotation.multVec(A.Vector(xmin+.1,w,t)),A.Vector(1,0,0));pads.append(feature('PowerLapCuffTargetR39_'+str(i),outer.cut(inner),'0.20 radial compliant-wrap target / no selected material/preload'))
fence=cut('PowerLapFencesR39',fuse('PowerLapFenceBlankR39',fences),fuse('PowerLapFencePortsR39',fence_ports));base=D.getObject('RetainedPackMateLeftHubR39');comb_clear=box('PowerLapCombLoadingPocketR39',[a-.2,wlo-.2,t-.2,b+.2,whi+.2,roof+3.2]);bridge_clear=box('PowerLapBridgeLoadingPocketR39',[a+.1,1.5,roof-.2,b+2.6,whi+6.2,roof+1.2]);upright_clear=box('PowerLapUprightLoadingPocketR39',[b+1.,1.5,5.4,b+2.6,8.9,roof+1.2]);root_clear=box('PowerLapRootLoadingPocketR39',[b+1.,3.3,4.6,b+2.6,10.7,6.7]);elbow_clear=box('PowerLapElbowLoadingPocketR39',[b+1.,1.5,5.4,b+2.6,10.7,6.7]);relieved=cut('PowerLapRelievedSourceHubR39',base,fuse('PowerLapLoadingClearanceToolsR39',[comb_clear,bridge_clear,upright_clear,root_clear,elbow_clear]));tab_travel=box('PowerLapTabTravelClearanceR39',[-23.3,3.1,1.8,-18.7,whi+1.,5.8]);additions=cut('PowerLapTrimmedAdditionsR39',fuse('PowerLapAdditionsBlankR39',[floor,platform,strap,fence]+struts),tab_travel);hub=cut('PowerLapRetainingHubR39',fuse('PowerLapHubBlankR39',[relieved,additions]),fuse('PowerLapSeatAndPortToolsR39',seats+ports+entries))
comb=cut('PowerLapDropInCombR39',box('PowerLapCombBlankR39',[a,wlo,t,b,whi,roof]),D.getObject('PowerLapSeatAndPortToolsR39'));comb.Label='Top-loaded two-power-lap comb; captive under mate-lid bridge'
capbase=D.getObject('PackMateLidR39');upright=box('PowerLapLidUprightR39',[b+1.2,1.7,5.5,b+2.4,2.9,roof+1.]);root=box('PowerLapLidRootR39',[b+1.2,3.3,4.8,b+2.4,4.5,6.5]);elbow=box('PowerLapLidElbowR39',[b+1.2,1.7,5.5,b+2.4,4.5,6.5]);bridge=box('PowerLapLidBridgeR39',[a+.3,1.7,roof,b+2.4,whi,roof+1.]);cap=fuse('LapCapturingMateLidR39',[capbase,upright,root,elbow,bridge]);cap.Label='Local keyed mate lid and lap-comb bridge / same one screw'
D.recompute()
for obj in [hub,comb,cap]:print('build state',obj.Name,obj.State,'valid',obj.Shape.isValid(),'solids',len(obj.Shape.Solids),flush=True)
assert hub.Shape.isValid()and len(hub.Shape.Solids)==1;assert comb.Shape.isValid()and len(comb.Shape.Solids)==1;assert cap.Shape.isValid()and len(cap.Shape.Solids)==1
excluded=[base.Name,capbase.Name]+['PackPowerJointSpaceR39_'+str(i)for i in [1,2]];fixed={n:D.getObject(n).Shape.copy()for n in r['fixed_roles']+list(r['new_roles'])if n not in excluded};new={o.Name:o.Shape.copy()for o in [hub,cap,comb]+pads+budgets};hits=[];known=[];count=0
for n,s in new.items():
 for m,q in fixed.items():
  count+=1;v=overlap(s,q)
  if v<=1e-5:continue
  old=overlap(base.Shape,q)if n==hub.Name else overlap(capbase.Shape,q)if n==cap.Name else 0.;original=base.Shape if n==hub.Name else capbase.Shape if n==cap.Name else None;added=volume(s.copy().common(q.copy()).cut(original.copy()))if original is not None else v
  intended=False
  for i in [1,2]:
   if n=='RetainedPowerJointSpaceR39_'+str(i)and m in [p+'R39_'+str(i)for p in ['SpareMateLead','SpareMateBare','BodyPackPowerWire','BodyPackPowerBare','PackPowerSolderBridge']]:intended=True
  row={'a':n,'b':m,'intersection_mm3':v,'source_intersection_mm3':old,'added_intersection_mm3':added};(known if intended or old>1e-5 and added<1e-5 else hits).append(row)
 print('static',n,'hits',hits,flush=True)
for(n,s),(m,q)in itertools.combinations(new.items(),2):
 count+=1;v=overlap(s,q)
 if v>1e-5:hits.append({'a':n,'b':m,'intersection_mm3':v})
contacts=[{'pin':i,'joint_to_cuff_gap_mm':budgets[i-1].Shape.distToShape(pads[i-1].Shape)[0],'cuff_to_comb_gap_mm':pads[i-1].Shape.distToShape(comb.Shape)[0]}for i in [1,2]]
out=OUT/'RetainedPackPowerR39.FCStd';D.Label='R39 conditional mate and two power laps / one local lid screw / DEVELOPMENT';D.saveAs(str(out));result={'native_sha256':sha(out),'source_mate_K_sha256':before,'builder_sha256':sha(Path(__file__)),'new_roles':{n:inv(s)for n,s in new.items()},'fixed_roles':list(fixed),'replaced_roles':excluded,'static_pairs':count,'unexpected_intersections':hits,'named_inherited_or_own_process_interfaces':known,'all_static_screens_clear':not hits,'lap_local_geometry':{'frame':frame,'joints':rows,'comb_bounds_XWT_mm':[a,wlo,t,b,whi,roof],'lid_loading_axis_xyz':list(rotation.multVec(A.Vector(0,1,0))),'comb_loading_axis_xyz':list(rotation.multVec(A.Vector(0,0,1))),'insulated_joint_budget_D_mm':2.8,'cuff_radial_thickness_mm':.2,'nominal_axial_end_gap_mm':.05,'comb_side_gap_mm':.2,'comb_loading_lift_T_mm':3.,'comb_front_approach_W_mm':8.},'nominal_contacts':contacts,'scope':'Conditional mate plus two power laps retained by integral hub trough/fences, separate drop-in comb/two compliant wrap targets and one keyed local lid/screw. D2.8 joint budgets supersede D2.5 source targets; copper/wire routes and topology unchanged. Actual insulation/cuff/preload, mating retention/strength and connected loading remain unqualified; battery OPEN/BOM unchanged. Source broad hub-box loss remains explicit, not reclassified as conserved.'};(OUT/'geometry-report.json').write_text(json.dumps(result,indent=2)+'\n');A.closeDocument(D.Name);assert sha(source)==before;print('SAVED retained power clear',not hits,'contacts',contacts,flush=True)
