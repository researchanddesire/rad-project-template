"""Separate, explicit .50/.20mm signal/ground-via manufacturing study."""
from pathlib import Path
import sys,json
import pcb_r2_route as R
K=R.k;ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/'hardware/pcb/route-r19/candidate-a';P=Path(sys.argv[1]).resolve();P.mkdir(parents=True,exist_ok=True);assert not any(P.iterdir())
records=['fp-lib-table','sym-lib-table','body-seed.json','local-power.json','power-refinement.json','local-interfaces.json','compact-driver.json','signal-first-seed.json','signal-ports.json','signal-application.json','ground-plan.json','ground-application.json','ground-rework.json','fresh-fill.json','local-seed-final.json','dock-port-rework.json','signal-repack.json','local-seed-conservation.json','board-width.json']
for p in SOURCE.rglob('*'):
 if p.is_file()and((p.suffix in ['.kicad_pro','.kicad_sch','.kicad_sym','.kicad_mod']or p.suffix=='.kicad_pcb'and p.name!='source-seed.kicad_pcb')or p.name in records):
  q=P/p.relative_to(SOURCE);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
bp=P/'body/body-r19.kicad_pcb';pro=bp.with_suffix('.kicad_pro');j=json.loads(pro.read_text());delta=[]
for path,value in [(('board','design_settings','rules','min_via_diameter'),.5),(('board','design_settings','rules','min_through_hole_diameter'),.2)]:
 d=j
 for key in path[:-1]:d=d[key]
 old=d[path[-1]];d[path[-1]]=value;delta.append({'path':list(path),'old':old,'new':value})
for i,c in enumerate(j['net_settings']['classes']):
 if c['name']!='Default':continue
 for key,value in [('via_diameter',.5),('via_drill',.2)]:
  old=c[key];c[key]=value;delta.append({'path':['net_settings','classes',i,key],'old':old,'new':value})
assert len(delta)==4;R.write(pro,j);b=K.LoadBoard(str(bp));original=R.route_records(b);changed=[];power={'SYS','PACK_P','VBUS_CHG','MOTOR_3V7','MOTOR_P','MOTOR_N','3V3'}
for t in b.GetTracks():
 if not isinstance(t,K.PCB_VIA)or t.GetNetname()in power:continue
 old={'net':t.GetNetname(),'xy_mm':R.mech(t.GetPosition()),'diameter_mm':K.ToMM(t.GetWidth()),'drill_mm':K.ToMM(t.GetDrillValue())};assert old['diameter_mm']==.6 and old['drill_mm']==.3;t.SetWidth(K.FromMM(.5));t.SetDrill(K.FromMM(.2));changed.append(old)
R.LAYERS['In1.Cu']=K.In1_Cu;K.SaveBoard(str(bp),b);saved=R.fill_save(bp);actual=R.route_records(saved)
assert [t for t in original if t['kind']=='track']==[t for t in actual if t['kind']=='track'];assert len(original)==len(actual)
R.write(P/'via-process.json',{'date':'2026-11-01','builder_sha256':R.sha(Path(__file__)),'source_directory':str(SOURCE.relative_to(ROOT)),'source_body_sha256':R.sha(SOURCE/'body/body-r19.kicad_pcb'),'native_body_sha256':R.sha(bp),'source_project_sha256':R.sha(SOURCE/'body/body-r19.kicad_pro'),'project_sha256':R.sha(pro),'project_delta':delta,'changed_signal_ground_vias':changed,'new_via_diameter_mm':.5,'new_via_drill_mm':.2,'nominal_annulus_mm':.15,'all_source_track_records_unchanged':sum(t['kind']=='track'for t in original),'all_power_3V3_vias_unchanged':True,'manufacturer_capability_reference':'https://jlcpcb.com/capabilities/pcb-capabilities/','process_note':'0.50/.20mm retains0.15mm annulus:0.1mm copper spacing gives0.25mm hole-to-other-net copper clearance. E failed that rule; no relaxation.', 'scope':'Explicit manufacturing-process candidate, not acceptance or a selected supplier. Only signal/GND via dimensions and the four declared minimum/default settings change. Cu spacing/edge/hole-spacing/annular rules, all source track geometry/widths, functions, parts/poses, outline/thickness and flange remain. Existing source has no Cu-clearance errors; no errors are waived. Review capacity/returns/DRC/drill/process after routing. No fabrication release.'});print(len(changed),'vias changed; source track geometry retained',flush=True)
