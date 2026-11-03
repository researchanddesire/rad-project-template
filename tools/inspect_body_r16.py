"""Actual R16 native placement/pad/outline extraction; conservative heights."""
from pathlib import Path
import sys,json,hashlib,math
import pcb_split_r12 as G
K=G.K;ROOT=Path(__file__).resolve().parents[1];P=Path(sys.argv[1]).resolve();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();heights=json.loads((ROOT/'hardware/pcb/prototype-r2/layout-candidates-r0.json').read_text())['parts'];result={}
for domain in ['body','flange']:
 bp=P/domain/(domain+'-r16.kicad_pcb');before=sha(bp);b=K.LoadBoard(str(bp));rows=[];mates=[]
 for f in b.GetFootprints():
  ref=f.GetReference();h={'J1':3.2,'J2':2.3,'J6':3.2,'J7':3.2}.get(ref,heights.get(ref,{}).get('height_mm',3.2));side='B'if f.IsFlipped()else'F';bb=G.rect(f,[K.F_Fab,K.B_Fab]);cu=G.rect(f,[K.F_CrtYd,K.B_CrtYd]);pads=[{'n':p.GetNumber(),'net':p.GetNetname(),'xy_mm':G.mech(p.GetPosition())}for p in f.Pads()];rows.append({'ref':ref,'value':f.GetValue(),'footprint':str(f.GetFPID().GetLibNickname())+':'+str(f.GetFPID().GetLibItemName()),'xy_mm':G.mech(f.GetPosition()),'angle_deg':f.GetOrientationDegrees(),'side':side,'body_xy_mm':bb,'courtyard_xy_mm':cu,'height_budget_mm':h,'z_bounds_mm':[-.5-h,-.5]if side=='B'else[.5,.5+h],'pads':pads})
  if ref.startswith('J')and any(p['n']=='MP'for p in pads):
   sig=[p['xy_mm']for p in pads if p['n']not in ['','MP']];mp=[p['xy_mm']for p in pads if p['n']=='MP'];v=[sum(q[i]for q in mp)/len(mp)-sum(q[i]for q in sig)/len(sig)for i in [0,1]];norm=math.hypot(*v);v=[round(z/norm)for z in v];u=[-v[1],v[0]];n=len(sig);width=10 if ref=='J2'else n+1;front=max(x*v[0]+y*v[1]for x in [bb[0],bb[2]]for y in [bb[1],bb[3]]);xy=G.mech(f.GetPosition());t=sum(xy[i]*u[i]for i in [0,1]);pts=[[(front+lead)*v[j]+(t+sign*width/2)*u[j]for j in [0,1]]for lead in [0,2]for sign in [-1,1]];height=2.3 if ref=='J2'else 3.2
   mates.append({'ref':ref,'direction_xy':v,'xy_bounds_mm':[min(p[0]for p in pts),min(p[1]for p in pts),max(p[0]for p in pts),max(p[1]for p in pts)],'z_bounds_mm':[-.5-height,-.5]if side=='B'else[.5,.5+height],'scope':'Nominal allowance only; J2 10mm transverse,2mm extension,2.3mm high. SH N+1 width,2mm extension,3.2mm high. Not controlled part maxima/wires.'})
 edges=[[G.mech(s.GetStart()),G.mech(s.GetEnd())]for s in b.GetDrawings()if isinstance(s,K.PCB_SHAPE)and s.GetLayer()==K.Edge_Cuts];a,c=edges.pop(0);outline=[a,c]
 while edges:
  i,a,c=next((i,a,c)for i,(a,c)in enumerate(edges)if a==outline[-1]or c==outline[-1]);edges.pop(i);outline.append(c if a==outline[-1]else a)
 assert outline[-1]==outline[0];outline.pop();assert sha(bp)==before
 result[domain]={'native_board_sha256':before,'placements':rows,'mates':mates,'outline_xy_mm':outline,'thickness_mm':K.ToMM(b.GetDesignSettings().GetBoardThickness()),'same_face_courtyard_overlaps':[[a['ref'],c['ref']]for i,a in enumerate(rows)for c in rows[i+1:]if a['side']==c['side']and G.overlap(a['courtyard_xy_mm'],c['courtyard_xy_mm'])]}
source=K.LoadBoard(str(ROOT/'hardware/pcb/route-r16/candidate-a/body/body-r16.kicad_pcb'));original={f.GetReference():{p.GetNumber():p.GetNetname()for p in f.Pads()if p.GetNumber()not in ['','MP']}for f in source.GetFootprints()};actual={f['ref']:{p['n']:p['net']for p in f['pads']if p['n']not in ['','MP']}for f in result['body']['placements']}
if(P/'input-partition.json').exists():
 original={r:p for r,p in original.items()if r not in ['F1','D1']};original['J6']['2']='VBUS_CHG'
assert actual==original
baseline={};source_hashes={}
for domain in ['body','flange']:
 path=ROOT/'hardware/pcb/route-r16/candidate-a'/domain/(domain+'-r16.kicad_pcb');source_hashes[domain]=sha(path);source_board=K.LoadBoard(str(path))
 for f in source_board.GetFootprints():
  ref=f.GetReference();assert ref not in baseline;baseline[ref]={'value':f.GetValue(),'footprint':str(f.GetFPID().GetLibNickname())+':'+str(f.GetFPID().GetLibItemName()),'pads':{p.GetNumber():p.GetNetname()for p in f.Pads()if p.GetNumber()not in ['','MP']}}
actual_all={f['ref']:f for b in result.values()for f in b['placements']};assert len(actual_all)==89 and set(actual_all)==set(baseline)
compact=set('R1 R2 R3 R4 R5 R23 R24 R25 R41 R42 R46 R47 R48'.split());changes=[]
for ref,old in baseline.items():
 f=actual_all[ref];wanted=old['pads'].copy()
 if ref in ['J6','J7']and(P/'input-partition.json').exists():assert wanted['2']=='DOCK_5V';wanted['2']='VBUS_CHG'
 assert {p['n']:p['net']for p in f['pads']if p['n']not in ['','MP']}==wanted,ref
 value=old['value'];foot=old['footprint']
 if ref in compact:
  assert value.startswith('TNPW0603')and value.endswith('BEEA');value=value.replace('TNPW0603','TNPW0402')[:-4]+'BEED';foot='PrototypeR0:R_0402_1005Metric'
 elif ref=='J2':value='504050-0491 candidate';foot='PrototypeR0:Molex_Pico-Lock_504050-0491_1x04-1MP_P1.50mm_Horizontal'
 assert f['value']==value and f['footprint']==foot,(ref,value,foot)
 if ref in compact|{'J2'}:changes.append({'ref':ref,'old_value':old['value'],'new_value':value,'old_footprint':old['footprint'],'new_footprint':foot})
out={'date':'2026-11-01','inspector_sha256':sha(Path(__file__)),'boards':result,'source_A_board_sha256':source_hashes,'body_pad_number_net_maps_match_declared_partition':True,'all_89_main_parts_once':True,'all_signal_pad_nets_match_A_except_two_declared_header_input_changes':True,'declared_PCB_value_footprint_changes':changes,'scope':'Actual native substrates/Fab/courtyards/pads plus conservative candidate height budgets. J2new2.3mm allowance,0402resistors retain old .6mm budget. Nominal schematic resistance/function values remain unchanged and are checked separately. No actual part maximum/terminal/process/wire/assembly acceptance.'};(P/'layout-inspection.json').write_text(json.dumps(out,indent=2)+'\n');print({k:len(v['placements'])for k,v in result.items()})
