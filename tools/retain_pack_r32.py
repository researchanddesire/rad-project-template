"""Pack/dual-NTC retention on current R31; separate one-screw pack lid.

The18x33x6 size gauge is not a battery selection. Source sizing space remains
unchanged and is explicitly distinguished from physical pack/head envelopes.
"""
from pathlib import Path
import sys,json,hashlib,itertools
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'hardware/cad/buttons-r31/candidate-d';OUT=Path(sys.argv[1]).resolve();OUT.mkdir(parents=True,exist_ok=True);assert not any(OUT.iterdir());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text());r=read(SRC/'geometry-report.json');nf=SRC/'ButtonsR31.FCStd';assert sha(nf)==r['native_sha256'];D=A.openDocument(str(nf));old={n:D.getObject(n).Shape.copy()for n in dict(r['parts'],**r['mates'],**r['allowances'])}
def box(n,b):
 x,y,z,u,v,w=b;o=D.addObject('Part::Box',n);o.Length=u-x;o.Width=v-y;o.Height=w-z;o.Placement.Base=A.Vector(x,y,z);return o
def cyl(n,rad,x,y,z,L):
 o=D.addObject('Part::Cylinder',n);o.Radius=rad;o.Height=L;o.Placement=A.Placement(A.Vector(x,y,z),A.Rotation(A.Vector(0,0,1),A.Vector(0,1,0)));return o
def zcyl(n,rad,x,y,z,L):
 o=D.addObject('Part::Cylinder',n);o.Radius=rad;o.Height=L;o.Placement.Base=A.Vector(x,y,z);return o
def fuse(n,ls):
 o=D.addObject('Part::MultiFuse',n);o.Shapes=ls;o.Refine=True;return o
def cut(n,a,b):
 o=D.addObject('Part::Cut',n);o.Base=a;o.Tool=b;o.Refine=True;return o
def common(n,a,b):
 o=D.addObject('Part::Common',n);o.Base=a;o.Tool=b;o.Refine=True;return o
gauge=box('PackSizeGaugeR32',[-9,36,-10,9,69,-4]);gauge.Label='18x33x6 finished-pack SIZE GAUGE / battery OPEN / not supplier maxima or swelling acceptance'
heads=[];stubs=[];films=[];pods=[];windows=[];motions=[];sensors=[]
for i,(x,y)in enumerate([(-2.,44.),(2.,50.)],1):
 z=-11.57
 head=cyl('PackNTCHeadR32_'+str(i),1.5,x,y,z,10);head.Label='TH'+str(i)+' / NTCLE413E2103F524A max3x10 head/entry envelope / not exact profile';heads.append(head)
 lead=[]
 for j,dx in enumerate([-.65,.65],1):
  o=cyl('PackNTCLeadStubR32_'+str(i)+'_'+str(j),.6,x+dx,y-4.5,z,4.5);o.Label='First4.5mm straight factory-lead allowance / OD1.2 candidate / unfinished route';stubs.append(o);lead.append(o.Name)
 film=box('PackNTCContactFilmR32_'+str(i),[x-1,y+1,-10.07,x+1,y+9,-10]);film.Label='0.07mm nominal compliant contact-film PROCESS reservation / bond and conforming contact unqualified';films.append(film)
 # The sensor clearance extends beyond nominal pack freeplay, so a head or
 # its lead is not the first rigid stop. This is not approved pack swelling.
 headmotion=box('PackNTCHeadMotionR32_'+str(i),[x-2.5,y-.7,z-2.4,x+2.5,y+10.7,z+2.4]);leadmotion=box('PackNTCLeadMotionR32_'+str(i),[x-2.15,y-5.2,z-1.4,x+2.15,y+.7,z+1.4]);motion=fuse('PackNTCMotionR32_'+str(i),[headmotion,leadmotion]);motions.append(motion)
 headwindow=box('PackNTCHeadWindowR32_'+str(i),[x-2.6,y-.8,z-2.5,x+2.6,y+10.8,z+2.5]);leadwindow=box('PackNTCLeadWindowR32_'+str(i),[x-2.25,y-5.9,z-1.5,x+2.25,y+.8,z+1.5]);window=fuse('PackNTCWindowR32_'+str(i),[headwindow,leadwindow]);windows.append(window)
 outside=cyl('PackNTCGuardCylinderR32_'+str(i),3.1,x,y-5.8,z,17.4);clip=box('PackNTCGuardLowerLimitR32_'+str(i),[x-3.2,y-5.9,-15,x+3.2,y+11.7,-10.65]);pods.append(common('PackNTCGuardBlankR32_'+str(i),outside,clip))
 sensors.append({'reference':'TH'+str(i),'candidate':'NTCLE413E2103F524A','head_start_xyz_mm':[x,y,z],'head_axis_xyz':[0,1,0],'head_maximum_envelope_diameter_length_mm':[3,10],'first_straight_factory_lead_mm':4.5,'lead_stub_roles':lead,'head_with_attachment_OD_study_mm':3.2,'common_module_positioning_study_plus_minus_xyz_mm':[.5,.5,.5],'sensor_guard_coverage_beyond_pack_freeplay_plus_minus_xyz_mm':[.9,.7,.8],'contact_film_minimum_nominal_mm':.07,'guard_window_extra_per_side_mm':.1,'scope':'Head/entry bounding cylinder, informative factory-lead geometry with larger engineering allowance. Guard coverage is not permitted pack movement or supplier growth qualification. Actual lead OD/pitch, tape/bond, stress/vibration/thermal performance and full adapter routing unqualified.'})
