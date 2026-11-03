"""Route the four unresolved K/L nets before 3V3 and other signal trunks.

Start/end components come from a fresh native DRC report. Grid points must lie
inside their actual same-net copper. No pad/net/outline/rule changes are made.
"""
from pathlib import Path
import sys,json,re,math,heapq,hashlib
import numpy as np
from shapely import points,intersects,linestrings,prepare
from shapely.geometry import Polygon,Point,LineString
from shapely.ops import unary_union
gp=Path(sys.argv[1]);report=Path(sys.argv[2]);out=Path(sys.argv[3]);g=json.loads(gp.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
layers=['F.Cu','In1.Cu','B.Cu'];step=.05
edges=g['outline_edges_xy_mm'][:];a,c=edges.pop();outline=[a,c]
while edges:
 i,a,c=next((i,a,c)for i,(a,c)in enumerate(edges)if a==outline[-1]or c==outline[-1]);edges.pop(i);outline.append(c if a==outline[-1]else a)
board=Polygon(outline);xmin,ymin,xmax,ymax=board.bounds;xs=np.arange(xmin,xmax+step/2,step);ys=np.arange(ymin,ymax+step/2,step);nx=len(xs);ny=len(ys);xx,yy=np.meshgrid(xs,ys);grid=np.column_stack((xx.ravel(),yy.ravel()));pp=points(grid);size=len(grid);pads=[(p,unary_union([Polygon(q)for q in p['polygons']]))for p in g['pads']];routes=g['routes'][:];new=[];results=[]
blocks=report.read_text().split('[unconnected_items]:')[1:];requests=[]
for block in blocks:
 rows=re.findall(r'@\(([\d.]+) mm, ([\d.]+) mm\): .*?\[([^]]+)\].*? on (F.Cu|B.Cu|In1.Cu|F.Cu - B.Cu)',block)
 if len(rows)<2:continue
 a,b=rows[:2];assert a[2]==b[2];requests.append((a[2],[(round(float(r[0])-100,6),round(130-float(r[1]),6),r[3])for r in [a,b]]))
priority={n:i for i,n in enumerate(['SYS','PACK_P','VBUS_CHG','MOTOR_3V7','MOTOR_P','MOTOR_N','3V3'])};hard={'ACCEL_INT_N','PACK_NTC','REG1_PS','TEMP_COLD_IN'}
requests.sort(key=lambda r:priority.get(r[0],20) if r[0] in priority and r[0]!='3V3' else 8 if r[0] in hard else 9 if r[0]=='3V3' else 20)
def shapes(net):
 items=[(s,set(p['layers']))for p,s in pads if p['net']==net and p['layers']]
 for t in routes:
  if t['net']!=net:continue
  if t['kind']=='via':items.append((Point(t['position']).buffer(t['diameter']/2),set(layers)))
  else:items.append((LineString([t['start'],t['end']]).buffer(t['width']/2),{t['layer']}))
 parent=list(range(len(items)))
 def find(i):
  while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
  return i
 for i,(s,l)in enumerate(items):
  for j,(q,m)in enumerate(items[:i]):
   if l&m and s.distance(q)<.00001:parent[find(i)]=find(j)
 return items,[find(i)for i in range(len(items))]
def compress(path):
 if len(path)<3:return path
 answer=[path[0]];last=None
 for a,b,c in zip(path,path[1:],path[2:]):
  u=(round(b[0]-a[0],5),round(b[1]-a[1],5));v=(round(c[0]-b[0],5),round(c[1]-b[1],5))
  if u!=v:answer.append(b)
 answer.append(path[-1]);return answer
for net,endpoints in requests:
 if net=='GND':continue
 items,groups=shapes(net);ends=[]
 for x,y,side in endpoints:
  ids=[i for i,(s,l)in enumerate(items)if side in l];i=min(ids,key=lambda i:items[i][0].distance(Point(x,y)));assert items[i][0].distance(Point(x,y))<.001,(net,x,y);ends.append(groups[i])
 if ends[0]==ends[1]:results.append({'net':net,'endpoints':endpoints,'status':'already_connected_by_planned_copper'});continue
 width=.6 if net in priority and net!='3V3'else .3 if net=='3V3'else .15
 via_diameter=.5;via_drill=.2;vr=via_diameter/2;hr=via_drill/2
 obs={l:[]for l in layers};vobs=[];ownvias=[]
 for p,s in pads:
  if p['layers']:vobs.append(s.buffer(hr+.006 if p['net']==net else max(vr+.106,hr+.256)))
  if p['paste']:vobs.append(s.buffer(hr+.006))
  if p['net']!=net:
   for l in set(p['layers'])&set(layers):obs[l].append(s.buffer(width/2+.106))
 for t in routes:
  same=t['net']==net
  if t['kind']=='via':
   s=Point(t['position']);vobs.append(s.buffer(hr+t['drill']/2+.256 if same else max(vr+t['diameter']/2+.106,hr+t['diameter']/2+.256,vr+t['drill']/2+.256)))
   if same:ownvias.append(t)
   else:
    for l in layers:obs[l].append(s.buffer(max(t['diameter']/2+.106,t['drill']/2+.256)+width/2))
  elif not same:
   s=LineString([t['start'],t['end']]);vobs.append(s.buffer(max(vr+.106,hr+.256)+t['width']/2))
   if t['layer']in obs:obs[t['layer']].append(s.buffer(.106+(width+t['width'])/2))
 for z in g['rules']:
  for poly in z['polygons']:
   s=Polygon(poly)
   if z['no_vias']:vobs.append(s.buffer(vr+.006))
   if z['no_tracks']:
    for l in set(z['layers'])&set(layers):obs[l].append(s.buffer(width/2+.001))
 obstacle={l:unary_union(obs[l])for l in layers}
 for shape in obstacle.values():prepare(shape)
 allowed=np.stack([intersects(board.buffer(-.301-width/2),pp)&~intersects(obstacle[l],pp)for l in layers])
 viaok=intersects(board.buffer(-(.306+vr)),pp)&~intersects(unary_union(vobs),pp)
 existing=set()
 for v in ownvias:
  q=np.rint((np.array(v['position'])-[xmin,ymin])/step).astype(int);idx=q[1]*nx+q[0]
  if 0<=idx<size:existing.add(idx)
 source=np.zeros((3,size),bool);target=source.copy()
 for li,l in enumerate(layers):
  source[li]=intersects(unary_union([s for (s,ls),c in zip(items,groups)if c==ends[0]and l in ls]),pp)&allowed[li]
  target[li]=intersects(unary_union([s for (s,ls),c in zip(items,groups)if c==ends[1]and l in ls]),pp)&allowed[li]
 starts=np.flatnonzero(source.ravel());goals=np.flatnonzero(target.ravel());found=None
 if len(starts)and len(goals):
  # Every complete grid edge is checked, rather than excluding an extra
  # half-cell diagonal around all copper. Native .1mm clearance +.006 margin
  # and minimum .15mm signal width remain unchanged.
  clear_edges={};ix=np.arange(size)%nx;iy=np.arange(size)//nx
  for li,l in enumerate(layers):
   for dx,dy in [(1,0),(0,1),(1,1),(-1,1)]:
    mask=(ix+dx>=0)&(ix+dx<nx)&(iy+dy>=0)&(iy+dy<ny)&allowed[li];ids=np.flatnonzero(mask);offset=dx+dy*nx;ids=ids[allowed[li,ids+offset]];segments=linestrings(np.stack([grid[ids],grid[ids+offset]],axis=1));ok=np.zeros(size,bool);ok[ids]=~intersects(obstacle[l],segments);clear_edges[li,dx,dy]=ok
  goalxy=grid[goals%size];lo=goalxy.min(axis=0);hi=goalxy.max(axis=0)
  def heuristic(index):
   xy=grid[index%size];return math.hypot(max(lo[0]-xy[0],0,xy[0]-hi[0]),max(lo[1]-xy[1],0,xy[1]-hi[1]))
  cost=np.full(3*size,np.inf);previous=np.full(3*size,-1,dtype=np.int32);heap=[]
  for i in starts:cost[i]=0;heap.append((heuristic(i),0,int(i)))
  heapq.heapify(heap);flatallowed=allowed.ravel();flattarget=target.ravel()
  while heap:
   _,c,u=heapq.heappop(heap)
   if c>cost[u]+1e-9:continue
   if flattarget[u]:found=u;break
   li,idx=divmod(u,size);y,x=divmod(idx,nx);neighbors=[]
   for dx,dy in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]:
    if 0<=x+dx<nx and 0<=y+dy<ny:
     v=u+dx+dy*nx
     ex,ey,base=(dx,dy,idx)if dy>0 or dy==0 and dx>0 else(-dx,-dy,v%size)
     if clear_edges[li,ex,ey][base]:neighbors.append((v,step*math.hypot(dx,dy)))
   if viaok[idx]or idx in existing:neighbors.extend((j*size+idx,2.0)for j in range(3)if j!=li)
   for v,w in neighbors:
    cc=c+w
    if flatallowed[v]and cc<cost[v]-1e-9:cost[v]=cc;previous[v]=u;heapq.heappush(heap,(cc+heuristic(v),cc,v))
 if found is None:results.append({'net':net,'endpoints':endpoints,'status':'NO_GRID_PATH','width_mm':width});print(net,'NO_GRID_PATH',flush=True);continue
 chain=[];u=found
 while u!=-1:chain.append(u);u=int(previous[u])
 chain.reverse();added=[];section=[];lastlayer=None;used=set()
 def finish():
  if len(section)<2:return
  for a,b in zip(compress(section),compress(section)[1:]):added.append({'kind':'track','net':net,'layer':layers[lastlayer],'width':width,'start':a,'end':b})
 for u in chain:
  li,idx=divmod(u,size);pt=[round(float(z),6)for z in grid[idx]]
  if lastlayer is not None and li!=lastlayer:
   finish();section=[pt]
   if idx not in existing and idx not in used:added.append({'kind':'via','net':net,'position':pt,'diameter':via_diameter,'drill':via_drill});used.add(idx)
  else:section.append(pt)
  lastlayer=li
 finish();routes.extend(added);new.extend(added);results.append({'net':net,'endpoints':endpoints,'status':'planned','width_mm':width,'records':len(added),'new_vias':len(used),'grid_path_cost':float(cost[found])});print(net,'planned',len(added),'records',flush=True)
out.write_text(json.dumps({'planner_sha256':sha(Path(__file__)),'source_geometry_sha256':sha(gp),'source_board_sha256':g['board_sha256'],'source_native_DRC_sha256':sha(report),'grid_step_mm':step,'routing_order':'Power, four unresolved K/L nets, 3V3, remaining signals; no width/rule changes', 'method':'Exact full-segment obstacle checks; .15mm low-current signals, .3mm3V3 and .6mm power; explicit .50/.20mm signal via process with explicit0.25mm hole-to-other-net copper clearance; original spacing rules retained','routes':new,'requests':results,'scope':'Conservative discrete F/In1/B path plan from actual same-net copper components and native missing-connection endpoints. In2 reserved GND. No rule relaxation or acceptance; apply only to a separate candidate and run fresh native DRC, circuit/pad/drill/reference reviews.'},indent=2)+'\n')
