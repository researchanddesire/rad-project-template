"""Read native surface conductors, paste and drills for cradle land review.

KiCad 7 Python. Never save or refill the source board. Coordinates match the
existing flange mechanical mapping; holes in filled polygons are retained.
"""
from pathlib import Path
import sys,json,hashlib
import pcb_r2_route as R
k=R.k
P=Path(sys.argv[1]).resolve(); O=Path(sys.argv[2]).resolve()
before=hashlib.sha256(P.read_bytes()).hexdigest(); b=k.LoadBoard(str(P))
def line(s):return [R.mech(s.CPoint(j)) for j in range(s.PointCount())]
def polys(s):
 return [{'outer':line(s.COutline(i)), 'holes':[line(s.CHole(i,j)) for j in range(s.HoleCount(i))]} for i in range(s.OutlineCount())]
items=[]; drills=[]
for f in b.GetFootprints():
 for p in f.Pads():
  for name,layer in [('F.Cu',k.F_Cu),('B.Cu',k.B_Cu),('F.Paste',k.F_Paste),('B.Paste',k.B_Paste)]:
   if not p.GetLayerSet().Contains(layer):continue
   if 'Paste' in name:
    m=p.GetSolderPasteMargin();assert m.x==m.y==0
   items.append({'kind':'pad','reference':f.GetReference()+'.'+p.GetNumber(),'layer':name,'polygons':polys(p.GetEffectivePolygon())})
  d=p.GetDrillSize()
  if d.x or d.y:drills.append({'reference':f.GetReference()+'.'+p.GetNumber(),'center':R.mech(p.GetPosition()),'size_mm':[k.ToMM(d.x),k.ToMM(d.y)],'angle_deg':p.GetOrientationDegrees()})
for t in b.GetTracks():
 if isinstance(t,k.PCB_VIA):
  items.append({'kind':'via','reference':str(t.m_Uuid),'center':R.mech(t.GetPosition()),'radius_mm':k.ToMM(t.GetWidth())/2,'layers':['F.Cu','B.Cu']})
  drills.append({'reference':'via/'+str(t.m_Uuid),'center':R.mech(t.GetPosition()),'size_mm':[k.ToMM(t.GetDrillValue())]*2,'angle_deg':0})
 elif t.GetLayer() in [k.F_Cu,k.B_Cu]:items.append({'kind':'track','reference':str(t.m_Uuid),'layer':k.LayerName(t.GetLayer()),'start':R.mech(t.GetStart()),'end':R.mech(t.GetEnd()),'radius_mm':k.ToMM(t.GetWidth())/2})
for i,z in enumerate(b.Zones()):
 if z.GetIsRuleArea():continue
 for name,layer in [('F.Cu',k.F_Cu),('B.Cu',k.B_Cu)]:
  if z.GetLayerSet().Contains(layer):items.append({'kind':'filled_zone','reference':str(i),'layer':name,'polygons':polys(z.GetFilledPolysList(layer))})
assert hashlib.sha256(P.read_bytes()).hexdigest()==before
O.parent.mkdir(parents=True,exist_ok=True);O.write_text(json.dumps({'board_sha256':before,'extractor_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'items':items,'drills':drills,'scope':'Read-only exact effective pad and saved filled-zone polygons with holes; native tracks/vias. Paste margins asserted zero. Drill rectangles are conservative envelopes.'},indent=2)+'\n')
print(O, len(items),len(drills),flush=True)
