"""Sample which encounters frame first: rigid size gauge or sensor assembly.

Use a3.2mm head+attachment allowance, not the bare3mm coating alone. These
are rigid nominal probes; no pouch deformation or load rating is implied.
"""
from pathlib import Path
import sys,json,hashlib
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part
P=Path(sys.argv[1]).resolve();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();r=json.loads((P/'geometry-report.json').read_text());nf=P/'PackRetentionR32.FCStd';before=sha(nf);assert before==r['native_sha256'];D=A.openDocument(str(nf));frame={n:D.getObject(n).Shape.copy()for n in ['PackRetainingCarrierR32','PackLidR32']};gauge=D.getObject('PackSizeGaugeR32').Shape.copy();sensors={}
for q in r['sensors']:
 x,y,z=q['head_start_xyz_mm'];sensors[q['reference']+'_head_and_attachment_D3_2']=Part.makeCylinder(1.6,10,A.Vector(x,y,z),A.Vector(0,1,0))
 for n in q['lead_stub_roles']:sensors[n]=D.getObject(n).Shape.copy()
for n in r['new_roles']:
 if n.startswith('PackNTCContactFilmR32_'):sensors[n]=D.getObject(n).Shape.copy()
def vol(a,b):
 u,v=a.BoundBox,b.BoundBox
 if any(min(getattr(u,k+'Max'),getattr(v,k+'Max'))<=max(getattr(u,k+'Min'),getattr(v,k+'Min'))+1e-7 for k in 'XYZ'):return 0.
 return a.copy().common(b.copy()).Volume
rows=[]
for axis in range(3):
 for sign in [-1,1]:
  samples=[];firstg=None;firsts=None
  for i in range(25):
   t=i*.05;d=[0,0,0];d[axis]=sign*t;g=gauge.copy();g.translate(A.Vector(*d));gs=[{'frame':n,'intersection_mm3':v}for n,b in frame.items()if(v:=vol(g,b))>1e-5];ss=[]
   for n,a in sensors.items():
    a=a.copy();a.translate(A.Vector(*d))
    for m,b in frame.items():
     v=vol(a,b)
     if v>1e-5:ss.append({'sensor':n,'frame':m,'intersection_mm3':v})
   if gs and firstg is None:firstg=t
   if ss and firsts is None:firsts=t
   samples.append({'translation_mm':t,'gauge_contacts':gs,'sensor_contacts':ss})
   if firstg is not None and firsts is not None:break
  gap=None
  if firstg is not None:
   d=[0,0,0];d[axis]=sign*firstg;dist=[]
   for a in sensors.values():
    a=a.copy();a.translate(A.Vector(*d));dist.extend(a.distToShape(b)[0]for b in frame.values())
   gap=min(dist)
  accepted=firstg is not None and(firsts is None or firsts-.05>=firstg-1e-9)and gap is not None and gap>=.05
  row={'axis':'XYZ'[axis],'sign':sign,'first_sampled_gauge_intersection_travel_mm':firstg,'first_sampled_sensor_intersection_travel_mm':firsts,'sensor_minimum_native_gap_at_first_gauge_sample_mm':gap,'gauge_encounter_precedes_sensor_with_study_margin':accepted,'samples':samples};rows.append(row);print('freeplay','XYZ'[axis],sign,'gauge',firstg,'sensor',firsts,'gap',gap,'pass',accepted,flush=True)
A.closeDocument(D.Name);assert sha(nf)==before;out={'native_sha256':before,'geometry_report_sha256':sha(P/'geometry-report.json'),'reviewer_sha256':sha(Path(__file__)),'sample_step_mm':.05,'maximum_sampled_translation_mm':1.2,'head_attachment_envelope_diameter_mm':3.2,'included_sensor_and_process_roles':list(sensors),'minimum_gap_study_target_mm':.05,'rows':rows,'all_six_translation_probes_keep_sensors_out_of_first_contact':all(q['gauge_encounter_precedes_sensor_with_study_margin']for q in rows),'scope':'Finite0.05mm rigid translation samples. First gauge intersection sample intentionally slightly penetrates frame; sensor clearance measured there. Includes contact-film process boxes, head+attachment envelopes and first4.5mm lead stubs. Not continuous contact ordering, rotation/deformation/soft-pouch motion, actual cured bond/tape, load/stress, attachment retention or vibration qualification.'};(P/'freeplay-review.json').write_text(json.dumps(out,indent=2)+'\n');print('freeplay probes pass',out['all_six_translation_probes_keep_sensors_out_of_first_contact'],flush=True)
