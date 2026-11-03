"""Conditional OEM pack/mate geometry screen; unmeasured lead exits remain explicit.

No source mutation, pack adoption or claim that legacy catalog nominal is a
controlled current maximum. Receives actual parts later against the reserved fit.
"""
from pathlib import Path
import hashlib,itertools,json,math,sys
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/'hardware/cad/pack-assembly-r37/body-anchor-b';OUT=Path(sys.argv[1]).resolve();OUT.mkdir(parents=True,exist_ok=True);assert not any(OUT.iterdir());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();r=json.loads((SOURCE/'geometry-report.json').read_text());source=SOURCE/'PackBodyAnchorR37.FCStd';before=sha(source);assert before==r['native_sha256']and r['all_static_screens_clear'];D=A.openDocument(str(source));fixed={n:D.getObject(n).Shape.copy()for n in r['fixed_roles']+list(r['new_roles'])}
def line(edges,a,b):
 if(a-b).Length>1e-8:edges.append(Part.makeLine(a,b))
 return b
def s_turn(edges,start,direction,delta,radius):
 amount=delta.Length
 if amount<1e-8:return start
 assert amount<4*radius
 n=delta/amount;t=math.acos(1-amount/(2*radius));middle=start+direction*(radius*math.sin(t))+n*(radius*(1-math.cos(t)));end=start+direction*(2*radius*math.sin(t))+delta
 first_mid=start+direction*(radius*math.sin(t/2))+n*(radius*(1-math.cos(t/2)));second_mid=end-direction*(radius*math.sin(t/2))-n*(radius*(1-math.cos(t/2)))
 edges.extend([Part.Arc(start,first_mid,middle).toShape(),Part.Arc(middle,second_mid,end).toShape()]);return end
def swept(edges,radius):
 path=Part.Wire(edges);start=edges[0].Vertexes[0].Point;axis=edges[0].tangentAt(edges[0].FirstParameter);profile=Part.Wire([Part.makeCircle(radius,start,axis)]);s=path.makePipeShell([profile],True,True);assert s.isValid()and len(s.Solids)==1;return s
def vol(a,b):
 u,v=a.BoundBox,b.BoundBox
 if any(min(getattr(u,k+'Max'),getattr(v,k+'Max'))<=max(getattr(u,k+'Min'),getattr(v,k+'Min'))+1e-7 for k in 'XYZ'):return 0.
 return a.copy().common(b.copy()).Volume
def rotated_box(x0,x1,width,thick,y,z,alpha):
 s=Part.makeBox(x1-x0,width,thick,A.Vector(x0,-width/2,-thick/2));s.rotate(A.Vector(),A.Vector(1,0,0),alpha);s.translate(A.Vector(0,y,z));return s
