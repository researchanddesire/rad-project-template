"""Inspect one actual saved split board per fresh KiCad process."""
from pathlib import Path
import argparse,hashlib,json,re
import wx
APP=wx.App(False)
import pcbnew as K
ROOT=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def mech(p):return[K.ToMM(p.x)-100,130-K.ToMM(p.y)]
def rect(fp,layers):
    ss=[s.GetBoundingBox()for s in fp.GraphicalItems()if isinstance(s,K.PCB_SHAPE)and s.GetLayer()in layers]
    if not ss:return None
    return[K.ToMM(min(s.GetLeft()for s in ss))-100,130-K.ToMM(max(s.GetBottom()for s in ss)),K.ToMM(max(s.GetRight()for s in ss))-100,130-K.ToMM(min(s.GetTop()for s in ss))]
def overlap(a,b):return min(a[2],b[2])-max(a[0],b[0])>1e-6 and min(a[3],b[3])-max(a[1],b[1])>1e-6
ap=argparse.ArgumentParser();ap.add_argument('directory',type=Path);ap.add_argument('domain',choices=['body','flange']);ap.add_argument('--drc',action='store_true');args=ap.parse_args()
p=args.directory.resolve();path=p/(args.domain+'-r12.kicad_pcb');before=sha(path);b=K.LoadBoard(str(path));b.BuildConnectivity()
source=json.loads((ROOT/'hardware/pcb/prototype-r2/candidate-pin-manifest.json').read_text())
expected={q['ref']:q for q in source['parts']if q.get('on_main_board')}
heights=json.loads((ROOT/'hardware/pcb/prototype-r2/layout-candidates-r0.json').read_text())['parts']
pinmap={str(i+1):n for i,n in enumerate(['GND','DOCK_5V','3V3','PACK_P','MOTOR_ARM','MOTOR_PWM','DOCK_PRESENT_N','I2C_SDA','I2C_SCL','ACCEL_INT_N'])}
rows=[];mismatches=[]
for f in b.GetFootprints():
    ref=f.GetReference();side='B'if f.GetLayer()==K.B_Cu else'F'
    actual={q.GetNumber():q.GetNetname()for q in f.Pads()if q.GetNumber()not in('','MP')}
    want=pinmap if ref in ['J6','J7']else{n:(v['net']or'')for n,v in expected[ref]['pins'].items()}
    if actual!=want:mismatches.append({'ref':ref,'actual':actual,'expected':want})
    h = heights[ref]['height_mm'] if ref in heights else 3.2
    sig=[mech(q.GetPosition())for q in f.Pads()if q.GetNumber()not in('','MP')]
    mp=[mech(q.GetPosition())for q in f.Pads()if q.GetNumber()=='MP'];direction=None
    if ref.startswith('J')and sig and mp:
        v=[sum(q[i]for q in mp)/len(mp)-sum(q[i]for q in sig)/len(sig)for i in[0,1]];ln=(v[0]**2+v[1]**2)**.5
        if ln>1e-8:direction=[v[0]/ln,v[1]/ln]
    rows.append({'ref':ref,'xy_mm':mech(f.GetPosition()),'side':side,'angle_deg':f.GetOrientationDegrees(),'courtyard_xy_mm':rect(f,[K.F_CrtYd,K.B_CrtYd]),'body_xy_mm':rect(f,[K.F_Fab,K.B_Fab]),'height_budget_mm':h,'z_bounds_mm':[-.5-h,-.5]if side=='B'else[.5,.5+h],'mating_direction_xy_study':direction,'pads':[{'n':q.GetNumber(),'net':q.GetNetname(),'xy_mm':mech(q.GetPosition()),'size_xy_mm':[K.ToMM(q.GetSize().x),K.ToMM(q.GetSize().y)]}for q in f.Pads()]})
overlaps=[{'a':a['ref'],'b':c['ref']}for i,a in enumerate(rows)for c in rows[i+1:]if a['side']==c['side']and overlap(a['courtyard_xy_mm'],c['courtyard_xy_mm'])]
counts=None;error=None
if args.drc:
    try:
        rpt=p/(args.domain+'-fresh-native-drc.txt');K.WriteDRCReport(b,str(rpt),K.EDA_UNITS_MILLIMETRES,True);t=rpt.read_text()
        counts={n:int(re.search(rx,t).group(1))for n,rx in [('violations',r'\*\* Found (\d+) DRC violations'),('unconnected',r'\*\* Found (\d+) unconnected pads'),('footprint_errors',r'\*\* Found (\d+) Footprint errors')]}
    except Exception as e:error=str(e)
assert sha(path)==before
r={'board_sha256':before,'inspector_sha256':sha(Path(__file__)),'domain':args.domain,'footprints':len(rows),'placements':rows,'pad_net_mismatches':mismatches,'same_face_courtyard_bbox_overlaps':overlaps,'native_DRC_counts':counts,'native_DRC_error':error,'scope':'Actual saved footprints/padnets/poses and conservative courtyard rectangles. Separate nativeDRC where requested. Unrouted; no complete circuit/schematic/PCB/harness/process acceptance.'}
(p/(args.domain+'-native-inspection.json')).write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({'domain':args.domain,'footprints':len(rows),'parity_mismatches':len(mismatches),'courtyard_bbox_overlaps':overlaps,'DRC':counts,'error':error},indent=2))
