"""Add native visibility state, preserving every existing archive member."""
from pathlib import Path
import hashlib,json,xml.etree.ElementTree as E,zipfile
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'hardware/cad/simple-assembly-r13/candidate-f';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
f=P/'SimpleAssemblyR13.FCStd';rp=P/'geometry-report.json';r=json.loads(rp.read_text());before=sha(f);assert before==r['native_sha256']
review=json.loads((P/'saved-review.json').read_text());assert review['native_sha256']==before
with zipfile.ZipFile(f)as z:
    assert 'GuiDocument.xml'not in z.namelist()
    names=[o.attrib['name']for o in E.fromstring(z.read('Document.xml')).find('Objects').findall('Object')]
    original={n:hashlib.sha256(z.read(n)).hexdigest()for n in z.namelist()}
(P/'geometry-before-view.json').write_bytes(rp.read_bytes());(P/'saved-review-before-view.json').write_bytes((P/'saved-review.json').read_bytes())
root=E.Element('Document',SchemaVersion='1',HasExpansion='1');E.SubElement(root,'Expand',count='0');vd=E.SubElement(root,'ViewProviderData',Count=str(len(names)))
visible=set(r['parts'])
for rank,n in enumerate(names):
    vp=E.SubElement(vd,'ViewProvider',name=n,expanded='0',treeRank=str(rank));ps=E.SubElement(vp,'Properties',Count='1',TransientCount='0')
    prop=E.SubElement(ps,'Property',name='Visibility',type='App::PropertyBool',status='1');E.SubElement(prop,'Bool',value='true'if n in visible else'false')
with zipfile.ZipFile(f,'a',compression=zipfile.ZIP_DEFLATED)as z:z.writestr('GuiDocument.xml',E.tostring(root,encoding='utf-8',xml_declaration=True))
with zipfile.ZipFile(f)as z:assert all(hashlib.sha256(z.read(n)).hexdigest()==h for n,h in original.items())
r['builder_saved_native_sha256']=before;r['native_sha256']=sha(f)
r['GUI_only_configuration']={'script_sha256':sha(Path(__file__)),'original_archive_entries_sha256':original,'all_original_entries_unchanged':True,'visible_primary_roles':sorted(visible),'hidden':'All source history, superseded budgets, tools and seven nominal mate probes'}
rp.write_text(json.dumps(r,indent=2)+'\n');print('Native visibility configured; every prior geometry/archive member unchanged')
