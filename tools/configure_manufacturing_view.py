"""Hide construction stock/cutters in the native manufacturing-study view.

Only GuiDocument.xml changes; all geometry archive entries are checked unchanged.
"""
from pathlib import Path
import hashlib,json,sys,zipfile
import xml.etree.ElementTree as E
folder=Path(sys.argv[1]).resolve();native=folder/'ManufacturingLayout.FCStd';review=folder/'review.json';r=json.loads(review.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();before=sha(native);assert before==r['native_sha256']
with zipfile.ZipFile(native)as z:
 payload=[(i,z.read(i))for i in z.infolist()];tree=E.fromstring(z.read('Document.xml'));names=[o.get('name')for o in tree.findall('Objects/Object')]
# Real final parts and references only: never display raw stock, cavities or cutters.
visible=set(r['native_object_names'].values())|{'ProductParts','ComponentReferences','StandardSoftGoods'}
for o in tree.findall('ObjectData/Object'):
 if o.get('name')in {'ComponentReferences','StandardSoftGoods'}:
  for link in o.findall("Properties/Property[@name='Group']/LinkList/Link"):visible.add(link.get('value'))
gui=E.Element('Document',SchemaVersion='1',HasExpansion='1');E.SubElement(gui,'Expand',count='0');data=E.SubElement(gui,'ViewProviderData',Count=str(len(names)))
for rank,name in enumerate(names):
 vp=E.SubElement(data,'ViewProvider',name=name,expanded='0',treeRank=str(rank));props=E.SubElement(vp,'Properties',Count='1',TransientCount='0');p=E.SubElement(props,'Property',name='Visibility',type='App::PropertyBool',status='1');E.SubElement(p,'Bool',value='true'if name in visible else'false')
pending=native.with_suffix('.view-tmp')
with zipfile.ZipFile(pending,'w',compression=zipfile.ZIP_DEFLATED)as z:
 for info,blob in payload:
  if info.filename!='GuiDocument.xml':z.writestr(info,blob)
 z.writestr('GuiDocument.xml',E.tostring(gui,encoding='utf-8',xml_declaration=True))
with zipfile.ZipFile(pending)as z:assert all(z.read(i.filename)==b for i,b in payload if i.filename!='GuiDocument.xml')
pending.replace(native);r['geometry_checked_native_sha256_before_view']=before;r['native_sha256']=sha(native);r['view_configuration']={'configurator_sha256':sha(Path(__file__)),'all_non_GUI_archive_entries_unchanged':True,'visible_objects':sorted(visible),'construction_stock_and_cutters_hidden':True};review.write_text(json.dumps(r,indent=2)+'\n');print('Native view configured; geometry unchanged')
