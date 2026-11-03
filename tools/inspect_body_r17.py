"""Actual R17 native placement/pad/outline extraction; conservative heights."""
from pathlib import Path
import sys,json,hashlib,math
import pcb_split_r12 as G
K=G.K;ROOT=Path(__file__).resolve().parents[1];P=Path(sys.argv[1]).resolve();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();heights=json.loads((ROOT/'hardware/pcb/prototype-r2/layout-candidates-r0.json').read_text())['parts'];result={};compact=json.loads((P/'compact-driver.json').read_text())if(P/'compact-driver.json').exists()else None
for domain in ['body','flange']:
 bp=next((P/domain).glob(domain+'-r*.kicad_pcb'));before=sha(bp);b=K.LoadBoard(str(bp));rows=[];mates=[]
 for f in b.GetFootprints():
  ref=f.GetReference();h={'J1':3.2,'J2':2.3,'J6':3.2,'J7':3.2}.get(ref,heights.get(ref,{}).get('height_mm',3.2));h=.6 if compact and ref in ['C28','C29']else h;side='B'if f.IsFlipped()else'F';bb=G.rect(f,[K.F_Fab,K.B_Fab]);cu=G.rect(f,[K.F_CrtYd,K.B_CrtYd]);pads=[{'n':p.GetNumber(),'net':p.GetNetname(),'xy_mm':G.mech(p.GetPosition())}for p in f.Pads()];rows.append({'ref':ref,'value':f.GetValue(),'footprint':str(f.GetFPID().GetLibNickname())+':'+str(f.GetFPID().GetLibItemName()),'xy_mm':G.mech(f.GetPosition()),'angle_deg':f.GetOrientationDegrees(),'side':side,'body_xy_mm':bb,'courtyard_xy_mm':cu,'height_budget_mm':h,'z_bounds_mm':[-.5-h,-.5]if side=='B'else[.5,.5+h],'pads':pads})
  if ref.startswith('J')and any(p['n']=='MP'for p in pads):
   sig=[p['xy_mm']for p in pads if p['n']not in ['','MP']];mp=[p['xy_mm']for p in pads if p['n']=='MP'];v=[sum(q[i]for q in mp)/len(mp)-sum(q[i]for q in sig)/len(sig)for i in [0,1]];norm=math.hypot(*v);v=[round(z/norm)for z in v];u=[-v[1],v[0]];n=len(sig);width=10 if ref=='J2'else n+1;front=max(x*v[0]+y*v[1]for x in [bb[0],bb[2]]for y in [bb[1],bb[3]]);xy=G.mech(f.GetPosition());t=sum(xy[i]*u[i]for i in [0,1]);pts=[[(front+lead)*v[j]+(t+sign*width/2)*u[j]for j in [0,1]]for lead in [0,2]for sign in [-1,1]];height=2.3 if ref=='J2'else 3.2
   mates.append({'ref':ref,'direction_xy':v,'xy_bounds_mm':[min(p[0]for p in pts),min(p[1]for p in pts),max(p[0]for p in pts),max(p[1]for p in pts)],'z_bounds_mm':[-.5-height,-.5]if side=='B'else[.5,.5+height],'scope':'Nominal allowance only; J2 10mm transverse,2mm extension,2.3mm high. SH N+1 width,2mm extension,3.2mm high. Not controlled part maxima/wires.'})
 edges=[[G.mech(s.GetStart()),G.mech(s.GetEnd())]for s in b.GetDrawings()if isinstance(s,K.PCB_SHAPE)and s.GetLayer()==K.Edge_Cuts];a,c=edges.pop(0);outline=[a,c]
 while edges:
  i,a,c=next((i,a,c)for i,(a,c)in enumerate(edges)if a==outline[-1]or c==outline[-1]);edges.pop(i);outline.append(c if a==outline[-1]else a)
 assert outline[-1]==outline[0];outline.pop();assert sha(bp)==before
 result[domain]={'native_board_sha256':before,'placements':rows,'mates':mates,'outline_xy_mm':outline,'thickness_mm':K.ToMM(b.GetDesignSettings().GetBoardThickness()),'same_face_courtyard_overlaps':[[a['ref'],c['ref']]for i,a in enumerate(rows)for c in rows[i+1:]if a['side']==c['side']and G.overlap(a['courtyard_xy_mm'],c['courtyard_xy_mm'])]}

