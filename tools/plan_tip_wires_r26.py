"""C2 individual tip-wire routes; exact Bezier poles plus a circular bend."""
from pathlib import Path
import json,hashlib,math,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];OUT=Path(sys.argv[1]).resolve();OUT.parent.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
PCB=ROOT/'hardware/pcb/stackup-r23/candidate-d';ip=PCB/'layout-inspection.json';i=json.loads(ip.read_text());j5=next(q for q in i['boards']['body']['placements']if q['ref']=='J5');mate=next(q for q in i['boards']['body']['mates']if q['ref']=='J5')
tip=ROOT/'hardware/pcb/tip-r1/buttplug-tip-r1.kicad_pcb';validation=ROOT/'hardware/pcb/tip-r1/validation-tip-r1.json';t=json.loads(validation.read_text())
assert sha(tip)==t['source_sha256'][str(tip.relative_to(ROOT))]
assert sha(PCB/'body/body-r23.kicad_pcb')==i['boards']['body']['native_board_sha256']
tip_face=93.41;bare_radius=.13;wire_radius=.30;end_y=tip_face-bare_radius;arc_start_y=end_y-2.5
knots=[mate['xy_bounds_mm'][3],55.975,66.475,70.2,76.0,88.3,arc_start_y]
assert abs(knots[0]-54.975)<1e-6
def ramp(y,a,b):
 t=(y-a)/(b-a)
 if t<=0:return 0.,0.,0.
 if t>=1:return 1.,0.,0.
 return 10*t**3-15*t**4+6*t**5,(30*t*t-60*t**3+30*t**4)/(b-a),(60*t-180*t*t+120*t**3)/(b-a)**2
def state(y,x0,xside,xend,lane):
 x,x1,x2=x0,0.,0.;z,z1,z2=2.1,0.,0.
 for a,b,delta,which in [(55.975,66.475,xside-x0,'x'),(55.975,66.475,-1.2*lane,'z'),(70.2,88.3,xend-xside,'x'),(66.475,76.,-7.05+1.2*lane,'z')]:
  f,g,h=ramp(y,a,b)
  if which=='x':x+=delta*f;x1+=delta*g;x2+=delta*h
  else:z+=delta*f;z1+=delta*g;z2+=delta*h
 return np.array([x,y,z]),np.array([x1,1.,z1]),np.array([x2,0.,z2])
rows=[]
for pin in range(1,5):
 p=next(v for v in j5['pads']if v['n']==str(pin));net=p['net'];assert t['footprints']['J101']['pad_nets'][str(pin)]==net
 x0=p['xy_mm'][0];xside=14.8-pin;xend=-(pin-2.5)*1.4
 segments=[]
 for a,b in zip(knots,knots[1:]):
  p0,d0,e0=state(a,x0,xside,xend,pin-1);p5,d5,e5=state(b,x0,xside,xend,pin-1);L=b-a
  p1=p0+L*d0/5;p2=2*p1-p0+L*L*e0/20;p4=p5-L*d5/5;p3=2*p4-p5+L*L*e5/20
  segments.append({'kind':'bezier5','Y_span_mm':[a,b],'poles_xyz_mm':[p.tolist()for p in [p0,p1,p2,p3,p4,p5]]})
 ts=np.linspace(knots[0],knots[-1],10001);states=[state(y,x0,xside,xend,pin-1)for y in ts]
 radius=min((np.linalg.norm(d)**3/np.linalg.norm(np.cross(d,e))for p,d,e in states if np.linalg.norm(np.cross(d,e))>1e-12),default=math.inf)
 arc={'kind':'circular_arc','center_xyz_mm':[xend,arc_start_y,-2.45],'radius_mm':2.5,'start_xyz_mm':[xend,arc_start_y,-4.95],'mid_xyz_mm':[xend,arc_start_y+2.5/math.sqrt(2),-2.45-2.5/math.sqrt(2)],'end_xyz_mm':[xend,end_y,-2.45]}
 path=np.array([p for p,d,e in states]);length=float(np.linalg.norm(np.diff(path,axis=0),axis=1).sum()+2.5*math.pi/2)
 rows.append({'pin':pin,'net':net,'J5_wire_exit_nominal_xyz_mm':[x0,knots[0],2.1],'J101_pad_center_xyz_mm':[xend,tip_face,-1.35],'insulation_OD_allowance_mm':.6,'bare_OD_allowance_mm':.26,'curves':segments+[arc],'bare_segment_xyz_mm':[[xend,end_y,-2.45],[xend,end_y,-1.35]],'minimum_sampled_polynomial_centerline_radius_mm':radius,'minimum_analytic_circular_radius_mm':2.5,'sampled_insulated_centerline_length_mm':length,'bare_length_mm':1.1})
 print(pin,net,'min polynomial R',radius,'insulated length',length,flush=True)
out={'planner_sha256':sha(Path(__file__)),'source_body_inspection_sha256':sha(ip),'source_native_tip_board_sha256':sha(tip),'source_tip_validation_sha256':sha(validation),'tip_pose_mapping':'globalX=-localX, globalZ=-localY; component planeY93.41; same native circuit/board, moved-.77Y','J5_wire_exit_basis':'PinX from nativeJ5 pad centres; exitY from existing nominal mate allowance; Z2.1 is an assumed wire centre, not controlled manufacturer datum. Actual housing/contact/egress and crimp still need confirmation.','wire_candidate':'Accu-Glass113094; OD.6/bare.26 are allowances, not controlled maxima; radius target2.5mm','wires':rows,'scope':'C2 quintic-polynomial transitions encoded as exact degree5 Bezier poles, then an exact R2.5 circular bend and bare solder leg. Curvature is sampled for polynomial paths; physical bends, service slack, true terminal departures/strain relief/crimp and thermal/electrical/physical acceptance remain open. Lengths are installed path estimates, not cut lengths.'}
OUT.write_text(json.dumps(out,indent=2)+'\n')
