"""Read native conductor polygons and route obstacles; never save source."""
from pathlib import Path
import sys,json,hashlib
import pcb_r2_route as R
K=R.k;R.LAYERS['In1.Cu']=K.In1_Cu;P=Path(sys.argv[1]);b=K.LoadBoard(str(P));out=Path(sys.argv[2]);R.LAYERS.update({b.GetLayerName(i):i for i in range(32)if b.GetEnabledLayers().Contains(i)});pads=[];rules=[]
def polys(poly):return[[R.mech(poly.COutline(i).CPoint(j))for j in range(poly.COutline(i).PointCount())]for i in range(poly.OutlineCount())]
for f in b.GetFootprints():
 for p in f.Pads():
  layers=[n for n,l in R.LAYERS.items()if p.GetLayerSet().Contains(l)]
  paste=[n for n,l in [('F.Cu',K.F_Paste),('B.Cu',K.B_Paste)]if p.GetLayerSet().Contains(l)]
  if paste:
   m=p.GetSolderPasteMargin();assert m.x==m.y==0,'Nonzero paste margins need separate aperture geometry'
  if layers or paste:pads.append({'ref':f.GetReference(),'number':p.GetNumber(),'net':p.GetNetname(),'layers':layers,'paste':paste,'polygons':polys(p.GetEffectivePolygon())})
 for z in f.Zones():
  if z.GetIsRuleArea():rules.append({'layers':[n for n,l in R.LAYERS.items()if z.GetLayerSet().Contains(l)],'no_tracks':z.GetDoNotAllowTracks(),'no_vias':z.GetDoNotAllowVias(),'polygons':polys(z.Outline())})
for z in b.Zones():
 if z.GetIsRuleArea():rules.append({'layers':[n for n,l in R.LAYERS.items()if z.GetLayerSet().Contains(l)],'no_tracks':z.GetDoNotAllowTracks(),'no_vias':z.GetDoNotAllowVias(),'polygons':polys(z.Outline())})
edges=[[R.mech(s.GetStart()),R.mech(s.GetEnd())]for s in b.GetDrawings()if isinstance(s,K.PCB_SHAPE)and s.GetLayer()==K.Edge_Cuts]
out.write_text(json.dumps({'extractor_sha256':R.sha(Path(__file__)),'outline_edges_xy_mm':edges,'board_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'pads':pads,'routes':R.route_records(b),'route_locks':[t.IsLocked()for t in b.GetTracks()],'rules':rules},indent=2)+'\n');print(out)
