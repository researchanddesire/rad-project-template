"""Partition the preserved native schematic; add explicit J6/J7 boundary.

Read existing cached symbols/parts/wires. Only instance context, board titles
and explanatory text change; pin/net parity is checked by native XML export.
The full device hierarchy retains off-board tip and pack sensor circuits.
"""
from pathlib import Path
import argparse,copy,hashlib,json,os,re,shutil,uuid
import electronics_r0_generate as G
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/'hardware/pcb/prototype-r0';PCB=ROOT/'hardware/pcb/split-r12/candidate-i'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
NS=uuid.UUID('fc19f3fe-fd14-43d3-ab89-ff643b254c42');uid=lambda s:str(uuid.uuid5(NS,s))
class Atom:
    def __init__(self,raw):self.raw=raw;self.value=json.loads(raw)if raw.startswith('"')else raw
def atom(s):return Atom(str(s))
def string(s):return Atom(json.dumps(str(s),ensure_ascii=False))
def parse(text):
    tokens=re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^()\s]+',text);stack=[];root=None
    for t in tokens:
        if t=='(':
            n=[]
            if stack:stack[-1].append(n)
            stack.append(n)
        elif t==')':
            n=stack.pop()
            if not stack:assert root is None;root=n
        else:stack[-1].append(Atom(t))
    assert not stack and root;return root
def tag(n):return n[0].value if isinstance(n,list)and n and isinstance(n[0],Atom)else''
def children(n,t):return[v for v in n if isinstance(v,list)and tag(v)==t]
def child(n,t):return next((v for v in n if isinstance(v,list)and tag(v)==t),None)
def value(n,t):
    c=child(n,t);return c[1].value if c else None
def dump(n,depth=0):
    if isinstance(n,Atom):return n.raw
    flat='('+' '.join(dump(v,99)if isinstance(v,list)else v.raw for v in n)+')'if depth<99 else '('+' '.join(dump(v,99)for v in n)+')'
    if depth>=99 or len(flat)<155:return flat
    return '('+'\n' .join(('  '*(depth+1)if i else'')+dump(v,depth+1)for i,v in enumerate(n))+')'
def named_property(n,name):return next((v[2].value for v in children(n,'property')if v[1].value==name),None)
def write(p,n):p.write_text(dump(n)+'\n')
def instance(project,path,ref=None,page=None):
    extra=f'(reference {json.dumps(ref)})(unit 1)'if ref else f'(page {json.dumps(str(page))})'
    return parse(f'(project {json.dumps(project)}(path {json.dumps(path)} {extra}))')
def patch_symbol(n,domain,leaf,system):
    ref=named_property(n,'Reference');n=copy.deepcopy(n)
    contexts=[]
    if domain in ['body','flange']:contexts.append(instance(domain+'-r14','/'+uid(domain+'-root')+'/'+leaf,ref=ref))
    contexts.append(instance('system-r14','/'+uid('system-root')+('/'+uid('system-'+domain)if domain in ['body','flange']else'')+'/'+leaf,ref=ref))
    old=child(n,'instances')
    if old:n.remove(old)
    n.append([atom('instances')]+contexts)
    return n

def selected_sheet(source_name,refs,domain,leaf,title,system):
    src=parsed[source_name];nodes=[];wire_ids=set();nc_ids=set()
    for ref in refs:
        for pin in manifest[ref]['pins']:
            wire_ids.add(G.uid(ref+'.wire.'+pin));nc_ids.add(G.uid(ref+'.nc.'+pin))
    wires=[copy.deepcopy(n)for n in children(src,'wire')if value(n,'uuid')in wire_ids]
    coords={tuple(float(a.value)for a in xy[1:])for w in wires for xy in child(w,'pts')[1:]}
    for n in src[1:]:
        t=tag(n)
        if t=='symbol'and named_property(n,'Reference')in refs:nodes.append(patch_symbol(n,domain,leaf,system))
        elif t=='wire'and value(n,'uuid')in wire_ids:nodes.append(copy.deepcopy(n))
        elif t=='no_connect'and value(n,'uuid')in nc_ids:nodes.append(copy.deepcopy(n))
        elif t=='global_label':
            at=child(n,'at');point=tuple(float(v.value)for v in at[1:3])
            if point in coords:nodes.append(copy.deepcopy(n))
    assert len(children([atom('root')]+nodes,'symbol'))==len(refs),(source_name,refs)
    notes=f'{title} / partitioned native R0 circuit; physical placement R12I. No fabrication or operating release.'
    return frame(leaf,title,copy.deepcopy(child(src,'lib_symbols')),nodes,notes,source_name=='01-power')
