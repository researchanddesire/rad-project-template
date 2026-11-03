"""Finite actual PCB/part-envelope loading checks in unchanged R11 carrier."""
from pathlib import Path
import argparse,hashlib,json,sys
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part
ROOT=Path(__file__).resolve().parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ap=argparse.ArgumentParser();ap.add_argument('directory',type=Path);args=ap.parse_args();P=args.directory.resolve()
f=ROOT/'hardware/cad/front-load-retention-r11/candidate-c/FrontLoadRetentionR11.FCStd';before=sha(f)
d=A.openDocument(str(f));r=json.loads((P/'body-mechanical-input.json').read_text());assert r['native_board_sha256']==sha(P/'body-r12.kicad_pcb')
points=[A.Vector(x,y,-.5)for x,y in r['outline_mechanical_xy_mm']]
parts={'body_substrate':Part.Face(Part.makePolygon(points+[points[0]])).extrude(A.Vector(0,0,1))}
for p in r['placements']:
    bb=p['body_xy_mm'];z0,z1=p['z_bounds_mm']
    if bb and z1-z0>1e-5:parts[p['ref']]=Part.makeBox(bb[2]-bb[0],bb[3]-bb[1],z1-z0,A.Vector(bb[0],bb[1],z0))
fixed={n:d.getObject(n).Shape.copy()for n in ['CarrierWithRetainingStem','NarrowPackAllowance']}
rows=[]
for axis,offsets in [('Y',list(range(36,-1,-2))),('Z',[12,8,4,2,1,.5,.25,0])]:
    for offset in offsets:
        hits=[]
        for n,shape in parts.items():
            s=shape.copy();s.translate(A.Vector(0,offset if axis=='Y'else 0,offset if axis=='Z'else 0))
            for target,t in fixed.items():
                if not s.BoundBox.intersect(t.BoundBox):continue
                v=s.common(t).Volume
                if v>1e-5:hits.append({'moving':n,'fixed':target,'intersection_mm3':v})
        rows.append({'axis':axis,'offset_mm':offset,'hits':hits})
out={'source_R11_native_sha256':before,'body_input_sha256':sha(P/'body-mechanical-input.json'),'reviewer_sha256':sha(Path(__file__)),
     'moving_parts':list(parts),'fixed_roles':list(fixed),'waiting':['PCB keeper and screws','motor','mating plugs and wires','metal body/cap','flange electronics/hub/covers','tip assembly'],
     'listed_poses':rows,'carrier_top_rail_features':[{'name':o.Name,'type':o.TypeId,'bounds':str(o.Shape.BoundBox)}for o in d.Objects if o.Name.startswith('TopRail')],
     'scope':'Finite rigid poses, actual PCB EdgeCuts/Fab height budgets. Not continuous motion, populated geometry maxima, hands/tools or physical assembly. Both failed routes remain evidence.'}
A.closeDocument(d.Name);assert sha(f)==before
(P/'board-loading-r11.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'poses':len(rows),'poses_with_hits':sum(bool(r['hits'])for r in rows),'examples':[r for r in rows if r['hits']][:2],'top_rails':out['carrier_top_rail_features']},indent=2),flush=True)
