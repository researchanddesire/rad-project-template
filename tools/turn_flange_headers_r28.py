"""Native placement correction: turn only J1/J7 toward opposite board edges.

Copies the routed flange into a clearly unreviewed placement candidate. Copper
is retained as reference and MUST be repaired/rechecked before fabrication.
"""
from pathlib import Path
import sys,json,hashlib,math,shutil,itertools
import pcb_split_r12 as G
K=G.K;ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'hardware/pcb/stackup-r23/candidate-d';OUT=Path(sys.argv[1]).resolve();OUT.mkdir(parents=True,exist_ok=True);assert not any(OUT.iterdir())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();source=SRC/'flange/flange-r23.kicad_pcb';oldhash=sha(source)
original=K.LoadBoard(str(source));before={f.GetReference():{'value':f.GetValue(),'pads':sorted((p.GetNumber(),p.GetNetname())for p in f.Pads()),'position':G.mech(f.GetPosition()),'angle':f.GetOrientationDegrees(),'layer':f.GetLayer()}for f in original.GetFootprints()};fps={f.GetReference():f for f in original.GetFootprints()}
assert before['J1']['angle']==0 and before['J7']['angle']==180
fps['J1'].SetOrientationDegrees(180);fps['J7'].SetOrientationDegrees(0)
board=OUT/'flange-r28.kicad_pcb';K.SaveBoard(str(board),original)
project=SRC/'flange/flange-r23.kicad_pro'
if project.is_file():shutil.copyfile(project,OUT/'flange-r28.kicad_pro')
(OUT/'fp-lib-table').write_text('(fp_lib_table (lib (name "PrototypeR0") (type "KiCad") (uri "${KIPRJMOD}/../../../stackup-r23/candidate-d/flange/PrototypeR0.pretty") (options "") (descr "Unchanged source candidate footprints")))\n')
b=K.LoadBoard(str(board));expected=json.loads((SRC/'layout-inspection.json').read_text())['boards']['flange'];heights={p['ref']:p['height_budget_mm']for p in expected['placements']};rows=[];mates=[]
for fp in b.GetFootprints():
 n=fp.GetReference();q=before[n];assert fp.GetValue()==q['value']and sorted((p.GetNumber(),p.GetNetname())for p in fp.Pads())==q['pads'];assert G.mech(fp.GetPosition())==q['position']and fp.GetLayer()==q['layer']
 if n not in ['J1','J7']:assert fp.GetOrientationDegrees()==q['angle']
 side='B'if fp.GetLayer()==K.B_Cu else'F';bb=G.rect(fp,[K.F_Fab,K.B_Fab]);h=heights[n]
 rows.append({'ref':n,'value':fp.GetValue(),'xy_mm':G.mech(fp.GetPosition()),'angle_deg':fp.GetOrientationDegrees(),'side':side,'body_xy_mm':bb,'courtyard_xy_mm':G.rect(fp,[K.F_CrtYd,K.B_CrtYd]),'height_budget_mm':h,'z_bounds_mm':[-.5-h,-.5]if side=='B'else[.5,.5+h],'pads':[{'n':p.GetNumber(),'net':p.GetNetname(),'xy_mm':G.mech(p.GetPosition())}for p in fp.Pads()]})
 if n.startswith('J'):
  sig=[G.mech(p.GetPosition())for p in fp.Pads()if p.GetNumber()not in ['','MP']];mp=[G.mech(p.GetPosition())for p in fp.Pads()if p.GetNumber()=='MP'];v=[sum(p[j]for p in mp)/len(mp)-sum(p[j]for p in sig)/len(sig)for j in [0,1]];L=math.hypot(*v);d=[round(u/L)for u in v];across=[-d[1],d[0]];count=len({p.GetNumber()for p in fp.Pads()if p.GetNumber()not in ['','MP']});anchor=G.mech(fp.GetPosition());s=anchor[0]*across[0]+anchor[1]*across[1];front=max(x*d[0]+y*d[1]for x in [bb[0],bb[2]]for y in [bb[1],bb[3]])
  pts=[[(front+lead)*d[j]+(s+transverse*(count+1)/2)*across[j]for j in [0,1]]for lead in [0,2]for transverse in [-1,1]]
  mates.append({'ref':n,'direction_xy':d,'xy_bounds_mm':[min(p[0]for p in pts),min(p[1]for p in pts),max(p[0]for p in pts),max(p[1]for p in pts)],'z_bounds_mm':[-3.7,-.5]if side=='B'else[.5,3.7],'scope':'Same N+1/2mm extension/3.2mm height nominal SH mate allowance, not actual part maxima or wires.'})
assert len(rows)==24 and len(mates)==3
def intersect(a,z,b,w):
 dims=[min(a[2],b[2])-max(a[0],b[0]),min(a[3],b[3])-max(a[1],b[1]),min(z[1],w[1])-max(z[0],w[0])]
 return math.prod(dims)if min(dims)>1e-7 else 0.
bodyhits=[];courthits=[]
for a,c in itertools.combinations(rows,2):
 v=intersect(a['body_xy_mm'],a['z_bounds_mm'],c['body_xy_mm'],c['z_bounds_mm'])
 if v>1e-5:bodyhits.append({'a':a['ref'],'b':c['ref'],'intersection_mm3':v})
 if a['side']==c['side']and G.overlap(a['courtyard_xy_mm'],c['courtyard_xy_mm']):courthits.append([a['ref'],c['ref']])
poses=[]
for m in mates:
 for distance in [20,10,5,2,1,.5,.25,0]:
  x,y=m['direction_xy'];a=m['xy_bounds_mm'];shift=[a[0]+x*distance,a[1]+y*distance,a[2]+x*distance,a[3]+y*distance];hits=[]
  for p in rows:
   if p['ref']==m['ref']:continue
   v=intersect(shift,m['z_bounds_mm'],p['body_xy_mm'],p['z_bounds_mm'])
   if v>1e-5:hits.append({'fixed':p['ref'],'intersection_mm3':v})
  poses.append({'mate':m['ref'],'outward_distance_mm':distance,'hits':hits})
report={'source_native_board_sha256':oldhash,'native_board_sha256':sha(board),'builder_sha256':sha(Path(__file__)),'source_inspection_sha256':sha(SRC/'layout-inspection.json'),'changed_poses':{'J1':{'from_deg':0,'to_deg':180},'J7':{'from_deg':180,'to_deg':0}},'all_24_ref_value_pad_net_maps_and_centres_conserved':True,'unchanged_22_poses':True,'placements':rows,'mates':mates,'component_Fab_box_intersections':bodyhits,'same_face_courtyard_overlaps':courthits,'nominal_mate_listed_approach_poses':poses,'all_nominal_mate_Fab_approaches_clear':not any(p['hits']for p in poses),'copper_status':'Source copper retained as reference. Rotated pads require routing repair and native DRC before this is an electrical candidate. No current DRC pass or fabrication outputs claimed.','scope':'Native two-header placement and conserved pin/net semantics; nominal box component/courtyard and finite plug-approach screens only. Unrouted correction, not current prototype circuit/build release. No actual mate/wires/flex/RF/mechanical/physical acceptance. BatteryOPEN/humanBOMunchanged.'}
(OUT/'placement-inspection.json').write_text(json.dumps(report,indent=2)+'\n');assert sha(source)==oldhash
print('24parts conserved; component hits',bodyhits,'courtyard',courthits,'plug failures',[p for p in poses if p['hits']],flush=True)
