"""Resolve the larger motor-feedback land at unchanged poses; reserve MEMS area."""
from pathlib import Path
import sys,json
import pcb_r2_route as R
K=R.k;ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/'hardware/pcb/route-r17/candidate-b';P=Path(sys.argv[1]).resolve();P.mkdir(parents=True,exist_ok=True);assert not any(P.iterdir())
for p in SOURCE.rglob('*'):
 if p.is_file()and(p.suffix in ['.kicad_pcb','.kicad_pro','.kicad_sch','.kicad_sym','.kicad_mod']or p.name in ['fp-lib-table','sym-lib-table','body-seed.json','local-power.json']):
  q=P/p.relative_to(SOURCE);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
bp=P/'body/body-r17.kicad_pcb';b=K.LoadBoard(str(bp));before=R.sha(bp);removed=[]
for t in list(b.GetTracks()):
 if not isinstance(t,K.PCB_VIA)and t.GetNetname()=='MOTOR_3V7'and {tuple(R.mech(t.GetStart())),tuple(R.mech(t.GetEnd()))}=={(-1.975,45.5),(-1.975,51.5)}:removed.append(str(t.m_Uuid.AsString()));b.Delete(t)
assert len(removed)==1;points=[[-1.975,45.5],[-1.3,46.175],[-1.3,50.825],[-1.975,51.5]];routes=[{'kind':'track','net':'MOTOR_3V7','layer':'B.Cu','width':.6,'start':p,'end':q}for p,q in zip(points,points[1:])];R.apply_routes(b,routes)
zone=K.ZONE(b);zone.SetIsRuleArea(True);layers=K.LSET();layers.AddLayer(K.F_Cu);layers.AddLayer(K.In1_Cu);zone.SetLayerSet(layers);zone.SetDoNotAllowTracks(True);zone.SetDoNotAllowVias(True);zone.SetDoNotAllowCopperPour(False);zone.SetDoNotAllowPads(False);zone.SetDoNotAllowFootprints(False);poly=zone.Outline();poly.NewOutline()
for p in [[4,27.2],[5.6,27.2],[5.6,28.8],[4,28.8]]:p=R.xy(*p);poly.Append(p.x,p.y)
b.Add(zone);K.SaveBoard(str(bp),b);R.fill_save(bp);R.write(P/'power-refinement.json',{'date':'2026-11-01','builder_sha256':R.sha(Path(__file__)),'source_B_body_sha256':before,'native_body_sha256':R.sha(bp),'removed_motor_bus_UUID':removed,'motor_bus_tracks':routes,'MEMS_nominal_inner_opposite_face_signal_and_via_exclusion_xy':[[4,27.2],[5.6,28.8]],'scope':'Move only motor bulk bus around larger0805feedback land. B-side MEMS terminal escapes and In2 GND remain available. 1.6mm-square rule is a nominal engineering precaution, not controlled package/process acceptance; no signal on In2 planned.'});print(P,flush=True)
