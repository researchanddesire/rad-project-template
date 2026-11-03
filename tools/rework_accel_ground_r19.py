"""Move one U7 GND stitch .15 mm toward the edge in a separate native candidate.

Retain the original protected seed file. Declare and account for the one via
and one B track replacement rather than silently changing that seed.
"""
from pathlib import Path
from collections import Counter
import sys,json,copy
import pcb_r2_route as R
K=R.k;ROOT=Path(__file__).resolve().parents[1]
source=Path(sys.argv[1]).resolve();P=Path(sys.argv[2]).resolve()
bp=next((source/'body').glob('body-r*.kicad_pcb'));sourcehash=R.sha(bp)
g=json.loads((source/'body-native-geometry-all-layers.json').read_text())
assert g['board_sha256']==sourcehash
P.mkdir(parents=True,exist_ok=True);assert not any(P.iterdir())
metadata={'fp-lib-table','sym-lib-table','body-seed.json','local-power.json','power-refinement.json','local-interfaces.json','compact-driver.json','signal-first-seed.json','signal-ports.json','signal-application.json','ground-plan.json','ground-application.json','ground-rework.json','fresh-fill.json','local-seed-final.json','dock-port-rework.json','signal-repack.json','local-seed-conservation.json','board-width.json','via-process.json'}
for p in source.rglob('*'):
    if p.is_file()and(p.suffix in ['.kicad_pro','.kicad_sch','.kicad_sym','.kicad_mod','.kicad_pcb']or p.name in metadata):
        q=P/p.relative_to(source);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
target=P/'body'/bp.name;b=K.LoadBoard(str(target));before=R.route_records(b)
old=[t for t in before if t['net']=='GND'and(t['kind']=='via'and t['position']==[5.7,26.75]or t['kind']=='track'and[5.7,26.75]in[t['start'],t['end']])]
assert len(old)==2 and {t['kind']for t in old}=={'via','track'}
canon=lambda t:json.dumps(t,sort_keys=True)
assert all(Counter(map(canon,before))[canon(t)]==1 for t in old)
new=copy.deepcopy(old)
for t in new:
    assert t['net']=='GND'
    if t['kind']=='via':
        assert t['diameter']==.5 and t['drill']==.2;t['position']=[5.7,26.6]
    else:
        assert t['layer']=='B.Cu'and t['width']==.25
        for name in ['start','end']:
            if t[name]==[5.7,26.75]:t[name]=[5.7,26.6]
changed=0
locks={t.m_Uuid.AsString():t.IsLocked()for t in b.GetTracks()}
for t in b.GetTracks():
    if t.GetNetname()!='GND':continue
    if isinstance(t,K.PCB_VIA):
        if R.mech(t.GetPosition())==[5.7,26.75]:t.SetPosition(R.xy(5.7,26.6));changed+=1
    else:
        for getter,setter in [(t.GetStart,t.SetStart),(t.GetEnd,t.SetEnd)]:
            if R.mech(getter())==[5.7,26.75]:setter(R.xy(5.7,26.6));changed+=1
assert changed==2
K.SaveBoard(str(target),b);saved=R.fill_save(target)
expected=Counter(map(canon,before));expected.subtract(map(canon,old));expected.update(map(canon,new))
assert +expected==Counter(map(canon,R.route_records(saved)))
assert locks=={t.m_Uuid.AsString():t.IsLocked()for t in saved.GetTracks()}
seed=P/'body/source-seed.kicad_pcb'
replacements=[{'old':a,'new':c}for a,c in zip(old,new)]
out={'date':'2026-11-01','builder_sha256':R.sha(Path(__file__)),'source_directory':str(source.relative_to(ROOT)),'source_native_board_sha256':sourcehash,'source_geometry_sha256':R.sha(source/'body-native-geometry-all-layers.json'),'native_board_sha256':R.sha(target),'original_protected_seed_sha256':R.sha(seed),'replacements':replacements,'source_records':len(before),'unchanged_parent_records':len(before)-2,'replaced_records':2,'total_records':len(R.route_records(saved)),'all_native_copper_locks_unchanged':True,'scope':'Only one GND via and its B lead move .15mm in Y. Original protected seed remains byte-identical; two replacements explicit. Fresh native DRC/pad/circuit/drill/reference checks required. No spacing, circuit, pose or stack rule changes.'}
R.write(P/'local-ground-rework-r19.json',out)
assert R.sha(bp)==sourcehash
print(P,flush=True)
