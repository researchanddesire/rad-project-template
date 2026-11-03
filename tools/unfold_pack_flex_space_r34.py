"""Unroll exact cylindrical mid-surfaces and flat regions of the R34 claim.

Compares developed area x reserved thickness to fresh formed volume. This is
geometric material accounting only; not a manufactured flex circuit.
"""
from pathlib import Path
import sys,json,hashlib,math
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'hardware/cad/pack-harness-r34/formed-f';OUT=Path(sys.argv[1]).resolve();OUT.mkdir(parents=True,exist_ok=True);assert not any(OUT.iterdir());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();r=json.loads((P/'geometry-report.json').read_text());f=P/'FormedFlexSpaceR34.FCStd';before=sha(f);assert before==r['native_sha256']and r['all_static_space_claim_screens_clear'];D=A.openDocument(str(f))
for o in D.Objects:o.touch()
D.recompute();formed=D.getObject('PackFormedFlexSpaceR34').Shape.copy();assert formed.isValid()and len(formed.Solids)==1 and abs(formed.Volume-r['space_claim_volume_mm3'])<1e-4
flat=A.newDocument('PackFlexDevelopedR34');pieces=[];mapping=[]
def rect(role,b):
 u,v,x,y=b;assert x>u and y>v
 p=[A.Vector(u,v,0),A.Vector(x,v,0),A.Vector(x,y,0),A.Vector(u,y,0)];face=Part.Face(Part.makePolygon(p+[p[0]]));o=flat.addObject('PartDesign::Feature',role+'Flat');o.Shape=face;pieces.append(face);mapping.append({'formed_role':role,'flat_bounds_uv_mm':b,'flat_area_mm2':face.Area,'source_region_volume_mm3':D.getObject(role).Shape.Volume,'region_volume_minus_developed_area_times_thickness_mm3':D.getObject(role).Shape.Volume-face.Area*r['space_claim_thickness_mm']});assert abs(mapping[-1]['region_volume_minus_developed_area_times_thickness_mm3'])<1e-5
rows={q['role']:q for q in r['parts_of_space_claim']};u=0.;height=5.7
rect('PackFlexUpperLapSpaceR34',[u,-2.85,u+1.715,2.85]);u+=1.715
for role in ['PackFlexUpperRiseFirstSpaceR34','PackFlexUpperRiseSecondSpaceR34']:
 L=rows[role]['centreline_arc_length_mm'];rect(role,[u,-2.85,u+L,2.85]);u+=L
L=r['body_upper_rise_end_X_mm']+11.4;rect('PackFlexUpperExitSpaceR34',[u,-2.85,u+L,2.85]);u+=L
L=rows['PackFlexBodyUTurnSpaceR34']['centreline_arc_length_mm'];rect('PackFlexBodyUTurnSpaceR34',[u,-2.85,u+L,2.85]);u+=L;lowerbase=u;uc=u+11.4
rect('PackFlexLowerLapSpaceR34',[lowerbase,-2.85,uc+2.25,2.85]);rect('PackFlexBodyRunSpaceR34',[uc-2.25,-35.5,uc+2.25,0]);v=-35.5
for role in ['PackFlexNeckSFirstSpaceR34','PackFlexNeckSSecondSpaceR34']:
 L=rows[role]['centreline_arc_length_mm'];rect(role,[uc-2.25,v-L,uc+2.25,v]);v-=L
L=r['S_transition_end_Y_mm']+24.475;rect('PackFlexNeckRunSpaceR34',[uc-2.25,v-L,uc+2.25,v]);v-=L
L=rows['PackFlexFlangeTurnSpaceR34']['centreline_arc_length_mm'];rect('PackFlexFlangeTurnSpaceR34',[uc-2.25,v-L,uc+2.25,v]);v-=L;flange_v=v
rect('PackFlexRearCrossbarSpaceR34',[uc-2.25,v-4.5,uc+39.775,v]);u=uc+39.775
for role in ['PackFlexOuterRearTurnSpaceR34','PackFlexOuterRunSpaceR34','PackFlexOuterFrontTurnSpaceR34']:
 L=rows[role].get('centreline_arc_length_mm',12.85);rect(role,[u,v-4.5,u+L,v]);u+=L
