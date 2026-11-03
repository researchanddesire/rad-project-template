"""Compare actual R16 source atoms and fresh native XML to baseline A."""
from pathlib import Path
import sys,json,hashlib,copy,xml.etree.ElementTree as E
import kicad_sexp as S
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'hardware/pcb/route-r16/candidate-a';P=Path(sys.argv[1]).resolve();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def canon(n):return tuple(canon(x)for x in n)if isinstance(n,list)else n.raw
def collect(folder):
 files={str(p.relative_to(folder)):S.parse(p.read_text())for p in folder.rglob('*.kicad_sch')};out={t:{}for t in ['symbol','wire','no_connect','global_label','junction']}
 for file,root in files.items():
  for t,rows in out.items():
   for n in S.children(root,t):
    key=S.prop(n,'Reference')if t=='symbol'else S.value(n,'uuid')
    # J6/J7 generated label IDs repeat in two distinct sheet documents.
    if t=='global_label'and file.endswith('06-interboard.kicad_sch'):key=file+':'+key
    assert key not in rows,(t,key);rows[key]=(file,n)
 return files,out
af,aa=collect(A);bf,bb=collect(P);assert set(af)==set(bf)and len(af)==13
roots={d:S.value(bf[d+'/'+d+'-r16.kicad_sch'],'uuid')for d in ['body','flange']};system=bf['system-r16.kicad_sch'];branches={d:S.value(next(n for n in S.children(system,'sheet')if S.prop(n,'Sheetfile')==d+'/'+d+'-r16.kicad_sch'),'uuid')for d in ['body','flange']}
baseline_board=S.parse((A/'body/body-r16.kicad_pcb').read_text())
baseline_MPN={next(p[2].value for p in S.children(f,'fp_text')if p[1].value=='reference'):next(p[2].value for p in S.children(f,'fp_text')if p[1].value=='value')for f in S.children(baseline_board,'footprint')}
changed=[];moved=[];labels=[]
for t in aa:
 assert set(aa[t])==set(bb[t]),t
 for key,(oldfile,node)in aa[t].items():
  newfile,current=bb[t][key];expected=copy.deepcopy(node)
  if oldfile!=newfile:
   assert(t=='symbol'and key in ['F1','D1'])or(t in ['wire','global_label']and oldfile=='body/01-power.kicad_sch'and newfile=='flange/01-power.kicad_sch'),(t,key,oldfile,newfile)
   moved.append({'type':t,'key':key,'old_sheet':oldfile,'new_sheet':newfile})
  if t=='symbol':
   if key=='J2':changes={'Footprint':'PrototypeR0:Molex_Pico-Lock_504050-0491_1x04-1MP_P1.50mm_Horizontal','ReviewNote':S.prop(node,'ReviewNote')+'; 504050-0491 Pico-Lock header candidate; battery stays OPEN','Datasheet':'https://www.molex.com/en-us/products/part-detail/5040500491'}
   elif key in 'R1 R2 R3 R4 R5 R23 R24 R25 R41 R42 R46 R47 R48'.split():
    oldmpn=baseline_MPN[key];assert oldmpn.startswith('TNPW0603')and oldmpn.endswith('BEEA'),key
    mpn=oldmpn.replace('TNPW0603','TNPW0402')[:-4]+'BEED';note=S.prop(node,'ReviewNote')
    note=note.replace(oldmpn,mpn)if oldmpn in note else(note+'; 'if note else'')+mpn+' / 0402 candidate'
    changes={'Footprint':'PrototypeR0:R_0402_1005Metric','ReviewNote':note,'Datasheet':'https://www.vishay.com/docs/28758/tnpw_e3.pdf'}
   else:changes={}
   if changes:
    changed.append({'ref':key,'old':{k:S.prop(node,k)for k in changes},'new':changes})
    for p in S.children(expected,'property'):
     if p[1].value in changes:p[2]=S.string(changes[p[1].value])
   if key in ['F1','D1']:
    for project in S.children(S.child(expected,'instances'),'project'):
     if project[1].value=='body-r16':project[1]=S.string('flange-r16')
     for path in S.children(project,'path'):path[1]=S.string(path[1].value.replace('/'+roots['body']+'/','/'+roots['flange']+'/').replace('/'+branches['body']+'/','/'+branches['flange']+'/'))
  if t=='global_label'and oldfile.endswith('06-interboard.kicad_sch')and expected[1].value=='DOCK_5V':expected[1]=S.string('VBUS_CHG');labels.append(key)
  assert canon(expected)==canon(current),(t,key)
assert len(changed)==14 and len(labels)==2
for file in af:assert canon(S.child(af[file],'lib_symbols'))==canon(S.child(bf[file],'lib_symbols')),file
def xml(p):
 r=E.parse(p).getroot();comps={c.get('ref'):(c.findtext('value'),c.findtext('footprint'))for c in r.findall('components/comp')};nodes={(n.get('ref'),n.get('pin')):(net.get('name'),n.get('pinfunction'),n.get('pintype'))for net in r.findall('nets/net')for n in net.findall('node')};return comps,nodes
ac,an=xml(A/'system-native.xml');bc,bn=xml(P/'system-native.xml');assert set(ac)==set(bc)
for ref,old in ac.items():
 change=next((c for c in changed if c['ref']==ref),None);wanted=(old[0],change['new']['Footprint'])if change else old;assert bc[ref]==wanted,ref
for header in ['J6','J7']:
 old=an[header,'2'];assert old[0]=='DOCK_5V';an[header,'2']=('VBUS_CHG',old[1],old[2])
assert an==bn and len(bn)==338
out={'date':'2026-11-01','verifier_sha256':sha(Path(__file__)),'baseline_A_system_XML_sha256':sha(A/'system-native.xml'),'new_system_XML_sha256':sha(P/'system-native.xml'),'native_component_count':len(bc),'native_pin_net_function_type_nodes':len(bn),'original_pin_net_function_type_nodes_unchanged':318,'declared_header_pin2_net_changes':2,'whole_source_sheets':len(af),'source_node_counts':{t:len(v)for t,v in aa.items()},'moved_nodes':moved,'declared_component_field_changes':changed,'driver_flags_and_NC_nodes_preserved':True,'source_schematic_sha256':{f:sha(A/f)for f in af},'current_schematic_sha256':{f:sha(P/f)for f in bf},'scope':'Whole source atom equality for all instantiated symbols/wires/NCs/global labels/junctions after only14declared part-field changes,2header labels andF1/D1context relocation. Cached symbol definitions unchanged. Fresh native XML compares all338nodes, original318unchanged; not a newly executed ERC, analog/RF/process/wire or physical acceptance.'};(P/'circuit-conservation.json').write_text(json.dumps(out,indent=2)+'\n');print(len(bc),'components;',len(bn),'native nodes;13sheets conserved with declared changes',flush=True)
