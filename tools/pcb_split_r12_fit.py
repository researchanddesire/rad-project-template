"""Read-only exact R11 fixed context against actual R12 Fab/height/mate budgets."""
from pathlib import Path
import argparse,hashlib,json,sys
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part
ROOT=Path(__file__).resolve().parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ap=argparse.ArgumentParser();ap.add_argument('directory',type=Path);args=ap.parse_args();P=args.directory.resolve()
CAD=ROOT/'hardware/cad/front-load-retention-r11/candidate-c';nf=CAD/'FrontLoadRetentionR11.FCStd';rr=json.loads((CAD/'geometry-report.json').read_text())
before=sha(nf);assert before==rr['native_sha256'];d=A.openDocument(str(nf))
superseded=['BodyPCBStudy','FrontComponentAllowance','BackComponentAllowance','FlangePCBStudy','FlexibleLinkSpace']
fixed={n:d.getObject(n).Shape.copy()for n in rr['parts']if n not in superseded}
parts={};mates={};inputs={};skipped=[]
for domain in ['body','flange']:
    f=P/(domain+'-mechanical-input.json');r=json.loads(f.read_text());assert r['native_board_sha256']==sha(P/(domain+'-r12.kicad_pcb'));inputs[f.name]=sha(f)
    points=[A.Vector(x,y,-.5)for x,y in r['outline_mechanical_xy_mm']];wire=Part.makePolygon(points+[points[0]])
    parts[domain+'_substrate']=Part.Face(wire).extrude(A.Vector(0,0,1))
    for p in r['placements']:
        bb=p['body_xy_mm'];z0,z1=p['z_bounds_mm']
        if not bb or z1-z0<1e-5:skipped.append({'ref':p['ref'],'reason':'Zero-height solderjumper or absent physicalFab; electrical pads remain in native PCB'});continue
        parts[p['ref']]=Part.makeBox(bb[2]-bb[0],bb[3]-bb[1],z1-z0,A.Vector(bb[0],bb[1],z0))
    for m in r['mates']:
        bb=m['xy_bounds_mm'];z0,z1=m['z_bounds_mm'];shape=Part.makeBox(bb[2]-bb[0],bb[3]-bb[1],z1-z0,A.Vector(bb[0],bb[1],z0))
        mates['Mate_'+m['ref']]={'shape':shape,'service_only':m['service_only']}
def volume(a,b):
    aa=a.BoundBox;bb=b.BoundBox
    if any(min(getattr(aa,k+'Max'),getattr(bb,k+'Max'))<=max(getattr(aa,k+'Min'),getattr(bb,k+'Min'))+1e-7 for k in'XYZ'):return 0
    return a.common(b).Volume
body_hits=[];mate_hits=[];tested=0
for n,s in parts.items():
    for target,t in fixed.items():
        tested+=1;v=volume(s,t)
        if v>1e-5:body_hits.append({'new':n,'fixed':target,'intersection_mm3':v})
for n,record in mates.items():
    for target,t in dict(fixed,**parts).items():
        if target==n[5:]:continue
        v=volume(record['shape'],t)
        if v>1e-5:mate_hits.append({'mate':n,'target':target,'intersection_mm3':v,'service_only':record['service_only']})
A.closeDocument(d.Name);assert sha(nf)==before and all(sha(P/f)==h for f,h in inputs.items())
out={'source_R11_native_sha256':before,'mechanical_inputs_sha256':inputs,'reviewer_sha256':sha(Path(__file__)),
     'retained_context_roles':list(fixed),'superseded_reservations':superseded,'new_envelopes_including_substrates':len(parts),'zero_height_records':skipped,
     'body_fixed_pairs_tested':tested,'body_intersections':body_hits,'mate_intersections':mate_hits,
     'scope':'Actual saved R12poses/EdgeCuts, Fab/height envelopes and nominal mating references vs unchanged20roleR11context. No source material removed. ServiceJ4mate requires its own open-cover context; no wire/termination/force/actual fit acceptance.'}
(P/'mechanical-fit.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'body_hits':body_hits,'mate_hits':mate_hits,'envelopes':len(parts)},indent=2),flush=True)
