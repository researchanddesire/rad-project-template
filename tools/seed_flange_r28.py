"""Remove obsolete connector copper; preserve USB/radio/local circuits."""
from pathlib import Path
import sys,json,shutil,collections
import pcb_r2_route as R
K=R.k;ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'hardware/pcb/flange-access-r28/candidate-a';OUT=Path(sys.argv[1]).resolve();OUT.mkdir(parents=True,exist_ok=True);assert not any(OUT.iterdir())
source=SRC/'flange-r28.kicad_pcb';before=R.sha(source)
for name in ['flange-r28.kicad_pcb','flange-r28.kicad_pro','fp-lib-table']:
 p=SRC/name
 if p.is_file():shutil.copyfile(p,OUT/name)
bp=OUT/'flange-r28.kicad_pcb';b=K.LoadBoard(str(bp));old=R.route_records(b);removed=[]
reopen={'DOCK_5V','VBUS_CHG','PACK_P','MOTOR_ARM','MOTOR_PWM','DOCK_PRESENT_N','I2C_SDA','I2C_SCL','ACCEL_INT_N','STRAP8'}
for item,q in zip(list(b.GetTracks()),old):
 why=None
 if q['net']in reopen:why='Reopen moved connector route or old STRAP8 crossing newJ7pad'
 if q['kind']=='track'and q['net']=='3V3'and q['layer']=='B.Cu'and max(q['start'][1],q['end'][1])>=-13.8 and q['start'][0]==-27.5:why='Remove obsolete J7 supply-pad escape only'
 if q['kind']=='track'and q['net']=='GND'and q['layer']=='B.Cu':
  bb=item.GetBoundingBox();xmin=K.ToMM(bb.GetLeft())-100;xmax=K.ToMM(bb.GetRight())-100;ymin=130-K.ToMM(bb.GetBottom());ymax=130-K.ToMM(bb.GetTop())
  if min(xmax,-23.1)>max(xmin,-37)and min(ymax,-11)>max(ymin,-19):why='Reopen B ground link near rotated J7 mounting pads; inner GND stays'
 if why:removed.append({'record':q,'reason':why});b.Delete(item)
fixed=R.route_records(b)
assert [q for q in fixed if q['net']in ['USB_DM','USB_DP']]==[q for q in old if q['net']in ['USB_DM','USB_DP']]
# Retain the .65mm radio trunk and its two existing vias. Escape on B rather
# than adding an inner-layer tap across the unchanged MODE_N route.
points=[[-32.5,-16.8],[-32.5,-15.0],[-28.8,-15.0],[-28.8,-14.3]]
added=[{'kind':'track','net':'3V3','layer':'B.Cu','start':a,'end':c,'width':.65}for a,c in zip(points,points[1:])]
R.apply_routes(b,added)
for t in b.GetTracks():t.SetLocked(True)
K.SaveBoard(str(bp),b);saved=R.fill_save(bp)
out={'source_native_board_sha256':before,'native_board_sha256':R.sha(bp),'builder_sha256':R.sha(Path(__file__)),'source_routes':len(old),'removed_routes':removed,'preserved_routes':fixed,'new_manual_supply_escape':added,'reopened_nets':sorted(reopen),'USB_source_records_exactly_preserved':True,'scope':'Routing seed after explicit obsolete-branch removal. Source native rules/outline/poses/pad nets retained, In1 GND preserved. .65mm radio feed and local supply/USB copper kept. Fresh DRC and route completion required; no current/process/electrical acceptance.'}
(OUT/'routing-seed.json').write_text(json.dumps(out,indent=2)+'\n');assert R.sha(source)==before
print('preserved',len(fixed),'removed',len(removed),'new supply',len(added),flush=True)
