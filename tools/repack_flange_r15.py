"""Repack flange for short supply/reset paths and an unobstructed F USB path.

SH2 dock candidate replaces PH2 (same two nets). User controls and antenna
stay at their R14 poses. Body circuit/placement is unchanged. No BOM edits.
"""
from pathlib import Path
import argparse,hashlib,json,random,shutil
import pcb_split_r12 as G
K=G.K;ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/'hardware/pcb/split-r14/candidate-b';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ap=argparse.ArgumentParser();ap.add_argument('directory',type=Path);args=ap.parse_args();OUT=args.directory.resolve();OUT.mkdir(parents=True,exist_ok=True)
assert not any(OUT.rglob('*.kicad_pcb')),'Preserve each executed placement attempt'
for p in SOURCE.rglob('*'):
 if not p.is_file()or p.suffix not in ['.kicad_sch','.kicad_pro','.kicad_sym','.kicad_mod']and p.name not in ['sym-lib-table','fp-lib-table']:continue
 relative=p.relative_to(SOURCE);q=OUT/str(relative).replace('-r14','-r15');q.parent.mkdir(parents=True,exist_ok=True)
 if p.suffix=='.kicad_sch':
  text=p.read_text()
  for name in ['system','body','flange']:text=text.replace('"'+name+'-r14"','"'+name+'-r15"').replace(name+'-r14.kicad_sch',name+'-r15.kicad_sch')
  if relative==Path('flange/01-power.kicad_sch'):
   old='PrototypeR0:JST_PH_S2B-PH-SM4-TB_1x02-1MP_P2.00mm_Horizontal';new='PrototypeR0:JST_SH_SM02B-SRSS-TB_1x02-1MP_P1.00mm_Horizontal';assert text.count(old)==1;text=text.replace(old,new)
  q.write_text(text)
 elif p.suffix=='.kicad_pro':
  pro=json.loads(p.read_text());pro['meta']['filename']=q.name;q.write_text(json.dumps(pro,indent=2)+'\n')
 else:shutil.copyfile(p,q)
shutil.copyfile(SOURCE/'body/body-r14.kicad_pcb',OUT/'body/body-r15.kicad_pcb')
sf=SOURCE/'flange/flange-r14.kicad_pcb';before=sha(sf);b=K.LoadBoard(str(sf));assert not list(b.GetTracks())and not list(b.Zones())
fps={f.GetReference():f for f in b.GetFootprints()};old=fps['J1'];path=old.GetPath();value=old.GetValue();b.Delete(old)
name='JST_SH_SM02B-SRSS-TB_1x02-1MP_P1.00mm_Horizontal';new=K.FootprintLoad(str(OUT/'flange/PrototypeR0.pretty'),name);new.SetReference('J1');new.SetValue(value);new.SetPath(path);new.SetFPID(K.LIB_ID('PrototypeR0',name));new.Reference().SetVisible(False);new.Value().SetVisible(False);b.Add(new);fps['J1']=new
for pad in new.Pads():
 if pad.GetNumber()in ['1','2']:pad.SetNet(b.FindNet('DOCK_5V'if pad.GetNumber()=='1'else'GND'))
heights=json.loads((ROOT/'hardware/pcb/prototype-r2/layout-candidates-r0.json').read_text())['parts'];height={r:heights[r]['height_mm']if r in heights else 3.2 for r in fps};height['J1']=3.2
fixed={'U6':(-31.7,-18.5,90,'F'),'SW1':(-22.85,-14,0,'F'),'SW2':(-16.85,-14,0,'F'),'J4':(-19.4,-22,180,'F'),
 'J7':(-30,-14.8,180,'B'),'J1':(-18.5,-22,0,'B'),
 'C32':(-36,-24.4,90,'B'),'C31':(-36.1,-21.5,90,'B'),'C33':(-30.1,-24.4,0,'B'),'R31':(-27,-24.4,180,'B'),
 'R39':(-25.6,-22,90,'B'),'R40':(-23.7,-22,90,'B'),'C34':(-23.9,-24.9,0,'B'),'SW3':(-21,-13.95,90,'B'),'SW4':(-16.8,-13.95,90,'B')}
metrics={}
for ref,fp in fps.items():
 metrics[ref]={}
 for angle in [0,90,180,270]:
  G.pose(fp,0,0,angle,'B');bb=G.rect(fp,[K.B_CrtYd]);metrics[ref][angle]={'rect':bb,'w':bb[2]-bb[0],'h':bb[3]-bb[1]}
placed={};free=[[-37.05,-25.75,-14.05,-11.25]];fixed_conflicts=[]
for ref,(x,y,angle,side)in fixed.items():
 fp=fps[ref];G.pose(fp,x,y,angle,side);bb=G.rect(fp,[K.F_CrtYd,K.B_CrtYd]);placed[ref]={'rect':bb,'side':side,'angle':angle,'anchor':[x,y]}
 if side=='B':free=G.split_free(free,bb)
for i,(ref,p)in enumerate(placed.items()):
 for other,q in list(placed.items())[i+1:]:
  if p['side']==q['side']and G.overlap(p['rect'],q['rect']):fixed_conflicts.append([ref,other])
