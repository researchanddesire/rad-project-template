"""Check proposed registration contacts against native saved surface geometry."""
from pathlib import Path
import sys,json,hashlib,math
from shapely.geometry import Polygon,LineString,Point,box
from shapely.ops import unary_union
from shapely.affinity import rotate
P=Path(sys.argv[1]);O=Path(sys.argv[2]);r=json.loads(P.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert r['board_sha256']=='521bbffad5ad2ea960973a6650904ff64e906639b86408db8227b640d531e542'
def shape(q):
 if 'polygons' in q:return unary_union([Polygon(p['outer'],p['holes']) for p in q['polygons']])
 # Inflate round buffers by the polygon sagitta so their chordal edges
 # enclose, rather than underbound, the ideal native track/via radius.
 radius=q['radius_mm']/math.cos(math.pi/256)
 if q['kind']=='track':return LineString([q['start'],q['end']]).buffer(radius,resolution=64)
 return Point(q['center']).buffer(radius,resolution=64)
items=[(q,shape(q)) for q in r['items']]
drills=[]
for q in r['drills']:
 x,y=q['center'];a,b=q['size_mm'];drills.append((q,rotate(box(x-a/2,y-b/2,x+a/2,y+b/2),q['angle_deg'],origin=(x,y))))
# Contacts mapped from worldX=x+1.5 / worldZ=y+18.5125.
contacts=[]
for side,spans in [('F.Cu',[(-22.6,-13)]),('B.Cu',[(-22.6,-13)])]:contacts.append((side+'/upper',side,box(spans[0][0]-1.5,-11.2,spans[0][1]-1.5,-11)))
for side,spans in [('F.Cu',[(-22.6,-21.65),(-14.15,-13)]),('B.Cu',[(-22.6,-18.75),(-15.25,-13)])]:
 for i,(a,b) in enumerate(spans):contacts.append((side+'/lower'+str(i),side,box(a-1.5,-26,b-1.5,-25.8)))
# Edge faces/end stops also reserve a .20mm inward projection on both faces.
for side in ['F.Cu','B.Cu']:
 contacts.extend([(side+'/upper_edge',side,box(-24.1,-11.2,-14.5,-11)),(side+'/lower_edge',side,box(-24.1,-26,-14.5,-25.8)),(side+'/inner_end',side,box(-14,-20.5125,-13.8,-16.5125)),(side+'/outer_end',side,box(-37.3,-11.4,-37.1,-11))])
rows=[];hits=[]
for name,side,s in contacts:
 nearby=[(q,t) for q,t in items if q.get('layer') in [side,side.replace('Cu','Paste')] or side in q.get('layers',[])]
 allgeom=nearby+drills
 conflicts=[{'kind':q.get('kind','drill'),'reference':q['reference'],'area_mm2':s.intersection(t).area}for q,t in allgeom if s.intersection(t).area>1e-9]
 row={'contact':name,'polygon_xy_mm':list(s.exterior.coords),'minimum_conductor_paste_gap_mm':min(s.distance(t)for q,t in nearby),'minimum_drill_envelope_gap_mm':min(s.distance(t)for q,t in drills),'hits':conflicts};rows.append(row);hits+=conflicts
O.write_text(json.dumps({'board_sha256':r['board_sha256'],'extracted_geometry_sha256':sha(P),'reviewer_sha256':sha(Path(__file__)),'contact_projection_count':len(rows),'rows':rows,'unexpected_intersections':hits,'all_contact_projections_clear':not hits,'scope':'Surface Cu/paste and conservative drill envelopes against nominal .20mm FR4 contacts. Includes saved filled zones with holes. Round track/via buffers at64segments/quadrant use radius/cos(pi/256) to enclose ideal arcs. No edge finish/tolerance, pad adhesion, strength or actual registration/deflection acceptance.'},indent=2)+'\n');print('contacts',len(rows),'hits',hits,'minimum conductor gap',min(q['minimum_conductor_paste_gap_mm']for q in rows),flush=True)