source_dir=ROOT/'hardware/pcb/route-r16/candidate-u';base=json.loads((source_dir/'layout-inspection.json').read_text());pose_changes=[]
for domain,bb in result.items():
 old={p['ref']:p for p in base['boards'][domain]['placements']};assert set(old)=={p['ref']for p in bb['placements']}
 for p in bb['placements']:
  q=old[p['ref']];change=compact['component_changes'].get(p['ref'])if compact else None;wanted_value=change['new_PCB_value']if change else q['value'];wanted_foot=change['new_footprint']if change else q['footprint'];assert p['value']==wanted_value and p['footprint']==wanted_foot,p['ref'];assert {x['n']:x['net']for x in p['pads']if x['n']not in ['','MP']}=={x['n']:x['net']for x in q['pads']if x['n']not in ['','MP']},p['ref']
  fields=['xy_mm','angle_deg','side']
  changed=p['side']!=q['side']or abs(p['angle_deg']-q['angle_deg'])>1e-5 or any(abs(a-b)>1e-5 for a,b in zip(p['xy_mm'],q['xy_mm']))
  if changed:pose_changes.append({'ref':p['ref'],'old':{k:q[k]for k in fields},'new':{k:p[k]for k in fields}})
 expected_outline=json.loads((P/'board-width.json').read_text())['new_outline_xy_mm']if domain=='body'and(P/'board-width.json').exists()else base['boards'][domain]['outline_xy_mm']
 def edges(poly):return{tuple(sorted([tuple(a),tuple(c)]))for a,c in zip(poly,poly[1:]+poly[:1])}
 assert edges(bb['outline_xy_mm'])==edges(expected_outline)and bb['thickness_mm']==base['boards'][domain]['thickness_mm']
expected=json.loads((P/'local-interfaces.json').read_text())['new_poses']
if compact:
 for ref,p in compact['component_changes'].items():expected[ref]=p['new_pose']
 expected['R4']=compact['R4_new_pose']
if(P/'signal-repack.json').exists():expected['R4']=json.loads((P/'signal-repack.json').read_text())['R4_new_pose']
assert {p['ref']for p in pose_changes}==set(expected)
for p in pose_changes:
 x,y,angle,side=expected[p['ref']];actual=p['new'];assert actual['side']==side and abs((actual['angle_deg']-angle)%360)<1e-5 and all(abs(a-b)<1e-5 for a,b in zip(actual['xy_mm'],[x,y]))
assert len(result['body']['placements'])==65 and len(result['flange']['placements'])==24
assert all(not b['same_face_courtyard_overlaps']for b in result.values())
out={'date':'2026-11-01','inspector_sha256':sha(Path(__file__)),'source_R16_inspection_sha256':sha(source_dir/'layout-inspection.json'),'boards':result,'all_89_parts_and_pad_nets_match_R16U':True,'declared_candidate_package_changes':compact['component_changes']if compact else{},'outlines_and_thickness_equal_R16U':not(P/'board-width.json').exists(),'declared_width_study_sha256':sha(P/'board-width.json')if(P/'board-width.json').exists()else None,'declared_pose_changes':pose_changes,'scope':'Actual R17 native substrate/Fab/courtyard/pad geometry and nominal mates. Only declared poses and optional two100nF0402candidate packages/heights change; schematic nominal values and all pad nets preserved. No controlled part/terminal/wire/process/assembly acceptance.'};(P/'layout-inspection.json').write_text(json.dumps(out,indent=2)+'\n');print(len(pose_changes),'declared pose changes, 89 parts conserved',flush=True)
