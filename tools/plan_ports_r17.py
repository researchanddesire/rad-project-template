"""Plan actual-pad escapes where whole-package router obstacles block access."""
from pathlib import Path
import sys,json,math,hashlib,heapq
import numpy as np
from shapely.geometry import Polygon,Point,LineString
from shapely.ops import unary_union
from shapely.prepared import prep
from shapely import points,intersects
gp=Path(sys.argv[1]);outpath=Path(sys.argv[2]);g=json.loads(gp.read_text());ignore='--ignore-unlocked'in sys.argv[3:];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();pads=[(p,unary_union([Polygon(q)for q in p['polygons']]))for p in g['pads']];original_routes=g['routes'];locks=g['route_locks'];routes=[t for t,l in zip(original_routes,locks)if l or not ignore];edges=g['outline_edges_xy_mm'][:];a,c=edges.pop();outline=[a,c]
while edges:
 i,a,c=next((i,a,c)for i,(a,c)in enumerate(edges)if a==outline[-1]or c==outline[-1]);edges.pop(i);outline.append(c if a==outline[-1]else a)
board=Polygon(outline);viaregion=board.buffer(-.601);xs=np.arange(-9,9.001,.05);ys=np.arange(26,54.001,.05);xx,yy=np.meshgrid(xs,ys);gridall=np.column_stack((xx.ravel(),yy.ravel()));pp=points(gridall);inboard=intersects(viaregion,pp);targets=[('U1','6',.25),('U9','3',.3),('U9','6',.3),('U7','6',.2),('U7','7',.2),('U7','9',.2),('U7','5',.2),('U7','10',.2),('U4','6',.2),('U4','4',.2),('U8','3',.2),('U3','1',.2),('U2','1',.2),('U1','12',.2),('U5','6',.2),('C14','1',.3),('C24','1',.3),('J6','3',.3),('J5','1',.25),('R4','1',.2),('R5','1',.2),('R48','1',.2),('R47','1',.2),('R43','2',.2)];newroutes=[];result=[];prior=None
if '--targets'in sys.argv:targets=[tuple(t)for t in json.loads(Path(sys.argv[sys.argv.index('--targets')+1]).read_text())]
priority={('U7','10'):0,('U2','1'):1,('U3','1'):2,('U5','6'):3,('U1','6'):4};targets.sort(key=lambda t:priority.get(t[:2],10))
if '--failed-from'in sys.argv:
 prior=json.loads(Path(sys.argv[sys.argv.index('--failed-from')+1]).read_text());assert prior['source_board_sha256']==g['board_sha256'];failed={(p['ref'],p['pad'])for p in prior['targets']if p['status']!='planned'};targets=[t for t in targets if t[:2]in failed];routes.extend(prior['routes'])
def surface_fallback(start,width,obstacles,via_obstacles,own):
 global fallback_diagnostic
 # A .025mm grid with an extra half-cell-diagonal obstacle margin makes
 # each full step clear, including diagonal segments. Actual start links
 # are checked separately; no minimum width/clearance rule is reduced.
 step=.025;radius=float(sys.argv[sys.argv.index('--radius')+1])if'--radius'in sys.argv else 3.5;xs=np.arange(max(-9,start[0]-radius),min(9,start[0]+radius)+step/2,step);ys=np.arange(max(26,start[1]-radius),min(54,start[1]+radius)+step/2,step);nx=len(xs);ny=len(ys);xx,yy=np.meshgrid(xs,ys);grid=np.column_stack((xx.ravel(),yy.ravel()));pp=points(grid)
 allowed=intersects(board.buffer(-.301-width/2),pp)&~intersects(obstacles.buffer(step*.708+.0001),pp);goals=intersects(viaregion,pp)&~intersects(via_obstacles,pp)
 for v in own:goals&=np.linalg.norm(grid-np.array(v),axis=1)>=.651
 nearby=np.flatnonzero(allowed&(np.linalg.norm(grid-np.array(start),axis=1)<=.075));cost=np.full(len(grid),np.inf);prev=np.full(len(grid),-1,dtype=np.int32);heap=[]
 for i in nearby:
  line=LineString([start,grid[i]])
  if board.buffer(-.301-width/2).covers(line)and not obstacles.intersects(line):cost[i]=math.dist(start,grid[i]);heap.append((cost[i],int(i)))
 heapq.heapify(heap);end=None;visited=0
 while heap:
  c,u=heapq.heappop(heap)
  if c>cost[u]+1e-9:continue
  visited+=1
  if goals[u]:end=u;break
  y,x=divmod(u,nx)
  for dx,dy in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]:
   if not(0<=x+dx<nx and 0<=y+dy<ny):continue
   v=u+dx+dy*nx;cc=c+step*math.hypot(dx,dy)
   if allowed[v]and cc<cost[v]-1e-9:cost[v]=cc;prev[v]=u;heapq.heappush(heap,(cc,v))
 fallback_diagnostic={'source_grid_cells':len(nearby),'free_grid_cells':int(allowed.sum()),'free_via_goal_cells':int(goals.sum()),'visited_cells':visited,'fallback_width_mm':width,'fallback_radius_mm':radius}
 if end is None:return None
 chain=[];u=end
 while u!=-1:chain.append(tuple(grid[u]));u=int(prev[u])
 chain.reverse();path=[tuple(start)]+chain;clean=[path[0]]
 for i,p in enumerate(path[1:-1],1):
  a,b=path[i-1],path[i+1]
  if abs((p[0]-a[0])*(b[1]-p[1])-(p[1]-a[1])*(b[0]-p[0]))>1e-8:clean.append(p)
 clean.append(path[-1]);assert not obstacles.intersects(LineString(clean));return True,tuple(grid[end]),clean
