"""Editable display copies; canonical native/check files stay unchanged."""
from pathlib import Path
import sys,json,hashlib,zipfile,xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1];P=Path(sys.argv[1]).resolve();mode=sys.argv[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
if mode=='support':
 f=P/'HarnessSupportR30.FCStd';r=json.loads((P/'geometry-report.json').read_text());visible=set(r['parts'])-{'FlangeCoverLower','FlangeCoverUpper','ServiceCoverReference','KeyedBodyR25','MotorSeatCapR25'}
else:
 f=P/'ParkedHarnessR30.FCStd';r=json.loads((P/'parking-review.json').read_text());s=json.loads((ROOT/'hardware/cad/harness-support-r30/candidate-b/geometry-report.json').read_text());r27=json.loads((ROOT/'hardware/cad/flange-controls-r27/candidate-d/geometry-report.json').read_text());exclude=set(r27['inverse_transformed_flange_roles'])|{'FlangeCoverLower','FlangeCoverUpper','ServiceCoverReference','KeyedBodyR25','MotorSeatCapR25','FlangeAnchorPadR30','HarnessKeeperR30','FlangeKeeperScrewEnvelopeR27'};visible={n for n in s['parts']if n not in exclude and not n.startswith('InterboardWireR29_')}|{q['role']for q in r['wires']}
before=sha(f);assert before==r['native_sha256']
with zipfile.ZipFile(f)as z:
 names=[o.attrib['name']for o in E.fromstring(z.read('Document.xml')).find('Objects').findall('Object')];payload=[(i,z.read(i))for i in z.infolist()];original={i.filename:hashlib.sha256(v).hexdigest()for i,v in payload if i.filename!='GuiDocument.xml'}
root=E.Element('Document',SchemaVersion='1',HasExpansion='1');E.SubElement(root,'Expand',count='0');vd=E.SubElement(root,'ViewProviderData',Count=str(len(names)))
for rank,n in enumerate(names):
 vp=E.SubElement(vd,'ViewProvider',name=n,expanded='0',treeRank=str(rank));ps=E.SubElement(vp,'Properties',Count='1',TransientCount='0');prop=E.SubElement(ps,'Property',name='Visibility',type='App::PropertyBool',status='1');E.SubElement(prop,'Bool',value='true'if n in visible else'false')
out=f.with_name(f.stem+'-review.FCStd')
with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED)as z:
 for i,v in payload:
  if i.filename!='GuiDocument.xml':z.writestr(i,v)
 z.writestr('GuiDocument.xml',E.tostring(root,encoding='utf-8',xml_declaration=True))
with zipfile.ZipFile(out)as z:assert all(hashlib.sha256(z.read(n)).hexdigest()==h for n,h in original.items())
assert sha(f)==before
proof={'source_native_sha256':before,'review_copy_sha256':sha(out),'configurator_sha256':sha(Path(__file__)),'geometry_archive_entries_sha256':original,'all_non_GUI_archive_members_unchanged':True,'visible_roles':sorted(visible),'scope':'Display-only fully editable copy. Canonical source and checks remain unchanged; exact non-GUI archive payload preserved. Display omits covers/metal and stage-waiting or superseded objects; no geometry translations.'};out.with_suffix('.json').write_text(json.dumps(proof,indent=2)+'\n');print(out,flush=True)
