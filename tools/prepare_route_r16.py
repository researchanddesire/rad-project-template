"""Restore nominal schematic labels and reopen local input/service routes."""
from pathlib import Path
import sys,json,math,copy
import pcb_r2_route as R
import kicad_sexp as S
K=R.k;ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/'hardware/pcb/route-r16/candidate-k';BASE=ROOT/'hardware/pcb/route-r16/candidate-a';P=Path(sys.argv[1]).resolve();P.mkdir(parents=True,exist_ok=True);assert not any(P.iterdir())
for p in SOURCE.rglob('*'):
 if p.is_file()and(p.suffix in ['.kicad_pcb','.kicad_pro','.kicad_sch','.kicad_sym','.kicad_mod']or p.name in ['fp-lib-table','sym-lib-table','input-partition.json','input-net-repair.json','flange-seed.json']):
  q=P/p.relative_to(SOURCE);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
refs='R1 R2 R3 R4 R5 R23 R24 R25 R41 R42 R46 R47 R48'.split();original={}
for f in(BASE/'body').glob('*.kicad_sch'):
 for n in S.children(S.parse(f.read_text()),'symbol'):
  ref=S.prop(n,'Reference')
  if ref in refs+['J2']:original[ref]={p[1].value:p[2].value for p in S.children(n,'property')}
body=K.LoadBoard(str(P/'body/body-r16.kicad_pcb'));fps={f.GetReference():f for f in body.GetFootprints()};proposals={}
for f in(P/'body').glob('*.kicad_sch'):
 root=S.parse(f.read_text())
 for n in S.children(root,'symbol'):
  ref=S.prop(n,'Reference')
  if ref not in original:continue
  old=original[ref];mpn=fps[ref].GetValue();note=old['ReviewNote']
  if ref=='J2':note+='; 504050-0491 Pico-Lock header candidate; battery stays OPEN';url='https://www.molex.com/en-us/products/part-detail/5040500491'
  else:
   assert mpn.startswith('TNPW0402')and mpn.endswith('BEED');oldmpn=mpn.replace('TNPW0402','TNPW0603')[:-4]+'BEEA';note=note.replace(oldmpn,mpn)if oldmpn in note else(note+'; 'if note else'')+mpn+' / 0402 candidate';url='https://www.vishay.com/docs/28758/tnpw_e3.pdf'
  changes={'Value':old['Value'],'ReviewNote':note,'Datasheet':url}
  for prop in S.children(n,'property'):
   if prop[1].value in changes:prop[2]=S.string(changes[prop[1].value])
  proposals[ref]={'schematic_nominal_value':old['Value'],'PCB_candidate_MPN':mpn,'footprint':S.prop(n,'Footprint'),'ReviewNote':note,'Datasheet':url}
 S.write(f,root)
assert len(proposals)==14
bp=P/'flange/flange-r16.kicad_pcb';b=K.LoadBoard(str(bp));before=R.sha(bp);removed=[]
for t in list(b.GetTracks()):
 delete=not t.IsLocked()and t.GetNetname()in ['VBAT_ADC','3V3']
 if not isinstance(t,K.PCB_VIA)and t.GetNetname()=='GND'and t.GetLayer()==K.B_Cu:
  ends={tuple(R.mech(t.GetStart())),tuple(R.mech(t.GetEnd()))}
  if ends=={(-22.5,-16),(-22.5,-19.925)}:delete=True
 if delete:removed.append(str(t.m_Uuid.AsString()));b.Delete(t)
routes=[];pts=[[-26.5,-12.8],[-26.5,-14.1],[-27.65,-15.25],[-28.2,-15.25]]
for p,q in zip(pts,pts[1:]):routes.append({'kind':'track','net':'VBUS_CHG','start':p,'end':q,'width':.6,'layer':'B.Cu'})
routes.append({'kind':'via','net':'VBUS_CHG','position':[-28.2,-15.25],'diameter':.6,'drill':.3});R.apply_routes(b,routes);K.SaveBoard(str(bp),b);R.fill_save(bp)
(P/'route-preparation.json').write_text(json.dumps({'date':'2026-11-01','builder_sha256':R.sha(Path(__file__)),'source_K_flange_sha256':before,'native_flange_sha256':R.sha(bp),'removed_UUIDs':removed,'new_manual_routes':routes,'scope':'Reopen only unlocked3V3pullup/ADC routes and oneBground link that conflict with new input fanouts/service pads; retain locked radiofeed/USB. Add explicitly escaped VBUS input atJ7. Fresh native check and route completion required.'},indent=2)+'\n');(P/'component-proposals.json').write_text(json.dumps({'refs':proposals,'scope':'Nominal resistance/function labels restored from exact A source. PCB values identify new candidates; notes/datasheets updated without changing electrical nodes. Generic0402lands, part availability/power/thermal and installed connector/wire current remain unqualified. Human BOM unchanged.'},indent=2)+'\n');print(P,flush=True)
