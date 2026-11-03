"""Functional power-stage repack inside the unchanged R12 body outline.

Native placement trial, not routing/MCAD acceptance. Preserve all parts/nets;
forward motor/tip headers require a fresh carrier/keeper mating screen.
"""
from pathlib import Path
import argparse,json,shutil,random,hashlib,re
import pcb_split_r12 as G
import kicad_sexp as S
K=G.K;ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/'hardware/pcb/route-r15/candidate-t';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ap=argparse.ArgumentParser();ap.add_argument('directory',type=Path);ap.add_argument('--source',type=Path,default=SOURCE);ap.add_argument('--compact-resistors',action='store_true');a=ap.parse_args();SOURCE=a.source.resolve();P=a.directory.resolve();P.mkdir(parents=True,exist_ok=True);assert not any(P.iterdir())
for p in SOURCE.rglob('*'):
 if p.is_file()and(p.suffix in ['.kicad_pcb','.kicad_pro','.kicad_sch','.kicad_sym','.kicad_mod']or p.name in ['fp-lib-table','sym-lib-table']):
  q=P/str(p.relative_to(SOURCE)).replace('-r15','-r16');q.parent.mkdir(parents=True,exist_ok=True)
  if p.suffix=='.kicad_sch':q.write_text(p.read_text().replace('-r15','-r16'))
  elif p.suffix=='.kicad_pro':
   j=json.loads(p.read_text());j['meta']['filename']=q.name;q.write_text(json.dumps(j,indent=2)+'\n')
  else:shutil.copyfile(p,q)
bp=P/'body/body-r16.kicad_pcb';b=K.LoadBoard(str(bp));assert not list(b.GetTracks());fps={f.GetReference():f for f in b.GetFootprints()};old=K.LoadBoard(str(ROOT/'hardware/pcb/prototype-r2/buttplug-r2.kicad_pcb'));oldfps={f.GetReference():f for f in old.GetFootprints()}
# Smaller positive-lock battery/header candidate; pin numbers/nets conserved.
name='Molex_Pico-Lock_504050-0491_1x04-1MP_P1.50mm_Horizontal';stock=Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/Connector_Molex.pretty');shutil.copyfile(stock/(name+'.kicad_mod'),P/'body/PrototypeR0.pretty'/(name+'.kicad_mod'));orig=fps['J2'];nets={p.GetNumber():p.GetNetname()for p in orig.Pads()if p.GetNumber()not in ['','MP']};context=orig.GetPath();b.Delete(orig);fp=K.FootprintLoad(str(P/'body/PrototypeR0.pretty'),name);fp.SetReference('J2');fp.SetValue('504050-0491 candidate');fp.SetPath(context);fp.SetFPID(K.LIB_ID('PrototypeR0',name));fp.Reference().SetVisible(False);fp.Value().SetVisible(False);b.Add(fp);fps['J2']=fp
for pad in fp.Pads():
 if pad.GetNumber()in nets:pad.SetNet(b.FindNet(nets[pad.GetNumber()]))
power=P/'body/01-power.kicad_sch';txt=power.read_text();txt=txt.replace('PrototypeR0:JST_PH_S4B-PH-SM4-TB_1x04-1MP_P2.00mm_Horizontal','PrototypeR0:'+name).replace('S4B-PH-SM4-TB','504050-0491 candidate');power.write_text(txt)
res_changes={}
if a.compact_resistors:
 rname='R_0402_1005Metric';stock=Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/Resistor_SMD.pretty');shutil.copyfile(stock/(rname+'.kicad_mod'),P/'body/PrototypeR0.pretty'/(rname+'.kicad_mod'))
 for ref in 'R1 R2 R3 R4 R5 R23 R24 R25 R41 R42 R46 R47 R48'.split():
  orig=fps[ref];value=orig.GetValue();assert value.startswith('TNPW0603')and value.endswith('BEEA');newvalue=value.replace('TNPW0603','TNPW0402')[:-4]+'BEED';context=orig.GetPath();nets={p.GetNumber():p.GetNetname()for p in orig.Pads()};b.Delete(orig);fp=K.FootprintLoad(str(P/'body/PrototypeR0.pretty'),rname);fp.SetReference(ref);fp.SetValue(newvalue);fp.SetPath(context);fp.SetFPID(K.LIB_ID('PrototypeR0',rname));fp.Reference().SetVisible(False);fp.Value().SetVisible(False);b.Add(fp);fps[ref]=fp
  for pad in fp.Pads():pad.SetNet(b.FindNet(nets[pad.GetNumber()]))
  res_changes[ref]={'old_value':value,'new_value':newvalue,'new_footprint':'PrototypeR0:'+rname,'scope':'Same resistance/0.1percent/25ppm candidate,0402/EDpackaging under Vishay28758 Apr2026 range<=100k. Generic IPC land/stencil/power/thermal/availability review required.'}
 for sheet in(P/'body').glob('*.kicad_sch'):
  root=S.parse(sheet.read_text())
  for symbol in S.children(root,'symbol'):
   ref=S.prop(symbol,'Reference')
   if ref not in res_changes:continue
   change=res_changes[ref];note=S.prop(symbol,'ReviewNote');oldmpn=change['old_value'];mpn=change['new_value']
   note=note.replace(oldmpn,mpn)if oldmpn in note else(note+'; 'if note else'')+mpn+' / 0402 candidate'
   changes={'Footprint':change['new_footprint'],'ReviewNote':note,'Datasheet':'https://www.vishay.com/docs/28758/tnpw_e3.pdf'}
   # Schematic Value remains the nominal resistance/function. The PCB Value
   # identifies the candidate MPN, following the existing board convention.
   for prop in S.children(symbol,'property'):
    if prop[1].value in changes:prop[2]=S.string(changes[prop[1].value])
  S.write(sheet,root)
