"""Read-only congestion probe: remove selected unlocked global copper virtually.

Protect every local seed record, including explicitly declared ground rework.
The sentinel board hash deliberately prevents applying any resulting plan.
"""
from pathlib import Path
from collections import Counter
import sys,json,hashlib
P,S,OUT=map(lambda x:Path(x).resolve(),sys.argv[1:4]);nets=set(sys.argv[4:]);assert nets
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
gp=P/'body-native-geometry-all-layers.json';g=json.loads(gp.read_text());bp=next((P/'body').glob('body-r*.kicad_pcb'));assert g['board_sha256']==sha(bp)
sg=S/'body-native-geometry-all-layers.json';seed=json.loads(sg.read_text());assert seed['board_sha256']==sha(next((S/'body').glob('body-r*.kicad_pcb')))
canon=lambda t:json.dumps(t,sort_keys=True);hard=Counter(map(canon,seed['routes']))
rework=P/'local-ground-rework-r19.json'
if rework.exists():
    for q in json.loads(rework.read_text())['replacements']:
        assert hard[canon(q['old'])]==1;hard.subtract([canon(q['old'])]);hard.update([canon(q['new'])])
hard=+hard;protected_count=sum(hard.values());routes=[];locks=[];removed=[];soft_count=0
for t,locked in zip(g['routes'],g['route_locks']):
    key=canon(t)
    if hard[key]:hard[key]-=1
    else:
        soft_count+=1;assert not locked,'Cannot release locked copper'
        if t['net']in nets:removed.append(t);continue
    routes.append(t);locks.append(locked)
assert not +hard and removed
g['probe_only']={'source_native_board_sha256':g['board_sha256'],'source_geometry_sha256':sha(gp),'protected_seed_geometry_sha256':sha(sg),'generator_sha256':sha(Path(__file__)),'protected_records':protected_count,'global_records':soft_count,'released_nets':sorted(nets),'removed_global_records':removed,'scope':'Read-only virtual copper release. No native board or accepted result. Never apply this probe plan.'}
g['board_sha256']='PROBE_ONLY_NO_NATIVE_BOARD';g['routes']=routes;g['route_locks']=locks
OUT.write_text(json.dumps(g,indent=2)+'\n');print(len(removed),'virtual global records removed; local seed protected',flush=True)
