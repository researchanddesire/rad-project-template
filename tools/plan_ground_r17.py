"""Plan short ground stitches using actual saved Cu/paste and all-layer obstacles."""
from pathlib import Path
import sys,json,math,hashlib
import numpy as np
from shapely.geometry import Polygon,Point,LineString
from shapely.ops import unary_union
from shapely import points,intersects
gpath=Path(sys.argv[1]);outpath=Path(sys.argv[2]);g=json.loads(gpath.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();pads=[(p,unary_union([Polygon(q)for q in p['polygons']]))for p in g['pads']];edges=g['outline_edges_xy_mm'][:];a,c=edges.pop();outline=[a,c]
while edges:
 i,a,c=next((i,a,c)for i,(a,c)in enumerate(edges)if a==outline[-1]or c==outline[-1]);edges.pop(i);outline.append(c if a==outline[-1]else a)
assert outline[-1]==outline[0];board=Polygon(outline);viaregion=board.buffer(-.601);trackregion=board.buffer(-.426);viaobs=[];pathobs={side:[]for side in ['F.Cu','B.Cu']}
for p,s in pads:
 if p['layers']:viaobs.append(s.buffer(.151 if p['net']=='GND'else .401))
 if p['paste']:viaobs.append(s.buffer(.151))
 for side in pathobs:
  if side in p['layers']and p['net']!='GND':pathobs[side].append(s.buffer(.226))
for t in g['routes']:
 if t['net']=='GND':continue
 if t['kind']=='via':
  s=Point(t['position']);viaobs.append(s.buffer(.701))
  for side in pathobs:pathobs[side].append(s.buffer(.526))
 else:
  s=LineString([t['start'],t['end']]);viaobs.append(s.buffer(.401+t['width']/2))
  if t['layer']in pathobs:pathobs[t['layer']].append(s.buffer(.226+t['width']/2))
for z in g['rules']:
 for poly in z['polygons']:
  s=Polygon(poly)
  if z['no_vias']:viaobs.append(s.buffer(.301))
  for side in pathobs:
   if z['no_tracks']and side in z['layers']:pathobs[side].append(s.buffer(.126))
viaobs=unary_union(viaobs);pathobs={s:unary_union(q)for s,q in pathobs.items()};xs=np.arange(-9,9.001,.05);ys=np.arange(26,54.001,.05);xx,yy=np.meshgrid(xs,ys);grid=np.column_stack((xx.ravel(),yy.ravel()));pp=points(grid);valid=intersects(viaregion,pp)&~intersects(viaobs,pp);grid=grid[valid];vias=[];routes=[];results=[]
targets=[(p,s)for p,s in pads if p['net']=='GND'and p['number']and p['number']!='MP'];skip={('U1','17'),('U2','10'),('U3','10'),('U5','9'),('U1','5'),('U5','5'),('U5','7')};targets=[(p,s)for p,s in targets if(p['ref'],p['number'])not in skip]
priority={n:i for i,n in enumerate('C51 C52 C53 C54 U2 U3 U1 U5 C1 C2 C3 C28 C29 C30'.split())};targets.sort(key=lambda ps:(priority.get(ps[0]['ref'],100),ps[0]['ref'],ps[0]['number']))
def clearpath(path,side):
 line=LineString(path)
 return trackregion.covers(line)and not pathobs[side].intersects(line)
for p,s in targets:
 side=next(n for n in ['F.Cu','B.Cu']if n in p['layers']);start=(s.centroid.x,s.centroid.y);dist=np.linalg.norm(grid-np.array(start),axis=1);mask=dist<=2.5
 for v in vias:mask&=np.linalg.norm(grid-np.array(v),axis=1)>=.651
 ids=np.flatnonzero(mask);ids=ids[np.argsort(dist[ids])][:180];choices=[(math.dist(start,v),False,v)for v in vias if math.dist(start,v)<=2.5]+[(float(dist[i])+.2,True,tuple(grid[i]))for i in ids];choices.sort(key=lambda x:x[0]);found=None
 for cost,new,v in choices:
  candidates=[[start,v],[start,(v[0],start[1]),v],[start,(start[0],v[1]),v]]
  for path in candidates:
   path=[q for i,q in enumerate(path)if i==0 or math.dist(q,path[i-1])>1e-7]
   if len(path)>1 and clearpath(path,side):found=new,v,path;break
  if found:break
 if not found:results.append({'ref':p['ref'],'pad':p['number'],'side':side,'status':'NO_CLEAR_LOCAL_STITCH'});continue
 new,v,path=found;v=[round(float(x),6)for x in v];path=[[round(float(x),6)for x in q]for q in path]
 if new:vias.append(v);routes.append({'kind':'via','net':'GND','position':v,'diameter':.6,'drill':.3})
 for a,c in zip(path,path[1:]):routes.append({'kind':'track','net':'GND','layer':side,'width':.25,'start':a,'end':c})
 results.append({'ref':p['ref'],'pad':p['number'],'side':side,'status':'planned','new_via':new,'via_xy':v,'path_xy':path,'path_length_mm':sum(math.dist(a,c)for a,c in zip(path,path[1:]))})
out={'date':'2026-11-01','planner_sha256':sha(Path(__file__)),'native_geometry_sha256':sha(gpath),'native_board_sha256':g['board_sha256'],'target_results':results,'skipped_exposed_pads_already_connected_to_discrete_ground_necks':sorted(skip),'new_vias':len(vias),'routes':routes,'scope':'Nominal .25mm surface stitches to .6/.3mm through-vias; actual all-face copper and paste polygons, existing tracks/vias and keepouts screened. .151mm same-GND pad/paste distance prevents nominal drill overlap; foreign copper/hole clearance includes .001mm margin. Not current/thermal/process/assembly acceptance. Fresh native DRC and drill/paste review remain required.'};outpath.write_text(json.dumps(out,indent=2)+'\n');print(len(results),'targets,',len(vias),'vias,',[r for r in results if r['status']!='planned'],flush=True)
