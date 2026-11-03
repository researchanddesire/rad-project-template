"""Shared exact native Bezier/circular wire-edge construction."""
import FreeCAD as A
import Part
def edges_from_plan(q):
 edges=[]
 for seg in q['curves']:
  if seg['kind']=='bezier5':
   c=Part.BezierCurve();c.setPoles([A.Vector(*p)for p in seg['poles_xyz_mm']]);edges.append(c.toShape())
  else:
   assert seg['kind']=='circular_arc'
   edges.append(Part.Arc(A.Vector(*seg['start_xyz_mm']),A.Vector(*seg['mid_xyz_mm']),A.Vector(*seg['end_xyz_mm'])).toShape())
 return edges
