"""Review project with preserved R23 body, repaired R28 flange and source sheets."""
from pathlib import Path
import sys,json,re,shutil,os
import pcb_r2_route as R
import kicad_sexp as S
ROOT=Path(__file__).resolve().parents[1];OLD=ROOT/'hardware/pcb/stackup-r23/candidate-d';ROUTED=Path(sys.argv[1]).resolve();OUT=Path(sys.argv[2]).resolve();OUT.mkdir(parents=True,exist_ok=True);assert not any(OUT.iterdir())
dr=json.loads((ROUTED/'drc-status.json').read_text());assert dr['counts']=={'drc_violations':0,'unconnected_items':0,'footprint_errors':0}and R.sha(ROUTED/'flange-r28.kicad_pcb')==dr['native_board_sha256']
sheets={};projects={};libs={}
for p in OLD.rglob('*'):
 if not p.is_file()or p.suffix not in ['.kicad_sch','.kicad_pro','.kicad_sym']and p.name not in ['fp-lib-table','sym-lib-table']:continue
 rel=str(p.relative_to(OLD)).replace('-r23','-r28');q=OUT/rel;q.parent.mkdir(parents=True,exist_ok=True)
 if p.suffix=='.kicad_sch':
  text=p.read_text()
  for domain in ['system','body','flange']:text=text.replace('"'+domain+'-r23"','"'+domain+'-r28"').replace(domain+'-r23.kicad_sch',domain+'-r28.kicad_sch')
  tree=S.parse(text)
  for title in S.children(tree,'title_block'):
   for field in title[1:]:
    if S.tag(field)in ['title','rev']:field[1]=S.string(re.sub(r'R\d+','R28',field[1].value))
    if S.tag(field)=='comment'and field[1].value=='1':field[2]=S.string('ROUTED CANDIDATE / BENCH REVIEW / NOT FABRICATION RELEASE')
  if p.relative_to(OLD)==Path('flange/01-power.kicad_sch'):
   symbol=next(n for n in S.children(tree,'symbol')if S.prop(n,'Reference')=='J1')
   assert S.prop(symbol,'Value')=='MAGNETIC_DOCK_5V'and S.prop(symbol,'Footprint').endswith('JST_SH_SM02B-SRSS-TB_1x02-1MP_P1.00mm_Horizontal')
   for prop in S.children(symbol,'property'):
    if prop[1].value=='ReviewNote':prop[2]=S.string(prop[2].value+'; internal SM02B-SRSS-TB SH2 header candidate, separate from exposed dock contacts; legacy PCB PH2 value corrected in R28')
    if prop[1].value=='Datasheet':prop[2]=S.string('https://www.jst.com/wp-content/uploads/2021/01/eSH-new.pdf')
  S.write(q,tree);sheets[rel]={'source_sha256':R.sha(p),'current_sha256':R.sha(q)}
 elif p.suffix=='.kicad_pro':
  old=json.loads(p.read_text());now=json.loads(p.read_text())
  if 'meta'in now and isinstance(now['meta'],dict)and 'filename'in now['meta']:now['meta']['filename']=q.name
  q.write_text(json.dumps(now,indent=2)+'\n')
  for key in ['board','erc','net_settings']:assert old.get(key)==now.get(key),(rel,key)
  projects[rel]={'source_sha256':R.sha(p),'current_sha256':R.sha(q),'board_ERC_net_rules_unchanged':True}
 elif p.name=='fp-lib-table':
  prefix=os.path.relpath(p.parent,q.parent);q.write_text(p.read_text().replace('${KIPRJMOD}/','${KIPRJMOD}/'+prefix+'/'))
 else:
  shutil.copyfile(p,q)
  if p.suffix=='.kicad_sym':libs[rel]=R.sha(q)
body=OUT/'body/body-r28.kicad_pcb';shutil.copyfile(OLD/'body/body-r23.kicad_pcb',body)
flange=OUT/'flange/flange-r28.kicad_pcb';shutil.copyfile(ROUTED/'flange-r28.kicad_pcb',flange);before=R.sha(flange);b=R.k.LoadBoard(str(flange));original=R.route_records(b);f=next(f for f in b.GetFootprints()if f.GetReference()=='J1');value=f.GetValue();assert value=='S2B-PH-SM4-TB';f.SetValue('SM02B-SRSS-TB');R.k.SaveBoard(str(flange),b)
assert original==R.route_records(R.k.LoadBoard(str(flange)))and R.sha(body)==R.sha(OLD/'body/body-r23.kicad_pcb')
assert len(sheets)==13 and len(projects)==3 and len(libs)==3
R.write(OUT/'project-package.json',{'date':'2026-11-01','packager_sha256':R.sha(Path(__file__)),'source_R23_body_sha256':R.sha(body),'source_repaired_flange_sha256':before,'flange_native_sha256':R.sha(flange),'sheets':sheets,'projects':projects,'copied_symbol_libraries_sha256':libs,'declared_changes':['R23-to-R28 native project contexts and sheet filenames','Title/revision/comment labels only','J1 schematic retains MAGNETIC_DOCK_5V logical value; ReviewNote/Datasheet clarify internal SH2 candidate','J1 PCB candidate value corrected from stale PH2 text to SM02B-SRSS-TB; footprint/pins/poses/copper unchanged'],'scope':'Complete review project, unchanged six-layer body and repaired four-layer flange. No circuit/wire/NC/rule change intended. Fresh native XML parity and DRC/copper/process/MCAD checks required; no fresh GUI ERC or manufacturing/physical result claimed. BatteryOPEN/humanBOMunchanged.'});print('13sheets/3projects/3libraries; body byte-identical; J1 PCB label corrected without copper change',flush=True)
