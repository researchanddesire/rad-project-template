"""Independent actual-copper/native-net/USB-reference audit of R16 flange."""
from pathlib import Path
import sys,json,math,re,xml.etree.ElementTree as E
import pcb_r2_route as R
K=R.k;ROOT=Path(__file__).resolve().parents[1];P=Path(sys.argv[1]).resolve();bp=P/'flange/flange-r16.kicad_pcb';before=R.sha(bp);b=K.LoadBoard(str(bp));xml=P/'flange/flange-native.xml';root=E.parse(xml).getroot();nodes={(n.get('ref'),n.get('pin')):net.get('name')for net in root.findall('nets/net')for n in net.findall('node')};nc={(n.get('ref'),n.get('pin'))for net in root.findall('nets/net')for n in net.findall('node')if n.get('pintype')=='no_connect'and n.get('pinfunction')=='NC'};mismatches=[];pins=0
for f in b.GetFootprints():
 for p in f.Pads():
  if p.GetNumber()in ['','MP']:continue
  key=f.GetReference(),p.GetNumber();wanted=''if key in nc else nodes.get(key,'');pins+=1
  if p.GetNetname()!=wanted:mismatches.append([*key,p.GetNetname(),wanted])
ground=next(z for z in b.Zones()if not z.GetIsRuleArea()and z.GetLayerSet().Contains(K.In1_Cu));routes=R.route_records(b);seedpath=ROOT/'hardware/pcb/route-r16/candidate-k/flange/flange-r16.kicad_pcb';seed=K.LoadBoard(str(seedpath));canon=lambda rr:sorted(json.dumps(r,sort_keys=True)for r in rr);usb={}
assert canon([r for r in R.route_records(seed)if r['net']in ['USB_DM','USB_DP']])==canon([r for r in routes if r['net']in ['USB_DM','USB_DP']])
for net in ['USB_DM','USB_DP']:
 tt=[t for t in b.GetTracks()if t.GetNetname()==net];samples=missing=0
 for t in tt:
  assert not isinstance(t,K.PCB_VIA)and t.GetLayer()==K.F_Cu;a,c=t.GetStart(),t.GetEnd();dx,dy=c.x-a.x,c.y-a.y;length=math.hypot(dx,dy);steps=max(1,math.ceil(K.ToMM(length)/.1))
  for i in range(steps+1):
   for offset in [-.1,0,.1]:
    p=K.VECTOR2I(round(a.x+dx*i/steps-dy/length*K.FromMM(offset)),round(a.y+dy*i/steps+dx/length*K.FromMM(offset)));samples+=1;missing+=not ground.HitTestFilledArea(K.In1_Cu,p)
 usb[net]={'length_mm':sum(K.ToMM(t.GetLength())for t in tt),'widths_mm':sorted({K.ToMM(t.GetWidth())for t in tt}),'layers':['F.Cu'],'signal_vias':0,'reference_samples':samples,'samples_without_In1_GND':missing}
report=P/'flange/routed-native-drc.txt';counts={key:int(re.search(r'\*\* Found (\d+) '+text,report.read_text())[1])for key,text in [('violations','DRC violations'),('unconnected','unconnected pads'),('footprint_errors','Footprint errors')]};inspection=P/'layout-inspection.json';ir=json.loads(inspection.read_text());assert ir['boards']['flange']['native_board_sha256']==before and len(ir['boards']['flange']['placements'])==24
out={'date':'2026-11-01','auditor_sha256':R.sha(Path(__file__)),'native_board_sha256':before,'project_sha256':R.sha(bp.with_suffix('.kicad_pro')),'drc_sha256':R.sha(report),'native_flange_xml_sha256':R.sha(xml),'native_inspection_sha256':R.sha(inspection),'DRC':counts,'footprints':24,'electrical_pad_entries_checked':pins,'pin_net_mismatches':mismatches,'explicit_native_NC_pins_kept_copper_netless':sorted(nc),'copper_layers':b.GetCopperLayerCount(),'track_via_records':len(routes),'through_vias':sum(r['kind']=='via'for r in routes),'In1_signal_tracks':sum(not isinstance(t,K.PCB_VIA)and t.GetLayer()==K.In1_Cu for t in b.GetTracks()),'USB_saved_copper_identical_to_K_seed':True,'USB_seed_sha256':R.sha(seedpath),'USB':usb,'USB_skew_mm':abs(usb['USB_DM']['length_mm']-usb['USB_DP']['length_mm']),'input_net_track_widths_mm':{n:sorted({r['width']for r in routes if r['net']==n and r['kind']=='track'})for n in ['DOCK_5V','DOCK_FUSED','VBUS_CHG']},'scope':'Actual saved native copper and pad/net parity. USB reference checked at0.1mm intervals/center and both0.1mm edges; discrete samples do not prove complete reference geometry. No impedance/RF/current/process/harness or physical acceptance.'};assert R.sha(bp)==before;R.write(P/'saved-copper-audit.json',out);print(json.dumps(out,indent=2),flush=True);assert not mismatches and counts=={'violations':0,'unconnected':0,'footprint_errors':0};assert all(v['samples_without_In1_GND']==0 for v in usb.values());assert not out['In1_signal_tracks']
