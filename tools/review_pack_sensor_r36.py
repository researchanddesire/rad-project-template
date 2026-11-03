"""Fresh moved-sensor, sizing-reserve, native return/lap and source review."""
from pathlib import Path
import hashlib
import itertools
import json
import sys
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part

ROOT=Path(__file__).resolve().parents[1]
P=Path(sys.argv[1]).resolve()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((P/'geometry-report.json').read_text())
path=P/'ConnectedPackSensorsR36.FCStd'
before=sha(path)
assert before==r['native_sha256']
D=A.openDocument(str(path))
for obj in D.Objects:
    if hasattr(obj,'Shape'):obj.touch()
D.recompute()

def vol(a,b):
    u,v=a.BoundBox,b.BoundBox
    if any(min(getattr(u,k+'Max'),getattr(v,k+'Max'))<=max(getattr(u,k+'Min'),getattr(v,k+'Min'))+1e-7 for k in 'XYZ'):return 0.
    return a.copy().common(b.copy()).Volume

physical={n:D.getObject(n).Shape.copy() for n in r['fixed_roles']+r['new_roles']}
for n,s in physical.items():assert s.isValid()and s.Volume>0,n
moved=[n for n in physical if n.startswith(('PackNTCHeadR33_','PackNTCContactFilmR33_'))]
changed_hubs=[q['replacement'] for q in r['hub_changes'].values()]
hits=[];checked=0
for n in moved:
    for m,s in physical.items():
        if n==m:continue
        checked+=1;v=vol(physical[n],s)
        if v>1e-5:hits.append({'moved_sensor':n,'other':m,'intersection_mm3':v})

module={n for n in physical if n.startswith(('PackNTCHeadR33_','PackNTCContactFilmR33_',
        'FactoryNTCWireR36_','FactoryLapBareR36_','NTCSpliceSpaceR36_',
        'NTCSolderBridgeR36_'))}
module.add('PackPublishedGaugeR33')
reserves={n:D.getObject(n).Shape.copy() for n in ['PackSizingReservationR33','PackNTCMotionR33_1','PackNTCMotionR33_2']}
reserve_hits=[];rc=0
for n,s in reserves.items():
    for m,a in physical.items():
        if m in module:continue
        rc+=1;v=vol(s,a)
        if v>1e-5:reserve_hits.append({'reservation':n,'other':m,'intersection_mm3':v})

lap=[]
for row in r['joint_construction']:
    factory,adapter=physical[row['factory_bare']],physical[row['adapter_bare']]
    gap=factory.distToShape(adapter)[0]
    overlap=vol(factory,adapter)
    joint=D.getObject('NTCSpliceSpaceR36_'+row['pair']).Shape.copy()
    outside=factory.copy().cut(joint.copy()).Volume+adapter.copy().cut(joint.copy()).Volume
    assert overlap<1e-5 and gap>.001 and outside<1e-5,(row['pair'],gap,overlap,outside)
    bridge=physical[row['solder_bridge']]
    assert vol(bridge,factory)<1e-5 and vol(bridge,adapter)<1e-5
    assert bridge.distToShape(factory)[0]<1e-6 and bridge.distToShape(adapter)[0]<1e-6
    lap.append({'pair':row['pair'],'bare_core_gap_mm':gap,'bare_core_overlap_mm3':overlap,
                'cores_outside_joint_budget_mm3':outside,'solder_bridge_touches_both_cores':True})

# Compare exact source shapes for exterior, boards, battery gauge, keeper,
# carrier, motor and all unrelated parts. Declared head/film moves, replaced
# stubs, hub cuts and replaced pigtail wires are excluded explicitly.
source=ROOT/'hardware/cad/pack-harness-r34/pigtail-j/PackPigtailTransitR34.FCStd'
source_report=json.loads((source.parent/'geometry-report.json').read_text())
source_before=sha(source)
assert source_before==source_report['native_sha256']
S=A.openDocument(str(source))
conserved=[]
for n in source_report['fixed_roles']:
    if n not in physical or n in moved or n in ['PackTailLeftHubR34','PackTailRightHubR34']:
        continue
    a=physical[n];b=S.getObject(n).Shape.copy()
    removed=b.copy().cut(a.copy()).Volume;added=a.copy().cut(b.copy()).Volume
    assert abs(removed)<1e-4 and abs(added)<1e-4,(n,removed,added)
    conserved.append(n)
    if len(conserved)%30==0:print('source conserved',len(conserved),flush=True)
out={'native_sha256':before,'reviewer_sha256':sha(Path(__file__)),'source_R34_sha256':source_before,
     'source_roles_conserved':conserved,'source_role_count':len(conserved),
     'moved_sensor_roles':moved,'fresh_moved_sensor_pairs':checked,'moved_sensor_hits':hits,
     'sizing_and_head_reservation_pairs':rc,'reservation_hits':reserve_hits,'separate_lap_core_checks':lap,
     'all_reviewed_screens_clear':not hits and not reserve_hits,
     'scope':'Fresh native recompute, exact unrelated-source material comparison, moved sensor/film and explicit source reservations, separated bare laps and touching solder targets. Installed wire comparison remains the bound builder result. No actual solder/sensor attachment/material/bond/loads, pack power mate, connected loading, sealing, current/thermal or physical acceptance.'}
(P/'saved-review.json').write_text(json.dumps(out,indent=2)+'\n')
A.closeDocument(D.Name);A.closeDocument(S.Name)
assert sha(path)==before and sha(source)==source_before
print('REVIEW moved sensor hits',hits,'reservation hits',reserve_hits,'source count',len(conserved),flush=True)
