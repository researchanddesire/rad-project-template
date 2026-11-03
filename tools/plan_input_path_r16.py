"""Plan a .6mm inner power path against actual native conductor polygons."""
import json,math,heapq,sys
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon,Point,LineString
from shapely.ops import unary_union
from shapely.prepared import prep
from shapely import points,intersects
r=json.loads(Path(sys.argv[1]).read_text());obs=[]
for t in r['routes']:
 if t['net']=='VBUS_CHG':continue
 if t['kind']=='via':obs.append(Point(t['position']).buffer(.701))
 elif t['layer']=='In2.Cu':obs.append(LineString([t['start'],t['end']]).buffer(t['width']/2+.401))
for p in r['pads']:
 if p['net']!='VBUS_CHG'and 'In2.Cu'in p['layers']:obs.extend(Polygon(q).buffer(.401)for q in p['polygons'])
for z in r['rules']:
 if z['no_tracks']and 'In2.Cu'in z['layers']:obs.extend(Polygon(q).buffer(.301)for q in z['polygons'])
blocked=unary_union(obs);ready=prep(blocked);step=.05;start=(-24.94,-15.32);end=(-16,-18.3);xs=np.arange(-36.7,-14.39,step);ys=np.arange(-25.9,-12.09,step);xx,yy=np.meshgrid(xs,ys);occupied=intersects(blocked,points(np.column_stack((xx.ravel(),yy.ravel())))).reshape(xx.shape)
def xy(n):return(float(xs[n[0]]),float(ys[n[1]]))
def nearest(p):return(min(range(len(xs)),key=lambda i:abs(xs[i]-p[0])),min(range(len(ys)),key=lambda i:abs(ys[i]-p[1])))
s=nearest(start);e=nearest(end);print('blocked endpoints',occupied[s[1],s[0]],occupied[e[1],e[0]],flush=True);assert not ready.intersects(LineString([start,xy(s)]))and not ready.intersects(LineString([end,xy(e)]));g={s:0};prev={};q=[(0,0,s)];found=False
while q:
 _,cost,n=heapq.heappop(q)
 if cost>g[n]+1e-9:continue
 if n==e:found=True;break
 for di,dj in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]:
  c=n[0]+di,n[1]+dj
  if not(0<=c[0]<len(xs)and 0<=c[1]<len(ys))or occupied[c[1],c[0]]:continue
  nc=cost+math.hypot(di,dj)
  if nc>=g.get(c,float('inf')):continue
  if ready.intersects(LineString([xy(n),xy(c)])):continue
  g[c]=nc;prev[c]=n;heapq.heappush(q,(nc+math.hypot(c[0]-e[0],c[1]-e[1]),nc,c))
print('found',found,'nodes',len(g),flush=True);assert found
path=[e]
while path[-1]!=s:path.append(prev[path[-1]])
path=[start]+[xy(n)for n in reversed(path)]+[end];short=[path[0]];i=0
while i<len(path)-1:
 j=len(path)-1
 while ready.intersects(LineString([path[i],path[j]])):j-=1
 assert j>i;short.append(path[j]);i=j
short=[[round(x,5),round(y,5)]for x,y in short];assert all(not ready.intersects(LineString([p,q]))for p,q in zip(short,short[1:]));out={'source_native_geometry_sha256':r['board_sha256'],'layer':'In2.Cu','width':.6,'points':short,'scope':'Grid/shortcut path against saved native pads, vias, inner tracks and keepouts with native minimum clearance/hole/edge allowances. Fresh native DRC remains authoritative.'};Path(sys.argv[2]).write_text(json.dumps(out,indent=2));print(short,flush=True)
