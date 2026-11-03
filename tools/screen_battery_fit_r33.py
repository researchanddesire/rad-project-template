"""Screen a published protected-pack option against fixed current geometry.

The20x33x8 option and .5mm sizing allowance are not pack adoption or supplier
maxima. Rebuilding carrier, lid, supports and affected wires remains required.
"""
from pathlib import Path
import sys,json,hashlib,itertools
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'hardware/cad/pack-retention-r32/candidate-e';OUT=Path(sys.argv[1]).resolve();OUT.mkdir(parents=True,exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text());r=read(P/'geometry-report.json');f=P/'PackRetentionR32.FCStd';before=sha(f);assert before==r['native_sha256'];D=A.openDocument(str(f));coverage=read(P/'body-group-coverage.json');moving_names=[q['CAD_role']for q in coverage['physical_component_rows']]+['BodyPCB_R17','PCBOnlyKeeperR25','KeeperScrew_1','KeeperScrew1']
moving_names+=[n for n,q in r['mates'].items()if q['bounds_xyz_mm'][1]>20]
physical={n:D.getObject(n).Shape.copy()for n in dict(r['parts'],**r['mates'],**r['allowances'])};wire_names={n for n in physical if n.startswith(('InterboardWire','TipWire','TipBareWire','TipSolderAllowance'))};omitted={n for n in physical if n.startswith('Pack')}|wire_names|set(moving_names)
fixed={n:s for n,s in physical.items()if n not in omitted}
for n in ['TipReceiverR26','SupportedWireCombR26']:fixed['preserved_'+n]=D.getObject(n).Shape.copy()
rear=physical['PackRetainingCarrierR32'].copy().common(Part.makeBox(100,66,100,A.Vector(-50,-40,-50)));fixed['preserved_rear_carrier_Y_below26']=rear
ntc_names=[n for n in physical if n.startswith(('PackNTCHeadR32','PackNTCLeadStub','PackNTCContactFilm'))];ntc={n:physical[n]for n in ntc_names}
for n in ['PackNTCMotionR32_1','PackNTCMotionR32_2']:ntc[n]=D.getObject(n).Shape.copy()
for i in [1,2]:ntc['provisional_guard_'+str(i)]=D.getObject('PackNTCGuardBlankR32_'+str(i)).Shape.copy().cut(D.getObject('PackSensorWindowToolsR32').Shape.copy())
def vol(a,b):
 u,v=a.BoundBox,b.BoundBox
 if any(min(getattr(u,k+'Max'),getattr(v,k+'Max'))<=max(getattr(u,k+'Min'),getattr(v,k+'Min'))+1e-7 for k in 'XYZ'):return 0.
 return a.copy().common(b.copy()).Volume
def shifted(s,z,angle):
 s=s.copy();s.translate(A.Vector(0,0,z));s.rotate(A.Vector(0,54,0),A.Vector(1,0,0),angle);return s
def hits(moving,against):
 rows=[]
 for n,a in moving.items():
  for m,b in against.items():
   v=vol(a,b)
   if v>1e-5:rows.append({'moving':n,'fixed':m,'intersection_mm3':v})
 return rows
rows=[];boardposes=[]
for dz,angle in itertools.product([1.5,2.,2.5,3.,3.5],[-6.,-8.,-10.,-12.,-14.]):
 body={n:shifted(physical[n],dz,angle)for n in moving_names};bh=hits(body,fixed);sensors={n:shifted(s,dz-2,angle)for n,s in ntc.items()};nh=hits(sensors,fixed);boardposes.append({'body_PCB_delta_Z_mm':dz,'pitch_X_deg':angle,'hits':bh,'sensor_and_guard_hits':nh});print('PCB Z/pitch',dz,angle,'bodyhits',bh,'NTChits',nh,flush=True)
 for y in [28.,28.5,29.,29.5,30.]:
  top=-4+dz;bottom=top-8;pack=Part.makeBox(20,33,8,A.Vector(-10,y,bottom));budget=Part.makeBox(21,34,9,A.Vector(-10.5,y-.5,bottom-.5));outer=Part.makeBox(22,35,10,A.Vector(-11,y-1,bottom-1))
  for q in [pack,budget,outer]:q.rotate(A.Vector(0,54,0),A.Vector(1,0,0),angle)
  ph=hits({'pack_option':pack,'pack_sizing_budget':budget},dict(fixed,**body));fh=hits({'provisional_outer_holder_box':outer},fixed);clear=not bh and not nh and not ph;rows.append({'body_PCB_delta_Z_mm':dz,'pitch_X_deg':angle,'rotation_pivot_xyz_mm':[0,54,0],'pack_minimum_Y_before_pitch_mm':y,'pack_bounds_before_pitch_xyz_mm':[-10,y,bottom,10,y+33,top],'sizing_budget_bounds_before_pitch_xyz_mm':[-10.5,y-.5,bottom-.5,10.5,y+33.5,top+.5],'hits':ph,'outer_holder_box_hits':fh,'all_fixed_geometry_rest_screens_clear':clear,'outer_holder_box_clear_of_fixed_geometry':not fh});print('option',dz,angle,y,'hits',ph,'framehits',fh,'clear',clear,flush=True)
A.closeDocument(D.Name);assert sha(f)==before;out={'source_R32_native_sha256':before,'source_R32_report_sha256':sha(P/'geometry-report.json'),'source_body_group_coverage_sha256':sha(P/'body-group-coverage.json'),'screener_sha256':sha(Path(__file__)),'reference_pack_url':'https://store.bitcraze.io/products/350mah-lipo-battery','reference_pack_published_XYZ_mm':[20,33,8],'battery_selection':'OPEN','moving_body_group':moving_names,'fixed_geometry':list(fixed),'requires_rebuild_roles':sorted(omitted-set(moving_names)),'board_pose_rows':boardposes,'pack_pose_rows':rows,'clear_pose_count':sum(q['all_fixed_geometry_rest_screens_clear']for q in rows),'clear_with_outer_holder_box_count':sum(q['all_fixed_geometry_rest_screens_clear']and q['outer_holder_box_clear_of_fixed_geometry']for q in rows),'scope':'Static pose screen of published body-size option plus .5mm engineering sizing budget, rigid bodyPCB/keeper/mates shift then pitch around(0,54,0), and matching provisionalNTC/guard transforms. Separate outer22x35x10 holder box vs fixed geometry only reserves .5mm wall outside sizing box, not a fabricated support. Preserves metal exterior, independent motor mount/conditional lead flare, flange and tip receiver/comb. Old carrier/lid/gauge and all affected wire shapes omitted pending rebuild, not accepted as compatible. No selected pack, controlled max/growth, real leads/connector, support/load/seal/electrical/runtime/physical or assembly acceptance.'};(OUT/'pose-screen.json').write_text(json.dumps(out,indent=2)+'\n');print('clear poses',out['clear_pose_count'],'with outer holder',out['clear_with_outer_holder_box_count'],flush=True)
