"""Editable display copy; all non-GUI native archive bytes stay identical."""
from pathlib import Path
import sys,json,hashlib,zipfile,xml.etree.ElementTree as E
P=Path(sys.argv[1]).resolve();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();r=json.loads((P/'geometry-report.json').read_text());f=P/'PackRetentionR32.FCStd';before=sha(f);assert before==r['native_sha256'];hidden={'FlangeCoverLower','FlangeCoverUpper','ButtonServiceCoverR31','ButtonBootR31','ButtonBezelR31','KeyedBodyR25','MotorSeatCapR25','PackSizeGaugeR32'};visible=set(r['parts'])-hidden
with zipfile.ZipFile(f)as z:
 names=[o.attrib['name']for o in E.fromstring(z.read('Document.xml')).find('Objects').findall('Object')];payload=[(i,z.read(i))for i in z.infolist()];original={i.filename:hashlib.sha256(v).hexdigest()for i,v in payload if i.filename!='GuiDocument.xml'}
root=E.Element('Document',SchemaVersion='1',HasExpansion='1');E.SubElement(root,'Expand',count='0');vd=E.SubElement(root,'ViewProviderData',Count=str(len(names)))
for rank,n in enumerate(names):
 vp=E.SubElement(vd,'ViewProvider',name=n,expanded='0',treeRank=str(rank));ps=E.SubElement(vp,'Properties',Count='1',TransientCount='0');prop=E.SubElement(ps,'Property',name='Visibility',type='App::PropertyBool',status='1');E.SubElement(prop,'Bool',value='true'if n in visible else'false')
out=f.with_name('PackRetentionR32-review.FCStd')
with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED)as z:
 for i,v in payload:
  if i.filename!='GuiDocument.xml':z.writestr(i,v)
 z.writestr('GuiDocument.xml',E.tostring(root,encoding='utf-8',xml_declaration=True))
with zipfile.ZipFile(out)as z:assert all(hashlib.sha256(z.read(n)).hexdigest()==h for n,h in original.items())
assert sha(f)==before;out.with_suffix('.json').write_text(json.dumps({'source_native_sha256':before,'review_copy_sha256':sha(out),'configurator_sha256':sha(Path(__file__)),'all_non_GUI_archive_members_unchanged':True,'geometry_archive_entries_sha256':original,'visible_roles':sorted(visible),'scope':'Display-only native copy: outer metal/skins, sizing reservations and pack gauge hidden. Fully editable geometry/history unchanged; no translations.'},indent=2)+'\n');print(out,flush=True)
