#!/usr/bin/env python3
"""Build an unrouted R2 placement candidate without modifying audited R0.
Run with KiCad7's bundled Python; pcbnew and wx are required.
"""
from pathlib import Path
import argparse,hashlib,json,math,re,shutil
import wx
APP=wx.App(False)
import pcbnew as k
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'hardware/pcb/prototype-r0'
OUT=ROOT/'hardware/pcb/prototype-r2'
BOARD=OUT/'buttplug-r2.kicad_pcb'
EXPECTED='12761321b7cd5f08918e6d36e5567a54701b3eada3c59ac0086185c2883e83c0'
OUTLINE=[[-35,-26],[31.6,-26],[31.6,-10.98],[25,-9],[4,-9],[4,20],[7,30],[7,52],[-7,52],[-7,30],[-4,20],[-4,-9],[-35,-9]]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def xy(x,y):return k.VECTOR2I(k.FromMM(100+x),k.FromMM(130-y))
def mech(v):return [round(k.ToMM(v.x)-100,6),round(130-k.ToMM(v.y),6)]
def write(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def snapshot():return {str(p.relative_to(ROOT)):sha(p) for p in BASE.rglob('*') if p.is_file() and p.suffix not in ('.kicad_prl',)}
def bbox(fp,layers):
 shapes=[s for s in fp.GraphicalItems() if isinstance(s,k.PCB_SHAPE) and s.GetLayer() in layers]
 rects=[s.GetBoundingBox() for s in shapes]
 if not rects:
  if k.F_CrtYd in layers:return None
  rects=[fp.GetBoundingBox(False,False)]
 return [round(k.ToMM(min(r.GetLeft() for r in rects))-100,5),round(130-k.ToMM(max(r.GetBottom() for r in rects)),5),round(k.ToMM(max(r.GetRight() for r in rects))-100,5),round(130-k.ToMM(min(r.GetTop() for r in rects)),5)]
def overlap(a,b):return min(a[2],b[2])-max(a[0],b[0])>1e-5 and min(a[3],b[3])-max(a[1],b[1])>1e-5
def main():
 global OUT,BOARD
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output-dir',type=Path,help='Alternative output for replay without replacing an active routed project');args=parser.parse_args()
 if args.output_dir:OUT=args.output_dir.resolve();BOARD=OUT/'buttplug-r2.kicad_pcb'
 if BOARD.exists():
  existing=k.LoadBoard(str(BOARD))
  if len(list(existing.GetTracks())):raise RuntimeError('Existing R2 board has routing. Use --output-dir for placement replay; do not replace routed source.')
 assert sha(BASE/'buttplug-r0.kicad_pcb')==EXPECTED,'Audited R0 changed; review source before regenerating'
 before=snapshot();OUT.mkdir(exist_ok=True)
 for fn in ['candidate-pin-manifest.json','layout-candidates-r0.json','footprint-register-r0.json','footprint-assignments-r0.json']:
  shutil.copyfile(BASE/fn,OUT/fn)
 shutil.copytree(BASE/'PrototypeR0.pretty',OUT/'PrototypeR0.pretty',dirs_exist_ok=True)
 (OUT/'fp-lib-table').write_text('(fp_lib_table (lib (name "PrototypeR0")(type "KiCad")(uri "${KIPRJMOD}/PrototypeR0.pretty")(options "")(descr "Byte-copied candidate footprints from audited R0; legacy library name retained")))\n')
 project=json.loads((BASE/'buttplug-r0.kicad_pro').read_text())
 project.setdefault('meta',{})['filename']='buttplug-r2.kicad_pro'
 write(OUT/'buttplug-r2.kicad_pro',project)
 snapshot_project=dict(project);snapshot_project['meta']=dict(project.get('meta',{}),filename='placement-source-r2.kicad_pro');write(OUT/'placement-source-r2.kicad_pro',snapshot_project)
 b=k.LoadBoard(str(BASE/'buttplug-r0.kicad_pcb'))
 for t in list(b.GetTracks()):b.Delete(t)
 for z in [b.GetArea(i) for i in range(b.GetAreaCount())]:
  if not z.GetIsRuleArea():b.Delete(z)
 for d in list(b.GetDrawings()):b.Delete(d)
 fps={f.GetReference():f for f in b.GetFootprints()}
 old={r:{'xy':mech(f.GetPosition()),'native_angle_deg':f.GetOrientationDegrees(),'side':'B' if f.GetLayer()==k.B_Cu else 'F'} for r,f in fps.items()}
 def pose(r,x,y,a=0,side='F'):
  f=fps[r]
  if (f.GetLayer()==k.B_Cu)!=(side=='B'):f.Flip(f.GetPosition(),True)
  f.SetOrientationDegrees(a);f.SetPosition(xy(x,y));f.SetLocked(False)
  f.SetProperty('PlacementStatus','R2 UNROUTED CANDIDATE / NOT FAB')
 # Rotate the complete U2 power bay into the central handle. Local feedback
 # is placed on the same face; all converter routes must be recreated.
 group=['U2','L1','C11','C12','C13','C14','C15','C16','C51','C52','R13']
 for r in group:
  x,y=old[r]['xy'];pose(r,7.5+y-7.7625,-19-x,old[r]['native_angle_deg']-90,'B')
 pose('R11',4.1,-18,0,'B');pose('R12',4.1,-19.6,0,'B')
 for r,x,y,a in [('C33',17.5,-15.3,90),('R33',17,-18.5,0),('R34',17,-20.5,0),('R39',-20.2,-23,90),('R40',-16.8,-23,90),('C34',-18.5,-24.5,90),('R37',-2.5,-10.5,0),('R38',-4.7,-11.2,90),('R48',0,-13.3,0)]:pose(r,x,y,a,'B')
 # Gate + motion stay in the handle; the narrow waist carries no components.
 for r,x,y,a in [('U4',0,-14.7,0),('C27',2.8,-14.7,90),('R23',-1.3,-11,90),('R24',3.3,-11,90),('U7',1,-20,0),('C41',-.8,-20,90),('C42',1,-17.7,0),('R41',1,-22,0),('J5',-20.8,-22.5,180)]:pose(r,x,y,a,'F')
 # Motor converter and bridge move to +Z, clear of the optional below-board
 # reference pack. Body pose/mated harness clearance still need mechanical CAD.
 for r in ['U3','L2','C21','C22','C23','C24','C25','C26','C53','C54','R21','R22','R26']:
  f=fps[r];f.Flip(xy(0,0),True);f.SetLocked(False)
 for r in ['U5','C28','C29','C30']:
  f=fps[r];f.Flip(xy(0,0),True);x,y=mech(f.GetPosition());f.SetPosition(xy(x,y-3.6));f.SetLocked(False)
 pose('C22',2.7,44.0,90,'F');pose('R25',0,47.8,0,'F');pose('J3',0,27.8,180,'F')
 for a,c in zip(OUTLINE,OUTLINE[1:]+OUTLINE[:1]):
  s=k.PCB_SHAPE();s.SetShape(k.SHAPE_T_SEGMENT);s.SetStart(xy(*a));s.SetEnd(xy(*c));s.SetLayer(k.Edge_Cuts);s.SetWidth(k.FromMM(.05));b.Add(s)
 t=k.PCB_TEXT(b);t.SetText('R2 PLACEMENT ONLY / UNROUTED / NOT FAB');t.SetPosition(xy(0,-29));t.SetLayer(k.Dwgs_User);t.SetTextSize(k.VECTOR2I(k.FromMM(.8),k.FromMM(.8)));t.SetTextThickness(k.FromMM(.1));b.Add(t)
 k.SaveBoard(str(BOARD),b);b=k.LoadBoard(str(BOARD));b.BuildConnectivity()
 rpt=OUT/'drc-placement-r2.txt';k.WriteDRCReport(b,str(rpt),k.EDA_UNITS_MILLIMETRES,True)
 parts={p['ref']:p for p in json.loads((OUT/'candidate-pin-manifest.json').read_text())['parts'] if p.get('assembly_domain')=='MAIN_T' and not p['ref'].startswith('#')}
 candidates=json.loads((OUT/'layout-candidates-r0.json').read_text())['parts']
 boxes=[];mismatches=[];rows=[]
 for f in b.GetFootprints():
  r=f.GetReference();side='B' if f.GetLayer()==k.B_Cu else 'F';bb=bbox(f,[k.F_Fab,k.B_Fab]);cc=bbox(f,[k.F_CrtYd,k.B_CrtYd]);height=candidates[r]['height_mm']
  actual={p.GetNumber():p.GetNetname() for p in f.Pads() if p.GetNumber() not in ('','MP')}
  expected={n:(v['net'] or '') for n,v in parts[r]['pins'].items()}
  for n in sorted(set(actual)|set(expected)):
   if actual.get(n)!=expected.get(n):mismatches.append([r,n,actual.get(n),expected.get(n)])
  boxes.append({'ref':r,'mpn':candidates[r]['mpn'],'side':side,'xy_bounds_mm':bb,'courtyard_xy_bounds_mm':cc,'z_bounds_mm':[-.5-height,-.5] if side=='B' else [.5,.5+height],'scope':'Conservative Fab/body projection and candidate height; mating plugs recorded separately; excludes wires/solder/tolerances'})
  rows.append({'ref':r,'xy_mm':mech(f.GetPosition()),'native_angle_deg':f.GetOrientationDegrees(),'side':side,'footprint':str(f.GetFPID().GetLibItemName()),'height_mm':height,'changed_from_R0':old[r]!={'xy':mech(f.GetPosition()),'native_angle_deg':f.GetOrientationDegrees(),'side':side}})
 pairs={'body_bbox':[],'courtyard_bbox':[]}
 for i,a in enumerate(boxes):
  for c in boxes[i+1:]:
   if a['side']!=c['side']:continue
   if overlap(a['xy_bounds_mm'],c['xy_bounds_mm']):pairs['body_bbox'].append([a['ref'],c['ref']])
   if a['courtyard_xy_bounds_mm'] and c['courtyard_xy_bounds_mm'] and overlap(a['courtyard_xy_bounds_mm'],c['courtyard_xy_bounds_mm']):pairs['courtyard_bbox'].append([a['ref'],c['ref']])
 mates=[]
 for r,n in [('J3',2),('J5',4)]:
  f=fps[r];f=next(q for q in b.GetFootprints() if q.GetReference()==r)
  mp=[mech(p.GetPosition()) for p in f.Pads() if p.GetNumber()=='MP'];sig=[mech(p.GetPosition()) for p in f.Pads() if p.GetNumber() not in ('','MP')]
  v=[sum(p[j] for p in mp)/len(mp)-sum(p[j] for p in sig)/len(sig) for j in [0,1]];ln=math.hypot(*v);v=[round(x/ln,6) for x in v];u=[-v[1],v[0]];x,y=mech(f.GetPosition());w=1.5 if n==2 else 2.5
  points=[[x+v[0]*a+u[0]*c,y+v[1]*a+u[1]*c] for a in [2.625,4.575] for c in [-w,w]]
  bb=[min(p[0] for p in points),min(p[1] for p in points),max(p[0] for p in points),max(p[1] for p in points)]
  mates.append({'ref':r,'mating_direction_xy':v,'plug_extension_xy_bounds_mm':bb,'z_bounds_mm':[.5,3.45],'source':'JST eSH.pdf plus historical native Fab/mated-geometry-input.json','scope':'Candidate3/5mm width x1.95mm axial extension, not wire/bend or toleranced envelope','overlapping_same_face_component_bboxes':[p['ref'] for p in boxes if p['ref']!=r and p['side']=='F' and overlap(bb,p['xy_bounds_mm'])]})
 text=rpt.read_text();counts={name:int(re.search(pattern,text).group(1)) for name,pattern in [('drc_violations',r'\*\* Found (\d+) DRC violations'),('unconnected_items',r'\*\* Found (\d+) unconnected pads'),('footprint_errors',r'\*\* Found (\d+) Footprint errors')]}
 record={'status':'UNROUTED R2 PLACEMENT CANDIDATE; not fabrication or full package-fit release','date':'2026-10-30','source_baseline_board_sha256':EXPECTED,'board_sha256':sha(BOARD),'project_sha256':sha(OUT/'buttplug-r2.kicad_pro'),'manifest_sha256':sha(OUT/'candidate-pin-manifest.json'),'generator_sha256':sha(Path(__file__)),'source_R0_hashes_before':before,'R0_unchanged':before==snapshot(),'circuit_scope':'All87MAIN_T footprints and48nets copied from audited R0; remote tip/circuit/firmware unchanged','circuit_pad_net_mismatches':mismatches,'pcb_outline_vertices_xy_mm':OUTLINE,'board_z_mm':[-.5,.5],'waist_component_free_y_mm':[0,20],'footprints':len(boxes),'nets':b.GetNetCount()-1,'copper_layers':b.GetCopperLayerCount(),'tracks_and_vias':len(list(b.GetTracks())),'board_copper_zones':sum(not b.GetArea(i).GetIsRuleArea() for i in range(b.GetAreaCount())),'footprint_keepouts_retained':len(next(f for f in b.GetFootprints() if f.GetReference()=='U6').Zones())==1,'native_DRC':{'report':rpt.name,'report_sha256':sha(rpt),'counts':counts,'scope':'Current unrouted placement; incomplete connections expected. Native copper/courtyard checks are not mechanical fit or accepted routing.'},'component_boxes':boxes,'placements':rows,'component_bodies_intersecting_waist':[p['ref'] for p in boxes if p['xy_bounds_mm'][3]>=0 and p['xy_bounds_mm'][1]<=20],'mechanical_clip_reservations':{'edge_lip_x_abs_mm':[3.7,4.0],'y_bands_mm':[[2,3],[14,15]],'scope':'Component-free waist; innerGND/route edge clearance, carrier electrical isolation and capture loads to review'},'USB_routing_scope':'No stale USB tracks retained. Restore controlled differential pair over continuous reference; central U2 placement requires fresh via/return review.','pack_selection':'OPEN; no selected battery and no fit claim from these component boxes','conservative_same_side_overlap_screen':pairs,'mated_connectors':mates,'open_gates':['New power/USB/signal routing and GND reference fill','Mechanical full assembly/final-position carrier, component, mated plug, wire/bend and shell-clearance screen','Pack selectionOPEN, actual pack+dualNTC/adapter requirements','RF enclosure and module clearance review','Supplier stackup/impedance/via/stencil/process','JP1open and firmware outputlocked until bench acceptance']}
 assert before==snapshot(),'R0 sources changed during placement operation'
 assert not mismatches,mismatches
 assert not record['component_bodies_intersecting_waist'],record['component_bodies_intersecting_waist']
 shutil.copyfile(BOARD,OUT/'placement-source-r2.kicad_pcb')
 record['placement_snapshot']='placement-source-r2.kicad_pcb'
 record['placement_project']='placement-source-r2.kicad_pro'
 record['placement_project_sha256']=sha(OUT/'placement-source-r2.kicad_pro')
 record['replay_scope']='Placement/nets/rules reproduce semantically; freshly generated native drawing UUIDs and DRC timestamps may differ. Replaying over a routed board is blocked; use --output-dir.'
 write(OUT/'placement-report-r2.json',record)
 print('board',record['board_sha256'],'counts',counts,'parity',mismatches,'overlaps',pairs)
 print('mates',mates)
if __name__=='__main__':main()
