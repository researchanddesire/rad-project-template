"""Prepare four ground-stitch refinements and source-bound remaining pin ports."""
from pathlib import Path
import sys,json,copy,hashlib,math
from shapely.geometry import Point,LineString,Polygon
from shapely.ops import unary_union
gp=Path(sys.argv[1]);first=Path(sys.argv[2]);second=Path(sys.argv[3]);outpath=Path(sys.argv[4]);g=json.loads(gp.read_text());p1=json.loads(first.read_text());p2=json.loads(second.read_text());assert g['board_sha256']==p1['source_board_sha256']==p2['source_board_sha256'];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();routes=g['routes'];locked=g['route_locks'];removed=[];added=p1['routes']+p2['routes'];notes=[]
def key(r):return json.dumps(r,sort_keys=True)
def add_line(net,pts,width,layer):
 for a,c in zip(pts,pts[1:]):added.append({'kind':'track','net':net,'layer':layer,'width':width,'start':a,'end':c})
def remove(r):
 if key(r)not in removed:removed.append(key(r))
def move_ground_via(old,new,reuse=False):
 found=[]
 for r in routes:
  if r['net']!='GND':continue
  if r['kind']=='via'and r['position']==old:
   remove(r);found.append(r)
   if not reuse:q=copy.deepcopy(r);q['position']=new;added.append(q)
  elif r['kind']=='track'and(old==r['start']or old==r['end']):
   remove(r);q=copy.deepcopy(r)
   for k in ['start','end']:
    if q[k]==old:q[k]=new
   added.append(q)
 assert len(found)==1,(old,found);notes.append({'old_ground_via':old,'new_ground_via':new,'reuse_existing':reuse})
move_ground_via([3.65,34.4],[4.3,34.25])
for r in routes:
 if r['kind']=='track'and r['net']=='GND'and {tuple(r['start']),tuple(r['end'])}=={(3.65,46.125),(3.5,45.1)}:remove(r)
assert any(json.loads(r).get('start')==[3.65,46.125]or json.loads(r).get('end')==[3.65,46.125]for r in removed)
added.append({'kind':'via','net':'GND','position':[4.3,46.22],'diameter':.6,'drill':.3});add_line('GND',[[3.65,46.125],[4.3,46.22]],.25,'B.Cu')
move_ground_via([5.95,47.05],[5.75,48.0],reuse=True)
for r in routes:
 if r['net']!='GND':continue
 if r['kind']=='via'and r['position']==[4.75,29.2]:remove(r)
 if r['kind']=='track'and {tuple(r['start']),tuple(r['end'])}in [{(5.35,28.6),(5.35,29.2)},{(5.35,29.2),(4.75,29.2)}]:remove(r)
added.append({'kind':'via','net':'GND','position':[6.85,28.6],'diameter':.6,'drill':.3});add_line('GND',[[5.35,28.6],[6.85,28.6]],.25,'B.Cu')
manual=[('REG1_PS',[3,34.2],[[3,34.7],[3,34.2]],'B.Cu'),('REG2_PS',[4.85,45.2],[[3,45.7],[3.3,45.75],[4.2,45.75],[4.85,45.2]],'B.Cu'),('I2C_SCL',[4.75,29.2],[[4.8,28.6],[4.75,29.2]],'B.Cu'),('MOTOR_IN1',[6.1,47.1],[[6.25,46.25],[6.1,46.65],[6.1,47.1]],'F.Cu')]
for net,p,pts,layer in manual:added.append({'kind':'via','net':net,'position':p,'diameter':.6,'drill':.3});add_line(net,pts,.2,layer)
def shape(r):return Point(r['position'])if r['kind']=='via'else LineString([r['start'],r['end']])
def conflict(a,c):
 if a['net']==c['net']:return False
 if a['kind']==c['kind']=='track'and a['layer']!=c['layer']:return False
 ra=a['diameter']/2 if a['kind']=='via'else a['width']/2;rc=c['diameter']/2 if c['kind']=='via'else c['width']/2
 return shape(a).distance(shape(c))<ra+rc+.1001-1e-6
rip={'CHARGE_STATUS_N'};protected=[]
for a in added:
 for c,l in zip(routes,locked):
  if key(c)in removed:continue
  if conflict(a,c):
   if l:protected.append({'new':a,'protected':c})
   else:rip.add(c['net'])
for i,a in enumerate(added):
 for c in added[i+1:]:
  if conflict(a,c):protected.append({'new':a,'other_new':c})
pad_errors=[]
for a in added:
 for p in g['pads']:
  s=unary_union([Polygon(poly)for poly in p['polygons']]);d=shape(a).distance(s)
  if a['kind']=='via':
   limit=.1501 if p['net']==a['net']else .4001
   if(p['layers']and d<limit-1e-6)or(p['paste']and d<.1501-1e-6):pad_errors.append({'route':a,'ref':p['ref'],'pad':p['number'],'pad_net':p['net'],'distance':d})
  elif a['layer']in p['layers']and a['net']!=p['net']and d<a['width']/2+.1001-1e-6:pad_errors.append({'route':a,'ref':p['ref'],'pad':p['number'],'pad_net':p['net'],'distance':d})
out={'date':'2026-11-01','planner_sha256':sha(Path(__file__)),'source_geometry_sha256':sha(gp),'source_board_sha256':g['board_sha256'],'first_plan_sha256':sha(first),'second_plan_sha256':sha(second),'removed_route_keys':removed,'new_routes':added,'unlocked_nets_to_rip':sorted(rip),'ground_via_moves':notes,'protected_route_conflicts':protected,'pad_geometry_conflicts':pad_errors,'direct_GND_pad_override':['R1','2'],'scope':'Plan explicit pin escapes and four ground refinements. C28/C29 shared local ground via retained; U3ground15 gets its own shorter stitch. U5IN2ground reuses existing ground via; MCground moves outward to free SCL. Remove only unlocked conflicting nets; preserve all other manual copper. Fresh native DRC/reference/drill/process review required.'};outpath.write_text(json.dumps(out,indent=2)+'\n');print('New records',len(added),'removed',len(removed),'ripnets',sorted(rip),'protected conflicts',len(protected),'pad conflicts',len(pad_errors),flush=True)
