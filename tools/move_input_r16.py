"""Place input protection beside dock; preserve original electrical nodes.

Move F1/D1 circuit islands and physical footprints to flange. Header pin2
becomes VBUS_CHG on both ends. Both boards still need new native checks.
"""
from pathlib import Path
import sys,shutil,json,hashlib,copy
import pcb_split_r12 as G
import electronics_r0_generate as E
import kicad_sexp as S
K=G.K;ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/'hardware/pcb/route-r16/candidate-h';P=Path(sys.argv[1]).resolve();P.mkdir(parents=True,exist_ok=True);assert not any(P.iterdir());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for p in SOURCE.rglob('*'):
 if p.is_file()and(p.suffix in ['.kicad_pcb','.kicad_pro','.kicad_sch','.kicad_sym','.kicad_mod']or p.name in ['fp-lib-table','sym-lib-table']):
  q=P/p.relative_to(SOURCE);q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)
power={d:S.parse((P/d/'01-power.kicad_sch').read_text())for d in ['body','flange']};roots={d:S.value(S.parse((P/d/(d+'-r16.kicad_sch')).read_text()),'uuid')for d in ['body','flange']};system=S.parse((P/'system-r16.kicad_sch').read_text());branches={d:S.value(next(n for n in S.children(system,'sheet')if S.prop(n,'Sheetfile')==d+'/'+d+'-r16.kicad_sch'),'uuid')for d in ['body','flange']}
ids={E.uid(ref+'.wire.'+pin)for ref in ['F1','D1']for pin in ['1','2']};selected=[];coords=set()
for n in S.children(power['body'],'wire'):
 if S.value(n,'uuid')in ids:
  selected.append(n)
  for xy in S.child(n,'pts')[1:]:coords.add(tuple(float(a.value)for a in xy[1:]))
assert len(selected)==4
selected +=[n for n in S.children(power['body'],'symbol')if S.prop(n,'Reference')in ['F1','D1']]
selected +=[n for n in S.children(power['body'],'global_label')if tuple(float(a.value)for a in S.child(n,'at')[1:3])in coords]
symbols={};moved_nodes=[]
for n in selected:
 power['body'].remove(n);n=copy.deepcopy(n)
 if S.tag(n)=='symbol':
  ref=S.prop(n,'Reference');symbols[ref]=S.value(n,'uuid')
  for project in S.children(S.child(n,'instances'),'project'):
   if project[1].value=='body-r16':project[1]=S.string('flange-r16')
   for path in S.children(project,'path'):path[1]=S.string(path[1].value.replace('/'+roots['body']+'/','/'+roots['flange']+'/').replace('/'+branches['body']+'/','/'+branches['flange']+'/'))
 power['flange'].append(n);moved_nodes.append({'type':S.tag(n),'uuid':S.value(n,'uuid')})
assert set(symbols)=={'F1','D1'}
for d in ['body','flange']:
 S.write(P/d/'01-power.kicad_sch',power[d]);q=P/d/'06-interboard.kicad_sch';root=S.parse(q.read_text());labels=[n for n in S.children(root,'global_label')if n[1].value=='DOCK_5V'];assert len(labels)==1;labels[0][1]=S.string('VBUS_CHG');S.write(q,root)
body=K.LoadBoard(str(P/'body/body-r16.kicad_pcb'));flange=K.LoadBoard(str(P/'flange/flange-r16.kicad_pcb'));removed=[]
for net in ['DOCK_FUSED','VBUS_CHG']:
 if not flange.FindNet(net):flange.Add(K.NETINFO_ITEM(flange,net))
for t in list(flange.GetTracks()):
 if t.GetNetname()=='DOCK_5V':removed.append(str(t.m_Uuid.AsString()));flange.Delete(t)
poses={'F1':(-21.97,-17.2,0),'D1':(-17.18,-17.2,0)}
for ref,(x,y,angle)in poses.items():
 src=next(f for f in body.GetFootprints()if f.GetReference()==ref);name=str(src.GetFPID().GetLibItemName());fp=K.FootprintLoad(str(P/'flange/PrototypeR0.pretty'),name);fp.SetReference(ref);fp.SetValue(src.GetValue());fp.SetFPID(K.LIB_ID('PrototypeR0',name));fp.SetPath(K.KIID_PATH('/'+roots['flange']+'/'+S.value(power['flange'],'uuid')+'/'+symbols[ref]));fp.Reference().SetVisible(False);fp.Value().SetVisible(False)
 for pad in fp.Pads():
  net=next(p.GetNetname()for p in src.Pads()if p.GetNumber()==pad.GetNumber());pad.SetNet(flange.FindNet(net))
 flange.Add(fp);G.pose(fp,x,y,angle,'F');body.Delete(src)
for board,ref in [(body,'J6'),(flange,'J7')]:
 fp=next(f for f in board.GetFootprints()if f.GetReference()==ref);p=next(p for p in fp.Pads()if p.GetNumber()=='2');assert p.GetNetname()=='DOCK_5V';p.SetNet(board.FindNet('VBUS_CHG'))
for domain,b in [('body',body),('flange',flange)]:K.SaveBoard(str(P/domain/(domain+'-r16.kicad_pcb')),b)
out={'date':'2026-11-01','tool_sha256':sha(Path(__file__)),'source_H_body_sha256':sha(SOURCE/'body/body-r16.kicad_pcb'),'source_H_flange_sha256':sha(SOURCE/'flange/flange-r16.kicad_pcb'),'new_body_sha256':sha(P/'body/body-r16.kicad_pcb'),'new_flange_sha256':sha(P/'flange/flange-r16.kicad_pcb'),'moved_native_nodes':moved_nodes,'new_flange_poses':poses,'removed_old_DOCK5V_copper_UUIDs':removed,'header_pin2_change':'J6/J7 DOCK_5V -> VBUS_CHG; F1/D1 original pins/net names remain unchanged','counts':{'body':len(list(body.GetFootprints())),'flange':len(list(flange.GetFootprints()))},'scope':'New physical/electrical partition trial; no original source symbols/wires added or removed. Input protection precedes cable. Flange input rerouting and all native source/pad/DRC/MCAD/cable checks required; unchanged USB not an impedance/RF proof.'};(P/'input-partition.json').write_text(json.dumps(out,indent=2)+'\n');print(out['counts'])
