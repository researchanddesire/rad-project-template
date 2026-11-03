"""Bounded clearance-grid search for two residual R28 signal connections.

Consumes read-only native polygons. Search uses conservative clearances;
actual saved native DRC, not this search, owns electrical geometry results.
"""
from pathlib import Path
import sys,json,heapq,math,hashlib
import numpy as np
import shapely as S
from shapely.geometry import Polygon,Point,LineString,box
from shapely.ops import unary_union
P=Path(sys.argv[1]);source=P/'route-geometry.json';g=json.loads(source.read_text());layers=['F.Cu','In2.Cu','B.Cu'];step=.1
xs=np.round(np.arange(-36.89,-14.20,step),6);ys=np.round(np.arange(-25.59,-11.40,step),6);X,Y=np.meshgrid(xs,ys);nx=len(xs);ny=len(ys)
padshape=lambda p:unary_union([Polygon(x)for x in p['polygons']])
for p in g['pads']:p['_shape']=padshape(p)
def rs(r):return Point(r['position']).buffer(r['diameter']/2)if r['kind']=='via'else LineString([r['start'],r['end']]).buffer(r['width']/2)
for r in g['routes']:r['_shape']=rs(r)
ruletracks={l:unary_union([Polygon(poly)for r in g['rules']if r['no_tracks']and l in r['layers']for poly in r['polygons']])for l in layers}
rulevias=unary_union([Polygon(poly)for r in g['rules']if r['no_vias']for poly in r['polygons']])
records=[];reports=[]
requests=[('MOTOR_ARM','U6','21','F.Cu',None),('MOTOR_PWM','U6','20','F.Cu',None),('STRAP8','U6','22','F.Cu',None),('I2C_SCL','U6','19','F.Cu',None),
 ('I2C_SDA','U6','18','F.Cu',('J7','8')),('I2C_SDA','R37','2','B.Cu',None),('ACCEL_INT_N','U6','16','F.Cu',None),('DOCK_PRESENT_N','U6','30','F.Cu',None),('PACK_P','J7','4','B.Cu',None),('UART_TX','U6','31','F.Cu',None)]
if(P/'search-order.json').exists():
 requests=json.loads((P/'search-order.json').read_text())
 requests=[(n,r,p,l,tuple(t)if t else None)for n,r,p,l,t in requests]
