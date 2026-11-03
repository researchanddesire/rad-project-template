"""Integrated X90 flange island, hub-mounted cradle and single end keeper."""
from pathlib import Path
import sys,json,hashlib,itertools
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part,MeshPart
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'hardware/cad/tip-support-r26/candidate-f';OUT=Path(sys.argv[2]).resolve();OUT.mkdir(parents=True,exist_ok=True);assert not any(OUT.iterdir())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
r=read(SRC/'geometry-report.json');nf=Path(sys.argv[1]).resolve();assert sha(nf)==r['native_sha256']
screenpath=ROOT/'hardware/cad/flange-controls-r27/placement-screen-a/orientation-screen.json';screen=read(screenpath)
assert screen['native_R26_sha256']==r['native_sha256'];chosen=next(q for q in screen['cases']if q['translation_xyz_mm']==[1.5,0,-.3]);assert not chosen['intersections']
D=A.openDocument(str(nf));base={n:D.getObject(n).Shape.copy()for n in dict(r['parts'],**r['mates'],**r['allowances'])}
centre=A.Vector(*screen['rotation_center_xyz_mm']);t=A.Placement(centre+A.Vector(1.5,0,-.3),A.Rotation(A.Vector(1,0,0),90)).multiply(A.Placement(-centre,A.Rotation()))
for n in screen['moving_roles']:
 o=D.getObject(n);o.Placement=t.multiply(o.Placement)
header_turns={};placement_source=None
if len(sys.argv)>3:
 placement_dir=Path(sys.argv[3]).resolve();placement_source=read(placement_dir/'placement-inspection.json')
 assert sha(placement_dir/'flange-r28.kicad_pcb')==placement_source['native_board_sha256']
 assert placement_source['all_24_ref_value_pad_net_maps_and_centres_conserved']and not placement_source['component_Fab_box_intersections']and not placement_source['same_face_courtyard_overlaps']and placement_source['all_nominal_mate_Fab_approaches_clear']
 for ref in ['J1','J7']:
  row=next(p for p in placement_source['placements']if p['ref']==ref);c=A.Vector(*row['xy_mm'],0);half=A.Placement(c,A.Rotation(A.Vector(0,0,1),180)).multiply(A.Placement(-c,A.Rotation()))
  header_turns[ref]=list(c)
  for n in ['R17_'+ref,'R17Mate_'+ref]:
   o=D.getObject(n);o.Placement=t.multiply(half).multiply(t.inverse()).multiply(o.Placement)
def box(n,b):
 x,y,z,u,v,w=b;o=D.addObject('Part::Box',n);o.Length=u-x;o.Width=v-y;o.Height=w-z;o.Placement.Base=A.Vector(x,y,z);return o
def cyl(n,rad,x,y,z,h):
 o=D.addObject('Part::Cylinder',n);o.Radius=rad;o.Height=h;o.Placement=A.Placement(A.Vector(x,y,z),A.Rotation(A.Vector(0,0,1),A.Vector(0,1,0)));return o
def fuse(n,ls):
 o=D.addObject('Part::MultiFuse',n);o.Shapes=ls;o.Refine=True;return o
def cut(n,a,b):
 o=D.addObject('Part::Cut',n);o.Base=a;o.Tool=b;o.Refine=True;return o
D.recompute();b=D.getObject('FlangePCB_R17').Shape.optimalBoundingBox(False,False);zlo,zhi=b.ZMin,b.ZMax;yf,yb=b.YMin,b.YMax
items=[box('FlangeBackplateR27',[-35.5,-14.5,zlo-1.4,-11.1,-13.5,zhi+1.4]),box('FlangeHubBridgeR27',[-13,-14.5,-5,-10.8,-11,5]),box('FlangeInnerEndstopR27',[b.XMax+.2,yf-.7,zlo-1.4,b.XMax+1.2,-13.5,zhi+1.4])]
for label,a,c,lip_a,lip_c in [('Lower',zlo-1.4,zlo-.2,zlo-1.4,zlo+.4),('Upper',zhi+.2,zhi+1.4,zhi-.4,zhi+1.4)]:
 items.extend([box('Flange'+label+'SideRailR27',[-35.5,yf-.7,a,b.XMax+1.2,-13.5,c]),box('Flange'+label+'RearSeatR27',[-35.5,yb+.2,lip_a,b.XMax+1.2,-13.5,lip_c]),box('Flange'+label+'FrontLipR27',[-35.5,yf-.7,lip_a,b.XMax+1.2,yf-.2,lip_c])])
