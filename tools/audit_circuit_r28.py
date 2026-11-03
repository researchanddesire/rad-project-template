"""Independent saved native circuit/copper/plane/pose review of the R28 package."""
from pathlib import Path
import sys,json,re,math,collections,xml.etree.ElementTree as E
import pcb_r2_route as R
import pcb_split_r12 as G
K=R.k;ROOT=Path(__file__).resolve().parents[1];P=Path(sys.argv[1]).resolve();OLD=ROOT/'hardware/pcb/stackup-r23/candidate-d'
def xml(path):
 t=E.parse(path).getroot();c={x.get('ref'):(x.findtext('value'),x.findtext('footprint'),x.find('libsource').attrib)for x in t.findall('components/comp')};n={(q.get('ref'),q.get('pin')):(net.get('name'),q.get('pinfunction'),q.get('pintype'))for net in t.findall('nets/net')for q in net.findall('node')};return c,n
oc,on=xml(OLD/'system-native.xml');nc,nn=xml(P/'system-native.xml');assert oc==nc and on==nn and len(nc)==94 and len(nn)==338
domains={};inspection={};current={};pose_source=json.loads((ROOT/'hardware/pcb/flange-access-r28/candidate-a/placement-inspection.json').read_text());oldi=json.loads((OLD/'layout-inspection.json').read_text())
for domain in ['body','flange']:
 bp=P/domain/(domain+'-r28.kicad_pcb');before=R.sha(bp);b=K.LoadBoard(str(bp));current[domain]=b;_,nodes=xml(P/domain/(domain+'-native.xml'));mismatch=[];pins=0;rows=[]
 expected=pose_source['placements']if domain=='flange'else oldi['boards']['body']['placements'];byref={q['ref']:q for q in expected};assert len(byref)==len(b.GetFootprints())
 for f in b.GetFootprints():
  ref=f.GetReference();old=byref[ref];side='B'if f.GetLayer()==K.B_Cu else'F';bb=G.rect(f,[K.F_Fab,K.B_Fab]);court=G.rect(f,[K.F_CrtYd,K.B_CrtYd]);xy=G.mech(f.GetPosition());assert side==old['side']and abs(f.GetOrientationDegrees()-old['angle_deg'])<1e-7
  assert max(abs(a-c)for a,c in zip(xy,old['xy_mm']))<1e-7 and (bb is None)==(old['body_xy_mm']is None)
  if bb is not None:assert max(abs(a-c)for a,c in zip(bb,old['body_xy_mm']))<1e-7
  pads=[]
  for p in f.Pads():
   pads.append({'n':p.GetNumber(),'net':p.GetNetname(),'xy_mm':G.mech(p.GetPosition())})
   if p.GetNumber()in ['','MP']:continue
   key=ref,p.GetNumber();target=nodes.get(key);assert target,key
   wanted=''if 'no_connect'in target[2].split('+')else target[0];pins+=1
   if p.GetNetname()!=wanted:mismatch.append([ref,p.GetNumber(),p.GetNetname(),wanted])
  rows.append({'ref':ref,'value':f.GetValue(),'xy_mm':xy,'angle_deg':f.GetOrientationDegrees(),'side':side,'body_xy_mm':bb,'courtyard_xy_mm':court,'height_budget_mm':old['height_budget_mm'],'z_bounds_mm':old['z_bounds_mm'],'pads':pads})
 counts=json.loads((P/domain/'drc-status.json').read_text());assert counts['native_board_sha256']==before and counts['counts']=={'drc_violations':0,'unconnected_items':0,'footprint_errors':0}and not mismatch,(domain,counts,mismatch)
 project=json.loads(bp.with_suffix('.kicad_pro').read_text());oldproject=json.loads((OLD/domain/(domain+'-r23.kicad_pro')).read_text())
 for key in ['board','erc','net_settings']:assert project[key]==oldproject[key],(domain,key)
 domains[domain]={'native_board_sha256':before,'native_xml_sha256':R.sha(P/domain/(domain+'-native.xml')),'native_project_sha256':R.sha(bp.with_suffix('.kicad_pro')),'DRC':counts['counts'],'native_DRC_report_sha256':counts['report_sha256'],'footprints':len(rows),'electrical_pad_entries_checked':pins,'pin_net_mismatches':mismatch,'source_board_ERC_net_rules_equal':True,'copper_layers':b.GetCopperLayerCount()};inspection[domain]={'native_board_sha256':before,'placements':rows}
 assert R.sha(bp)==before
