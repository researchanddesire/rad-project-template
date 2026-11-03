"""Export five current mechanical parts and independently re-read each STEP."""
from pathlib import Path
import sys,json,hashlib
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part
P=Path(sys.argv[1]).resolve();OUT=Path(sys.argv[2]).resolve();OUT.mkdir(parents=True,exist_ok=True)
assert not any(OUT.iterdir()),'Preserve previous export attempts'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((P/'geometry-report.json').read_text());nf=P/'ShellMotorMountR25.FCStd';before=sha(nf);assert before==r['native_sha256']
D=A.openDocument(str(nf));rows={}
def bounds(s):
 b=s.optimalBoundingBox(False,False)
 return [getattr(b,k)for k in ['XMin','YMin','ZMin','XMax','YMax','ZMax']]
for name in ['ShellMotorMountR25','KeyedBodyR25','MotorSeatCapR25','PortedCarrierR20','PCBOnlyKeeperR25']:
 obj=D.getObject(name);source=obj.Shape.copy();p=OUT/(name+'.step');Part.export([obj],str(p))
 imported=Part.read(str(p));dv=imported.Volume-source.Volume
 delta=max(abs(a-b)for a,b in zip(bounds(source),bounds(imported)))
 removed=source.copy().cut(imported.copy()).Volume;added=imported.copy().cut(source.copy()).Volume
 row={'STEP_sha256':sha(p),'native_volume_mm3':source.Volume,'imported_volume_mm3':imported.Volume,'volume_delta_mm3':dv,'maximum_bounds_delta_mm':delta,'native_solids':len(source.Solids),'imported_solids':len(imported.Solids),'valid':imported.isValid(),'removed_material_mm3':removed,'added_material_mm3':added}
 row['numeric_screen_pass']=row['valid']and row['native_solids']==row['imported_solids']and abs(dv)<.001 and delta<.001 and removed<.001 and added<.001
 rows[name]=row;print(name,row,flush=True)
 out={'native_sha256':before,'geometry_report_sha256':sha(P/'geometry-report.json'),'exporter_sha256':sha(Path(__file__)),'parts':rows,'scope':'Saved native STEP export and independent re-read; validity/solid counts/bounds/mass/material numerical screens only. Not a maximum surface-deviation or supplier import, dimension, tolerance, fabrication or physical acceptance. Failed screens remain explicit; native FreeCAD is authoritative.'}
 (OUT/'export-review.json').write_text(json.dumps(out,indent=2)+'\n')
A.closeDocument(D.Name);assert sha(nf)==before