fences=[box('PackRearFenceR32',[-9.8,35,-11.2,9.8,35.4,-3.5]),box('PackFrontFenceR32',[-9.8,69.6,-11.2,9.8,70.,-3.4])]
hoods=[];lipbits=[]
for sign in [-1,1]:
 def span(a,b):return(a,b)if sign>0 else(-b,-a)
 a,b=span(8.3,9.5);lipbits.append(box('PackLidSideRailR32_'+str(sign),[a,34.6,-3.4,b,69.3,-2.0]))
 a,b=span(8.2,10.2);hoods.append(box('PackRearHoodRoofR32_'+str(sign),[a,34.5,-1.9,b,35.8,-1.3]))
 a,b=span(9.6,10.2);hoods.append(box('PackRearHoodWebR32_'+str(sign),[a,34.5,-4.2,b,35.8,-1.3]))
post=zcyl('PackLidPostR32',1.4,-11.2,59.,-8.,5.1);pilot=zcyl('PackLidPilotR32',.625,-11.2,59.,-8.1,5.5);windows.append(pilot)
carrier=cut('PackRetainingCarrierR32',fuse('PackCarrierBlankR32',[D.getObject('TipReadyCarrierR26'),post]+fences+hoods+pods),fuse('PackSensorWindowToolsR32',windows));carrier.Label='Carrier / pack end stops, rear lid hoods, one post and non-contact NTC guards'
lipbits.extend([box('PackLidFrontCrossbarR32',[-9.5,56.4,-3.4,9.5,58.2,-2.0]),box('PackLidRaisedOutboardTieR32',[-12.8,56.4,-2.9,-9.4,59.1,-2.]),zcyl('PackLidScrewTabR32',2.,-11.2,59.,-2.9,.9)])
lid=cut('PackLidR32',fuse('PackLidBlankR32',lipbits),zcyl('PackLidClearanceR32',.9,-11.2,59.,-3.,1.1));lid.Label='Separate pack lid / rear tongues then one M1.6x6 candidate / PCB keeper unchanged'
screw=fuse('PackLidScrewEnvelopeR32',[zcyl('PackLidScrewShankR32',.8,-11.2,59.,-8,6.),zcyl('PackLidScrewHeadR32',1.6,-11.2,59.,-2.,1.6)]);screw.Label='M1.6x6 candidate / D3.2x1.6 head allowance / actual profile and thread unqualified'
D.recompute();replace={'TipReadyCarrierR26':carrier.Name};parts={n:D.getObject(n)for n in r['parts']if n not in set(replace)|{'NarrowPackAllowance'}};new={o.Name:o for o in [carrier,lid,screw,gauge]+heads+stubs+films};parts.update(new);mates={n:D.getObject(n)for n in r['mates']};allowances={n:D.getObject(n)for n in r['allowances']};reservations={'NarrowPackAllowance':D.getObject('NarrowPackAllowance')};reservations.update({o.Name:o for o in motions})
def inv(s):
 b=s.optimalBoundingBox(False,False);return {'valid':s.isValid(),'solids':len(s.Solids),'volume_mm3':s.Volume,'bounds_xyz_mm':[getattr(b,k)for k in ['XMin','YMin','ZMin','XMax','YMax','ZMax']]}
