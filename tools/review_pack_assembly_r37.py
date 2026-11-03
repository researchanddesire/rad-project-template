"""Read-only review of saved R37 carrier and conditional power geometry."""
from pathlib import Path
import hashlib,itertools,json,sys,zipfile,xml.etree.ElementTree as ET
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'hardware/cad/pack-assembly-r37'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
bp=P/'body-anchor-b/PackBodyAnchorR37.FCStd';fp=P/'power-f/ConditionalPackPowerR37.FCStd'
br=json.loads((bp.parent/'geometry-report.json').read_text());fr=json.loads((fp.parent/'geometry-report.json').read_text())
assert sha(bp)==br['native_sha256']==fr['source_body_anchor_B_sha256'] and sha(fp)==fr['native_sha256']
source=ROOT/'hardware/cad/pack-sensor-r36/access-i/ServiceablePackSensorsR36.FCStd'
assert sha(source)==br['source_R36I_sha256']
S=A.openDocument(str(source));B=A.openDocument(str(bp));F=A.openDocument(str(fp))
def volume(s):return 0. if s.isNull() else s.Volume
def equal(a,b):
 assert a.isValid() and b.isValid()
 minus=volume(a.copy().cut(b.copy()));plus=volume(b.copy().cut(a.copy()))
 assert max(abs(minus),abs(plus))<1e-4,(minus,plus)
 return {'removed_mm3':minus,'added_mm3':plus}
def overlap(a,b):
 u,v=a.BoundBox,b.BoundBox
 if any(min(getattr(u,k+'Max'),getattr(v,k+'Max'))<=max(getattr(u,k+'Min'),getattr(v,k+'Min'))+1e-7 for k in 'XYZ'):return 0.
 return volume(a.copy().common(b.copy()))
def conserve(old,new,names,oldpath,newpath):
 fast=[];material=[]
 with zipfile.ZipFile(oldpath)as oz,zipfile.ZipFile(newpath)as nz:
  def poses(z):
   root=ET.fromstring(z.read('Document.xml'))
   return {o.get('name'):ET.tostring(o.find("Properties/Property[@name='Placement']")) if o.find("Properties/Property[@name='Placement']")is not None else None for o in root.findall('ObjectData/Object')}
  op,np=poses(oz),poses(nz)
  for n in dict.fromkeys(names):
   member=n+'.Shape.brp'
   if member in oz.namelist()and member in nz.namelist()and oz.read(member)==nz.read(member)and op[n]==np[n]:fast.append(n)
   else:material.append({'name':n,**equal(old.getObject(n).Shape.copy(),new.getObject(n).Shape.copy())})
 return {'count':len(fast)+len(material),'BRep_and_placement_matches':fast,'native_material_comparisons':material}
rr=json.loads((source.parent/'access-review.json').read_text())
hr=json.loads((ROOT/'hardware/cad/pack-sensor-r36/connected-h/geometry-report.json').read_text())
source_roles=[n for n in hr['fixed_roles']+hr['new_roles'] if n!='ConnectedSensorWiredRightHubR36']+['ServiceablePackHubR36']
anchor_source=conserve(S,B,source_roles,source,bp);print('anchor source roles',anchor_source['count'],flush=True)
expected=B.getObject('PackWireCarrierBlankR37').Shape.copy().cut(B.getObject('PackAnchorCutToolsR37').Shape.copy())
carrier_equality=equal(expected,B.getObject('PackAnchoredCarrierR37').Shape.copy())
power_source=conserve(B,F,br['fixed_roles']+list(br['new_roles']),bp,fp);print('power source roles',power_source['count'],flush=True)
hub_equal={}
for n,q in fr['hub_changes'].items():
 expected=B.getObject(n).Shape.copy().cut(F.getObject('PackPowerClearanceToolsR37').Shape.copy())
 hub_equal[n]=equal(expected,F.getObject(q['replacement']).Shape.copy())
