"""Create two UNROUTED native placement candidates from the preserved R2 board.

All87 source footprints/pad nets retained once; add two candidate SH10 headers.
Bounded rectangle placement is floorplanning, not power-layout acceptance.
"""
from pathlib import Path
import argparse,hashlib,json,math,random,shutil,collections,re
import wx
APP=wx.App(False)
import pcbnew as K
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'hardware/pcb/prototype-r2'
SOURCE=BASE/'buttplug-r2.kicad_pcb'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def xy(x,y):return K.VECTOR2I(K.FromMM(100+x),K.FromMM(130-y))
def mech(p):return [K.ToMM(p.x)-100,130-K.ToMM(p.y)]
def rect(fp,layers):
    ss=[s.GetBoundingBox()for s in fp.GraphicalItems()if isinstance(s,K.PCB_SHAPE)and s.GetLayer()in layers]
    if not ss:return None
    return [K.ToMM(min(s.GetLeft()for s in ss))-100,130-K.ToMM(max(s.GetBottom()for s in ss)),
            K.ToMM(max(s.GetRight()for s in ss))-100,130-K.ToMM(min(s.GetTop()for s in ss))]
def overlap(a,b):return min(a[2],b[2])-max(a[0],b[0])>1e-6 and min(a[3],b[3])-max(a[1],b[1])>1e-6
def area(a):return(a[2]-a[0])*(a[3]-a[1])
def split_free(free,p):
    p=[p[0]-.01,p[1]-.01,p[2]+.01,p[3]+.01]
    result=[]
    for f in free:
        if not overlap(f,p):result.append(f);continue
        if p[0]>f[0]:result.append([f[0],f[1],p[0],f[3]])
        if p[2]<f[2]:result.append([p[2],f[1],f[2],f[3]])
        if p[1]>f[1]:result.append([f[0],f[1],f[2],p[1]])
        if p[3]<f[3]:result.append([f[0],p[3],f[2],f[3]])
    result=[f for f in result if f[2]-f[0]>.3 and f[3]-f[1]>.3]
    unique=[]
    for i,f in enumerate(result):
        if any(j!=i and g[0]<=f[0]+1e-7 and g[1]<=f[1]+1e-7 and g[2]>=f[2]-1e-7 and g[3]>=f[3]-1e-7 and (area(g)>area(f)+1e-7 or j<i)for j,g in enumerate(result)):continue
        unique.append(f)
    return unique
