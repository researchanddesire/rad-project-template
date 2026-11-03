"""A 14-to-20mm PCB study inside the preserved metal body; poses unchanged."""
from pathlib import Path
import sys,json
import pcb_r2_route as R
K=R.k;ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/'hardware/pcb/route-r17/candidate-ad';P=Path(sys.argv[1]).resolve();P.mkdir(parents=True,exist_ok=True);assert not any(P.iterdir());records=['fp-lib-table','sym-lib-table','body-seed.json','local-power.json','power-refinement.json','local-interfaces.json','compact-driver.json','signal-first-seed.json','ground-rework.json','fresh-fill.json','ground-plan.json','ground-application.json','signal-ports.json','signal-application.json','local-seed-final.json','dock-port-rework.json','signal-repack.json','local-seed-conservation.json']
for p in SOURCE.rglob('*'):
 if not p.is_file():continue
 if not((p.suffix in ['.kicad_pro','.kicad_sch','.kicad_sym','.kicad_mod']or p.suffix=='.kicad_pcb'and p.name!='source-seed.kicad_pcb')or p.name in records):continue
 q=P/str(p.relative_to(SOURCE)).replace('-r17','-r19');q.parent.mkdir(parents=True,exist_ok=True)
 if p.suffix=='.kicad_sch':q.write_text(p.read_text().replace('-r17','-r19'))
 elif p.suffix=='.kicad_pro':v=json.loads(p.read_text());v['meta']['filename']=q.name;R.write(q,v)
 else:q.write_bytes(p.read_bytes())
bp=P/'body/body-r19.kicad_pcb';b=K.LoadBoard(str(bp));before=R.sha(bp);original=R.route_records(b);oldedges=[]
for o in list(b.GetDrawings()):
 if isinstance(o,K.PCB_SHAPE)and o.GetLayer()==K.Edge_Cuts:oldedges.append([R.mech(o.GetStart()),R.mech(o.GetEnd())]);b.Delete(o)
assert len(oldedges)==6;outline=[[-7,26],[7,26],[10,31],[10,54],[-10,54],[-10,31]]
for a,c in zip(outline,outline[1:]+outline[:1]):
 o=K.PCB_SHAPE(b);o.SetShape(K.SHAPE_T_SEGMENT);o.SetLayer(K.Edge_Cuts);o.SetStart(R.xy(*a));o.SetEnd(R.xy(*c));o.SetWidth(K.FromMM(.05));b.Add(o)
oldzones=[]
for z in list(b.Zones()):
 if z.GetIsRuleArea():continue
 assert z.GetNetname()=='GND';oldzones.append({'layer':K.LayerName(z.GetLayer()),'clearance_mm':K.ToMM(z.GetLocalClearance()),'min_fill_mm':K.ToMM(z.GetMinThickness()),'thermal_gap_mm':K.ToMM(z.GetThermalReliefGap()),'thermal_spoke_mm':K.ToMM(z.GetThermalReliefSpokeWidth())});b.Delete(z)
assert len(oldzones)==4 and all(z['clearance_mm']==.1 and z['min_fill_mm']==.2 and z['thermal_gap_mm']==.2 and z['thermal_spoke_mm']==.3 for z in oldzones);R.ground_planes(b,outline);K.SaveBoard(str(bp),b);saved=R.fill_save(bp);R.LAYERS['In1.Cu']=K.In1_Cu;assert R.route_records(saved)==original
assert R.sha(P/'flange/flange-r19.kicad_pcb')==R.sha(SOURCE/'flange/flange-r17.kicad_pcb');screen=ROOT/'hardware/design/body-width-r19/width-screen.json';sr=json.loads(screen.read_text());accepted=next(r for r in sr['candidates']if r['maximum_PCB_width_mm']==20);assert accepted['PCB_metal_intersection_mm3']==0 and accepted['side_support_allowance_metal_intersection_mm3']==0
R.write(P/'board-width.json',{'date':'2026-11-01','builder_sha256':R.sha(Path(__file__)),'source_AD_body_sha256':before,'native_body_sha256':R.sha(bp),'old_outline_edges_xy_mm':oldedges,'new_outline_xy_mm':outline,'source_ground_zone_settings':oldzones,'all_source_local_copper_records_unchanged':len(original),'flange_byte_identical_to_R16U':True,'width_screen_sha256':R.sha(screen),'R13_native_metal_sha256':sr['source_R13_native_sha256'],'scope':'14-to-20mm body substrate, same Y26..54,1mm/four layers and all part poses/nets. Actual four ground pours extend to the widened outline with identical settings; In2 GND reserved. Nominal metal/support screen is clear, but carrier/keeper and screw positions must be revised and loaded-fit checked. Native project/sheet names change toR19; no electrical function/rule changes, no fabrication or physical acceptance.'});print(P,flush=True)
