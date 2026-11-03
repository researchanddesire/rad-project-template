"""Close R16's single input-power gap with a source-bound inner-layer path."""
from pathlib import Path
import sys,json
import pcb_r2_route as R
import kicad_sexp as S
K=R.k;ROOT=Path(__file__).resolve().parents[1];source=ROOT/'hardware/pcb/route-r16/candidate-t';P=Path(sys.argv[1]).resolve();path=Path(sys.argv[2]).resolve();plan=json.loads(path.read_text());P.mkdir(parents=True,exist_ok=True);assert not any(P.iterdir())
for p in source.rglob('*'):
 if p.is_file()and(p.suffix in ['.kicad_pcb','.kicad_pro','.kicad_sch','.kicad_sym','.kicad_mod']or p.name in ['fp-lib-table','sym-lib-table','input-partition.json','input-net-repair.json','flange-seed.json','route-preparation.json','component-proposals.json','input-escape.json']):
  q=P/p.relative_to(source);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
bp=P/'flange/flange-r16.kicad_pcb';b=K.LoadBoard(str(bp));before=R.sha(bp);sboard=ROOT/'hardware/pcb/route-r16/candidate-s/flange/flange-r16.kicad_pcb';assert R.sha(sboard)==plan['source_native_geometry_sha256'];s=K.LoadBoard(str(sboard));routekey=lambda r:json.dumps(r,sort_keys=True)
assert sorted(routekey(r)for r in R.route_records(s)if r['net']!='VBUS_CHG')==sorted(routekey(r)for r in R.route_records(b)if r['net']!='VBUS_CHG')
def canon(n):return tuple(canon(x)for x in n)if isinstance(n,list)else n.raw
assert [canon(n)for n in S.children(S.parse(sboard.read_text()),'footprint')]==[canon(n)for n in S.children(S.parse(bp.read_text()),'footprint')]
assert plan['layer']=='In2.Cu'and plan['width']==.6 and plan['points'][0]==[-24.94,-15.32]and plan['points'][-1]==[-16,-18.3]
routes=[{'kind':'track','net':'VBUS_CHG','layer':'In2.Cu','width':.6,'start':p,'end':q}for p,q in zip(plan['points'],plan['points'][1:])];R.apply_routes(b,routes);K.SaveBoard(str(bp),b);R.fill_save(bp);(P/'input-power-path.json').write_bytes(path.read_bytes());R.write(P/'input-completion.json',{'builder_sha256':R.sha(Path(__file__)),'source_T_flange_sha256':before,'native_flange_sha256':R.sha(bp),'path_plan_sha256':R.sha(path),'non_VBUS_obstacles_equal_plan_source_S':True,'all_footprints_equal_plan_source_S':True,'new_tracks':routes,'scope':'Six .6mm In2 tracks close only the remaining input power gap; actual fresh DRC, return/drill/paste and complete source reviews remain required. No process/current/physical acceptance.'});print(P,flush=True)
