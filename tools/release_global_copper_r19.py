"""Release selected unlocked global nets; preserve the full local seed exactly."""
from pathlib import Path
from collections import Counter
import sys,json
import pcb_r2_route as R
K=R.k;ROOT=Path(__file__).resolve().parents[1]
source,S,P=map(lambda x:Path(x).resolve(),sys.argv[1:4]);nets=set(sys.argv[4:]);assert nets
bp=next((source/'body').glob('body-r*.kicad_pcb'));sourcehash=R.sha(bp)
gp=source/'body-native-geometry-all-layers.json';g=json.loads(gp.read_text());assert g['board_sha256']==sourcehash
sg=S/'body-native-geometry-all-layers.json';seed=json.loads(sg.read_text());assert seed['board_sha256']==R.sha(next((S/'body').glob('body-r*.kicad_pcb')))
P.mkdir(parents=True,exist_ok=True);assert not any(P.iterdir())
metadata={'local-ground-rework-r19.json','fp-lib-table','sym-lib-table','body-seed.json','local-power.json','power-refinement.json','local-interfaces.json','compact-driver.json','signal-first-seed.json','signal-ports.json','signal-application.json','ground-plan.json','ground-application.json','ground-rework.json','fresh-fill.json','local-seed-final.json','dock-port-rework.json','signal-repack.json','local-seed-conservation.json','board-width.json','via-process.json'}
for p in source.rglob('*'):
    if p.is_file()and(p.suffix in ['.kicad_pro','.kicad_sch','.kicad_sym','.kicad_mod','.kicad_pcb']or p.name in metadata):
        q=P/p.relative_to(source);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
target=P/'body'/bp.name;b=K.LoadBoard(str(target));before=R.route_records(b);items=list(b.GetTracks());assert before==g['routes']and len(items)==len(before)
canon=lambda t:json.dumps(t,sort_keys=True);hard=Counter(map(canon,seed['routes']))
rework=P/'local-ground-rework-r19.json'
if rework.exists():
    for q in json.loads(rework.read_text())['replacements']:
        assert hard[canon(q['old'])]==1;hard.subtract([canon(q['old'])]);hard.update([canon(q['new'])])
hard=+hard;protected=hard.copy();removed=[];removed_uuids=[];locks={t.m_Uuid.AsString():t.IsLocked()for t in items}
for t,item in zip(before,items):
    key=canon(t)
    if hard[key]:hard[key]-=1;continue
    assert not item.IsLocked(),'Global candidate must be unlocked'
    if t['net']in nets:
        assert item.GetNetname()==t['net'];removed.append(t);removed_uuids.append(item.m_Uuid.AsString());b.Remove(item)
assert not +hard and removed
K.SaveBoard(str(target),b);saved=R.fill_save(target);actual=Counter(map(canon,R.route_records(saved)))
expected=Counter(map(canon,before));expected.subtract(map(canon,removed));assert +expected==actual and not protected-actual
for uid in removed_uuids:del locks[uid]
assert locks=={t.m_Uuid.AsString():t.IsLocked()for t in saved.GetTracks()}
R.write(P/'global-release-r19.json',{'date':'2026-11-01','builder_sha256':R.sha(Path(__file__)),'source_directory':str(source.relative_to(ROOT)),'source_native_board_sha256':sourcehash,'source_geometry_sha256':R.sha(gp),'protected_seed_geometry_sha256':R.sha(sg),'native_board_sha256':R.sha(target),'released_nets':sorted(nets),'removed_global_records':removed,'all_local_seed_records_retained':sum(protected.values()),'unchanged_parent_records':len(before)-len(removed),'total_records':sum(actual.values()),'remaining_lock_states_unchanged':True,'scope':'Only specified unlocked global copper released. All local seed records, including declared ground rework, retained. No pad/net/pose/rule changes; fresh native checks and rerouting required.'})
assert R.sha(bp)==sourcehash
print(len(removed),'global records released;',sum(protected.values()),'local seed records protected',flush=True)