for n,o in new.items():print('new',n,inv(o.Shape),flush=True)
output=OUT/'PackRetentionR32.FCStd';D.Label='R32 / pack and two NTC guards / battery OPEN / DEVELOPMENT';D.saveAs(str(output));out={'native_sha256':sha(output),'source_R31_native_sha256':sha(nf),'source_R31_report_sha256':sha(SRC/'geometry-report.json'),'builder_sha256':sha(Path(__file__)),'parts':{n:inv(o.Shape)for n,o in parts.items()},'mates':r['mates'],'allowances':r['allowances'],'co_moving_size_reservations':{n:inv(o.Shape)for n,o in reservations.items()},'reclassified_source_role':{'NarrowPackAllowance':'Unchanged19x34x7 sizing reservation; not a physical battery. Actual18x33x6 pack-size gauge and co-moving sensor envelopes checked separately. No supplier tolerance/swelling acceptance.'},'replaced_roles':replace,'new_roles':list(new),'sensors':sensors,'new_fasteners':1,'scope':'Conditional prototype size gauge, positive end stops and separate one-screw lid with rear tongues; PCB keeper and motor mount unchanged. Non-contact NTC guards. Cell/pouch/PCM/connector/lead/temperature/growth limits and battery choice OPEN. No supplier pack adoption, fabricated parts, physical retention, thermal response or complete device build claim.'}
conserved={}
for n,a in old.items():
 if n in replace:continue
 b=D.getObject(n).Shape;eq=a.exportBrepToString()==b.exportBrepToString();remove,add=(0.,0.)if eq else(a.copy().cut(b.copy()).Volume,b.copy().cut(a.copy()).Volume);delta=max(abs(x-y)for x,y in zip(inv(a)['bounds_xyz_mm'],inv(b)['bounds_xyz_mm']));assert abs(remove)<1e-4 and abs(add)<1e-4 and delta<1e-5,(n,remove,add,delta);conserved[n]={'exact_BRep_equal':eq,'removed_mm3':remove,'added_mm3':add,'maximum_bounds_delta_mm':delta}
out['source_roles_conserved']=conserved
def vol(a,b):
 u,v=a.BoundBox,b.BoundBox
 if any(min(getattr(u,k+'Max'),getattr(v,k+'Max'))<=max(getattr(u,k+'Min'),getattr(v,k+'Min'))+1e-7 for k in 'XYZ'):return 0.
 return a.copy().common(b.copy()).Volume
base=read(ROOT/'hardware/cad/tip-support-r26/candidate-f/geometry-report.json');named={tuple(sorted(replace.get(n,n)for n in [q['a'],q['b']]))for q in base['named_unqualified_screw_pilot_interfaces']};physical=dict(parts,**mates,**allowances);seen=set();hits=[];interfaces=[];pairs=0
named.add(tuple(sorted([carrier.Name,screw.Name])))
for n,o in new.items():
 bad=[]
 for m,p in physical.items():
  key=tuple(sorted([n,m]))
  if n==m or key in seen:continue
  seen.add(key);pairs+=1;v=vol(o.Shape,p.Shape)
  if v>1e-5:(interfaces if key in named else bad).append({'a':n,'b':m,'intersection_mm3':v})
 hits+=bad;print('static',n,bad,flush=True)
module={o.Name for o in [gauge]+heads+stubs+films};reservehits=[];reservepairs=0
for n,o in reservations.items():
 for m,p in physical.items():
  if m in module:continue
  reservepairs+=1;v=vol(o.Shape,p.Shape)
  if v>1e-5:reservehits.append({'reservation':n,'fixed':m,'intersection_mm3':v})
out.update({'new_pairs_tested':pairs,'unexpected_intersections':hits,'named_unqualified_screw_pilot_interfaces':interfaces,'rigid_vs_module_reservation_pairs':reservepairs,'unexpected_rigid_vs_module_reservation_intersections':reservehits});(OUT/'geometry-report.json').write_text(json.dumps(out,indent=2)+'\n');print('saved',output,'staticunexpected',len(hits),'reservationhits',reservehits,flush=True);A.closeDocument(D.Name);assert sha(nf)==r['native_sha256']
