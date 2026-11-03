"""Audit saved native body pad nets, reserved ground layer and protected routes."""
from pathlib import Path
import sys,json,math,re,xml.etree.ElementTree as E
import pcb_r2_route as R
K=R.k;R.LAYERS['In1.Cu']=K.In1_Cu;P=Path(sys.argv[1]).resolve();bp=next((P/'body').glob('body-r*.kicad_pcb'));before=R.sha(bp);b=K.LoadBoard(str(bp))
xml=P/'body/body-native.xml';root=E.parse(xml).getroot();nodes={(n.get('ref'),n.get('pin')):net.get('name')for net in root.findall('nets/net')for n in net.findall('node')};nc={(n.get('ref'),n.get('pin'))for net in root.findall('nets/net')for n in net.findall('node')if 'no_connect'in n.get('pintype','').split('+')}
mismatches=[];pins=0;seen=set()
for f in b.GetFootprints():
 seen.add(f.GetReference())
 for p in f.Pads():
  if p.GetNumber()in ['','MP']:continue
  key=f.GetReference(),p.GetNumber();assert key in nodes,key;wanted=''if key in nc else nodes[key];pins+=1
  if p.GetNetname()!=wanted:mismatches.append([*key,p.GetNetname(),wanted])
assert seen=={c.get('ref')for c in root.findall('components/comp')}
routes=R.route_records(b)
seed=K.LoadBoard(str(P/'body/source-seed.kicad_pcb'));canon=lambda r:json.dumps(r,sort_keys=True)
from collections import Counter
fixed=Counter(map(canon,R.route_records(seed)));original_seed_count=sum(fixed.values());replacements=[]
rework=P/'local-ground-rework-r19.json'
if rework.exists():
 rr=json.loads(rework.read_text());assert rr['original_protected_seed_sha256']==R.sha(P/'body/source-seed.kicad_pcb');replacements=rr['replacements'];assert len(replacements)==2
 for change in replacements:
  old,new=change['old'],change['new'];assert old['net']==new['net']=='GND';expected=json.loads(canon(old))
  if old['kind']=='via':
   assert old['position']==[5.7,26.75]and old['diameter']==.5 and old['drill']==.2;expected['position']=[5.7,26.6]
  else:
   assert old['layer']=='B.Cu'and old['width']==.25
   for k in ['start','end']:
    if expected[k]==[5.7,26.75]:expected[k]=[5.7,26.6]
  assert expected==new and fixed[canon(old)]==1
  fixed.subtract([canon(old)]);fixed.update([canon(new)])
 fixed=+fixed
actual=Counter(map(canon,routes));unused=P/'unused-copper-r23.json';retirements=[];retired_seed_count=0
if unused.exists():
 ur=json.loads(unused.read_text());src=R.ROOT/ur['source_directory'];srcboard=next((src/'body').glob('body-r*.kicad_pcb'));assert R.sha(srcboard)==ur['source_native_board_sha256'];assert R.sha(P/'cleanup-evidence/source-native-drc.txt')==ur['source_native_DRC_sha256'];assert R.sha(P/'cleanup-evidence/source-plan.json')==ur['plan_sha256']
 evidence=(P/'cleanup-evidence/source-native-drc.txt').read_text();warned=[]
 for block in evidence.split('[via_dangling]:')[1:]:
  x,y,net=re.search(r'@\(([\d.]+) mm, ([\d.]+) mm\): Via \[([^]]+)\]',block).groups();warned.append((net,round(float(x)-100,6),round(130-float(y),6)))
 assert set(warned)=={(q['net'],*q['position'])for q in ur['retired_vias']}
 prior=Counter(map(canon,R.route_records(K.LoadBoard(str(srcboard)))));retirements=ur['retired_records'];expected=prior.copy()
 for t in retirements:
  key=canon(t);assert t['net']!='GND'and expected[key]>0;expected.subtract([key])
  if fixed[key]:fixed.subtract([key]);retired_seed_count+=1
 expected.update(map(canon,ur['added_planar_junctions']));assert +expected==actual
 for phase in ur['native_cleanup_phases']:
  f=P/'cleanup-evidence'/('phase-'+str(phase['phase']).zfill(2)+'-drc.txt');assert R.sha(f)==phase['native_report_sha256'];assert phase['counts']['unconnected']==phase['counts']['footprint_errors']==0 and set(phase['classes'])<={'track_dangling'}
 fixed=+fixed
