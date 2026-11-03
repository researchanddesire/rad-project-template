"""Fresh read-only native saved-history/source comparison for R13D."""
from pathlib import Path
import argparse,hashlib,json,sys
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part
ROOT=Path(__file__).resolve().parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ap=argparse.ArgumentParser();ap.add_argument('directory',type=Path);args=ap.parse_args();P=args.directory.resolve()
nf=P/'SimpleAssemblyR13.FCStd';rp=P/'geometry-report.json';r=json.loads(rp.read_text());before=sha(nf);assert before==r['native_sha256'];report_sha=sha(rp)
d=A.openDocument(str(nf));saved={n:d.getObject(n).Shape.copy()for n in dict(r['parts'],**r['mates'])}
for o in d.Objects:o.touch()
d.recompute();rows={}
for n,old in saved.items():
    s=d.getObject(n).Shape;b=old.optimalBoundingBox(False,False);c=s.optimalBoundingBox(False,False)
    dv=s.Volume-old.Volume;db=max(abs(getattr(b,k)-getattr(c,k))for k in ['XMin','YMin','ZMin','XMax','YMax','ZMax'])
    assert s.isValid()and len(s.Solids)==len(old.Solids)and abs(dv)<1e-4 and db<1e-5,(n,dv,db)
    rows[n]={'valid':True,'solids':len(s.Solids),'volume_delta_mm3':dv,'bounds_max_delta_mm':db}
external=[{'object':o.Name,'dependency':v.Name,'document':v.Document.Name}for o in d.Objects for v in o.OutList if v.Document!=d];assert not external
src=ROOT/'hardware/cad/front-load-retention-r11/candidate-c/FrontLoadRetentionR11.FCStd';assert sha(src)==r['source_R11_native_sha256']
old=A.openDocument(str(src));equality={}
for n in r['source_roles_unchanged']:
    a=d.getObject(n).Shape.copy();b=old.getObject(n).Shape.copy()
    equal=hashlib.sha256(a.exportBrepToString().encode()).hexdigest()==hashlib.sha256(b.exportBrepToString().encode()).hexdigest()
    # Recompute can change BRep serialization/tolerances. Preserve that finding;
    # require common-volume conservation and both material differences instead
    # of silently treating a byte-unequal shape as source-identical.
    common=a.copy().common(b.copy()).Volume;removed=b.copy().cut(a.copy()).Volume;added=a.copy().cut(b.copy()).Volume
    assert abs(common-min(a.Volume,b.Volume))<1e-4 and removed<1e-4 and added<1e-4,(n,common,removed,added)
    equality[n]={'BRep_bytes_equal_after_recompute':equal,'common_volume_mm3':common,'source_volume_mm3':b.Volume,'recomputed_volume_mm3':a.Volume,'removed_mm3':removed,'added_mm3':added}
cap_partitions=[]
for z0,z1 in [(-100,0),(0,100)]:
    t=Part.makeBox(200,250,z1-z0,A.Vector(-100,-100,z0));s=d.getObject('FullerClosingCap').Shape.copy().common(t)
    assert s.isValid()and len(s.Solids)>0
    cap_partitions.append({'Z_span_mm':[z0,z1],'volume_mm3':s.Volume,'solids':len(s.Solids)})
assert abs(sum(p['volume_mm3']for p in cap_partitions)-d.getObject('FullerClosingCap').Shape.Volume)<.01
curves={}
for name,a,b in [('FullerOuterNoseMeridian',43.12,18.669),('FullerInnerNoseMeridian',41.62,17.169)]:
    c=d.getObject(name).Shape.Edges[0].Curve;assert abs(c.MajorRadius-a)<1e-7 and abs(c.MinorRadius-b)<1e-7
    curves[name]={'curve_type':str(type(c)),'major_radius_mm':c.MajorRadius,'minor_radius_mm':c.MinorRadius,'center_xyz_mm':[c.Center.x,c.Center.y,c.Center.z]}
out={'native_sha256':before,'geometry_report_sha256':report_sha,'reviewer_sha256':sha(Path(__file__)),
     'saved_roles':rows,'external_document_links':external,'fixed_source_roles_material_comparison':equality,'native_nose_ellipses':curves,'fresh_cap_partition_controls':cap_partitions,
     'scope':'Fresh saved-history recompute of110primary+7mate roles,17roleR11 material/volume comparison with byte differences retained, actual native ellipse axes and cap partition-volume controls. No save, manufacture, physical fit or load/thermal/wear qualification.'}
A.closeDocument(old.Name);A.closeDocument(d.Name);assert sha(nf)==before and sha(rp)==report_sha
(P/'saved-review.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'checked_roles':len(rows),'source_roles_equal':len(equality),'external_links':external,'ellipses':curves},indent=2),flush=True)
