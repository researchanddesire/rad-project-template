"""Export actual saved PCB outlines and native Fab/height envelopes for MCAD."""
from pathlib import Path
import argparse,hashlib,json
import wx
APP=wx.App(False)
import pcbnew as K
ROOT=Path(__file__).resolve().parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def mech(p):return[round(K.ToMM(p.x)-100,6),round(130-K.ToMM(p.y),6)]
ap=argparse.ArgumentParser();ap.add_argument('directory',type=Path);ap.add_argument('domain',choices=['body','flange']);args=ap.parse_args()
P=args.directory.resolve();f=P/(args.domain+'-r12.kicad_pcb');before=sha(f)
inspection=json.loads((P/(args.domain+'-native-inspection.json')).read_text());assert inspection['board_sha256']==before
b=K.LoadBoard(str(f));segments=[]
for s in b.GetDrawings():
    if isinstance(s,K.PCB_SHAPE)and s.GetLayer()==K.Edge_Cuts:segments.append([mech(s.GetStart()),mech(s.GetEnd())])
outline=[segments.pop(0)[0]]
while segments:
    matches=[(i,a,c)for i,(a,c)in enumerate(segments)if a==outline[-1]or c==outline[-1]]
    if not matches:
        # The first segment's other endpoint has not yet been added.
        start=[s for s in b.GetDrawings()if isinstance(s,K.PCB_SHAPE)and s.GetLayer()==K.Edge_Cuts][0]
        if len(outline)==1:outline.append(mech(start.GetEnd()));continue
        raise RuntimeError('Cannot order native outline')
    i,a,c=matches[0];segments.pop(i);outline.append(c if a==outline[-1]else a)
assert len(outline)>=4
if outline[-1]==outline[0]:outline.pop()
# Initial segment is included by the ordered traversal in either direction.
thickness=K.ToMM(b.GetDesignSettings().GetBoardThickness());assert abs(thickness-1)<1e-6
mates=[]
for p in inspection['placements']:
    if not p['ref'].startswith('J')or not p['mating_direction_xy_study']:continue
    fp=next(f for f in b.GetFootprints()if f.GetReference()==p['ref'])
    n=len({pad.GetNumber()for pad in fp.Pads()if pad.GetNumber()not in('','MP')})
    ph='_PH_'in str(fp.GetFPID().GetLibItemName());width=2*n+1.8 if ph else n+1
    height=5.5 if ph else 3.2
    v=[round(q)for q in p['mating_direction_xy_study']];assert sum(abs(q)for q in v)==1
    u=[-v[1],v[0]];bb=p['body_xy_mm'];corners=[(x,y)for x in[bb[0],bb[2]]for y in[bb[1],bb[3]]]
    s=max(x*v[0]+y*v[1]for x,y in corners);t=p['xy_mm'][0]*u[0]+p['xy_mm'][1]*u[1]
    points=[[(s+lead)*v[j]+(t+side*width/2)*u[j]for j in[0,1]]for lead in[0,2]for side in[-1,1]]
    bounds=[min(q[0]for q in points),min(q[1]for q in points),max(q[0]for q in points),max(q[1]for q in points)]
    mates.append({'ref':p['ref'],'family':'PH'if ph else'SH','positions':n,'xy_bounds_mm':bounds,
       'z_bounds_mm':[-.5-height,-.5]if p['side']=='B'else[.5,.5+height],
       'service_only':p['ref']=='J4','scope':'Nominal catalog-style extension2mm beyond nativeFabfront/widthN+1SHor2N+1.8PH; referenced R2mate construction, not controlled max or accepted assembly. No wires/strain.'})
assert sha(f)==before
out={'native_board_sha256':before,'native_inspection_sha256':sha(P/(args.domain+'-native-inspection.json')),'exporter_sha256':sha(Path(__file__)),
     'outline_mechanical_xy_mm':outline,'thickness_mm':thickness,'placements':inspection['placements'],'mates':mates,
     'scope':'Actual saved EdgeCuts and Fab/height budgets. Chip/connector bodies are envelopes; no solder/process/terminal/max tolerance or physical fit acceptance.'}
(P/(args.domain+'-mechanical-input.json')).write_text(json.dumps(out,indent=2)+'\n')
print(args.domain,'native outline',outline,'mate probes',len(mates))
