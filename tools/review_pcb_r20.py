"""Independent read-only R20 native saved-history and part-envelope review."""
from pathlib import Path
import sys,json,hashlib
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part
ROOT=Path(__file__).resolve().parents[1];P=Path(sys.argv[1]).resolve();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=P/'PCBIntegrationR20.FCStd';rp=P/'geometry-report.json';r=json.loads(rp.read_text());before=sha(f);assert before==r['native_sha256'];rh=sha(rp);d=A.openDocument(str(f));snap={n:d.getObject(n).Shape.copy()for n in dict(r['parts'],**r['mates'])}
for o in d.Objects:o.touch()
d.recompute();rows={}
for n,old in snap.items():
 s=d.getObject(n).Shape;b=s.optimalBoundingBox(False,False);c=old.optimalBoundingBox(False,False);bb=[getattr(b,k)for k in ['XMin','YMin','ZMin','XMax','YMax','ZMax']];saved=dict(r['parts'],**r['mates'])[n];delta=max(abs(a-b)for a,b in zip(bb,saved['bounds_xyz_mm']));dv=s.Volume-saved['volume_mm3'];assert s.isValid()and len(s.Solids)==saved['solids']and abs(dv)<1e-4 and delta<1e-5,(n,dv,delta);rows[n]={'valid':True,'solids':len(s.Solids),'saved_report_volume_delta_mm3':dv,'saved_report_bounds_max_delta_mm':delta}
external=[{'object':o.Name,'dependency':v.Name,'document':v.Document.Name}for o in d.Objects for v in o.OutList if v.Document!=d];assert not external
src=Path(sys.argv[2]).resolve()if len(sys.argv)>2 else ROOT/'hardware/cad/simple-assembly-r13/candidate-f/SimpleAssemblyR13.FCStd';assert sha(src)==r['source_R13_native_sha256'];source=A.openDocument(str(src));comparison={}
for n in r['retained_source_material_comparison']:
 if n in r.get('declared_source_geometry_changes',[]):continue
 a=d.getObject(n).Shape.copy();b=source.getObject(n).Shape.copy();removed=b.cut(a).Volume;added=a.cut(b).Volume;assert removed<1e-4 and added<1e-4,(n,removed,added);comparison[n]={'removed_mm3':removed,'added_mm3':added}
for n in ['PortedKeeperR20','PortedCarrierR20']:assert len(d.getObject(n).Shape.Solids)==1
pcb=ROOT/r['PCB_directory'];inp=pcb/'layout-inspection.json';assert sha(inp)==r['PCB_inspection_sha256'];ir=json.loads(inp.read_text());partchecks=[]
for domain,board in ir['boards'].items():
 assert sha(pcb/domain/(domain+'-r19.kicad_pcb'))==r['PCB_native_sha256'][domain]
 for p in board['placements']:
  if not p['body_xy_mm']:continue
  bb=p['body_xy_mm'];zz=p['z_bounds_mm'];want=[bb[0],bb[1],zz[0],bb[2],bb[3],zz[1]];got=r['parts']['R17_'+p['ref']]['bounds_xyz_mm'];assert max(abs(a-b)for a,b in zip(want,got))<1e-5,p['ref'];partchecks.append(p['ref'])
curves={}
for n,a,b in [('FullerOuterNoseMeridian',43.12,18.669),('FullerInnerNoseMeridian',41.62,17.169)]:
 c=d.getObject(n).Shape.Edges[0].Curve;assert abs(c.MajorRadius-a)<1e-7 and abs(c.MinorRadius-b)<1e-7;curves[n]={'major_mm':c.MajorRadius,'minor_mm':c.MinorRadius}
out={'native_sha256':before,'geometry_report_sha256':rh,'reviewer_sha256':sha(Path(__file__)),'saved_roles':rows,'retained_R13_material_comparison':comparison,'native_PCB_part_envelopes_checked':partchecks,'source_read_path':str(src),'source_R13_native_sha256':sha(src),'external_document_links':external,'native_fuller_nose_ellipses':curves,'scope':'Fresh forced native history recompute, saved-report geometry and PCB Fab/height bounds, retained R13 material and ellipse checks. Read-only; no real mate/wire/load/process/physical acceptance.'};A.closeDocument(source.Name);A.closeDocument(d.Name);assert sha(f)==before and sha(rp)==rh;(P/'saved-review.json').write_text(json.dumps(out,indent=2)+'\n');print(len(rows),'saved roles;',len(partchecks),'actual PCB part envelopes; no external links',flush=True)
