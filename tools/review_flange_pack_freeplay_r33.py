"""Sample rigid gauge stops before sensor or outside-cover contact; R33."""
from pathlib import Path
import sys,json,hashlib,itertools
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part
P=Path(sys.argv[1]).resolve();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();r=json.loads((P/'geometry-report.json').read_text());f=P/'FlangePackR33.FCStd';before=sha(f);assert before==r['native_sha256'];D=A.openDocument(str(f));frame={n:D.getObject(n).Shape.copy()for n in ['PackSupportHubR33','PackLidR33']};covers={n:D.getObject(n).Shape.copy()for n in ['FlangeCoverUpper','FlangeCoverLower','ButtonServiceCoverR31']};gauge=D.getObject('PackPublishedGaugeR33').Shape.copy();sensors={}
for q in r['sensors']:
 sensors[q['reference']+'_head_attachment_D3_2']=Part.makeCylinder(1.6,10,A.Vector(*q['head_start_xyz_mm']),A.Vector(1,0,0))
for n in r['new_roles']:
 if n.startswith(('PackNTCLeadStub','PackNTCContactFilm')):sensors[n]=D.getObject(n).Shape.copy()
def vol(a,b):
 u,v=a.BoundBox,b.BoundBox
 if any(min(getattr(u,k+'Max'),getattr(v,k+'Max'))<=max(getattr(u,k+'Min'),getattr(v,k+'Min'))+1e-7 for k in 'XYZ'):return 0.
 return a.copy().common(b.copy()).Volume
rows=[]
for axis,sign in itertools.product(range(3),[-1,1]):
 samples=[];firstg=None;firsts=None;firstcover=None
 for i in range(25):
  t=i*.05;d=[0,0,0];d[axis]=sign*t;v=A.Vector(*d);g=gauge.copy();g.translate(v);gc=[{'frame':n,'intersection_mm3':w}for n,b in frame.items()if(w:=vol(g,b))>1e-5];cc=[{'cover':n,'intersection_mm3':w}for n,b in covers.items()if(w:=vol(g,b))>1e-5];sc=[]
  for n,a in sensors.items():
   a=a.copy();a.translate(v)
   for m,b in dict(frame,**covers).items():
    w=vol(a,b)
    if w>1e-5:sc.append({'sensor':n,'fixed':m,'intersection_mm3':w})
  if gc and firstg is None:firstg=t
  if sc and firsts is None:firsts=t
  if cc and firstcover is None:firstcover=t
  samples.append({'translation_mm':t,'gauge_frame_contacts':gc,'gauge_cover_contacts':cc,'sensor_contacts':sc})
  if firstg is not None and firsts is not None and firstcover is not None:break
 gap=None;covergap=None
 if firstg is not None:
  d=[0,0,0];d[axis]=sign*firstg;v=A.Vector(*d);dist=[]
  for a in sensors.values():
   a=a.copy();a.translate(v);dist.extend(a.distToShape(b)[0]for b in dict(frame,**covers).values())
  gap=min(dist);g=gauge.copy();g.translate(v);covergap=min(g.distToShape(b)[0]for b in covers.values())
 passed=firstg is not None and(firsts is None or firsts-.05>=firstg-1e-9)and(firstcover is None or firstcover-.05>=firstg-1e-9)and gap is not None and gap>=.05 and covergap>=.05
 row={'axis':'XYZ'[axis],'sign':sign,'first_gauge_frame_intersection_sample_mm':firstg,'first_sensor_intersection_sample_mm':firsts,'first_gauge_cover_intersection_sample_mm':firstcover,'sensor_minimum_gap_at_first_gauge_frame_sample_mm':gap,'gauge_cover_minimum_gap_at_first_gauge_frame_sample_mm':covergap,'frame_precedes_sensor_and_cover_with_study_margin':passed,'samples':samples};rows.append(row);print('freeplay','XYZ'[axis],sign,'frame',firstg,'sensor',firsts,'cover',firstcover,'sensorGap',gap,'coverGap',covergap,'pass',passed,flush=True)
out={'native_sha256':before,'geometry_report_sha256':sha(P/'geometry-report.json'),'reviewer_sha256':sha(Path(__file__)),'sample_step_mm':.05,'maximum_sampled_translation_mm':1.2,'head_attachment_diameter_mm':3.2,'included_sensor_and_process_roles':list(sensors),'rows':rows,'all_six_probes_frame_before_sensors_and_cover':all(q['frame_precedes_sensor_and_cover_with_study_margin']for q in rows),'scope':'Rigid0.05mm translation samples only. First frame sample intentionally penetrates nominal gauge stops; sensor and housing gaps measured there. Includes two head+attachment envelopes, eight current sensor/stub/process roles, first4.5mm leads only. Not a continuous contact-order proof, pouch deformation/rotation, supplier expansion allowance, load/creep, actual tape/contact, thermal/vibration or physical qualification.'};(P/'freeplay-review.json').write_text(json.dumps(out,indent=2)+'\n');A.closeDocument(D.Name);assert sha(f)==before;print('all pass',out['all_six_probes_frame_before_sensors_and_cover'],flush=True)