def pose(fp,x,y,angle,side):
    if(fp.GetLayer()==K.B_Cu)!=(side=='B'):fp.Flip(fp.GetPosition(),True)
    fp.SetOrientationDegrees(angle);fp.SetPosition(xy(x,y));fp.SetLocked(False)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output-dir',type=Path,required=True);ap.add_argument('--seeds',type=int,default=100);args=ap.parse_args()
    out=args.output_dir.resolve();out.mkdir(parents=True,exist_ok=True)
    assert not any(out.glob('*.kicad_pcb')),'Preserve executed candidates'
    assert sha(SOURCE)=='5ba844fad77f58a8a5dfcb67f50e9070cf021048c29ed45a2751a9b8067f0bd4'
    allocation=json.loads((ROOT/'hardware/design/body-flange-partition-r9/partition.json').read_text())['allocation']
    manifest=json.loads((BASE/'candidate-pin-manifest.json').read_text())
    expected={p['ref']:p for p in manifest['parts']if p.get('on_main_board')}
    candidates=json.loads((BASE/'layout-candidates-r0.json').read_text())['parts']
    lib=out/'PrototypeR0.pretty';shutil.copytree(BASE/'PrototypeR0.pretty',lib)
    newname='JST_SH_SM10B-SRSS-TB_1x10-1MP_P1.00mm_Horizontal'
    stock=Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/Connector_JST.pretty')/(newname+'.kicad_mod')
    shutil.copyfile(stock,lib/stock.name)
    (out/'fp-lib-table').write_text('(fp_lib_table (lib (name "PrototypeR0")(type "KiCad")(uri "${KIPRJMOD}/PrototypeR0.pretty")(options "")(descr "Copied candidate footprints plus isolated SH10 candidate")))\n')
    pinmap={str(i+1):n for i,n in enumerate(['GND','DOCK_5V','3V3','PACK_P','MOTOR_ARM','MOTOR_PWM','DOCK_PRESENT_N','I2C_SDA','I2C_SCL','ACCEL_INT_N'])}
    reg1=set('U2 L1 C11 C12 C13 C14 C15 C16 C51 C52 R11 R12 R13'.split())
    reg2=set('U3 L2 C21 C22 C23 C24 C25 C26 C53 C54 R21 R22 R26'.split())
    charge=set('U1 F1 D1 C1 C2 C3 R1 R2 R3 R4 R5'.split())
    boards={};fpsets={};metrics={};heights={};output={}
    outlines={'body':[[-7,26],[7,26],[9,31],[9,54],[-9,54],[-9,31]],
              'flange':[[-37.3,-26],[-13.8,-26],[-13.8,-11],[-37.3,-11]]}
    boxes={'body':[-8.65,26.25,8.65,53.75],'flange':[-37.05,-25.75,-14.05,-11.25]}
    for domain,newref in [('body','J6'),('flange','J7')]:
        b=K.LoadBoard(str(SOURCE))
        for track in list(b.GetTracks()):b.Delete(track)
        for zone in list(b.Zones()):b.Delete(zone)
        for drawing in list(b.GetDrawings()):b.Delete(drawing)
        for fp in list(b.GetFootprints()):
            if allocation[fp.GetReference()]!=domain:b.Delete(fp)
        new=K.FootprintLoad(str(lib),newname);new.SetReference(newref);new.SetValue('SM10B-SRSS-TB candidate');new.SetFPID(K.LIB_ID('PrototypeR0',newname));b.Add(new)
        new.Reference().SetVisible(False);new.Value().SetVisible(False)
        for pad in new.Pads():
            if pad.GetNumber()in pinmap:pad.SetNet(b.FindNet(pinmap[pad.GetNumber()]))
        boards[domain]=b;fpsets[domain]={fp.GetReference():fp for fp in b.GetFootprints()}
        for ref,fp in fpsets[domain].items():
            heights[ref]=candidates[ref]['height_mm']if ref in candidates else 3.2
            metrics[ref]={}
            for side in ['F','B']:
                for angle in [0,90,180,270]:
                    pose(fp,0,0,angle,side);bb=rect(fp,[K.F_CrtYd,K.B_CrtYd]);assert bb,ref
                    body=rect(fp,[K.F_Fab,K.B_Fab]);mate=None
                    sig=[mech(q.GetPosition())for q in fp.Pads()if q.GetNumber()not in('','MP')]
                    mp=[mech(q.GetPosition())for q in fp.Pads()if q.GetNumber()=='MP']
                    if ref.startswith('J')and sig and mp:
                        v=[sum(q[i]for q in mp)/len(mp)-sum(q[i]for q in sig)/len(sig)for i in[0,1]]
                        length=math.hypot(*v);v=[round(q/length)for q in v];u=[-v[1],v[0]]
                        n=len({q.GetNumber()for q in fp.Pads()if q.GetNumber()not in('','MP')})
                        width=2*n+1.8 if '_PH_'in str(fp.GetFPID().GetLibItemName())else n+1
                        front=max(x*v[0]+y*v[1]for x in[body[0],body[2]]for y in[body[1],body[3]])
                        pts=[[(front+lead)*v[j]+transverse*width/2*u[j]for j in[0,1]]for lead in[0,2]for transverse in[-1,1]]
                        mate=[min(q[0]for q in pts),min(q[1]for q in pts),max(q[0]for q in pts),max(q[1]for q in pts)]
                    metrics[ref][(side,angle)]={'rect':bb,'w':bb[2]-bb[0],'h':bb[3]-bb[1],'body':body,'mate':mate}

    def allowed(domain,r,ref,side):
        edge=boxes[domain]
        if r[0]<edge[0]-1e-6 or r[1]<edge[1]-1e-6 or r[2]>edge[2]+1e-6 or r[3]>edge[3]+1e-6:return False
        if domain=='body':
            half=min(9,7+.4*(r[1]-26))-.35
            if max(abs(r[0]),abs(r[2]))>half+1e-6:return False
            if side=='B'and heights[ref]>2.75:return False
            if r[1]<31 and heights[ref]>3 and ref!='J6':return False
        return True
    neighbors=collections.defaultdict(list)
    netrefs=collections.defaultdict(set)
    for ref,p in expected.items():
        for v in p['pins'].values():
            if v['net']:netrefs[v['net']].add(ref)
    for net,refs in netrefs.items():
        if net in ['GND','3V3','SYS','PACK_P','VBUS_CHG']or len(refs)>8:continue
        for a in refs:
            for b in refs:
                if a!=b:neighbors[a].append((b,4 if net.startswith(('SW_','FB_')) else 1))
    fixed={'body':{'J6':(0,31.1,0,'F'),'J2':(-3.525,41.125,90,'F'),'J3':(-4.7,50.8,90,'F'),
                   'J5':(5,49.7,270,'F'),'U1':(4.7,39.4,0,'F')},
           'flange':{'J7':(-33.4,-18.5,270,'B'),'J1':(-24.6,-20.5,0,'B'),'J4':(-19.4,-22,0,'F'),
                     'SW1':(-22.85,-14,0,'F'),'SW2':(-16.85,-14,0,'F')}}
    for domain in boards:
        refs=list(fpsets[domain]);best=None
        for seed in range(args.seeds):
            rng=random.Random(seed);free={'F':[boxes[domain][:]],'B':[boxes[domain][:]]};placed={};failed=[];mate_reservations=[]
            if domain=='flange':
                fp=fpsets[domain]['U6'];pose(fp,-31.7,-18.5,90,'F');bb=rect(fp,[K.F_CrtYd,K.B_CrtYd])
                placed['U6']={'rect':bb,'side':'F','angle':90,'anchor':[-31.7,-18.5]};free['F']=split_free(free['F'],bb)
            for ref,(x,y,a,side)in fixed[domain].items():
                mm=metrics[ref][(side,a)];rr=[x-mm['w']/2,y-mm['h']/2,x+mm['w']/2,y+mm['h']/2]
                if not allowed(domain,rr,ref,side)or any(p['side']==side and overlap(rr,p['rect'])for p in placed.values()):failed.append(ref)
                placed[ref]={'rect':rr,'side':side,'angle':a};free[side]=split_free(free[side],rr)
            # Reserve plugs after fixed headers are placed. Plug may overlap its
            # own header courtyard, but must not occupy another component body.
            for ref,p in placed.items():
                mm=metrics[ref][(p['side'],p['angle'])]
                if not mm['mate']:continue
                dx=p['rect'][0]-mm['rect'][0];dy=p['rect'][1]-mm['rect'][1]
                mate=[q+(dx if i%2==0 else dy)for i,q in enumerate(mm['mate'])]
                mate_reservations.append({'ref':ref,'side':p['side'],'rect':mate})
                free[p['side']]=split_free(free[p['side']],mate)
                for other,q in placed.items():
                    if other==ref or q['side']!=p['side']:continue
                    qm=metrics[other][(q['side'],q['angle'])];offset=[q['rect'][0]-qm['rect'][0],q['rect'][1]-qm['rect'][1]]
                    qb=[v+offset[i%2]for i,v in enumerate(qm['body'])]
                    if overlap(mate,qb):failed.append(ref+'-mate-vs-'+other)
            remaining=[r for r in refs if r not in placed]
            remaining.sort(key=lambda r:-(metrics[r][('F',0)]['w']*metrics[r][('F',0)]['h'])*(1+rng.uniform(-.22,.22)))
            for ref in remaining:
                choices=[]
                # Keep charger power capacitors on its face; put the series
                # input diode with the input fuse on B. Setting resistors may
                # use either face. Routing still
                # must earn the loop/thermal requirements, independent of fit.
                sides=['B']if domain=='body'and ref in reg1|reg2|{'F1','D1'} else ['F']if domain=='body'and ref in {'U1','C1','C2','C3'} else ['F','B']
                target=(4,41)if ref in reg1 else(-4,46)if ref in reg2 else(4.4,39.4)if ref in charge else(0,39)if domain=='body'else(-28,-19)
                for side in sides:
                    for angle in [0,90,180,270]:
                        mm=metrics[ref][(side,angle)];w,h=mm['w'],mm['h']
                        for f in free[side]:
                            if w>f[2]-f[0]+1e-6 or h>f[3]-f[1]+1e-6:continue
                            ys={f[1],f[3]-h,max(f[1],min(f[3]-h,target[1]-h/2))}
                            if domain=='body'and f[1]<=31<=f[3]-h:ys.add(31)
                            for y in ys:
                                xs={f[0],f[2]-w,max(f[0],min(f[2]-w,target[0]-w/2))}
                                if domain=='body':
                                    half=min(9,7+.4*(y-26))-.35;xs.add(max(f[0],-half));xs.add(min(f[2]-w,half-w))
                                for x in xs:
                                    rr=[x,y,x+w,y+h]
                                    if x<f[0]-1e-6 or x+w>f[2]+1e-6 or not allowed(domain,rr,ref,side):continue
                                    cx,cy=x+w/2,y+h/2
                                    dist=abs(cx-target[0])+abs(cy-target[1])
                                    for n,weight in neighbors[ref]:
                                        if n in placed:
                                            q=placed[n]['rect'];dist+=weight*(abs(cx-(q[0]+q[2])/2)+abs(cy-(q[1]+q[3])/2))
                                    short=min(f[2]-f[0]-w,f[3]-f[1]-h)
                                    score=short+.035*dist+.0005*(area(f)-w*h)+rng.random()*.02
                                    choices.append((score,side,angle,rr))
                if not choices:failed.append(ref);continue
                _,side,angle,rr=min(choices,key=lambda q:q[0]);placed[ref]={'rect':rr,'side':side,'angle':angle};free[side]=split_free(free[side],rr)
            score=(len(failed),-sum(area(p['rect'])for ref,p in placed.items()if ref not in fixed[domain]))
            if best is None or score<best[0]:best=(score,seed,placed,failed,mate_reservations)
            if not failed:break
        _,seed,placed,failed,mate_reservations=best;print(domain,'seed',seed,'placed',len(placed),'unplaced/fixed-conflicts',failed,flush=True)
        b=boards[domain]
        for j,(ref,fp)in enumerate(fpsets[domain].items()):
            if ref not in placed:pose(fp,35+j*4,-40,0,'F');continue
            p=placed[ref]
            if 'anchor'in p:pose(fp,*p['anchor'],p['angle'],p['side'])
            else:
                mm=metrics[ref][(p['side'],p['angle'])]['rect'];x=p['rect'][0]-mm[0];y=p['rect'][1]-mm[1];pose(fp,x,y,p['angle'],p['side'])
            fp.SetProperty('PlacementStatus','R12 UNROUTED / split candidate / not fabrication')
        for a,c in zip(outlines[domain],outlines[domain][1:]+outlines[domain][:1]):
            s=K.PCB_SHAPE();s.SetShape(K.SHAPE_T_SEGMENT);s.SetStart(xy(*a));s.SetEnd(xy(*c));s.SetLayer(K.Edge_Cuts);s.SetWidth(K.FromMM(.05));b.Add(s)
        board=out/(domain+'-r12.kicad_pcb');project=out/(domain+'-r12.kicad_pro')
        pr=json.loads((BASE/'buttplug-r2.kicad_pro').read_text());pr.setdefault('meta',{})['filename']=project.name;project.write_text(json.dumps(pr,indent=2)+'\n')
        K.SaveBoard(str(board),b);saved=K.LoadBoard(str(board));saved.BuildConnectivity()
        rpt=out/(domain+'-placement-drc.txt')
        rows=[];parity=[]
        for fp in saved.GetFootprints():
            ref=fp.GetReference();want=pinmap if ref in ['J6','J7']else{n:(p['net']or'')for n,p in expected[ref]['pins'].items()}
            actual={p.GetNumber():p.GetNetname()for p in fp.Pads()if p.GetNumber()not in('','MP')}
            if actual!=want:parity.append({'ref':ref,'actual':actual,'expected':want})
            side='B'if fp.GetLayer()==K.B_Cu else'F'
            rows.append({'ref':ref,'source_domain':allocation.get(ref,'new_interboard_header'),'xy_mm':mech(fp.GetPosition()),'side':side,'angle_deg':fp.GetOrientationDegrees(),
                         'courtyard_xy_mm':rect(fp,[K.F_CrtYd,K.B_CrtYd]),'body_xy_mm':rect(fp,[K.F_Fab,K.B_Fab]),'height_budget_mm':heights[ref],
                         'z_bounds_mm':[-.5-heights[ref],-.5]if side=='B'else[.5,.5+heights[ref]],'pads':[{'n':p.GetNumber(),'net':p.GetNetname(),'xy_mm':mech(p.GetPosition())}for p in fp.Pads()]})
        output[domain]={'board_sha256':sha(board),'project_sha256':sha(project),'placements':rows,'seed':seed,'unplaced_or_fixed_conflicts':failed,'pad_net_mismatches':parity,'mate_reservations_nominal_xy_mm':mate_reservations,'native_DRC_counts':None,'native_DRC_status':'Pending fresh one-board native process; do not claim DRC from packing','outline_mechanical_xy_mm':outlines[domain]}
    assert sha(SOURCE)=='5ba844fad77f58a8a5dfcb67f50e9070cf021048c29ed45a2751a9b8067f0bd4'
    result={'status':'UNROUTED two-board floorplan, not fabrication/assembly acceptance','date':'2026-11-01','generator_sha256':sha(Path(__file__)),
            'source_board_sha256':sha(SOURCE),'source_partition_sha256':sha(ROOT/'hardware/design/body-flange-partition-r9/partition.json'),
            'new_connector_candidate':{'header':'SM10B-SRSS-TB','housing':'SHR-10V-S-B','contact':'SSH-003T-P0.2-H','pinmap':pinmap,'primary_source':'https://www.jst-mfg.com/product/pdf/eng/eSH.pdf','stock_footprint_sha256':sha(stock),'height_budget_mm':3.2,'qualified_harness':False},
            'preserved_source_footprints':87,'new_footprints':2,'boards':output,
            'scope':'Actual native footprint geometry/nets split from unchanged R2. Placement rectangles/coupling only; power loop routing, interboard schematic integration, mates/wires/strain, working controls, RF3D/case/carrier fit and manufacturing process remain open. No copper routes or ground fills transferred.'}
    (out/'placement-report.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({d:{'counts':v['native_DRC_counts'],'unplaced':v['unplaced_or_fixed_conflicts'],'parity':v['pad_net_mismatches']}for d,v in output.items()},indent=2),flush=True)
if __name__=='__main__':main()