rect('PackFlexFrontIslandSpaceR34',[u,v-11.275,u+15.775,v+6.725]);front_u=u
thickness=r['space_claim_thickness_mm'];solids=[p.extrude(A.Vector(0,0,thickness))for p in pieces];flat_sheet=solids[0]
for p in solids[1:]:flat_sheet=flat_sheet.fuse(p)
flat_sheet=flat_sheet.removeSplitter();tops=[q for q in flat_sheet.Faces if q.BoundBox.ZMin>=thickness-1e-7 and q.BoundBox.ZMax<=thickness+1e-7];assert len(tops)==1,(len(tops),len(flat_sheet.Solids));face=tops[0].copy();face.translate(A.Vector(0,0,-thickness));assert face.isValid()and len(face.Faces)==1 and len(face.Wires)==1,(face.isValid(),len(face.Faces),len(face.Wires));delta=flat_sheet.Volume-formed.Volume;assert flat_sheet.isValid()and len(flat_sheet.Solids)==1 and abs(delta)<1e-4,(delta,flat_sheet.Volume,formed.Volume)
o=flat.addObject('PartDesign::Feature','PackFlexFlatEnvelopeR34');o.Shape=flat_sheet;o.Label='DEVELOPED SPACE CLAIM / NOT COPPER OR FABRICATION';flat.recompute();out=OUT/'PackFlexFlatSpaceR34.FCStd';flat.saveAs(str(out));vertices=[[q.Point.x,q.Point.y]for q in face.OuterWire.OrderedVertexes];area_sum=sum(q['flat_area_mm2']for q in mapping);native_sum=sum(D.getObject(q['formed_role']).Shape.Volume for q in mapping)
report={'source_formed_native_sha256':before,'source_formed_report_sha256':sha(P/'geometry-report.json'),'native_flat_sha256':sha(out),'unfolder_sha256':sha(Path(__file__)),'reserved_thickness_mm':r['space_claim_thickness_mm'],'fresh_formed_volume_mm3':formed.Volume,'flat_area_mm2':face.Area,'flat_extruded_volume_mm3':flat_sheet.Volume,'flat_minus_formed_volume_mm3':delta,'sum_region_flat_area_mm2':area_sum,'sum_region_native_volume_mm3':native_sum,'flat_union_overlap_area_mm2':area_sum-face.Area,'native_union_overlap_volume_mm3':native_sum-formed.Volume,'all_sixteen_regions_volume_preserved_individually':len(mapping)==16,'region_mapping':mapping,'outer_outline_ordered_uv_mm':vertices,'flat_coordinate_basis':'Body lap u=-(nativeX+1.485),v=nativeY-40.5; after each bend use exact mid-surface arc length and continuous material coordinates. No arc approximations or bounding-box length substitution.','body_lower_flat_mapping':{'u_center_at_X0_mm':uc,'v_at_Y40_5_mm':0},'flange_rear_mapping':{'u_center_at_X0_mm':uc,'v_at_Z_minus2_275_mm':flange_v},'front_island_mapping':{'u_at_X39_775_mm':front_u,'v_at_Z_minus2_275_mm':flange_v},'body_lap_pad_centres_uv_mm':{'1':[.5,2.25],'2':[.5,.75],'3':[.5,-.75],'4':[.5,-2.25]},'scope':'Fresh forced formed single-solid reservation and exact16-region cylindrical mid-surface unrolling. Each region volume and full union volume agree with developed area x.25mm within1e-4mm3; flat union one face/no holes. This accounts for flat overlaps without inventing material. Not actual stackup/copper layout, bend strain/life, solder/anchor/lead or assembly/physical acceptance. J2 header/mate omission remains only a comparison; no native PCB DNP implementation.'};(OUT/'unfold-review.json').write_text(json.dumps(report,indent=2)+'\n');A.closeDocument(flat.Name);A.closeDocument(D.Name);assert sha(f)==before;print('UNFOLDED area',face.Area,'volume delta',delta,'outline vertices',len(vertices),'regions',len(mapping),flush=True)
