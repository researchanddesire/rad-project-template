"""Offline body exchange with In2 reserved for GND and fixed local power paths."""
from pathlib import Path
import argparse,json,re,math
import pcb_r2_route as R
K=R.k;R.LAYERS['In1.Cu']=K.In1_Cu;ROOT=Path(__file__).resolve().parents[1];ap=argparse.ArgumentParser();ap.add_argument('action',choices=['export','import']);ap.add_argument('directory',type=Path);ap.add_argument('--seed',type=Path);a=ap.parse_args();P=a.directory.resolve();board_name=next(((a.seed.resolve()if a.action=='export'else P)/'body').glob('body-r*.kicad_pcb')).name;board=P/'body'/board_name;dsn=board.with_suffix('.dsn');ses=board.with_suffix('.ses')
def sig(r):
 if r['kind']=='via':return('via',r['net'],tuple(r['position']),r['diameter'],r['drill'])
 return('track',r['net'],r['layer'],tuple(sorted([tuple(r['start']),tuple(r['end'])])),r['width'])
records=['fp-lib-table','sym-lib-table','body-seed.json','local-power.json','power-refinement.json','local-interfaces.json','compact-driver.json','signal-first-seed.json','signal-ports.json','signal-application.json','ground-plan.json','ground-application.json','ground-rework.json','fresh-fill.json','local-seed-final.json','dock-port-rework.json','signal-repack.json','local-seed-conservation.json','board-width.json','via-process.json']
if a.action=='export':
 assert a.seed;source=a.seed.resolve();P.mkdir(parents=True,exist_ok=True);assert not any(P.iterdir())
 for p in source.rglob('*'):
  if p.is_file()and((p.suffix in ['.kicad_pro','.kicad_sch','.kicad_sym','.kicad_mod']or p.suffix=='.kicad_pcb'and p.name!='source-seed.kicad_pcb')or p.name in records):
   q=P/p.relative_to(source);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
 b=K.LoadBoard(str(board))
 for t in b.GetTracks():t.SetLocked(True)
 K.SaveBoard(str(board),b);R.fill_save(board);b=K.LoadBoard(str(board));(P/'body/source-seed.kicad_pcb').write_bytes(board.read_bytes())
 for z in list(b.Zones()):
  if not z.GetIsRuleArea()and not z.GetLayerSet().Contains(K.In2_Cu):b.Delete(z)
 assert K.ExportSpecctraDSN(b,str(dsn));txt=dsn.read_text();begin=txt.index('(class kicad_default');end=txt.index('(circuit',begin);header=txt[begin:end];classes=[('WidePower', ['SYS','PACK_P','VBUS_CHG','MOTOR_3V7','MOTOR_P','MOTOR_N'],600),('LogicSupply',['3V3'],300)]
 for _,nets,_ in classes:
  for net in nets:header=re.sub(r'(?<!\S)'+net+r'(?=\s)','',header)
 txt=txt[:begin]+header+txt[end:];insert=txt.rfind('\n  )',0,txt.index('\n  (wiring'));extra=''
 for name,nets,width in classes:extra+='\n    (class '+name+' '+' '.join(nets)+'\n      (circuit (use_via Via[0-3]_600:300_um))\n      (rule (width '+str(width)+') (clearance 100.1))\n    )'
 txt=txt[:insert]+extra+txt[insert:]
 # KiCad 7 DSN uses the .1001mm general router clearance at its boundary.
 # An extra .2mm planning-only inset preserves the native .3mm edge rule.
 match=re.search(r'\(boundary\s*\(path pcb 0\s+([\d\s.\-]+)\)\s*\)',txt);assert match
 nums=list(map(float,match[1].split()));vertices=list(zip(nums[::2],nums[1::2]));assert vertices[0]==vertices[-1];vertices.pop()
 area=sum(a[0]*b[1]-b[0]*a[1]for a,b in zip(vertices,vertices[1:]+vertices[:1]));sign=1 if area>0 else-1;lines=[]
 for p,q in zip(vertices,vertices[1:]+vertices[:1]):
  dx,dy=q[0]-p[0],q[1]-p[1];length=math.hypot(dx,dy);normal=(-sign*dy/length,sign*dx/length);lines.append((normal,normal[0]*p[0]+normal[1]*p[1]+200))
 inset=[]
 for i,(n,c)in enumerate(lines):
  m,d=lines[i-1];det=m[0]*n[1]-m[1]*n[0];assert abs(det)>1e-9;inset.append(((d*n[1]-m[1]*c)/det,(m[0]*c-d*n[0])/det))
 assert all(n[0]*p[0]+n[1]*p[1]>=c-.01 for p in inset for n,c in lines)
 inset.append(inset[0]);replacement='(boundary (path pcb 0 '+' '.join(f'{v:.3f}'for p in inset for v in p)+'))';txt=txt[:match.start()]+replacement+txt[match.end():]
 dsn.write_text(txt);R.write(P/'router-exchange.json',{'date':'2026-11-01','exchange_tool_sha256':R.sha(Path(__file__)),'seed_directory':str(source.relative_to(ROOT)),'source_seed_sha256':R.sha(source/'body'/board_name),'seed_board_sha256':R.sha(board),'export_dsn_sha256':R.sha(dsn),'router_only_boundary_inset_mm':.2,'rule_note':'Native outline and rules unchanged. DSN planning boundary inset .2mm plus .1001mm router clearance respects native .3mm edge rule. In2 GND only; F/In1/B routable. Six power/output nets .6mm,3V3 .3mm, other .2mm. Protected local switch/feedback/IC pin necks, ground stitches and motor fanout retained at explicit widths. Not current/thermal/process/physical acceptance.'});print(dsn,flush=True)
else:
 r=json.loads((P/'router-exchange.json').read_text());assert R.sha(board)==r['seed_board_sha256']and R.sha(dsn)==r['export_dsn_sha256'];b=K.LoadBoard(str(board));before=R.route_records(b);assert all(t.IsLocked()for t in b.GetTracks());fixed={sig(t)for t in before};incoming=R.parse_ses(ses);added=[t for t in incoming if sig(t)not in fixed];assert all(t['kind']=='via'or t['layer']!='In2.Cu'for t in added);R.apply_routes(b,added,locked=False);K.SaveBoard(str(board),b);saved=R.fill_save(board);assert fixed<={sig(t)for t in R.route_records(saved)};r.update({'import_session_sha256':R.sha(ses),'session_records':len(incoming),'exact_seed_duplicates_skipped':len(incoming)-len(added),'added_records':len(added),'preserved_manual_records':len(before),'native_board_sha256':R.sha(board),'scope':'Offline body candidate. All protected manual copper preserved; actual fresh native DRC, full source/NC/pad/reference/drill/thermal/fit review still required.'});R.write(P/'router-exchange.json',r);print(json.dumps(r,indent=2),flush=True)