def frame(identity,title,lib,nodes,notes,a2=False):
    base=parse(f'(kicad_sch(version 20230121)(generator split_schematic_r14)(uuid {identity})(paper "{"A2"if a2 else"A3"}")(title_block(title {json.dumps(title)})(date "2026-11-01")(rev "R14 candidate")(company "Research and Desire")(comment 1 "UNROUTED / REVIEW ONLY"))(lib_symbols)(sheet_instances(path "/"(page "1"))))')
    base.remove(child(base,'lib_symbols'));base.insert(6,lib)
    base.extend(nodes)
    base.append(parse(f'(text {json.dumps(notes)}(at 15.24 15.24 0){G.effects(1.524,"(justify left top)")}(uuid {uid(identity+notes)}))'))
    return base
def root_schematic(domain,leaves):
    rootid=uid(domain+'-root');nodes=[]
    for i,(name,leaf,title)in enumerate(leaves):
        x=25.4+(i%2)*190.5;y=76.2+(i//2)*63.5
        n=parse(f'(sheet(at {x} {y})(size 160.02 35.56)(stroke(width 0.254)(type default))(fill(color 0 0 0 0))(uuid {leaf})(property "Sheetname" {json.dumps(title)}(at {x} {y-2.54} 0){G.effects(1.27,"(justify left)")})(property "Sheetfile" {json.dumps(name)}(at {x} {y+38.1} 0){G.effects(1.27,"(justify left)")})(instances))')
        page=[2,8,12,13][i]if domain=='system'else i+2
        contexts=[instance(domain+'-r14','/'+rootid,page=page)]
        if domain in ['body','flange']:contexts.append(instance('system-r14','/'+uid('system-root')+'/'+uid('system-'+domain),page=(i+3 if domain=='body'else i+9)))
        child(n,'instances').extend(contexts);nodes.append(n)
    note=('Full-device circuit: body and flange boards connected by explicitly numbered J6/J7. Remote tip and two pack sensors remain separate. Numeric cable mapping is mandatory; wire/current/fault/strain/RF and operating checks remain open.'if domain=='system'else domain.title()+' board only. Use system-r14.kicad_sch for complete-device ERC and cross-board sources. Board-alone ERC can lack the other board drivers. No added driver flags or suppressed electrical checks. JP1 remains OPEN; firmware motor locked.')
    return frame(rootid,'Buttplug R14 / '+domain,[atom('lib_symbols')],nodes,note)

ap=argparse.ArgumentParser();ap.add_argument('directory',type=Path);args=ap.parse_args();OUT=args.directory.resolve();OUT.mkdir(parents=True,exist_ok=True)
assert not list(OUT.rglob('*.kicad_sch')),'Preserve executed schematic attempts'
source_hashes={p.name:sha(p)for p in SOURCE.glob('*.kicad_sch')};source_hashes['candidate-pin-manifest.json']=sha(SOURCE/'candidate-pin-manifest.json')
manifest={p['ref']:p for p in json.loads((SOURCE/'candidate-pin-manifest.json').read_text())['parts']}
allocation=json.loads((ROOT/'hardware/design/body-flange-partition-r9/partition.json').read_text())['allocation']
parsed={p.stem:parse(p.read_text())for p in sorted(SOURCE.glob('*.kicad_sch'))if p.stem!='buttplug-r0'}
G.connector('Conn10',10);pinmap={str(i+1):n for i,n in enumerate(['GND','DOCK_5V','3V3','PACK_P','MOTOR_ARM','MOTOR_PWM','DOCK_PRESENT_N','I2C_SDA','I2C_SCL','ACCEL_INT_N'])}
newlib=G.LIB['Conn10']['text'];symtext=(SOURCE/'PrototypeR0.kicad_sym').read_text().rstrip();assert symtext.endswith(')');symtext=symtext[:-1]+newlib+'\n)\n'
paths={};project_files={};roots={}
for domain,newref in [('body','J6'),('flange','J7')]:
    folder=OUT/domain;folder.mkdir();leaves=[];refs={r for r,a in allocation.items()if a==domain}
    if domain=='body':refs|={'#FLG01','#FLG02'}
    for name,template in parsed.items():
        keep={r for r in refs if manifest[r]['sheet']==name}
        if not keep:continue
        leaf=value(template,'uuid');title=domain.title()+' / '+{'01-power':'dock and power interfaces','02-motor':'regulated motor and inhibit','03-control':'radio, local controls and service','04-sensors':'motion and tip connector','05-charge-guard':'independent charge permission'}[name]
        n=selected_sheet(name,keep,domain,leaf,title,'system-r14');filename=name+'.kicad_sch';write(folder/filename,n);leaves.append((filename,leaf,title))
        for s in children(n,'symbol'):
            ref=named_property(s,'Reference')
            if ref in allocation:paths[ref]={'domain':domain,'path':'/'+uid(domain+'-root')+'/'+leaf+'/'+value(s,'uuid')}
    G.PROJECT=domain+'-r14';G.OUT=folder;G.PARTS=[]
    sh=G.Sheet('06-interboard',domain+' / interboard connector');sh.part('Conn10',newref,'SM10B-SRSS-TB candidate',101.6,88.9,pinmap,footprint='PrototypeR0:JST_SH_SM10B-SRSS-TB_1x10-1MP_P1.00mm_Horizontal',note='Passive numeric header; not an active source. Match every pin to the other board; harness is unqualified.')
    leaf=uid(domain+'-interboard');nodes=[]
    for text in sh.content:
        n=parse(text)
        if tag(n)=='symbol':n=patch_symbol(n,domain,leaf,'system-r14');paths[newref]={'domain':domain,'path':'/'+uid(domain+'-root')+'/'+leaf+'/'+value(n,'uuid')}
        nodes.append(n)
    lib=parse('(lib_symbols '+newlib.replace('(symbol "Conn10"','(symbol "PrototypeR0:Conn10"',1)+')')
    n=frame(leaf,domain.title()+' / interboard J6–J7 numeric mapping',lib,nodes,'Ten passive connector pins. Actual mate orientation, wires, current/return/fault and supported bends remain to qualify.')
    write(folder/'06-interboard.kicad_sch',n);leaves.append(('06-interboard.kicad_sch',leaf,'Interboard connection'))
    roots[domain]=leaves;write(folder/(domain+'-r14.kicad_sch'),root_schematic(domain,leaves))
    shutil.copytree(PCB/'PrototypeR0.pretty',folder/'PrototypeR0.pretty')
    (folder/'PrototypeR0.kicad_sym').write_text(symtext)
    (folder/'sym-lib-table').write_text('(sym_lib_table(lib(name "PrototypeR0")(type "KiCad")(uri "${KIPRJMOD}/PrototypeR0.kicad_sym")(options "")(descr "Preserved R0 symbols plus passive interboard header")))\n')
    (folder/'fp-lib-table').write_text('(fp_lib_table(lib(name "PrototypeR0")(type "KiCad")(uri "${KIPRJMOD}/PrototypeR0.pretty")(options "")(descr "Unchanged R12 footprints")))\n')
    pro=json.loads((PCB/(domain+'-r12.kicad_pro')).read_text());pro['meta']['filename']=domain+'-r14.kicad_pro';pro.setdefault('erc',{})['erc_exclusions']=[]
    (folder/(domain+'-r14.kicad_pro')).write_text(json.dumps(pro,indent=2)+'\n');project_files[domain]=len(refs-{'#FLG01','#FLG02'})+1

# Full-device circuit adds the original off-board tip and cell sensor symbols.
system_leaves=[(domain+'/'+domain+'-r14.kicad_sch',uid('system-'+domain),domain.title()+' electronics')for domain in ['body','flange']]
for name,refs in [('04-sensors',{'J101','U101','C101'}),('05-charge-guard',{'TH1','TH2'})]:
    leaf=uid('external-'+name);title='Remote tip'if name=='04-sensors'else'Cell-coupled dual NTCs';n=selected_sheet(name,refs,'external',leaf,title,'system-r14');filename='external-'+name+'.kicad_sch';write(OUT/filename,n);system_leaves.append((filename,leaf,title))
write(OUT/'system-r14.kicad_sch',root_schematic('system',system_leaves))
(OUT/'PrototypeR0.kicad_sym').write_text(symtext);shutil.copyfile(OUT/'body/sym-lib-table',OUT/'sym-lib-table')
(OUT/'fp-lib-table').write_text('(fp_lib_table(lib(name "PrototypeR0")(type "KiCad")(uri "${KIPRJMOD}/body/PrototypeR0.pretty")(options "")(descr "System review; physical boards are separate")) (lib(name "TipR1")(type "KiCad")(uri "${KIPRJMOD}/../../tip-r1/TipR1.pretty")(options "")(descr "Preserved remote tip")))\n')
pro=json.loads((SOURCE/'buttplug-r0.kicad_pro').read_text());pro['meta']['filename']='system-r14.kicad_pro';pro.setdefault('erc',{})['erc_exclusions']=[];(OUT/'system-r14.kicad_pro').write_text(json.dumps(pro,indent=2)+'\n')
out={'date':'2026-11-01','generator_sha256':sha(Path(__file__)),'source_schematics_sha256':source_hashes,'source_symbol_library_sha256':sha(SOURCE/'PrototypeR0.kicad_sym'),'board_instances':paths,'board_counts':project_files,'connector_pinmap':pinmap,'scope':'Native R0 instances/wires partitioned without changed pin assignments; two new passive headers. Full-device hierarchy retains remote circuits. Native XML parity/ERC and PCB-instance rebinding still pending.'}
(OUT/'partition-source.json').write_text(json.dumps(out,indent=2)+'\n')
assert all(sha(SOURCE/name)==h for name,h in source_hashes.items());print(json.dumps({'board_counts':project_files,'linked_instances':len(paths),'source_symbols':len(manifest)},indent=2))
