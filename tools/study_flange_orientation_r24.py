"""Rigid orientation screen of actual saved flange envelopes, not a flex design.

Reads the verified local native cache and binds it to the retained source and
current PCB inspection. Writes new native studies without changing any source.
"""
from pathlib import Path
import sys, json, hashlib, itertools
sys.path.insert(0, '/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT/'hardware/cad/motor-retention-r21/candidate-c'
PCB = ROOT/'hardware/pcb/stackup-r23/candidate-d'
OUT = Path(sys.argv[2]).resolve()
OUT.mkdir(parents=True, exist_ok=True)
assert not any(OUT.iterdir()), 'Preserve previous attempts'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
r = json.loads((SOURCE/'geometry-report.json').read_text())
inspection = json.loads((PCB/'layout-inspection.json').read_text())
nf = Path(sys.argv[1]).resolve()
assert sha(nf) == r['native_sha256']
flange = inspection['boards']['flange']
assert sha(PCB/'flange/flange-r23.kicad_pcb') == flange['native_board_sha256']
source = A.openDocument(str(nf))
refs = [q['ref'] for q in flange['placements'] if q['body_xy_mm']]
roles = ['FlangePCB_R17'] + ['R17_'+ref for ref in refs] + ['R17Mate_'+m['ref'] for m in flange['mates']]
for q in flange['placements']:
    if not q['body_xy_mm']: continue
    a,b,c,d = q['body_xy_mm']; z,w = q['z_bounds_mm']
    assert max(abs(u-v) for u,v in zip([a,b,z,c,d,w],r['parts']['R17_'+q['ref']]['bounds_xyz_mm'])) < 1e-5
context = ['FlangeCoverLower','FlangeCoverUpper','ServiceCoverReference',
           'HubLeft','HubRight','HubBolt_1','HubBolt1','HubNut_1','HubNut1','KeyedOnePieceBody']

def bounds(shapes):
    b = Part.makeCompound(shapes).BoundBox
    return [getattr(b,k) for k in ['XMin','YMin','ZMin','XMax','YMax','ZMax']]

def intersection(a,b):
    u,v = a.BoundBox,b.BoundBox
    if any(min(getattr(u,k+'Max'),getattr(v,k+'Max')) <= max(getattr(u,k+'Min'),getattr(v,k+'Min'))+1e-7 for k in 'XYZ'): return 0
    return a.copy().common(b.copy()).Volume

base = {n:source.getObject(n).Shape.copy() for n in roles}
bb = bounds(list(base.values()))
center = A.Vector(*[(bb[i]+bb[i+3])/2 for i in range(3)])
cases = [('flat',(0,0,1),0),('roll-x-90',(1,0,0),90),
         ('pitch-y-90',(0,1,0),90),('in-plane-z-90',(0,0,1),90)]
report = {'source_native_sha256':r['native_sha256'],
          'source_geometry_report_sha256':sha(SOURCE/'geometry-report.json'),
          'current_PCB_inspection_sha256':sha(PCB/'layout-inspection.json'),
          'current_flange_native_sha256':flange['native_board_sha256'],
          'builder_sha256':sha(Path(__file__)), 'rotation_center_xyz_mm':list(center),
          'source_roles':roles, 'context_roles':context, 'cases':[],
          'scope':'Exact rigid transforms of saved substrate, Fab-height component and nominal mate shapes at a fixed envelope center. No wire/flex design, connector access, antenna performance, tolerances, continuous motion or physical fit acceptance. Existing covers/hub remain fixed. R21 motor/PCB keeper is rejected and excluded.'}
for label,axis,angle in cases:
    doc = A.newDocument('Flange_'+label.replace('-','_'))
    group = doc.addObject('App::Part','FlangeIsland')
    group.addProperty('App::PropertyString','StudyScope')
    group.StudyScope = report['scope']
    transform = A.Placement(center,A.Rotation(A.Vector(*axis),angle)).multiply(A.Placement(-center,A.Rotation()))
    moving = {}
    for n,s in base.items():
        obj = doc.addObject('PartDesign::Feature',n)
        obj.Shape = s
        obj.Placement = transform.multiply(obj.Placement)
        group.addObject(obj)
        moving[n] = obj
    for n in context:
        obj = doc.addObject('PartDesign::Feature','Context_'+n)
        obj.Shape = source.getObject(n).Shape.copy()
    doc.recompute()
    for n,o in moving.items():
        assert abs(o.Shape.Volume-base[n].Volume)<1e-5,n
        restored=o.Shape.copy()
        restored.Placement=transform.inverse().multiply(restored.Placement)
        assert max(abs(u-v)for u,v in zip(bounds([restored]),bounds([base[n]])))<1e-5,n
    hits=[]
    for n,o in moving.items():
        for m in context:
            v=intersection(o.Shape,source.getObject(m).Shape)
            if v>1e-5: hits.append({'moving':n,'fixed':m,'intersection_mm3':v})
    b=bounds([o.Shape for o in moving.values()])
    if angle==0: assert max(abs(u-v)for u,v in zip(b,bb))<1e-5
    substrate=bounds([moving['FlangePCB_R17'].Shape])
    assert all(o.Shape.isValid() for o in moving.values())
    f=OUT/(label+'.FCStd');doc.saveAs(str(f))
    item={'case':label,'axis':axis,'angle_deg':angle,
          'populated_bounds_xyz_mm':b,'populated_spans_xyz_mm':[b[i+3]-b[i] for i in range(3)],
          'substrate_spans_xyz_mm':[substrate[i+3]-substrate[i] for i in range(3)],
          'fixed_context_intersections':hits,'native_file':f.name,'native_sha256':sha(f)}
    report['cases'].append(item)
    print(label,item['populated_spans_xyz_mm'],'context hits',len(hits),flush=True)
    A.closeDocument(doc.Name)
(OUT/'orientation-screen.json').write_text(json.dumps(report,indent=2)+'\n')
print('saved',OUT,flush=True)