# All five actual installed wire jackets retain the same under-board anchor
# section, including the two power paths which were extended only at the flange.
clip=Part.makeBox(30,2.2,20,A.Vector(-15,34.9,-15));contacts=[]
for before,after in [('PackConnectedWireR36_1','BodyPackPowerWireR37_1'),('SensorReturnCoatingR36','SensorReturnCoatingR36'),('PackConnectedWireR36_3','BodyPackPowerWireR37_2'),('PackConnectedWireR36_4','PackConnectedWireR36_4'),('PackConnectedWireR36_5','PackConnectedWireR36_5')]:
 a=B.getObject(before).Shape.copy().common(clip.copy());b=F.getObject(after).Shape.copy().common(clip.copy());assert a.Volume>0
 equal(a,b);row={'wire':after,'anchor_section_conserved':True}
 for target in ['PackWireSoftPadR37','PackTieBandSpaceR37']:
  t=F.getObject(target).Shape.copy();gap=b.distToShape(t)[0];ov=overlap(b,t)
  assert gap<1e-5 and ov<1e-5,(after,target,gap,ov)
  row[target]={'nominal_gap_mm':gap,'intersection_mm3':ov}
 contacts.append(row)
print('five jackets touch pad and band; anchor sections conserved',flush=True)
# Re-read every new/fixed shape from the saved native file. Only exact pairwise
# interfaces declared by the builder are allowed; no blanket name exemption.
allowed={frozenset([q['a'],q['b']])for q in fr['named_process_interfaces']}
new={n:F.getObject(n).Shape.copy()for n in fr['new_roles']};fixed={n:F.getObject(n).Shape.copy()for n in fr['fixed_roles']};hits=[];count=0
for n,a in new.items():
 assert a.isValid()and len(a.Solids)==1,n
 for m,b in fixed.items():
  count+=1;v=overlap(a,b)
  if v>1e-5:hits.append({'a':n,'b':m,'mm3':v})
for(n,a),(m,b)in itertools.combinations(new.items(),2):
 count+=1;v=overlap(a,b)
 if v>1e-5 and frozenset([n,m])not in allowed:hits.append({'a':n,'b':m,'mm3':v})
assert not hits,hits
cores=[]
for q in fr['bare_core_pairs']:
 a=F.getObject(q['factory_core']).Shape.copy();b=F.getObject(q['body_core']).Shape.copy();s=F.getObject(q['solder_bridge']).Shape.copy()
 gap=a.distToShape(b)[0];assert gap>=.09999 and overlap(a,b)<1e-5
 assert s.distToShape(a)[0]<1e-5 and s.distToShape(b)[0]<1e-5 and overlap(s,a)<1e-5 and overlap(s,b)<1e-5
 cores.append({'pin':q['pin'],'bare_gap_mm':gap,'solder_target_touches_both_separate_cores':True})
out={'source_R36I_sha256':sha(source),'body_anchor_B_sha256':sha(bp),'power_F_sha256':sha(fp),'reviewer_sha256':sha(Path(__file__)),'anchor_source_conservation':anchor_source,'carrier_equals_declared_fuse_minus_tools':carrier_equality,'power_source_conservation':power_source,'hub_equals_source_minus_declared_tools':hub_equal,'five_wire_anchor_contacts':contacts,'saved_power_static_pairs':count,'unexpected_intersections':hits,'power_core_checks':cores,'all_saved_checks_pass':True,'scope':'Independent saved-native conservation, exact declared cuts, five nominal wire-to-pad/band contacts, conditional power static geometry and separate lap cores. Does not qualify tie force, received connector/lead dimensions, connected loading, strength, current, sealing or physical assembly.'}
(P/'saved-review.json').write_text(json.dumps(out,indent=2)+'\n')
for d in [S,B,F]:A.closeDocument(d.Name)
assert sha(bp)==br['native_sha256'] and sha(fp)==fr['native_sha256'] and sha(source)==br['source_R36I_sha256']
print('SAVED R37 review pass',count,'power comparisons',flush=True)
