"""Add the current ten-wire plan to an unchanged R27D native model.

Write failures as evidence; never hide part intersections behind envelope-only
screens. This checks installed geometry, not assembly motion or dynamic flex.
"""
from pathlib import Path
import sys,json,hashlib,itertools
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part,Sketcher
from tip_wire_native_r26 import edges_from_plan
ROOT=Path(__file__).resolve().parents[1];PLAN=Path(sys.argv[1]).resolve();OUT=Path(sys.argv[2]).resolve();OUT.mkdir(parents=True,exist_ok=True);assert not any(OUT.iterdir());SRC=ROOT/'hardware/cad/flange-controls-r27/candidate-d'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();r=json.loads((SRC/'geometry-report.json').read_text());plan=json.loads(PLAN.read_text());nf=SRC/'FlangeCradleR27.FCStd';assert sha(nf)==r['native_sha256']==plan['source_CAD_native_sha256']
pcb=ROOT/'hardware/pcb/flange-access-r28/candidate-s'
assert sha(pcb/'layout-inspection.json')==plan['source_layout_inspection_sha256']
for domain,digest in plan['source_current_native_board_sha256'].items():assert sha(pcb/domain/(domain+'-r28.kicad_pcb'))==digest
proof=json.loads((pcb/'saved-circuit-review.json').read_text());assert proof['current_CAD_native_sha256']==sha(nf)
assert all(q.get('guarded_minimum_centerline_radius_mm',0)>=4 for q in plan['wires'])
d=A.openDocument(str(nf));parts={n:d.getObject(n)for n in r['parts']};mates={n:d.getObject(n)for n in r['mates']};allowances={n:d.getObject(n)for n in r['allowances']};source={n:o.Shape.exportBrepToString()for n,o in dict(parts,**mates,**allowances).items()};new={};rows=[]
for q in plan['wires']:
 edges=edges_from_plan(q);spine=d.addObject('Part::Feature','InterboardPathR29_'+str(q['pin']));spine.Shape=Part.Wire(edges)
 profile=d.addObject('Sketcher::SketchObject','InterboardProfileR29_'+str(q['pin']));profile.Placement=A.Placement(A.Vector(*q['start_xyz_mm']),A.Rotation(A.Vector(0,0,1),A.Vector(0,-1,0)));profile.addGeometry(Part.Circle(A.Vector(),A.Vector(0,0,1),q['wire_OD_allowance_mm']/2),False)
 wire=d.addObject('Part::Sweep','InterboardWireR29_'+str(q['pin']));wire.Sections=[profile];wire.Spine=spine;wire.Solid=True;wire.Frenet=True;wire.Label=str(q['pin'])+' / '+q['net']+' / 28AWG candidate OD0.60 allowance'
 d.recompute();s=wire.Shape;assert s.isValid()and len(s.Solids)==1,(q['pin'],s.isValid(),len(s.Solids))
 new[wire.Name]=wire;rows.append({'pin':q['pin'],'net':q['net'],'role':wire.Name,'native_path_length_mm':spine.Shape.Length,'sampled_path_length_mm':q['sampled_path_length_mm'],'sampled_minimum_radius_mm':q['minimum_sampled_centerline_radius_mm']});assert abs(spine.Shape.Length-q['sampled_path_length_mm'])<.001
 print('wire',q['pin'],'length',spine.Shape.Length,'R',q['minimum_sampled_centerline_radius_mm'],flush=True)
assert all(d.getObject(n).Shape.exportBrepToString()==s for n,s in source.items())
parts.update(new)
def inv(s):
 b=s.optimalBoundingBox(False,False);return {'valid':s.isValid(),'solids':len(s.Solids),'volume_mm3':s.Volume,'bounds_xyz_mm':[getattr(b,k)for k in ['XMin','YMin','ZMin','XMax','YMax','ZMax']]}
def vol(a,b):
 u,v=a.BoundBox,b.BoundBox
 if any(min(getattr(u,k+'Max'),getattr(v,k+'Max'))<=max(getattr(u,k+'Min'),getattr(v,k+'Min'))+1e-7 for k in 'XYZ'):return 0.
 return a.copy().common(b.copy()).Volume
hits=[];seen=set();pairs=0
for n,o in new.items():
 local=[]
 for m,p in dict(parts,**mates,**allowances).items():
  if n==m:continue
  key=tuple(sorted([n,m]))
  if key in seen:continue
  seen.add(key);pairs+=1;v=vol(o.Shape,p.Shape)
  if v>1e-5:local.append({'a':n,'b':m,'intersection_mm3':v})
 hits+=local;print('static',n,local,flush=True)
gaps=[]
for (n,o),(m,p)in itertools.combinations(new.items(),2):
 gaps.append({'a':n,'b':m,'native_surface_distance_mm':o.Shape.distToShape(p.Shape)[0]})
report={'builder_sha256':sha(Path(__file__)),'path_library_sha256':sha(Path(__file__).with_name('tip_wire_native_r26.py')),'source_R27_native_sha256':sha(nf),'source_report_sha256':sha(SRC/'geometry-report.json'),'plan_sha256':sha(PLAN),'parts':{n:inv(o.Shape)for n,o in parts.items()},'mates':r['mates'],'allowances':r['allowances'],'all_source_primary_mate_allowance_BReps_identical':True,'individual_wires':rows,'new_pairs_tested':pairs,'new_wire_intersections':hits,'wire_surface_distances':gaps,'scope':'Ten native OD0.60 swept wire allowances on source R27D with every source role unchanged. Candidate wire exits/OD and sampled radius basis only. No actual connector geometry, restraint/strain relief, assembly motion, service slack, flex-cycle, electrical, sealing or physical acceptance. Source PCB unchanged; battery OPEN.'}
output=OUT/'InterboardR29.FCStd';d.Label='R29 / ten-wire interboard candidate / REVIEW';d.saveAs(str(output));report['native_sha256']=sha(output);(OUT/'geometry-report.json').write_text(json.dumps(report,indent=2)+'\n');A.closeDocument(d.Name);assert sha(nf)==r['native_sha256'];print('saved',output,'hits',len(hits),flush=True)
