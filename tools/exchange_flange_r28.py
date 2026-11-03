"""Offline local exchange, fixed seed/USB and reserved In1 GND plane."""
from pathlib import Path
import sys,json,re,shutil,collections
import pcb_r2_route as R
K=R.k;ROOT=Path(__file__).resolve().parents[1];action=sys.argv[1];P=Path(sys.argv[2]).resolve();bp=P/'flange-r28.kicad_pcb';dsn=bp.with_suffix('.dsn');ses=bp.with_suffix('.ses')
def sig(q):
 return('via',q['net'],tuple(q['position']),q['diameter'],q['drill'])if q['kind']=='via'else('track',q['net'],q['layer'],tuple(sorted([tuple(q['start']),tuple(q['end'])])),q['width'])
if action=='export':
 src=Path(sys.argv[3]).resolve();P.mkdir(parents=True,exist_ok=True);assert not any(P.iterdir())
 for name in ['flange-r28.kicad_pcb','flange-r28.kicad_pro','fp-lib-table','routing-seed.json','reserved-ports.json']:
  if(src/name).is_file():shutil.copyfile(src/name,P/name)
 b=K.LoadBoard(str(bp));assert all(t.IsLocked()for t in b.GetTracks());fixed=R.route_records(b)
 for z in list(b.Zones()):
  if not z.GetIsRuleArea()and not z.GetLayerSet().Contains(K.In1_Cu):b.Delete(z)
 assert K.ExportSpecctraDSN(b,str(dsn));text=dsn.read_text();start=text.index('(class kicad_default');end=text.index('(circuit',start);header=text[start:end]
 classes=[('DockFeed',['DOCK_5V','DOCK_FUSED','VBUS_CHG'],600),('RadioSupply',['3V3'],300)]
 for _,nets,_ in classes:
  for net in nets:header=re.sub(r'(?<!\S)'+net+r'(?=\s)','',header)
 text=text[:start]+header+text[end:]
 # Low-current logic uses the existing native .15mm minimum. Power classes
 # and all fixed copper stay wider. Disable router neckdown in run settings.
 cstart=text.index('(class kicad_default');cend=text.index('\n    )',cstart)+6;cb=text[cstart:cend];assert cb.count('(width 200)')==1;text=text[:cstart]+cb.replace('(width 200)','(width 150)')+text[cend:]
 insert=text.rfind('\n  )',0,text.index('\n  (wiring'));extra=''
 for name,nets,width in classes:extra+='\n    (class '+name+' '+' '.join(nets)+'\n      (circuit (use_via Via[0-3]_600:300_um))\n      (rule (width '+str(width)+') (clearance 100.1))\n    )'
 text=text[:insert]+extra+text[insert:]
 # Router-only inset compensates for KiCad7's DSN boundary clearance. Native
 # outline and .3mm edge rule stay unchanged. Source flange is rectangular.
 match=re.search(r'\(boundary\s*\(path pcb 0\s+([\d\s.\-]+)\)\s*\)',text);assert match
 nums=list(map(float,match[1].split()));pts=list(zip(nums[::2],nums[1::2]));xmin=min(x for x,y in pts);xmax=max(x for x,y in pts);ymin=min(y for x,y in pts);ymax=max(y for x,y in pts)
 assert all(x in [xmin,xmax]and y in [ymin,ymax]for x,y in pts)
 inset=[(x+200 if x==xmin else x-200,y+200 if y==ymin else y-200)for x,y in pts]
 replacement='(boundary (path pcb 0 '+' '.join(f'{v:.3f}'for p in inset for v in p)+'))';text=text[:match.start()]+replacement+text[match.end():]
 settings='\n    (autoroute_settings (autoroute on) (postroute off) (vias on) (layer_rule F.Cu (active on) (preferred_direction horizontal)) (layer_rule In1.Cu (active off)) (layer_rule In2.Cu (active on) (preferred_direction vertical)) (layer_rule B.Cu (active on) (preferred_direction horizontal)))';pos=text.index('\n    (plane GND');text=text[:pos]+settings+text[pos:];dsn.write_text(text)
 R.write(P/'router-exchange.json',{'seed_directory':str(src.relative_to(ROOT)),'seed_board_sha256':R.sha(bp),'DSN_sha256':R.sha(dsn),'exchange_tool_sha256':R.sha(Path(__file__)),'fixed_records':fixed,'routable_layers':['F.Cu','In2.Cu','B.Cu'],'In1_GND_only':True,'scope':'Native rules unchanged. Dock/fused/charger.6mm, new3V3branches.3mm, low-current logic.15mm; existing.65radio feed/USB/local copper locked. Router boundary inset.2mm; no neckdown permitted by run settings. Offline candidate requires fresh native and copper/plane/process review.'})
 print(dsn,flush=True)
elif action=='import':
 r=json.loads((P/'router-exchange.json').read_text());assert R.sha(bp)==r['seed_board_sha256']and R.sha(dsn)==r['DSN_sha256'];b=K.LoadBoard(str(bp));old=R.route_records(b);fixed={sig(q)for q in old};incoming=R.parse_ses(ses);added=[q for q in incoming if sig(q)not in fixed]
 assert not any(q['net']in ['USB_DM','USB_DP']for q in added)
 assert not any(q['kind']=='track'and q['layer']=='In1.Cu'for q in added)
 R.apply_routes(b,added,locked=False);K.SaveBoard(str(bp),b);now=R.fill_save(bp)
 assert not collections.Counter(json.dumps(q,sort_keys=True)for q in old)-collections.Counter(json.dumps(q,sort_keys=True)for q in R.route_records(now))
 r.update({'session_sha256':R.sha(ses),'added_routes':len(added),'native_board_sha256':R.sha(bp),'status':'Imported; fresh native DRC and complete saved checks required.'});R.write(P/'router-exchange.json',r);print('new routes',len(added),flush=True)
else:raise ValueError(action)
