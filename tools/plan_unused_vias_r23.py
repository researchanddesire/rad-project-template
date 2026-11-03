"""Replace native single-layer dangling vias with any needed planar junctions."""
from pathlib import Path
import sys,json,re,hashlib
from shapely.geometry import Polygon,Point,LineString
from shapely.ops import unary_union,nearest_points
P=Path(sys.argv[1]).resolve();out=Path(sys.argv[2]).resolve();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
gp=P/'body-native-geometry-all-layers.json';g=json.loads(gp.read_text());dr=P/'body/fresh-native-drc.txt';txt=dr.read_text();bp=next((P/'body').glob('body-r*.kicad_pcb'));assert sha(bp)==g['board_sha256']
assert '** Found 0 unconnected pads **'in txt and '** Found 0 Footprint errors **'in txt
assert set(re.findall(r'^\[([^]]+)\]:',txt,re.M))=={'via_dangling'}
warnings=[]
for block in txt.split('[via_dangling]:')[1:]:
    x,y,net=re.search(r'@\(([\d.]+) mm, ([\d.]+) mm\): Via \[([^]]+)\]',block).groups();warnings.append((net,[round(float(x)-100,6),round(130-float(y),6)]))
retired=[];bridges=[];contacts=[]
for net,xy in warnings:
    assert net!='GND'
    via=next(t for t in g['routes']if t['kind']=='via'and t['net']==net and t['position']==xy)
    centre=Point(xy);radius=via['diameter']/2;tracks=[];pads=[];layers=set()
    for t in g['routes']:
        if t['kind']!='track'or t['net']!=net:continue
        line=LineString([t['start'],t['end']])
        if centre.distance(line)>radius+t['width']/2+1e-6:continue
        tracks.append((t,line));layers.add(t['layer'])
    for p in g['pads']:
        if p['net']!=net or not p['layers']:continue
        shape=unary_union([Polygon(poly)for poly in p['polygons']])
        if centre.distance(shape)>radius+1e-6:continue
        pads.append((p,shape));layers.update(p['layers'])
    assert len(layers)==1,(net,xy,layers)
    layer=next(iter(layers));assert layer not in ['In2.Cu','In4.Cu']
    width=max([t['width']for t,_ in tracks]+[.15])
    candidates=[]
    for t,line in tracks:
        if centre.distance(line)>t['width']/2-1e-6:candidates.append(line.interpolate(line.project(centre)))
    for p,shape in pads:
        if centre.distance(shape)>1e-6:candidates.append(nearest_points(centre,shape)[1])
    for q in candidates:
        end=[round(q.x,6),round(q.y,6)]
        if centre.distance(q)<1e-6:continue
        bridges.append({'kind':'track','net':net,'layer':layer,'width':width,'start':xy,'end':end})
    retired.append(via);contacts.append({'net':net,'via_xy_mm':xy,'only_connected_layer':layer,'same_net_track_contacts':len(tracks),'same_net_pad_contacts':[(p['ref'],p['number'])for p,_ in pads],'junction_width_mm':width,'new_junction_segments':len(candidates)})
canon=lambda t:json.dumps(t,sort_keys=True);unique={canon(t):t for t in bridges};bridges=list(unique.values())
out.write_text(json.dumps({'planner_sha256':sha(Path(__file__)),'source_board_sha256':sha(bp),'source_geometry_sha256':sha(gp),'source_native_DRC_sha256':sha(dr),'retired_vias':retired,'same_layer_junctions':bridges,'contact_review':contacts,'scope':'Only native dangling single-layer vias. Planar junctions preserve contact at original through-via locations; source tracks untouched by this plan. Native DRC must approve, and any new dead-end stubs must be separately retired from native track-dangling evidence. No net/pad/rule/stack/part changes.'},indent=2)+'\n')
print(len(retired),'unused vias;',len(bridges),'same-layer junctions',flush=True)