regs='U2 L1 C11 C12 C13 C14 C15 C16 C51 C52 R11 R12 R13'.split();regs2='U3 L2 C21 C22 C23 C24 C25 C26 C53 C54 R21 R22 R26'.split();fixed={};group_boxes=[]
for names,dy in [(regs,56.5),(regs2,67.5)]:
 for orig,ref in zip(regs,names):
  src=oldfps[orig];x,y=G.mech(src.GetPosition());x-=7.4875;y+=dy
  if ref=='R21':y+=.15
  if ref=='C23':y+=.3
  fixed[ref]=(x,y,src.GetOrientationDegrees(),'B')
fixed.update({'J6':(0,31.0,0,'F'),'J2':(-4.78,40.5,270,'F'),'U1':(4.7,39.4,0,'F'),
 'C1':(7.725,36.240001,90,'F'),'C2':(7.725,39.4,90,'F'),'C3':(.8,39.45,180,'F'),
 'J3':(-4.4,50.35,180,'F'),'J5':(3.3,50.35,180,'F'),
 'U5':(6,45.3,90,'F'),'C28':(3.8,45.3,270,'F'),'C29':(7.975,44.8,90,'F'),'C30':(1.05,43.5,90,'F'),
 'Q1':(.8,36.4,90,'F'),'U7':(4.8,28,180,'B'),'C27':(5,30.2,0,'B'),
 'U8':(-5.025,28.325,90,'B'),'U9':(-1.565,28.325,90,'B'),'U4':(1.895,28.325,90,'B'),
 'C41':(-5.025,31.085,0,'B'),'C42':(-2.465,31.085,0,'B'),'C43':(.095,31.085,0,'B')})
height=json.loads((ROOT/'hardware/pcb/prototype-r2/layout-candidates-r0.json').read_text())['parts'];metrics={}
for ref,fp in fps.items():
 metrics[ref]={}
 for side in ['F','B']:
  for angle in [0,90,180,270]:
   G.pose(fp,0,0,angle,side);bb=G.rect(fp,[K.F_CrtYd,K.B_CrtYd]);metrics[ref][side,angle]=bb
placed={};fixed_conflicts=[];mates=[];fixed_bounds=[]
for ref,(x,y,angle,side)in fixed.items():
 fp=fps[ref];G.pose(fp,x,y,angle,side);placed[ref]={'side':side,'angle':angle,'rect':G.rect(fp,[K.F_CrtYd,K.B_CrtYd]),'anchor':[x,y]}
for names in [regs,regs2]:
 boxes=[placed[n]['rect']for n in names];group_boxes.append([min(c[0]for c in boxes),min(c[1]for c in boxes),max(c[2]for c in boxes),max(c[3]for c in boxes)])
for i,(ref,p)in enumerate(placed.items()):
 for other,q in list(placed.items())[i+1:]:
  if p['side']==q['side']and G.overlap(p['rect'],q['rect']):fixed_conflicts.append([ref,other])
for ref in ['J2','J3','J5','J6']:
 fp=fps[ref];bb=G.rect(fp,[K.F_Fab,K.B_Fab]);sig=[G.mech(p.GetPosition())for p in fp.Pads()if p.GetNumber()not in ['','MP']];mp=[G.mech(p.GetPosition())for p in fp.Pads()if p.GetNumber()=='MP'];v=[sum(q[i]for q in mp)/len(mp)-sum(q[i]for q in sig)/len(sig)for i in [0,1]];v=[round(z/(sum(t*t for t in v)**.5))for z in v];u=[-v[1],v[0]];n=len(sig);width=10 if ref=='J2'else n+1;front=max(x*v[0]+y*v[1]for x in [bb[0],bb[2]]for y in [bb[1],bb[3]]);cx,cy=G.mech(fp.GetPosition());t=cx*u[0]+cy*u[1];pts=[[(front+lead)*v[j]+(t+sign*width/2)*u[j]for j in [0,1]]for lead in [0,2]for sign in [-1,1]];rr=[min(p[0]for p in pts),min(p[1]for p in pts),max(p[0]for p in pts),max(p[1]for p in pts)];mates.append({'ref':ref,'rect':rr,'direction':v,'scope':'J2 nominal10mm transverse/2mm extension/2.3mm height allowance only; actual housing/locking fingers/wires drawing needed.'if ref=='J2'else'Inherited SH nominal probe only'})
 for other,q in placed.items():
  if other!=ref and q['side']=='F'and G.overlap(rr,G.rect(fps[other],[K.F_Fab,K.B_Fab])):fixed_conflicts.append([ref+'-mate',other])
