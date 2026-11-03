"""Native R15 flange pose/pad/Fab/mate extraction for actual saved board."""
from pathlib import Path
import argparse,hashlib,json,math
import pcb_split_r12 as G
K=G.K;ROOT=Path(__file__).resolve().parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ap=argparse.ArgumentParser();ap.add_argument('directory',type=Path);a=ap.parse_args();P=a.directory.resolve();f=P/'flange/flange-r15.kicad_pcb';before=sha(f);b=K.LoadBoard(str(f));rows=[];mates=[]
heights=json.loads((ROOT/'hardware/pcb/prototype-r2/layout-candidates-r0.json').read_text())['parts']
for fp in b.GetFootprints():
 ref=fp.GetReference();side='B'if fp.GetLayer()==K.B_Cu else'F';h=3.2 if ref in ['J1','J7']else heights[ref]['height_mm'];bb=G.rect(fp,[K.F_Fab,K.B_Fab]);sig=[G.mech(p.GetPosition())for p in fp.Pads()if p.GetNumber()not in['','MP']];mp=[G.mech(p.GetPosition())for p in fp.Pads()if p.GetNumber()=='MP'];direction=None
 if ref.startswith('J')and mp:
  v=[sum(p[i]for p in mp)/len(mp)-sum(p[i]for p in sig)/len(sig)for i in[0,1]];length=math.hypot(*v);direction=[round(q/length)for q in v];u=[-direction[1],direction[0]];n=len({p.GetNumber()for p in fp.Pads()if p.GetNumber()not in['','MP']})
  front=max(x*direction[0]+y*direction[1]for x in[bb[0],bb[2]]for y in[bb[1],bb[3]]);anchor=G.mech(fp.GetPosition());t=anchor[0]*u[0]+anchor[1]*u[1];points=[[(front+lead)*direction[j]+(t+transverse*(n+1)/2)*u[j]for j in[0,1]]for lead in[0,2]for transverse in[-1,1]]
  mates.append({'ref':ref,'xy_bounds_mm':[min(p[0]for p in points),min(p[1]for p in points),max(p[0]for p in points),max(p[1]for p in points)],'z_bounds_mm':[-3.7,-.5]if side=='B'else[.5,3.7],'service_only':ref=='J4','scope':'SH nominal N+1 width/2mm extension/3.2mm height allowance only; no wires/controlled maximum.'})
 rows.append({'ref':ref,'xy_mm':G.mech(fp.GetPosition()),'side':side,'angle_deg':fp.GetOrientationDegrees(),'courtyard_xy_mm':G.rect(fp,[K.F_CrtYd,K.B_CrtYd]),'body_xy_mm':bb,'height_budget_mm':h,'z_bounds_mm':[-.5-h,-.5]if side=='B'else[.5,.5+h],'mating_direction_xy':direction,'footprint':str(fp.GetFPID().GetLibNickname())+':'+str(fp.GetFPID().GetLibItemName()),'pads':[{'n':p.GetNumber(),'net':p.GetNetname(),'xy_mm':G.mech(p.GetPosition())}for p in fp.Pads()]})
segments=[[G.mech(s.GetStart()),G.mech(s.GetEnd())]for s in b.GetDrawings()if isinstance(s,K.PCB_SHAPE)and s.GetLayer()==K.Edge_Cuts];first=segments.pop(0);outline=[first[0],first[1]]
while segments:
 i,a,c=next((i,a,c)for i,(a,c)in enumerate(segments)if a==outline[-1]or c==outline[-1]);segments.pop(i);outline.append(c if a==outline[-1]else a)
assert outline[-1]==outline[0];outline.pop();assert sha(f)==before
r={'native_board_sha256':before,'inspector_sha256':sha(Path(__file__)),'placements':rows,'mates':mates,'outline_mechanical_xy_mm':outline,'thickness_mm':K.ToMM(b.GetDesignSettings().GetBoardThickness()),'scope':'Actual saved native EdgeCuts/Fab/pad geometry with candidate heights. New J1 SH2 height3.2 allowance. Not actual part maxima, wire or physical acceptance.'}
(P/'flange-native-inspection.json').write_text(json.dumps(r,indent=2)+'\n');print(len(rows),'native parts;',len(mates),'mate probes; outline',outline)