cases=[]
for alpha,zc,yc in itertools.product([20.],[-11.6,-12.0,-12.4],[-20.,-19.4,-18.8]):
 ar=math.radians(alpha);n=A.Vector(0,math.cos(ar),math.sin(ar));beta=math.radians(alpha+40);v=A.Vector(0,math.cos(beta),math.sin(beta));root=A.Vector(7,-20.,-9.);delta=A.Vector(0,yc-root.y,zc-root.z);theta=math.acos(1-delta.Length/22.);arc_length=22.*theta;straight=21.8-arc_length;assert straight>0
 shrink_root_x=7-22.*math.sin(theta)-straight;stock_back_x=shrink_root_x-4.;male_back_x=stock_back_x-14.8
 housing=rotated_box(male_back_x-.8,stock_back_x+.8,8.8,4.2,yc,zc,alpha)
 shrink=rotated_box(stock_back_x-.8,stock_back_x+4.,6.4,4.2,yc,zc,alpha);coupler=housing.fuse(shrink).removeSplitter();assert coupler.isValid()and len(coupler.Solids)==1
 shapes={'coupler_process_budget':coupler};plans=[]
 for pin,sign in [(1,1),(2,-1)]:
  start=root+n*sign;edges=[];end=s_turn(edges,start,A.Vector(-1,0,0),delta,11.);end=line(edges,end,A.Vector(shrink_root_x,yc,zc)+n*sign);length=sum(e.Length for e in edges);assert abs(length-21.8)<1e-6;shapes['stock_lead_'+str(pin)]=swept(edges,.9)
  mstart=A.Vector(male_back_x,yc,zc)+n*sign;medges=[];umid=mstart+A.Vector(-4.75,0,0)+v*4.75;uend=mstart+v*9.5;medges.append(Part.Arc(mstart,umid,uend).toShape());mend=s_turn(medges,uend,A.Vector(1,0,0),n*(sign*.6),4.);rest=18.5-sum(e.Length for e in medges);assert rest>0;mend=line(medges,mend,mend+A.Vector(rest,0,0));shapes['mate_lead_'+str(pin)]=swept(medges,.6)
  joint=Part.makeCylinder(1.25,5.5,A.Vector(mend.x-1.5,mend.y+.35,mend.z),A.Vector(1,0,0));shapes['joint_budget_'+str(pin)]=joint
  plans.append({'pin':pin,'stock_exit_assumption_xyz_mm':list(start),'stock_flexible_length_mm':length,'stock_min_centre_radius_mm':11.,'stock_OD_allowance_mm':1.8,'mate_coated_length_mm':sum(e.Length for e in medges),'mate_min_centre_radius_mm':4.,'mate_OD_allowance_mm':1.2,'mate_coated_end_xyz_mm':list(mend),'mate_bare_target_length_mm':2.5,'mate_free_length_min_reference_mm':21.,'mate_loop_plane_unit_xyz':list(v)})
 hits=[];pairs=0
 for name,s in shapes.items():
  for m,a in fixed.items():
   pairs+=1;overlap=vol(s,a)
   if overlap>1e-5:hits.append({'new':name,'fixed':m,'intersection_mm3':overlap})
 own=[]
 for(a,s),(b,t)in itertools.combinations(shapes.items(),2):
  # Own wire insertion at the process housing is intentional, only where
  # the actual swept allowance meets the reserved housing/strain volume.
  if 'coupler_process_budget'in[a,b]:continue
  if any({a,b}=={'mate_lead_'+str(pin),'joint_budget_'+str(pin)}for pin in [1,2]):continue
  overlap=vol(s,t);gap=s.distToShape(t)[0]
  own.append({'a':a,'b':b,'intersection_mm3':overlap,'surface_gap_mm':gap})
 modifiable=['ConnectedPackTailLeftHubR34','ServiceablePackHubR36']
 hard=[q for q in hits if q['fixed']not in modifiable]
 case={'alpha_X_deg':alpha,'coupler_centre_YZ_mm':[yc,zc],'male_housing_back_X_mm':male_back_x,'stock_housing_back_X_mm':stock_back_x,'shrink_flexible_boundary_X_mm':shrink_root_x,'plans':plans,'fixed_comparisons':pairs,'intersections':hits,'wire_pair_checks':own,'hard_intersections':hard,'all_nominal_static_clear':not hits and not any(q['intersection_mm3']>1e-5 for q in own),'only_modifiable_hub_hits':not hard and not any(q['intersection_mm3']>1e-5 for q in own)}
 cases.append(case);print('case',alpha,zc,'hard',[(q['new'],q['fixed'],round(q['intersection_mm3'],4))for q in hard],'all',len(hits),'wire overlaps',sum(q['intersection_mm3']>1e-5 for q in own),flush=True)
out={'source_native_sha256':before,'screener_sha256':sha(Path(__file__)),'case_count':len(cases),'cases':cases,'reference_assumptions':{'pack_body':'Published33x8x20XYZ gauge, not selected pack','pack_exit_centre_xyz_mm':[7,-20,-9],'pack_exit_pair_axis':'Assumed same rotated pin axis as connector; photos show corner exit but no controlled 3D coordinates','published_pack_cable_including_female_connector_mm':35.,'catalog_female_length_mm':9.2,'shrink_rigid_extension_assumption_mm':4.,'conditional_flexible_stock_lead_mm':21.8,'catalog_mated_housing_nominal_mm':14.8,'reserved_mated_housing_LWT_mm':[16.4,8.8,4.2],'spare_mate_total_free_wire_mm':'22+/-1 incl2+/-0.5bare; proposed trim/strip requires actual wire/process qualification'},'scope':'Conditional OEM-part spatial screen only. Pack lead exit, actual bendable length/OD, shrink envelope and bend allowance are assumptions awaiting actual pack/OEM drawing or receiving data. No current fit acceptance, complete body power extensions/joints/retention/loading or battery adoption. Existing source native and human BOM unchanged.'};(OUT/'placement-screen.json').write_text(json.dumps(out,indent=2)+'\n');A.closeDocument(D.Name);assert sha(source)==before;print('nominal clear',sum(q['all_nominal_static_clear']for q in cases),'hub-only',sum(q['only_modifiable_hub_hits']for q in cases),flush=True)