assert domains['body']['native_board_sha256']==R.sha(OLD/'body/body-r23.kicad_pcb')
f=current['flange'];routes=R.route_records(f);oldroutes=R.route_records(K.LoadBoard(str(OLD/'flange/flange-r23.kicad_pcb')));canon=lambda rows:collections.Counter(json.dumps(q,sort_keys=True)for q in rows)
assert canon(q for q in routes if q['net']in ['USB_DM','USB_DP'])==canon(q for q in oldroutes if q['net']in ['USB_DM','USB_DP'])
source_local=ROOT/'hardware/pcb/flange-access-r28/candidate-d/routing-seed.json';preserved=json.loads(source_local.read_text())['preserved_routes'];assert not canon(preserved)-canon(routes)
assert not any(q['kind']=='track'and q['layer']=='In1.Cu'and q['net']!='GND'for q in routes)
ground=next(z for z in f.Zones()if not z.GetIsRuleArea()and z.GetLayerSet().Contains(K.In1_Cu));usb={}
for net in ['USB_DM','USB_DP']:
 tt=[t for t in f.GetTracks()if t.GetNetname()==net];samples=missing=0
 for t in tt:
  assert not isinstance(t,K.PCB_VIA)and t.GetLayer()==K.F_Cu;a,c=t.GetStart(),t.GetEnd();dx,dy=c.x-a.x,c.y-a.y;length=math.hypot(dx,dy);steps=max(1,math.ceil(K.ToMM(length)/.1))
  for i in range(steps+1):
   for offset in [-.1,0,.1]:
    point=K.VECTOR2I(round(a.x+dx*i/steps-dy/length*K.FromMM(offset)),round(a.y+dy*i/steps+dx/length*K.FromMM(offset)));samples+=1;missing+=not ground.HitTestFilledArea(K.In1_Cu,point)
 usb[net]={'length_mm':sum(K.ToMM(t.GetLength())for t in tt),'widths_mm':sorted({K.ToMM(t.GetWidth())for t in tt}),'F_only_no_vias':True,'reference_samples':samples,'samples_without_In1_GND':missing};assert missing==0,(net,missing)
drill=json.loads((P/'flange/drill-paste-review.json').read_text());assert drill['native_board_sha256']==domains['flange']['native_board_sha256']and drill['vias_drilling_SMD_copper']==drill['vias_drilling_paste']==0
j1=next(f for f in current['flange'].GetFootprints()if f.GetReference()=='J1');assert j1.GetValue()=='SM02B-SRSS-TB'
cad=ROOT/'hardware/cad/flange-controls-r27/candidate-d';cr=json.loads((cad/'saved-review.json').read_text());assert cr['native_R28_placement_geometry_binding']['native_board_sha256']==pose_source['native_board_sha256']
assert R.sha(ROOT/'hardware/pcb/flange-access-r28/candidate-a/flange-r28.kicad_pcb')==pose_source['native_board_sha256']
out={'date':'2026-11-01','auditor_sha256':R.sha(Path(__file__)),'whole_system_native_XML_sha256':R.sha(P/'system-native.xml'),'source_system_native_XML_sha256':R.sha(OLD/'system-native.xml'),'components':94,'pin_net_function_type_nodes':338,'all_source_components_and_nodes_equal':True,'domains':domains,'source_body_byte_identical':True,'preserved_local_route_records':len(preserved),'USB_source_copper_exactly_equal':True,'USB':usb,'In1_GND_only':True,'flange_routes':len(routes),'flange_through_vias':sum(q['kind']=='via'for q in routes),'minimum_signal_track_width_mm':min(q['width']for q in routes if q['kind']=='track'),'input_power_track_widths_mm':{n:sorted({q['width']for q in routes if q['kind']=='track'and q['net']==n})for n in ['DOCK_5V','DOCK_FUSED','VBUS_CHG']},'drill_paste_review_sha256':R.sha(P/'flange/drill-paste-review.json'),'current_CAD_native_sha256':cr['native_sha256'],'current_CAD_saved_review_sha256':R.sha(cad/'saved-review.json'),'CAD_binding':'All24 flange Fab/height poses equal sourceA used by R27D; current body byte-identical to sourceR23. Routing/value-text changes add no physical component/PCB-envelope change.','scope':'Saved native DRC, full native XML/pad/pose/rule conservation and sampled USB ground reference; all41drills vs125native pad shapes reviewed separately. No fresh GUI ERC, full continuous return/impedance/RF/current/thermal/process/harness or physical acceptance. BatteryOPEN/humanBOMunchanged.'}
R.write(P/'layout-inspection.json',{'boards':inspection,'inspector_sha256':R.sha(Path(__file__))});R.write(P/'saved-circuit-review.json',out);print('94components/338nodes conserved;',domains['body']['DRC'],domains['flange']['DRC'],'USB reference',usb,'all24flange poses match R27D',flush=True)
