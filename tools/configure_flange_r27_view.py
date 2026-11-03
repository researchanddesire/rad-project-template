"""Show current primary CAD roles; preserve every geometry archive member."""
from pathlib import Path
import sys,json,hashlib,zipfile,xml.etree.ElementTree as E
P=Path(sys.argv[1]).resolve();f=P/'FlangeCradleR27.FCStd';rp=P/'geometry-report.json';r=json.loads(rp.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();before=sha(f);assert before==r['native_sha256']
with zipfile.ZipFile(f)as z:
 names=[o.attrib['name']for o in E.fromstring(z.read('Document.xml')).find('Objects').findall('Object')];payload=[(i,z.read(i))for i in z.infolist()];original={i.filename:hashlib.sha256(v).hexdigest()for i,v in payload if i.filename!='GuiDocument.xml'}
root=E.Element('Document',SchemaVersion='1',HasExpansion='1');E.SubElement(root,'Expand',count='0');vd=E.SubElement(root,'ViewProviderData',Count=str(len(names)));visible=(set(r['parts'])|set(r['allowances']))-{'FlangeCoverUpper','ServiceCoverReference','KeyedBodyR25','MotorSeatCapR25','TipStrainReliefProcessAllowanceR26'}
for rank,n in enumerate(names):
 vp=E.SubElement(vd,'ViewProvider',name=n,expanded='0',treeRank=str(rank));ps=E.SubElement(vp,'Properties',Count='1',TransientCount='0');prop=E.SubElement(ps,'Property',name='Visibility',type='App::PropertyBool',status='1');E.SubElement(prop,'Bool',value='true'if n in visible else'false')
tmp=f.with_suffix('.view-tmp')
with zipfile.ZipFile(tmp,'w',compression=zipfile.ZIP_DEFLATED)as z:
 for i,v in payload:
  if i.filename!='GuiDocument.xml':z.writestr(i,v)
 z.writestr('GuiDocument.xml',E.tostring(root,encoding='utf-8',xml_declaration=True))
with zipfile.ZipFile(tmp)as z:assert all(hashlib.sha256(z.read(n)).hexdigest()==h for n,h in original.items())
tmp.replace(f);(P/'geometry-before-view.json').write_bytes(rp.read_bytes());r['builder_saved_native_sha256']=before;r['native_sha256']=sha(f);r['GUI_only_configuration']={'script_sha256':sha(Path(__file__)),'geometry_archive_entries_sha256':original,'all_geometry_archive_entries_unchanged':True,'visible_roles':sorted(visible)};rp.write_text(json.dumps(r,indent=2)+'\n');print('R27 current internals visible; geometry entries unchanged',flush=True)
