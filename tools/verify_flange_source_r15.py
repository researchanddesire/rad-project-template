"""Prove every schematic source change is declared; compare native rules."""
from pathlib import Path
import sys,re,json,hashlib
ROOT=Path(__file__).resolve().parents[1];OLD=ROOT/'hardware/pcb/split-r14/candidate-b';P=Path(sys.argv[1]).resolve();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();sheets={};libs={};projects={}
for p in OLD.rglob('*.kicad_sch'):
 relative=p.relative_to(OLD);q=P/str(relative).replace('-r14','-r15');s=p.read_text()
 for name in ['system','body','flange']:s=s.replace('"'+name+'-r14"','"'+name+'-r15"').replace(name+'-r14.kicad_sch',name+'-r15.kicad_sch')
 if relative==Path('flange/01-power.kicad_sch'):s=s.replace('PrototypeR0:JST_PH_S2B-PH-SM4-TB_1x02-1MP_P2.00mm_Horizontal','PrototypeR0:JST_SH_SM02B-SRSS-TB_1x02-1MP_P1.00mm_Horizontal')
 s=re.sub(r'\((title|rev) "([^"\n]*)"\)',lambda m:'('+m[1]+' "'+m[2].replace('R14','R15')+'")',s);s=s.replace('"UNROUTED / REVIEW ONLY"','"REVIEW ONLY / BODY UNROUTED / FLANGE ROUTE R15"')
 assert s==q.read_text(),relative;sheets[str(q.relative_to(P))]={'R14_sha256':sha(p),'R15_sha256':sha(q),'exact_text_equal_after_declared_changes':True}
for p in OLD.rglob('*.kicad_sym'):
 q=P/p.relative_to(OLD);assert sha(p)==sha(q);libs[str(q.relative_to(P))]=sha(q)
for p in OLD.rglob('*.kicad_pro'):
 q=P/str(p.relative_to(OLD)).replace('-r14','-r15');a=json.loads(p.read_text());b=json.loads(q.read_text())
 for field in ['board','erc','net_settings']:
  assert a[field]==b[field],(q,field)
 projects[str(q.relative_to(P))]={'R14_sha256':sha(p),'R15_sha256':sha(q),'board_ERC_net_settings_equal_R14':True}
out={'date':'2026-11-01','verifier_sha256':sha(Path(__file__)),'schematics':sheets,'symbol_libraries_equal_sha256':libs,'projects':projects,'allowed_source_changes':['R14toR15project context and sheet filenames','J1PH2toSH2footprint field in flange power sheet','Schematic title/revision/comment labels only'],'scope':'Exact whole-source text comparison after named transformations preserves every wire, symbol, no-connect, driver flag and exclusion annotation. Board/erc/net_settings JSON objects unchanged. This is not a newly executed R15 GUI ERC or a manufactured-circuit result.'}
(P/'source-conservation.json').write_text(json.dumps(out,indent=2)+'\n');print(len(sheets),'whole native schematics conserved;',len(libs),'libraries;',len(projects),'native rule objects unchanged')