# Nominal SH mating extensions: reserve actual mouth direction after flip.
mates=[]
for ref in ['J1','J7','J4']:
 fp=fps[ref];side=fixed[ref][3];body=G.rect(fp,[K.F_Fab,K.B_Fab]);v=-1 if ref=='J7'else 1
 n=len({p.GetNumber()for p in fp.Pads()if p.GetNumber()not in['','MP']});front=body[1]if v<0 else body[3];cy=(front+v,front+v)
 bb=[fixed[ref][0]-(n+1)/2,min(front,front+v*2),fixed[ref][0]+(n+1)/2,max(front,front+v*2)]
 mates.append({'ref':ref,'side':side,'rect':bb})
 if side=='B':free=G.split_free(free,bb)
remaining=[r for r in fps if r not in fixed];best=None
targets={'R32':(-32.5,-23),'R33':(-32.5,-21),'R34':(-15,-18),'R35':(-28,-21),'R36':(-31.7,-22),'R37':(-27,-20),'R38':(-29,-20)}
for seed in range(160):
 rng=random.Random(seed);spaces=[f[:]for f in free];pnew={};failed=[];order=remaining[:];rng.shuffle(order)
 for ref in order:
  choices=[];tx,ty=targets[ref]
  for angle,metric in metrics[ref].items():
   w,h=metric['w'],metric['h']
   for f in spaces:
    if f[2]-f[0]<w or f[3]-f[1]<h:continue
    for x in [f[0],f[2]-w,max(f[0],min(f[2]-w,tx-w/2))]:
     for y in [f[1],f[3]-h,max(f[1],min(f[3]-h,ty-h/2))]:
      rr=[x,y,x+w,y+h];score=min(f[2]-f[0]-w,f[3]-f[1]-h)+.05*(abs(x+w/2-tx)+abs(y+h/2-ty));choices.append((score,angle,rr))
  if not choices:failed.append(ref);continue
  _,angle,rr=min(choices,key=lambda c:c[0]);pnew[ref]={'side':'B','angle':angle,'rect':rr};spaces=G.split_free(spaces,rr)
 if best is None or len(failed)<len(best[2]):best=(seed,pnew,failed)
 if not failed:break
seed,pnew,failed=best;placed.update(pnew)
for ref,p in pnew.items():
 mm=metrics[ref][p['angle']]['rect'];G.pose(fps[ref],p['rect'][0]-mm[0],p['rect'][1]-mm[1],p['angle'],'B')
for i,ref in enumerate(failed):G.pose(fps[ref],30+i*4,-40,0,'F')
for fp in fps.values():fp.SetProperty('PlacementStatus','R15 flange repack / routing study / not fabrication')
out=OUT/'flange/flange-r15.kicad_pcb';K.SaveBoard(str(out),b)
rows=[]
saved=K.LoadBoard(str(out))
for fp in saved.GetFootprints():
 ref=fp.GetReference();side='B'if fp.GetLayer()==K.B_Cu else'F';h=height[ref]
 rows.append({'ref':ref,'xy_mm':G.mech(fp.GetPosition()),'side':side,'angle_deg':fp.GetOrientationDegrees(),'courtyard_xy_mm':G.rect(fp,[K.F_CrtYd,K.B_CrtYd]),'body_xy_mm':G.rect(fp,[K.F_Fab,K.B_Fab]),'height_budget_mm':h,'z_bounds_mm':[-.5-h,-.5]if side=='B'else[.5,.5+h],'pads':[{'n':p.GetNumber(),'net':p.GetNetname(),'xy_mm':G.mech(p.GetPosition())}for p in fp.Pads()]})
assert sha(sf)==before
r={'date':'2026-11-01','generator_sha256':sha(Path(__file__)),'source_R14_flange_sha256':before,'native_flange_sha256':sha(out),'body_native_unchanged':sha(SOURCE/'body/body-r14.kicad_pcb')==sha(OUT/'body/body-r15.kicad_pcb'),
 'component_count':len(rows),'seed':seed,'fixed_courtyard_conflicts':fixed_conflicts,'unplaced':failed,'placements':rows,'nominal_mate_reservations':mates,
 'dock_header_change':{'old':'S2B-PH-SM4-TB','new_candidate':'SM02B-SRSS-TB','housing_candidate':'SHR-02V-S-B','contact_candidate':'SSH-003T-P0.2-H','pin1':'DOCK_5V','pin2':'GND','study_height_mm':3.2,'source':'https://www.jst-mfg.com/product/pdf/eng/eSH.pdf','current_rating_note':'1A specification is atAWG28; no harness/current/temperature qualification or BOM change.'},
 'scope':'Actual native repack, same substrate/antenna/user controls and67body/22flange allocation. All flange passives nowB. DockSH2candidate replacesPH2; J4port rotated. Fresh DRC/padparity/MCAD/mates/routing/updatedERC still required.'}
(OUT/'flange-repack.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'seed':seed,'unplaced':failed,'fixed_conflicts':fixed_conflicts,'parts':len(rows)},indent=2),flush=True)
