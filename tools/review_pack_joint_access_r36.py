"""Verify saved access-I source geometry and actual cut, using BRep fast path."""
from pathlib import Path
import hashlib,json,sys,zipfile,xml.etree.ElementTree as ET
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part
ROOT=Path(__file__).resolve().parents[1];P=Path(sys.argv[1]).resolve();H=ROOT/'hardware/cad/pack-sensor-r36/connected-h';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();r=json.loads((P/'access-review.json').read_text());h=json.loads((H/'geometry-report.json').read_text());ip=P/'ServiceablePackSensorsR36.FCStd';hp=H/'ConnectedPackSensorsR36.FCStd';before=sha(ip);source_before=sha(hp);assert before==r['native_sha256']and source_before==r['source_connected_H_sha256']==h['native_sha256'];D=A.openDocument(str(ip));S=A.openDocument(str(hp));D.getObject('ServiceablePackHubR36').touch();D.recompute();fast=[];material=[]
with zipfile.ZipFile(ip)as iz,zipfile.ZipFile(hp)as hz:
 def placements(z):
  root=ET.fromstring(z.read('Document.xml'))
  return {o.get('name'):ET.tostring(o.find("Properties/Property[@name='Placement']"))if o.find("Properties/Property[@name='Placement']")is not None else None for o in root.findall('ObjectData/Object')}
 pi,ps=placements(iz),placements(hz)
 for name in h['fixed_roles']+h['new_roles']:
  member=name+'.Shape.brp'
  if member in iz.namelist()and member in hz.namelist()and iz.read(member)==hz.read(member)and pi[name]==ps[name]:
   fast.append(name);continue
  a=D.getObject(name).Shape.copy();b=S.getObject(name).Shape.copy();assert a.isValid()and b.isValid()
  removed=b.copy().cut(a.copy()).Volume;added=a.copy().cut(b.copy()).Volume
  assert abs(removed)<1e-4 and abs(added)<1e-4,(name,removed,added)
  material.append({'name':name,'removed_mm3':removed,'added_mm3':added})
  print('native material conserved',name,flush=True)
column=D.getObject('ReturnJointServiceColumnR36').Shape.copy();b=column.optimalBoundingBox(False,False);bounds=[getattr(b,k)for k in ['XMin','YMin','ZMin','XMax','YMax','ZMax']];assert max(abs(a-b)for a,b in zip(bounds,r['service_column_xyz_mm']))<1e-6
old=S.getObject('ConnectedSensorWiredRightHubR36').Shape.copy();expected=old.copy().cut(column.copy());current=D.getObject('ServiceablePackHubR36').Shape.copy();assert current.isValid()and len(current.Solids)==1;minus=expected.copy().cut(current.copy()).Volume;plus=current.copy().cut(expected.copy()).Volume;assert abs(minus)<1e-4 and abs(plus)<1e-4
witness=old.copy().common(Part.makeBox(4.,6.,7.,A.Vector(5.6,-14.,4.5)));loss=witness.copy().cut(current.copy()).Volume;assert loss<1e-5
out={'native_sha256':before,'source_H_sha256':source_before,'reviewer_sha256':sha(Path(__file__)),'source_physical_role_count':len(fast)+len(material),'source_BRep_and_placement_byte_matches':fast,'source_exact_material_comparisons':material,'saved_new_hub_matches_source_minus_column':True,'upper_nut_bearing_witness_loss_mm3':loss,'all_source_physical_geometry_conserved':True,'scope':'Source physical shapes preserved in saved I via BRep/placement identity or exact native material comparison; new hub equals source minus declared service column and retains the stated nut-seat region. Generic finite tool-pose result stays separately scoped. No strength, actual solder/tool/process, connected loading or physical acceptance.'};(P/'saved-access-review.json').write_text(json.dumps(out,indent=2)+'\n');A.closeDocument(D.Name);A.closeDocument(S.Name);assert sha(ip)==before and sha(hp)==source_before;print('Service I source roles conserved',len(fast)+len(material),'byte fast path',len(fast),'native fallbacks',len(material),flush=True)
