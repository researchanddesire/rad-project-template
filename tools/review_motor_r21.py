"""Read-only forced-history review of a saved R21 conditional motor cage."""
from pathlib import Path
import sys,json,hashlib
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part
P=Path(sys.argv[1]).resolve();S=Path(sys.argv[2]).resolve()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
f=P/'MotorRetentionR21.FCStd';rp=P/'geometry-report.json';r=json.loads(rp.read_text())
before=sha(f);rh=sha(rp);assert before==r['native_sha256']
assert sha(S/'PCBIntegrationR20.FCStd')==r['source_R20_native_sha256']
assert sha(S/'geometry-report.json')==r['source_R20_report_sha256']
D=A.openDocument(str(f))
for o in D.Objects:o.touch()
D.recompute()
rows={}
for n,q in dict(r['parts'],**r['mates'],**r['allowances']).items():
    s=D.getObject(n).Shape;b=s.optimalBoundingBox(False,False)
    bounds=[getattr(b,k)for k in ['XMin','YMin','ZMin','XMax','YMax','ZMax']]
    dv=s.Volume-q['volume_mm3'];delta=max(abs(a-c)for a,c in zip(bounds,q['bounds_xyz_mm']))
    assert s.isValid()and len(s.Solids)==q['solids']and abs(dv)<1e-4 and delta<1e-5,(n,dv,delta)
    rows[n]={'valid':True,'solids':len(s.Solids),'volume_delta_mm3':dv,'bounds_max_delta_mm':delta}
external=[(o.Name,v.Name,v.Document.Name)for o in D.Objects for v in o.OutList if v.Document!=D]
assert not external
source=A.openDocument(str(S/'PCBIntegrationR20.FCStd'));retained={}
for n in r['retained_R20_material_comparison']:
    a=D.getObject(n).Shape.copy();b=source.getObject(n).Shape.copy()
    exact=a.exportBrepToString()==b.exportBrepToString()
    removed,added=(0,0)if exact else(b.cut(a).Volume,a.cut(b).Volume)
    assert removed<1e-4 and added<1e-4,(n,removed,added)
    retained[n]={'removed_mm3':removed,'added_mm3':added,'exact_BRep_equal':exact}
for n in ['MotorKeeperR21','PortedCarrierR20']:assert len(D.getObject(n).Shape.Solids)==1
def overlap(a,b):
    aa,bb=a.BoundBox,b.BoundBox
    if any(min(getattr(aa,k+'Max'),getattr(bb,k+'Max'))<=max(getattr(aa,k+'Min'),getattr(bb,k+'Min'))+1e-7 for k in 'XYZ'):return 0
    return a.copy().common(b.copy()).Volume
body=[D.getObject(n)for n in r['cartridge_roles']if n.startswith('R17_')or n=='BodyPCB_R17']
motor_loading=[];board_loading=[]
for z in [12,8,4,2,1,.5,.25,0]:
    bad=[]
    for n in ['MotorMaxEnvelope','MotorLeadFlareAllowanceR21']:
        s=D.getObject(n).Shape.copy();s.translate(A.Vector(0,0,z))
        for o in [D.getObject('PortedCarrierR20'),D.getObject('NarrowPackAllowance')]+body+[D.getObject(n)for n in r['mates']]:
            v=overlap(s,o.Shape)
            if v>1e-5:bad.append({'moving':n,'target':o.Name,'intersection_mm3':v})
    motor_loading.append({'Z_offset_mm':z,'hits':bad})
    bad=[]
    for o in body:
        s=o.Shape.copy();s.translate(A.Vector(0,0,z))
        for n in ['PortedCarrierR20','NarrowPackAllowance']:
            v=overlap(s,D.getObject(n).Shape)
            if v>1e-5:bad.append({'moving':o.Name,'target':n,'intersection_mm3':v})
    board_loading.append({'Z_offset_mm':z,'hits':bad})
translation_witnesses=[]
for v in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]:
    s=D.getObject('MotorMaxEnvelope').Shape.copy();s.translate(A.Vector(*v))
    hits={n:overlap(s,D.getObject(n).Shape)for n in ['PortedCarrierR20','MotorKeeperR21']}
    assert any(x>1e-5 for x in hits.values()),(v,hits)
    translation_witnesses.append({'motor_displacement_xyz_mm':v,'cage_intersections_mm3':hits})
A.closeDocument(source.Name);A.closeDocument(D.Name)
assert sha(f)==before and sha(rp)==rh
out={'native_sha256':before,'geometry_report_sha256':rh,'reviewer_sha256':sha(Path(__file__)),'saved_roles':rows,'retained_R20_material_comparison':retained,'external_document_links':external,'motor_lowering_listed_poses_keeper_waiting':motor_loading,'board_lowering_listed_poses_motor_keeper_waiting':board_loading,'fixed_axis_motor_translation_witnesses':translation_witnesses,'scope':'Fresh forced native history, saved geometry/material conservation, listed rigid drop-in poses and six fixed-axis translation obstruction witnesses only. Does not prove arbitrary extraction/rotation, physical retention, inferred motor flare, liner, wires, tolerances, process or load.'}
(P/'saved-review.json').write_text(json.dumps(out,indent=2)+'\n')
print(len(rows),'saved roles; native single keeper/carrier; retained R20 material; no external links',flush=True)