boss_x=-20.5 if header_turns else -32.5
boss=cyl('FlangeKeeperBossBlankR27',1.8,boss_x,-18.8,9.1,5.3)
pilot=cyl('FlangeKeeperPilotR27',.625,boss_x,-18.9,9.1,5.5)
bossrelief=box('FlangeKeeperPCBReliefR27',[boss_x-2.5,-19,0,boss_x+2.5,yb+.2,zhi+.2])
items.append(cut('FlangeKeeperBossR27',boss,fuse('FlangeBossCutToolsR27',[pilot,bossrelief])))
blank=fuse('FlangeCradleBlankR27',[D.getObject('HubLeft')]+items)
keeperpocket=box('FlangeKeeperSeatPocketR27',[-36.95,-25,7.95,boss_x+1.85,-18.8,10.65])
plug=D.getObject('R17Mate_J4').Shape.optimalBoundingBox(False,False)
plugnotch=box('FlangeServicePlugNotchR27',[plug.XMin-.3,plug.YMin-.3,zlo-3,plug.XMax+.3,plug.YMax+.3,plug.ZMax+.3])
cuttools=[keeperpocket,plugnotch]
if header_turns:
 for ref in ['J1','J7']:
  v=D.getObject('R17Mate_'+ref).Shape.optimalBoundingBox(False,False);a,c=(zlo-4,v.ZMax+.3)if ref=='J1'else(v.ZMin-.3,zhi+5)
  cuttools.append(box('Flange'+ref+'EdgePlugNotchR27',[v.XMin-.3,v.YMin-.3,a,v.XMax+.3,v.YMax+.3,c]))
cradle=cut('FlangeSupportHubR27',blank,fuse('FlangeCradleCutToolsR27',cuttools));cradle.Label='Left capture hub with flange cradle / no PCB load path for body removal'
keeperblank=fuse('FlangeEndKeeperBlankR27',[box('FlangeKeeperBarR27',[-36.8,-19.8,8.1,boss_x+1.7,-18.8,10.5]),box('FlangeKeeperHookR27',[-36.8,yf-.8,zhi-.4,-36.0,-18.0,9.0])])
keeper=cut('FlangeEndKeeperR27',keeperblank,cyl('FlangeKeeperClearanceR27',.9,boss_x,-20,9.1,1.4));keeper.Label='Single removable outer end keeper / slide board in from wing'
screw=fuse('FlangeKeeperScrewEnvelopeR27',[cyl('FlangeKeeperScrewShaftR27',.8,boss_x,-19.8,9.1,6),cyl('FlangeKeeperScrewHeadR27',1.6,boss_x,-21.4,9.1,1.6)]);screw.Label='M1.6x6 candidate / headD3.2 allowance / polymer pilot unqualified'
D.recompute();parts={n:D.getObject(n)for n in r['parts']if n!='HubLeft'};parts.update({o.Name:o for o in [cradle,keeper,screw]});mates={n:D.getObject(n)for n in r['mates']};allowances={n:D.getObject(n)for n in r['allowances']}
def inv(s):
 b=s.optimalBoundingBox(False,False);return {'valid':s.isValid(),'solids':len(s.Solids),'volume_mm3':s.Volume,'bounds_xyz_mm':[getattr(b,k)for k in ['XMin','YMin','ZMin','XMax','YMax','ZMax']]}