def allowed(rr):
 return rr[1]>=26.25 and rr[3]<=53.75 and max(abs(rr[0]),abs(rr[2]))<=min(8.65,6.65+.4*(rr[1]-26))+1e-7
for ref,p in placed.items():
 if not allowed(p['rect']):fixed_bounds.append(ref)
remaining=[r for r in fps if r not in fixed];base_free={'F':[[-8.65,26.25,8.65,53.75]],'B':[[-8.65,26.25,8.65,53.75]]}
for side in ['F','B']:
 for ref,p in placed.items():
  if p['side']==side:base_free[side]=G.split_free(base_free[side],p['rect'])
 for box in group_boxes if side=='B'else []:base_free[side]=G.split_free(base_free[side],box)
for m in mates:base_free['F']=G.split_free(base_free['F'],m['rect'])
best=None
local_caps={'C41':'U8','C42':'U9','C43':'U4','C27':'U7'}
for seed in range(400):
 rng=random.Random(seed);free={s:[r[:]for r in rr]for s,rr in base_free.items()};new={};failed=[];order=remaining[:];order.sort(key=lambda r:(0 if r.startswith('U')else 1 if r in local_caps else 2,-(metrics[r]['F',0][2]-metrics[r]['F',0][0])*(metrics[r]['F',0][3]-metrics[r]['F',0][1])*rng.uniform(.75,1.25)))
 for ref in order:
  choices=[]
  for side in ['F','B']:
   for angle in [0,90,180,270]:
    bb=metrics[ref][side,angle];w,h=bb[2]-bb[0],bb[3]-bb[1]
    for f in free[side]:
     if f[2]-f[0]<w or f[3]-f[1]<h:continue
     for y in [f[1],f[3]-h]:
      half=min(8.65,6.65+.4*(y-26));left=max(f[0],-half);right=min(f[2]-w,half-w)
      if right<left:continue
      for x in [left,right]:
       rr=[x,y,x+w,y+h]
       distance=0
       if ref in local_caps:
        target=new.get(local_caps[ref],placed.get(local_caps[ref]))
        if target is None or side!=target['side']:continue
        tb=metrics[local_caps[ref]][target['side'],target['angle']];tx,ty=target['rect'][0]-tb[0],target['rect'][1]-tb[1];distance=((x-bb[0]-tx)**2+(y-bb[1]-ty)**2)**.5
        if distance>3.8:continue
       if allowed(rr):choices.append((min(f[2]-f[0]-w,f[3]-f[1]-h)+(.01 if side=='F'else 0)+distance,side,angle,rr))
  if not choices:failed.append(ref);continue
  _,side,angle,rr=min(choices,key=lambda t:t[0]);new[ref]={'side':side,'angle':angle,'rect':rr};free[side]=G.split_free(free[side],rr)
 if best is None or len(failed)<len(best[2]):best=(seed,new,failed)
 if not failed:break
seed,new,failed=best;placed.update(new)
for ref,p in new.items():
 bb=metrics[ref][p['side'],p['angle']];G.pose(fps[ref],p['rect'][0]-bb[0],p['rect'][1]-bb[1],p['angle'],p['side'])
for i,ref in enumerate(failed):G.pose(fps[ref],30+i*4,40,0,'F')
for fp in fps.values():fp.SetProperty('PlacementStatus','R16 functional power placement trial / UNROUTED / NOT FABRICATION')
source_body=next(SOURCE.glob('body/body-*.kicad_pcb'));source_flange=next(SOURCE.glob('flange/flange-*.kicad_pcb'))
K.SaveBoard(str(bp),b);record={'date':'2026-11-01','generator_sha256':sha(Path(__file__)),'source_directory':str(SOURCE.relative_to(ROOT)),'source_body_sha256':sha(source_body),'native_body_sha256':sha(bp),'flange_board_byte_identical_to_source':sha(P/'flange/flange-r16.kicad_pcb')==sha(source_flange),'fixed_poses':fixed,'resistor_changes':res_changes,'regulator_group_reserved_boxes':group_boxes,'fixed_courtyard_or_mate_conflicts':fixed_conflicts,'fixed_outline_failures':fixed_bounds,'nominal_mates':mates,'packing_seed':seed,'unplaced':failed,'scope':'New physical native functional placement trial only. Reuses R2 regulator1 local poses for both identical power IC packages; motor feedback0805/outputcap explicit offsets. J2PicoLockcandidate and listed0402resistors changefootprint/value only; all nets/parts/outline preserved. Forward header mates require a fresh mechanical check; no routing/ERC/physical acceptance.'};(P/'body-repack.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps({k:record[k]for k in ['fixed_courtyard_or_mate_conflicts','fixed_outline_failures','packing_seed','unplaced']},indent=2),flush=True)
