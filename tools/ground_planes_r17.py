"""Add actual native ground pours; earlier split body had no copper zones."""
from pathlib import Path
import sys,json
import pcb_r2_route as R
K=R.k;ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/'hardware/pcb/route-r17/candidate-f';P=Path(sys.argv[1]).resolve();P.mkdir(parents=True,exist_ok=True);assert not any(P.iterdir())
for p in SOURCE.rglob('*'):
 if p.is_file()and((p.suffix in ['.kicad_pro','.kicad_sch','.kicad_sym','.kicad_mod']or p.suffix=='.kicad_pcb'and p.name!='source-seed.kicad_pcb')or p.name in ['fp-lib-table','sym-lib-table','body-seed.json','local-power.json','power-refinement.json','local-interfaces.json','ground-plan.json','ground-application.json']):
  q=P/p.relative_to(SOURCE);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
bp=P/'body/body-r17.kicad_pcb';b=K.LoadBoard(str(bp));before=R.sha(bp);assert not[z for z in b.Zones()if not z.GetIsRuleArea()];edges=[[R.mech(s.GetStart()),R.mech(s.GetEnd())]for s in b.GetDrawings()if isinstance(s,K.PCB_SHAPE)and s.GetLayer()==K.Edge_Cuts];a,c=edges.pop();outline=[a,c]
while edges:
 i,a,c=next((i,a,c)for i,(a,c)in enumerate(edges)if a==outline[-1]or c==outline[-1]);edges.pop(i);outline.append(c if a==outline[-1]else a)
assert outline[0]==outline[-1];outline.pop();R.ground_planes(b,outline);K.SaveBoard(str(bp),b);R.fill_save(bp);R.write(P/'ground-planes.json',{'date':'2026-11-01','builder_sha256':R.sha(Path(__file__)),'source_F_body_sha256':before,'native_body_sha256':R.sha(bp),'actual_source_non_rule_zone_count':0,'new_GND_layers':['F.Cu','In1.Cu','In2.Cu','B.Cu'],'reserved_continuous_GND_layer':'In2.Cu','outline_xy_mm':outline,'scope':'Corrects the earlier seed note assumption: the split source body had no ground pours. Add/fill actual all-layer native GND zones; In2 reserved without signal tracks. F/In1/B may carry later routes. Ground continuity, return samples, current/thermal and received process still need review.'});print(P,flush=True)
