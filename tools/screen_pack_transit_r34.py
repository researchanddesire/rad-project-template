"""Read-only neck transit comparison: four larger wires or thin flex strip.

Only straight corridor occupancy; not bent flex, harness or cable acceptance.
"""
from pathlib import Path
import sys,json,hashlib,itertools
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'hardware/cad/battery-fit-r33/candidate-f';OUT=Path(sys.argv[1]).resolve();OUT.mkdir(parents=True,exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();r=json.loads((P/'geometry-report.json').read_text());f=P/'FlangePackR33.FCStd';before=sha(f);assert before==r['native_sha256'];D=A.openDocument(str(f));fixed={n:D.getObject(n).Shape.copy()for n in dict(r['parts'],**r['mates'],**r['allowances'])}
def vol(a,b):
 u,v=a.BoundBox,b.BoundBox
 if any(min(getattr(u,k+'Max'),getattr(v,k+'Max'))<=max(getattr(u,k+'Min'),getattr(v,k+'Min'))+1e-7 for k in 'XYZ'):return 0.
 return a.copy().common(b.copy()).Volume
rows=[]
for x in [-1.,0.,1.]:
 for z in [-4.8,-4.2,-3.6,-3.,-2.4,-1.8]:
  for kind in ['four_D1_15_wires_two_by_two','horizontal_thin_flex_space_claim']:
   if kind=='four_D1_15_wires_two_by_two':s=Part.makeCompound([Part.makeCylinder(.575,42.9,A.Vector(x+a,-18,z+b),A.Vector(0,1,0))for a,b in itertools.product([-.8,.8],repeat=2)])
   else:s=Part.makeBox(4.5,42.9,.25,A.Vector(x-2.25,-18,z-.125))
   hits=[]
   for n,b in fixed.items():
    v=vol(s,b)
    if v>1e-5:
     c=s.copy().common(b.copy());bb=c.optimalBoundingBox(False,False);hits.append({'fixed':n,'intersection_mm3':v,'intersection_bounds_xyz_mm':[getattr(bb,k)for k in ['XMin','YMin','ZMin','XMax','YMax','ZMax']]})
   row={'kind':kind,'centre_XZ_mm':[x,z],'Y_range_mm':[-18,24.9],'hits':hits,'clear':not hits};rows.append(row);print(kind,x,z,hits,flush=True)
A.closeDocument(D.Name);assert sha(f)==before;(OUT/'transit-screen.json').write_text(json.dumps({'source_R33_native_sha256':before,'source_report_sha256':sha(P/'geometry-report.json'),'screener_sha256':sha(Path(__file__)),'fixed_roles':list(fixed),'rows':rows,'scope':'Unchanged native physical parts and nominal mates/allowances versus straight42.9mm transit claims only. Flex.25x4.5 section is a provisional space claim, not a stackup/part, bent/developed geometry, copper/ampacity, exit/termination, restraint, assembly/flex life or physical acceptance. Fourwire1.15 is connector-budget comparison, not selected wire maximum.'},indent=2)+'\n');print('clear claims',sum(q['clear']for q in rows),flush=True)