assert not fixed-actual
assert all(not actual[canon(q['old'])]for q in replacements)
report=json.loads((P/'body/native-drc.json').read_text());assert report['native_board_sha256']==before;assert report['native_report_sha256']==R.sha(P/'body/fresh-native-drc.txt')
plane=next(z for z in b.Zones()if not z.GetIsRuleArea()and z.GetLayerSet().Contains(K.In2_Cu));samples=missing=0
reference_points=[]
local_nets=sorted({t.GetNetname()for t in seed.GetTracks()if not isinstance(t,K.PCB_VIA)and t.GetLayer()==K.B_Cu and ('SW'in t.GetNetname()or 'AUX'in t.GetNetname()or 'FB'in t.GetNetname()or re.fullmatch(r'REG[12]_L[12]',t.GetNetname()))})
for t in seed.GetTracks():
 if isinstance(t,K.PCB_VIA)or t.GetLayer()!=K.B_Cu or t.GetNetname()not in local_nets:continue
 a,c=t.GetStart(),t.GetEnd();dx,dy=c.x-a.x,c.y-a.y;length=math.hypot(dx,dy);steps=max(1,math.ceil(K.ToMM(length)/.1))
 for i in range(steps+1):
  for off in [-K.ToMM(t.GetWidth())/2,0,K.ToMM(t.GetWidth())/2]:
   p=K.VECTOR2I(round(a.x+dx*i/steps-dy/length*K.FromMM(off)),round(a.y+dy*i/steps+dx/length*K.FromMM(off)));samples+=1;missing+=not plane.HitTestFilledArea(K.In2_Cu,p);reference_points.append(p)
adjacent_reference=None
if b.GetCopperLayerCount()==6:
 adjacent=next(z for z in b.Zones()if not z.GetIsRuleArea()and z.GetLayerSet().Contains(K.In4_Cu))
 adjacent_reference={'layer':'In4.Cu','sample_count':len(reference_points),'samples_without_filled_adjacent_GND':sum(not adjacent.HitTestFilledArea(K.In4_Cu,p)for p in reference_points)}
 assert adjacent_reference['samples_without_filled_adjacent_GND']==0
 assert not any(t['kind']=='track'and t['layer']=='In4.Cu'and t['net']!='GND'for t in routes)
inspection=P/'layout-inspection.json';ir=json.loads(inspection.read_text());assert ir['boards']['body']['native_board_sha256']==before
out={'date':'2026-11-01','auditor_sha256':R.sha(Path(__file__)),'native_board_sha256':before,'project_sha256':R.sha(bp.with_suffix('.kicad_pro')),'native_body_xml_sha256':R.sha(xml),'native_inspection_sha256':R.sha(inspection),'drc_record_sha256':R.sha(P/'body/native-drc.json'),'DRC':report['counts'],'footprints':len(seen),'electrical_pad_entries_checked':pins,'pin_net_mismatches':mismatches,'explicit_native_NC_pins_kept_copper_netless':sorted(nc),'copper_layers':b.GetCopperLayerCount(),'track_via_records':len(routes),'through_vias':sum(t['kind']=='via'for t in routes),'In2_signal_tracks':sum(t['kind']=='track'and t['layer']=='In2.Cu'and t['net']!='GND'for t in routes),'protected_seed_records_preserved':sum(fixed.values()),'original_protected_seed_records_unchanged':original_seed_count-len(replacements)-retired_seed_count,'original_protected_seed_total':original_seed_count,'retired_from_protected_seed_count':retired_seed_count,'declared_unused_copper_retirements':retirements,'declared_unused_copper_sha256':R.sha(unused)if unused.exists()else None,'declared_protected_seed_replacements':replacements,'declared_ground_rework_sha256':R.sha(rework)if rework.exists()else None,'local_B_power_adjacent_ground_reference':adjacent_reference,'local_B_power_reference':{'nets':local_nets,'sample_count':samples,'samples_without_filled_In2_GND':missing},'power_net_widths_mm':{n:sorted({t['width']for t in routes if t['kind']=='track'and t['net']==n})for n in ['SYS','PACK_P','VBUS_CHG','3V3','MOTOR_3V7','MOTOR_P','MOTOR_N']},'scope':'Actual native pad-net parity, protected seed copper accounted for through any explicit GND replacement and native unused-via/dead-end retirement, In2 signal exclusion and discrete local B-route reference samples. Sampled reference is not full return-path, impedance, loop/current/thermal/process or physical acceptance.'}
assert R.sha(bp)==before;R.write(P/'saved-body-copper-audit.json',out);print(json.dumps(out,indent=2),flush=True)
assert not mismatches and not out['In2_signal_tracks']
if '--allow-unfinished'not in sys.argv[2:]:assert out['DRC']=={'violations':0,'unconnected':0,'footprint_errors':0}
