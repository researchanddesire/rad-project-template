"""Apply source-bound via cleanup, then retire only native dangling track stubs."""
from pathlib import Path
from collections import Counter
import sys,json,re,math,shutil,subprocess
import pcb_r2_route as R
K=R.k;ROOT=Path(__file__).resolve().parents[1]
source=Path(sys.argv[1]).resolve();planfile=Path(sys.argv[2]).resolve();P=Path(sys.argv[3]).resolve();plan=json.loads(planfile.read_text());bp=next((source/'body').glob('body-r*.kicad_pcb'))
assert R.sha(bp)==plan['source_board_sha256']and R.sha(source/'body-native-geometry-all-layers.json')==plan['source_geometry_sha256']and R.sha(source/'body/fresh-native-drc.txt')==plan['source_native_DRC_sha256']
P.mkdir(parents=True,exist_ok=True);assert not any(P.iterdir())
metadata={'stackup-r23.json','global-release-r19.json','local-ground-rework-r19.json','fp-lib-table','sym-lib-table','body-seed.json','local-power.json','power-refinement.json','local-interfaces.json','compact-driver.json','signal-first-seed.json','signal-ports.json','signal-application.json','ground-plan.json','ground-application.json','ground-rework.json','fresh-fill.json','local-seed-final.json','dock-port-rework.json','signal-repack.json','local-seed-conservation.json','board-width.json','via-process.json'}
for p in source.rglob('*'):
    if p.is_file()and(p.suffix in ['.kicad_pro','.kicad_sch','.kicad_sym','.kicad_mod','.kicad_pcb']or p.name in metadata):
        q=P/p.relative_to(source);q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)
target=P/'body'/bp.name;b=K.LoadBoard(str(target));R.LAYERS.update({b.GetLayerName(i):i for i in range(32)if b.GetEnabledLayers().Contains(i)});before=R.route_records(b);canon=lambda t:json.dumps(t,sort_keys=True)
retired=plan['retired_vias'][:];retired_keys=Counter(map(canon,retired));pending=retired_keys.copy()
for item,record in zip(list(b.GetTracks()),before):
    key=canon(record)
    if pending[key]:assert isinstance(item,K.PCB_VIA);b.Delete(item);pending[key]-=1
assert not +pending
R.apply_routes(b,plan['same_layer_junctions'],locked=True);K.SaveBoard(str(target),b);R.fill_save(target)
e=P/'cleanup-evidence';e.mkdir();(e/'source-native-drc.txt').write_bytes((source/'body/fresh-native-drc.txt').read_bytes());(e/'source-plan.json').write_bytes(planfile.read_bytes())
phases=[];trim_records=[]
for phase in range(64):
    subprocess.run([sys.executable,str(ROOT/'tools/drc_body_r17.py'),str(P)],check=True,capture_output=True,text=True);b=K.LoadBoard(str(target));report=e/('phase-'+str(phase).zfill(2)+'-drc.txt');shutil.copyfile(P/'body/fresh-native-drc.txt',report);txt=report.read_text();counts={key:int(re.search(rx,txt).group(1))for key,rx in [('violations',r'\*\* Found (\d+) DRC violations'),('unconnected',r'\*\* Found (\d+) unconnected pads'),('footprint_errors',r'\*\* Found (\d+) Footprint errors')]}
    classes=set(re.findall(r'^\[([^]]+)\]:',txt,re.M));phases.append({'phase':phase,'native_board_sha256':R.sha(target),'native_report_sha256':R.sha(report),'counts':counts,'classes':sorted(classes)})
    print('phase',phase,counts,sorted(classes),flush=True)
    assert counts['unconnected']==0 and counts['footprint_errors']==0 and classes<={'track_dangling'},'Unexpected cleanup finding; preserve this candidate and source'
    if counts['violations']==0:break
    records=R.route_records(b);items=list(b.GetTracks());remove={}
    for block in txt.split('[track_dangling]:')[1:]:
        m=re.search(r'@\(([\d.]+) mm, ([\d.]+) mm\): Track \[([^]]+)\] on ([^,\n]+), length ([\d.]+) mm',block);assert m,block
        x,y,net,layer,length=m.groups();xy=[round(float(x)-100,6),round(130-float(y),6)];found=[]
        for item,t in zip(items,records):
            if t['kind']!='track'or t['net']!=net or t['layer']!=layer:continue
            if min(math.dist(t['start'],xy),math.dist(t['end'],xy))>1e-4:continue
            if abs(math.dist(t['start'],t['end'])-float(length))>1e-4:continue
            found.append((item,t))
        assert len(found)==1,(net,xy,layer,length,len(found));item,t=found[0];assert net!='GND';remove[item.m_Uuid.AsString()]=(item,t)
    assert remove
    for item,t in remove.values():b.Delete(item);retired.append(t);trim_records.append({'phase':phase,'native_report_sha256':R.sha(report),'record':t})
    K.SaveBoard(str(target),b);R.fill_save(target)
else:raise AssertionError('Cleanup did not converge in64native phases')
after=R.route_records(b);expected=Counter(map(canon,before));expected.subtract(map(canon,retired));expected.update(map(canon,plan['same_layer_junctions']));assert +expected==Counter(map(canon,after))
R.write(P/'unused-copper-r23.json',{'date':'2026-11-01','builder_sha256':R.sha(Path(__file__)),'source_directory':str(source.relative_to(ROOT)),'source_native_board_sha256':plan['source_board_sha256'],'source_native_DRC_sha256':plan['source_native_DRC_sha256'],'source_geometry_sha256':plan['source_geometry_sha256'],'plan_sha256':R.sha(planfile),'native_board_sha256':R.sha(target),'source_records':len(before),'retired_vias':plan['retired_vias'],'retired_dead_end_track_records':trim_records,'retired_records':retired,'added_planar_junctions':plan['same_layer_junctions'],'all_other_parent_records_preserved':len(before)-len(retired),'total_records':len(after),'native_cleanup_phases':phases,'scope':'Only native single-layer unused vias and resulting native dangling dead-end tracks retired; planar junctions preserve connectivity. Every phase has0unconnected/0footprint/no other errors. Same circuits/parts/stack/rules. Fresh full native/circuit/pad/drill/dual-reference audit required.'})
assert R.sha(bp)==plan['source_board_sha256'];print(P,flush=True)