for net,ref,pin,layer,onlytarget in requests:
 startpad=next(p for p in g['pads']if(p['ref'],p['number'])==(ref,pin));center=startpad['_shape'].centroid;sx,sy=round(center.x,6),round(center.y,6)
 def node(x,y,l):return(l,round((y-ys[0])/step),round((x-xs[0])/step))
 start=node(sx,sy,layers.index(layer));assert startpad['_shape'].contains(Point(xs[start[2]],ys[start[1]])),(net,sx,sy,'nearest grid node must lie inside actual native pad')
 target={l:unary_union([p['_shape']for p in g['pads']if p is not startpad and p['net']==net and l in p['layers']and(onlytarget is None or(p['ref'],p['number'])==onlytarget)]+[r['_shape']for r in g['routes']if onlytarget is None and r['net']==net and(r['kind']=='via'or r['layer']==l)])for l in layers}
 obs={};allowed={};goals={}
 for l in layers:
  shapes=[p['_shape']for p in g['pads']if p['net']!=net and l in p['layers']]
  shapes +=[r['_shape']for r in g['routes']if r['net']!=net and(r['kind']=='via'or r['layer']==l)]
  obs[l]=unary_union(shapes).buffer(.211).union(ruletracks[l].buffer(.111))
  allowed[l]=~S.intersects_xy(obs[l],X,Y)
  goals[l]=S.intersects_xy(target[l].buffer(.03),X,Y)&allowed[l]
 via_shapes=[p['_shape'].buffer(.411)for p in g['pads']if p['net']!=net]
 via_shapes +=[p['_shape'].buffer(.171)for p in g['pads']if p['net']==net and p['paste']]
 via_shapes +=[r['_shape'].buffer(.411)for r in g['routes']if r['net']!=net]
 viaobs=unary_union(via_shapes+[rulevias.buffer(.011)])
 viaok=(~S.intersects_xy(viaobs,X,Y))&(X>=-36.69)&(X<=-14.41)&(Y>=-25.39)&(Y<=-11.61)
 goalpoints=np.argwhere(np.logical_or.reduce(list(goals.values())))
 assert len(goalpoints),net
 def heuristic(n):
  l,y,x=n
  return float(np.min(np.hypot(goalpoints[:,1]-x,goalpoints[:,0]-y)))*step
 q=[(heuristic(start),0,start)];cost={start:0};previous={};closed=set();end=None
 while q:
  _,c,n=heapq.heappop(q)
  if n in closed:continue
  closed.add(n);l,y,x=n;name=layers[l]
  if goals[name][y,x]:end=n;break
  candidates=[]
  for dy,dx in [(0,1),(0,-1),(1,0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]:
   yy,xx=y+dy,x+dx
   if 0<=yy<ny and 0<=xx<nx and allowed[name][yy,xx]:
    line=LineString([(xs[x],ys[y]),(xs[xx],ys[yy])])
    if not obs[name].intersects(line):candidates.append(((l,yy,xx),step*math.hypot(dx,dy)))
  if viaok[y,x]:
   for ll in range(3):
    if ll!=l and allowed[layers[ll]][y,x]:candidates.append(((ll,y,x),1.8))
  for nn,delta in candidates:
   cc=c+delta
   if cc<cost.get(nn,1e30):cost[nn]=cc;previous[nn]=n;heapq.heappush(q,(cc+heuristic(nn),cc,nn))
 if end is None:raise RuntimeError('No bounded route for '+net+'; visited '+str(len(closed)))
 route=[end]
 while route[-1]!=start:route.append(previous[route[-1]])
 route=route[::-1];new=[];vialocs=set()
 for a,b in zip(route,route[1:]):
  la,ya,xa=a;lb,yb,xb=b;p=[float(xs[xa]),float(ys[ya])];p2=[float(xs[xb]),float(ys[yb])]
  if la!=lb:
   if tuple(p)not in vialocs:new.append({'kind':'via','net':net,'position':p,'diameter':.6,'drill':.3});vialocs.add(tuple(p))
  else:new.append({'kind':'track','net':net,'layer':layers[la],'start':p,'end':p2,'width':.2})
 # Merge collinear neighboring search segments without changing their path.
 merged=[]
 for r in new:
  if r['kind']=='track'and merged and merged[-1]['kind']=='track'and r['layer']==merged[-1]['layer']and r['start']==merged[-1]['end']:
   p=merged[-1];a=[p['end'][i]-p['start'][i]for i in range(2)];b=[r['end'][i]-r['start'][i]for i in range(2)]
   if abs(a[0]*b[1]-a[1]*b[0])<1e-7:p['end']=r['end'];continue
  merged.append(r)
 for r in merged:r['_shape']=rs(r);g['routes'].append(r)
 records.extend([{k:v for k,v in r.items()if k!='_shape'}for r in merged]);reports.append({'net':net,'start':[sx,sy,layer],'visited':len(closed),'length_cost':cost[end],'new_vias':len(vialocs),'new_records':len(merged)})
 print(json.dumps(reports[-1]),flush=True)
 (P/'partial-routes.json').write_text(json.dumps({'complete':False,'geometry_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'requests_completed':reports,'routes':records},indent=2)+'\n')
(P/'searched-routes.json').write_text(json.dumps({'geometry_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'search_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'grid_mm':step,'track_width_mm':.2,'clearance_mm':.111,'through_via_mm':[.6,.3],'requests':reports,'routes':records,'scope':'Geometric search candidate only; fresh native DRC, reference, pad parity and drill/paste review required.'},indent=2)+'\n')
