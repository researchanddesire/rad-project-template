"""Shorten driver VCC bypass path before planning signal escapes and grounds."""
from pathlib import Path
import sys,json
import pcb_r2_route as R
K=R.k;ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/'hardware/pcb/route-r17/candidate-h';P=Path(sys.argv[1]).resolve();P.mkdir(parents=True,exist_ok=True);assert not any(P.iterdir())
for p in SOURCE.rglob('*'):
 if p.is_file()and((p.suffix in ['.kicad_pro','.kicad_sch','.kicad_sym','.kicad_mod']or p.suffix=='.kicad_pcb'and p.name!='source-seed.kicad_pcb')or p.name in ['fp-lib-table','sym-lib-table','body-seed.json','local-power.json','power-refinement.json','local-interfaces.json','compact-driver.json']):
  q=P/p.relative_to(SOURCE);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
bp=P/'body/body-r17.kicad_pcb';b=K.LoadBoard(str(bp));before=R.sha(bp);removed=[]
for t in list(b.GetTracks()):
 if not isinstance(t,K.PCB_VIA)and t.GetNetname()=='3V3'and t.GetLayer()==K.F_Cu:removed.append(str(t.m_Uuid.AsString()));b.Delete(t)
assert len(removed)==2;routes=[{'kind':'track','net':'3V3','layer':'F.Cu','width':.25,'start':[5.25,46.25],'end':[4.13,45.54]}];R.apply_routes(b,routes)
for f in b.GetFootprints():
 if f.GetReference()in ['R1','R2']:
  for p in f.Pads():
   if p.GetNumber()=='2':assert p.GetNetname()=='GND';p.SetZoneConnection(K.ZONE_CONNECTION_FULL)
K.SaveBoard(str(bp),b);R.fill_save(bp);R.write(P/'signal-first-seed.json',{'date':'2026-11-01','builder_sha256':R.sha(Path(__file__)),'source_H_body_sha256':before,'native_body_sha256':R.sha(bp),'removed_old_VCC_neck_UUIDs':removed,'new_driver_VCC_neck':routes,'direct_GND_pad_overrides':['R1.2','R2.2'],'scope':'Straight shorter driver VCC bypass neck frees local space. Plan hard signal escapes before ground stitches; EN2/MODE/IN2 logic grounds already have explicit local links to exposed ground pads and do not need separate vias. No placement, circuit or global rule changes.'});print(P,flush=True)
