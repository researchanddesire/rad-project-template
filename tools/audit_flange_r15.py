"""Read-only saved-copper/pad/USB-reference screen for actual R15 flange."""
from pathlib import Path
import sys,json,math,re,xml.etree.ElementTree as E
import pcb_r2_route as R
K=R.k;ROOT=Path(__file__).resolve().parents[1];P=Path(sys.argv[1]).resolve();bp=P/'flange/flange-r15.kicad_pcb';b=K.LoadBoard(str(bp));before=R.sha(bp);report=P/'flange/routed-native-drc.txt';rows=json.loads((P/'flange-native-inspection.json').read_text());base=json.loads((ROOT/'hardware/pcb/route-r15/candidate-b/flange-native-inspection.json').read_text());assert rows['placements']==base['placements']and rows['outline_mechanical_xy_mm']==base['outline_mechanical_xy_mm']
xml=P/'flange/flange-native.xml';root=E.parse(xml).getroot();nodes={(n.get('ref'),n.get('pin')):net.get('name')for net in root.findall('nets/net')for n in net.findall('node')};mismatches=[];pins=0
nc={(n.get('ref'),n.get('pin'))for net in root.findall('nets/net')for n in net.findall('node')if n.get('pintype')=='no_connect'and n.get('pinfunction')=='NC'}
for fp in b.GetFootprints():
 for p in fp.Pads():
  if p.GetNumber()in ['','MP']:continue
  key=(fp.GetReference(),p.GetNumber());wanted=''if key in nc else nodes.get(key,'');pins+=1
  if p.GetNetname()!=wanted:mismatches.append([fp.GetReference(),p.GetNumber(),p.GetNetname(),wanted])
ground=next(z for z in b.Zones()if not z.GetIsRuleArea()and z.GetLayerSet().Contains(K.In1_Cu));routes=R.route_records(b);seed=K.LoadBoard(str(ROOT/'hardware/pcb/route-r15/candidate-e/flange/flange-r15.kicad_pcb'))
usb={};seed_usb=[r for r in R.route_records(seed)if r['net']in ['USB_DM','USB_DP']];actual_usb=[r for r in routes if r['net']in ['USB_DM','USB_DP']]
canonical=lambda rr:sorted(json.dumps(r,sort_keys=True)for r in rr)
assert canonical(seed_usb)==canonical(actual_usb)
for net in ['USB_DM','USB_DP']:
 tt=[t for t in b.GetTracks()if t.GetNetname()==net];samples=missing=0
 for t in tt:
  assert not isinstance(t,K.PCB_VIA)and t.GetLayer()==K.F_Cu
  a,c=t.GetStart(),t.GetEnd();dx,dy=c.x-a.x,c.y-a.y;length=math.hypot(dx,dy);steps=max(1,math.ceil(K.ToMM(length)/.1))
  for i in range(steps+1):
   for offset in [-.1,0,.1]:
    point=K.VECTOR2I(round(a.x+dx*i/steps-dy/length*K.FromMM(offset)),round(a.y+dy*i/steps+dx/length*K.FromMM(offset)));samples+=1
    if not ground.HitTestFilledArea(K.In1_Cu,point):missing+=1
 usb[net]={'length_mm':sum(K.ToMM(t.GetLength())for t in tt),'signal_vias':0,'widths_mm':sorted({K.ToMM(t.GetWidth())for t in tt}),'layers':['F.Cu'],'reference_samples':samples,'samples_without_In1_GND':missing}
counts={key:int(re.search(r'\*\* Found (\d+) '+text,report.read_text())[1])for key,text in [('violations','DRC violations'),('unconnected','unconnected pads'),('footprint_errors','Footprint errors')]}
out={'date':'2026-11-01','auditor_sha256':R.sha(Path(__file__)),'native_board_sha256':before,'project_sha256':R.sha(bp.with_suffix('.kicad_pro')),'drc_sha256':R.sha(report),'native_flange_xml_sha256':R.sha(xml),'native_inspection_sha256':R.sha(P/'flange-native-inspection.json'),'DRC':counts,'footprints':len(list(b.GetFootprints())),'electrical_pad_entries_checked':pins,'pin_net_mismatches':mismatches,'physical_poses_pad_coordinates_nets_and_footprint_IDs_equal_R15B':True,'copper_layers':b.GetCopperLayerCount(),'all_tracks_and_vias':len(routes),'through_vias':sum(r['kind']=='via'for r in routes),'In1_signal_tracks':sum(not isinstance(t,K.PCB_VIA)and t.GetLayer()==K.In1_Cu for t in b.GetTracks()),'USB_saved_copper_identical_to_E_seed':True,'USB':usb,'USB_skew_mm':abs(usb['USB_DM']['length_mm']-usb['USB_DP']['length_mm']),'scope':'Actual native saved copper/pad parity and discrete reference samples. No impedance/RF/current/process/fabrication/harness or physical acceptance; .1mm samples at center and both .1mm edges do not prove complete reference geometry.'}
out['explicit_native_NC_pins_kept_copper_netless']=sorted(nc)
assert R.sha(bp)==before
(P/'saved-copper-audit.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2),flush=True)
assert not mismatches and counts=={'violations':0,'unconnected':0,'footprint_errors':0}
assert all(v['samples_without_In1_GND']==0 for v in usb.values())