def volume(a,b):
 u,v=a.BoundBox,b.BoundBox
 if any(min(getattr(u,k+'Max'),getattr(v,k+'Max'))<=max(getattr(u,k+'Min'),getattr(v,k+'Min'))+1e-7 for k in 'XYZ'):return 0.
 return a.copy().common(b.copy()).Volume
for n,o in dict(parts,**mates,**allowances).items():assert o.Shape.isValid()and len(o.Shape.Solids)==(2 if n=='TipComponentEnvelope'else 1),(n,inv(o.Shape))
preserved={};rotated={}
for n,s in base.items():
 if n=='HubLeft':continue
 now=D.getObject(n).Shape.copy()
 if n in screen['moving_roles']:
  now.Placement=t.inverse().multiply(now.Placement);target=rotated
  for ref,c0 in header_turns.items():
   if n in ['R17_'+ref,'R17Mate_'+ref]:
    c0=A.Vector(*c0);half=A.Placement(c0,A.Rotation(A.Vector(0,0,1),180)).multiply(A.Placement(-c0,A.Rotation()));now.Placement=half.inverse().multiply(now.Placement)
 else:target=preserved
 eq=s.exportBrepToString()==now.exportBrepToString();a,c=(0,0)if eq else(s.copy().cut(now.copy()).Volume,now.copy().cut(s.copy()).Volume)
 assert abs(a)<1e-4 and abs(c)<1e-4,(n,a,c);target[n]={'exact_BRep_equal':eq,'removed_mm3':a,'added_mm3':c}
assert D.getObject('HubLeft').Shape.copy().cut(cradle.Shape.copy()).Volume<1e-4
hits=[];named=[];same_net=[];pairs=0
oldnamed={tuple(sorted([q['a'],q['b']]))for q in r['named_unqualified_screw_pilot_interfaces']}
for (n,o),(m,p)in itertools.combinations(parts.items(),2):
 pairs+=1;v=volume(o.Shape,p.Shape)
 if v<=1e-5:continue
 row={'a':n,'b':m,'intersection_mm3':v}
 if tuple(sorted([n,m]))in oldnamed or set([n,m])==set([cradle.Name,screw.Name]):named.append(row)
 elif n.startswith(('TipWireR26_','TipBareWireR26_','TipSolderAllowanceR26_'))and m.startswith(('TipWireR26_','TipBareWireR26_','TipSolderAllowanceR26_'))and n.rsplit('_',1)[-1]==m.rsplit('_',1)[-1]:same_net.append(row)
 else:hits.append(row)
matehits=[]
for n,o in mates.items():
 for m,p in parts.items():
  v=volume(o.Shape,p.Shape)
  if v>1e-5:matehits.append({'mate':n,'fixed':m,'intersection_mm3':v})
print('static',pairs,'unexpected',hits,'mates',matehits,flush=True)
out={'builder_sha256':sha(Path(__file__)),'source_native_sha256':sha(nf),'source_report_sha256':sha(SRC/'geometry-report.json'),'placement_screen_sha256':sha(screenpath),'chosen_rotation':{'axis':[1,0,0],'angle_deg':90,'center_xyz_mm':list(centre),'translation_xyz_mm':[1.5,0,-.3]},'parts':{n:inv(o.Shape)for n,o in parts.items()},'mates':{n:inv(o.Shape)for n,o in mates.items()},'allowances':{n:inv(o.Shape)for n,o in allowances.items()},'preserved_roles':preserved,'inverse_transformed_flange_roles':rotated,'static_pairs_tested':pairs,'unexpected_intersections':hits,'named_unqualified_screw_pilot_interfaces':named,'same_net_solder_tail_interfaces':same_net,'nominal_mate_intersections':matehits,'cradle_interface':{'board_front_Y_mm':yf,'board_back_Y_mm':yb,'board_Z_span_mm':[zlo,zhi],'slot_side_clearance_mm':.2,'slot_front_back_clearance_each_mm':.2,'outer_keeper_side_gap_mm':b.XMin-(-36.0),'inner_endstop_gap_mm':.2,'pilot_diameter_mm':1.25,'candidate_fastener':'M1.6x6 / D3.2head envelope / 1.5hex reference; actual thread/pilot/retention unqualified'},'scope':'Integrated X90+inward1.5/down.3 flange, source circuit unchanged; left hub gains open rail cradle with one end keeper/screw allowance. R26 tip and independent motor mount preserved. No operational button mechanism, interboard wires/flex, service/dock leads, RF, load/compliance, seal or physical acceptance. BatteryOPEN.'}
output=OUT/'FlangeCradleR27.FCStd';D.Label='R27 / retained X90 flange candidate / controls and flex in development';D.saveAs(str(output));out['native_sha256']=sha(output)
out['local_header_half_turns']=header_turns;out['keeper_boss_X_mm']=boss_x
if placement_source:
 out['placement_R28_native_sha256']=placement_source['native_board_sha256'];out['placement_R28_inspection_sha256']=sha(placement_dir/'placement-inspection.json');out['electrical_status']='R28A changes header poses only. Source copper retained as reference; routing repair/native DRC required. This CAD is not an electrical build candidate.'