def existing_escape(padshape,side,net):
 items=[(s,set(p['layers']),None)for p,s in pads if p['net']==net and p['layers']]
 for t in routes:
  if t['net']!=net:continue
  if t['kind']=='via':items.append((Point(t['position']).buffer(t['diameter']/2),{'F.Cu','B.Cu','In1.Cu'},t['position']))
  else:items.append((LineString([t['start'],t['end']]).buffer(t['width']/2),{t['layer']},None))
 queue=[(padshape,{side})];seen=set()
 while queue:
  shape,ls=queue.pop()
  for i,(s,ll,via)in enumerate(items):
   if i in seen or not ls&ll or shape.distance(s)>.00001:continue
   seen.add(i)
   if via is not None:return via
   queue.append((s,ll))
 return None
for ref,num,width in targets:
 p,s=next((p,s)for p,s in pads if p['ref']==ref and p['number']==num and p['layers']);net=p['net'];side=next(n for n in ['F.Cu','B.Cu']if n in p['layers']);start=(s.centroid.x,s.centroid.y);vobs=[];obs=[];own=[]
 escaped=existing_escape(s,side,net)
 if escaped is not None:result.append({'ref':ref,'pad':num,'net':net,'side':side,'status':'planned','new_via':False,'via':escaped,'path':[],'already_connected_to_existing_via':True,'neck_width_mm':None});continue
 for p2,shape in pads:
  if p2['layers']:vobs.append(shape.buffer(.151 if p2['net']==net else .401))
  if p2['paste']:vobs.append(shape.buffer(.151))
  if side in p2['layers']and p2['net']!=net:obs.append(shape.buffer(width/2+.101))
 for t in routes:
  if t['net']==net:
   if t['kind']=='via':own.append(t['position'])
   continue
  if t['kind']=='via':shape=Point(t['position']);vobs.append(shape.buffer(.701));obs.append(shape.buffer(.401+width/2))
  else:
   shape=LineString([t['start'],t['end']]);vobs.append(shape.buffer(.401+t['width']/2))
   if t['layer']==side:obs.append(shape.buffer(width/2+.101+t['width']/2))
 for z in g['rules']:
  for poly in z['polygons']:
   shape=Polygon(poly)
   if z['no_vias']:vobs.append(shape.buffer(.301))
   if z['no_tracks']and side in z['layers']:obs.append(shape.buffer(width/2+.001))
 vobs=unary_union(vobs);obs=unary_union(obs);ready=prep(obs);region=board.buffer(-.301-width/2);valid=inboard&~intersects(vobs,pp);dist=np.linalg.norm(gridall-np.array(start),axis=1);valid&=dist<=2.5
 for v in own:valid&=np.linalg.norm(gridall-np.array(v),axis=1)>=.651
 ids=np.flatnonzero(valid);ids=ids[np.argsort(dist[ids])][:1500];choices=[(math.dist(start,v),False,v)for v in own if math.dist(start,v)<=2.5]+[(float(dist[i])+.2,True,tuple(gridall[i]))for i in ids];choices.sort(key=lambda x:x[0]);found=None
 for _,new,v in choices:
  for path in [[start,v],[start,(start[0],v[1]),v],[start,(v[0],start[1]),v]]:
   path=[q for i,q in enumerate(path)if i==0 or math.dist(q,path[i-1])>1e-7]
   if len(path)<2:continue
   line=LineString(path)
   if region.covers(line)and not ready.intersects(line):found=new,v,path;break
  if found:break
 if not found:found=surface_fallback(start,width,obs,vobs,own)
 if not found:result.append({'ref':ref,'pad':num,'net':net,'side':side,'status':'NO_CLEAR_PORT','surface_diagnostic':fallback_diagnostic});continue
 new,v,path=found;v=[round(float(q),6)for q in v];path=[[round(float(q),6)for q in pt]for pt in path];added=[]
 if new:added.append({'kind':'via','net':net,'position':v,'diameter':.6,'drill':.3})
 for a,c in zip(path,path[1:]):added.append({'kind':'track','net':net,'layer':side,'width':width,'start':a,'end':c})
 routes.extend(added);newroutes.extend(added);result.append({'ref':ref,'pad':num,'net':net,'side':side,'status':'planned','new_via':new,'via':v,'path':path,'neck_width_mm':width})
allresults=([p for p in prior['targets']if p['status']=='planned']if prior else[])+result;allroutes=(prior['routes']if prior else[])+newroutes
out={'date':'2026-11-01','planner_sha256':sha(Path(__file__)),'source_geometry_sha256':sha(gp),'source_board_sha256':g['board_sha256'],'unlocked_copper_ignored':ignore,'prior_plan_routes_preserved':prior['routes']if prior else[],'targets':allresults,'routes':allroutes,'new_records_this_pass':len(newroutes),'scope':'Actual all-layer Cu/paste/route/rule geometry port plan; narrow local signal or low-current logic-select/sensor supply necks only. Main input/power paths stay at protected widths. Multi-bend fallback .025mm grid has extra cell-diagonal clearance margin. No nominal drill overlap; fresh native DRC and process/received clearance review required.'};outpath.write_text(json.dumps(out,indent=2)+'\n');print(len(allresults),'targets,',len(allroutes),'total new records,',[x for x in allresults if x['status']!='planned'],flush=True)
