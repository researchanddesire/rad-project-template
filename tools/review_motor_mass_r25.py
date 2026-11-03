"""Finite adaptive mass/partition diagnostics; never alter native or STEP."""
from pathlib import Path
import sys,json,hashlib,time,warnings
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part,OCC
from OCC.Core.BRepGProp import brepgprop
from OCC.Core.GProp import GProp_GProps
warnings.filterwarnings('ignore',category=DeprecationWarning)
P=Path(sys.argv[1]).resolve();source=Path(sys.argv[2]).resolve()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((P/'geometry-report.json').read_text());nf=P/'ShellMotorMountR25.FCStd'
assert sha(nf)==r['native_sha256']and sha(source)==r['source_native_sha256']
D=A.openDocument(str(nf));S=A.openDocument(str(source))
body0=S.getObject('KeyedOnePieceBody').Shape.copy();body=D.getObject('KeyedBodyR25').Shape.copy();key=D.getObject('CoveredMouthKeySlotR25').Shape.copy()
shapes={'source_body':body0,'new_body':body,'body_expected_key_removal':body0.copy().common(key.copy()),'body_actual_removed':body0.copy().cut(body.copy())}
oldcap=S.getObject('FullerClosingCap').Shape.copy();cap=D.getObject('MotorSeatCapR25').Shape.copy();q=r['cap_assembly'];T=A.Placement(A.Vector(0,q['Y_translation_mm'],0),A.Rotation(A.Vector(0,1,0),q['Y_rotation_deg']));cap.Placement=T.inverse().multiply(cap.Placement)
shapes.update({'source_cap':oldcap,'new_cap_local':cap,'cap_added':cap.copy().cut(oldcap.copy())})
exports=json.loads((P/'step-review-r1/export-review.json').read_text())
for name,v in exports['parts'].items():
 f=P/'step-review-r1'/(name+'.step');assert sha(f)==v['STEP_sha256']
 shapes['native_'+name]=D.getObject(name).Shape.copy();shapes['STEP_'+name]=Part.read(str(f))
out={'native_sha256':sha(nf),'source_native_sha256':sha(source),'export_review_sha256':sha(P/'step-review-r1/export-review.json'),'reviewer_sha256':sha(Path(__file__)),'runtime':{'FreeCAD':list(A.Version()),'OCCT':Part.OCC_VERSION,'PythonOCC':OCC.VERSION},'method':'Matching OCCT BRepGProp.VolumePropertiesGK(shape,props,eps,True,True,False,False,False) via FreeCAD/PythonOCC bridge, two finite requested errors1e-9/1e-11; no repair, retolerance, export retry or source save.','rows':{},'scope':'Numerical mass/partition stability diagnostics only. The original default-volume/Boolean STEP failures remain preserved. Equal adaptive mass does not establish maximum surface deviation, dimensional/supplier/physical acceptance.'}
for name,s in shapes.items():
 vals=[]
 for eps in [1e-9,1e-11]:
  props=GProp_GProps();start=time.monotonic();err=brepgprop.VolumePropertiesGK(Part.__toPythonOCC__(s),props,eps,True,True,False,False,False)
  vals.append({'requested_relative_error':eps,'volume_mm3':props.Mass(),'estimated_relative_error':err,'seconds':time.monotonic()-start})
 out['rows'][name]={'default_volume_mm3':s.Volume,'adaptive':vals,'convergence_change_mm3':vals[1]['volume_mm3']-vals[0]['volume_mm3']}
 print(name,out['rows'][name],flush=True)
 (P/'adaptive-volume-diagnostic.json').write_text(json.dumps(out,indent=2)+'\n')
v=lambda n:out['rows'][n]['adaptive'][-1]['volume_mm3']
out['partition_residuals_mm3']={'body_before_minus_after_minus_expected_key':v('source_body')-v('new_body')-v('body_expected_key_removal'),'body_actual_minus_expected_removed':v('body_actual_removed')-v('body_expected_key_removal'),'cap_after_minus_before_minus_added':v('new_cap_local')-v('source_cap')-v('cap_added')}
out['STEP_minus_native_adaptive_mm3']={name:v('STEP_'+name)-v('native_'+name)for name in exports['parts']}
out['mass_diagnostic_screen']={'all_row_convergence_below_0_0001_mm3':all(abs(row['convergence_change_mm3'])<.0001 for row in out['rows'].values()),'all_partition_residuals_below_0_001_mm3':all(abs(x)<.001 for x in out['partition_residuals_mm3'].values()),'STEP_adaptive_mass_below_0_001_mm3':{n:abs(x)<.001 for n,x in out['STEP_minus_native_adaptive_mm3'].items()}}
(P/'adaptive-volume-diagnostic.json').write_text(json.dumps(out,indent=2)+'\n')
A.closeDocument(S.Name);A.closeDocument(D.Name);assert sha(nf)==r['native_sha256']and sha(source)==r['source_native_sha256']
print(out['mass_diagnostic_screen'],flush=True)