(OUT/'geometry-report.json').write_text(json.dumps(out,indent=2)+'\n')
# Island loads along+X from the outer wing before covers and end keeper fit.
moving={n:D.getObject(n).Shape for n in screen['moving_roles']if n not in mates};fixed={n:o.Shape for n,o in parts.items()if n not in set(moving)|{'FlangeCoverLower','FlangeCoverUpper','ServiceCoverReference',keeper.Name,screw.Name}}
loading=[]
for x in [-50,-40,-30,-20,-10,-5,-2,-1,-.5,-.25,0]:
 bad=[]
 for n,s0 in moving.items():
  s=s0.copy();s.translate(A.Vector(x,0,0))
  for m,p in fixed.items():
   v=volume(s,p)
   if v>1e-5:bad.append({'moving':n,'fixed':m,'intersection_mm3':v})
 loading.append({'X_offset_mm':x,'hits':bad});print('flange load',x,bad,flush=True)
out['island_listed_loading_poses']=loading
plugmotion=[]
mate_specs=placement_source['mates']if placement_source else read(ROOT/'hardware/pcb/stackup-r23/candidate-d/layout-inspection.json')['boards']['flange']['mates']
for q in mate_specs:
 n='R17Mate_'+q['ref'];direction=t.Rotation.multVec(A.Vector(*q['direction_xy'],0));fixed={m:o.Shape for m,o in dict(parts,**mates).items()if m not in [n,'FlangeCoverLower','FlangeCoverUpper','ServiceCoverReference']}
 for distance in [20,10,5,2,1,.5,.25,0]:
  s=mates[n].Shape.copy();s.translate(direction*distance);bad=[]
  for m,p in fixed.items():
   v=volume(s,p)
   if v>1e-5:bad.append({'fixed':m,'intersection_mm3':v})
  plugmotion.append({'mate':n,'outward_distance_mm':distance,'outward_direction_xyz':list(direction),'hits':bad})
out['nominal_mate_listed_approach_poses']=plugmotion;print('plug approach hits',[q for q in plugmotion if q['hits']],flush=True)
meshes={};section=Part.makeBox(200,250,100,A.Vector(-100,-100,-100))
for n,o in dict(parts,**mates,**allowances).items():
 for suffix,s in [('',o.Shape)]+([('-section',o.Shape.copy().common(section.copy()))]if n in [cradle.Name,'FlangeCoverLower','FlangeCoverUpper','ServiceCoverReference']else[]):
  if s.Volume<1e-6:continue
  f=OUT/(n+suffix+'.stl');MeshPart.meshFromShape(Shape=s,LinearDeflection=.04,AngularDeflection=.12,Relative=False).write(str(f));meshes[f.name]=sha(f)
out['review_meshes_sha256']=meshes;(OUT/'geometry-report.json').write_text(json.dumps(out,indent=2)+'\n');A.closeDocument(D.Name);assert sha(nf)==r['native_sha256'];print('saved',output,flush=True)
