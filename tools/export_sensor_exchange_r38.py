"""R38 STEP round trip, with explicit exact-Boolean comparison limitations."""
from pathlib import Path
import hashlib,json,sys
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'hardware/cad/joint-retention-r38/sensor-c';path=P/'RetainedSensorJointsR38.FCStd';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();before=sha(path);r=json.loads((P/'geometry-report.json').read_text());assert before==r['native_sha256'];D=A.openDocument(str(path));out=P/'exchange';out.mkdir(exist_ok=True);files={}
def samples(s):
 return[v.Point for v in s.Vertexes]+[e.valueAt((e.FirstParameter+e.LastParameter)/2)for e in s.Edges]
def error(a,b):return max(b.distToShape(Part.Vertex(v))[0]for v in samples(a))
for name in ['JointRetainingHubR38','SensorJointCombR38','ReturnJointDropInPlugR38']:
 s=D.getObject(name).Shape.copy();assert s.isValid()and len(s.Solids)==1
 f=out/(name+'.step');s.exportStep(str(f));loaded=Part.Shape();loaded.read(str(f));assert loaded.isValid()and len(loaded.Solids)==1
 minus=s.copy().cut(loaded.copy()).Volume;plus=loaded.copy().cut(s.copy()).Volume
 volume_delta=abs(s.Volume-loaded.Volume);a,b=s.optimalBoundingBox(False,False),loaded.optimalBoundingBox(False,False);bounds=max(abs(getattr(a,k)-getattr(b,k))for k in ['XMin','YMin','ZMin','XMax','YMax','ZMax'])
 forward,reverse=error(s,loaded),error(loaded,s)
 assert volume_delta<1e-4 and bounds<1e-5 and max(forward,reverse)<1e-5
 files[f.name]={'sha256':sha(f),'valid_single_solid_readback':True,'native_volume_mm3':s.Volume,'readback_volume_mm3':loaded.Volume,'volume_difference_mm3':volume_delta,'maximum_bounds_difference_mm':bounds,'native_vertex_edge_midpoint_sample_count':len(samples(s)),'readback_vertex_edge_midpoint_sample_count':len(samples(loaded)),'max_native_sample_distance_to_STEP_mm':forward,'max_STEP_sample_distance_to_native_mm':reverse,'direct_native_minus_STEP_mm3':minus,'direct_STEP_minus_native_mm3':plus,'direct_material_boolean_comparison_pass':max(abs(minus),abs(plus))<1e-4}
 print(name,'volume delta',volume_delta,'bidirectional vertex/edge samples',forward,reverse,'direct Boolean agreement',files[f.name]['direct_material_boolean_comparison_pass'],flush=True)
A.closeDocument(D.Name);assert sha(path)==before
(out/'exchange-review.json').write_text(json.dumps({'native_sha256':before,'exporter_sha256':sha(Path(__file__)),'step_files':files,'all_valid_single_solid_volume_bounds_and_sample_checks_pass':True,'scope':'Three development solids in installed coordinates. STEP readback checks valid single solids, volume/bounds and bidirectional vertex/edge-midpoint surface-distance samples. Exact Boolean material differences are separately reported; nearly coincident hub Boolean subtraction is inconsistent despite matching volume/bounds/samples, so exact hub material equivalence is not claimed. Finite samples are not continuous surface proof or CAM/manufacturing acceptance.'},indent=2)+'\n')
