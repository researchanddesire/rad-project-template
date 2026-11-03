"""Nominal native geometry sections and machining-tool reservation; SVG + PNG."""
from pathlib import Path
import sys,json,hashlib,html
import pymupdf
ROOT=Path(__file__).resolve().parents[1];folder=Path(sys.argv[1]);r=json.loads((folder/'review.json').read_text());s=json.loads((folder/'section-data.json').read_text());nf=folder/'ManufacturingLayout.FCStd';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
# GUI visibility can change native archive bytes after section extraction.
assert s['native_sha256'] in [r['native_sha256'],r.get('geometry_checked_native_sha256_before_view')]
assert sha(nf)==r['native_sha256']
S=s['sections'];out=ROOT/'developer-docs/docs/assets/manufacturing-sections.svg'
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1680" height="1220" viewBox="0 0 1680 1220">', '<rect width="1680" height="1220" fill="white"/>','<style>text{font-family:Arial,sans-serif;fill:#263747} .muted{fill:#586b7b} .line{fill:none;stroke:#526575;stroke-width:1.4} .dim{font-size:19px} .small{font-size:18px}</style>']
def text(x,y,t,size=20,cls='',weight='normal'):
 svg.append(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" font-family="Helvetica,Arial,sans-serif" fill="{'#586b7b' if cls=='muted' else '#263747'}">{html.escape(t)}</text>')
def clip_polygon(poly):
 # Rear detail is clipped in section coordinates because some SVG rasterizers
 # ignore clipPath. This crops only the drawing, never manufacturing geometry.
 for axis,bound,greater in [(0,-16,True),(0,16,False),(1,-17.8,True),(1,-2,False)]:
  result=[]
  for a,b in zip(poly,poly[1:]+poly[:1]):
   ai=a[axis]>=bound if greater else a[axis]<=bound
   bi=b[axis]>=bound if greater else b[axis]<=bound
   if ai:result.append(a)
   if ai!=bi:
    t=(bound-a[axis])/(b[axis]-a[axis]);result.append([a[j]+t*(b[j]-a[j])for j in range(2)])
  poly=result
  if not poly:break
 return poly
def path(name,cx,cy,k,origin=0,fill='#c0c8ce',clip=None):
 paths=[]
 for loop in S[name]:
  if clip:loop=clip_polygon(loop)
  if not loop:continue
  paths.append('M'+' L'.join(f'{cx+k*x:.3f},{cy-k*(y-origin):.3f}'for x,y in loop)+' Z')
 extra=f' clip-path="url(#{clip})"'if clip else''
 svg.append(f'<path d="{" ".join(paths)}" fill="{fill}" fill-rule="evenodd" stroke="#344957" stroke-width="1.2"{extra}/>')
def leader(points,t,x,y):
 svg.append('<polyline fill="none" stroke="#526575" stroke-width="1.4" points="'+' '.join(f'{a},{b}'for a,b in points)+'"/>');text(x,y,t,19)
def line(x,y,xx,yy):svg.append(f'<line fill="none" stroke="#526575" stroke-width="1.4" x1="{x}" y1="{y}" x2="{xx}" y2="{yy}"/>')
text(35,45,'Turning and flange joint / nominal geometry sections',31,weight='bold')
text(35,82,'Review drawing — not a fabrication print. Fits, material, loads, finish and supplier tooling are unresolved.',21,'muted')
text(35,134,'BODY + CAP / SECTION THROUGH AXIS AND SENSOR',22,weight='bold')
path('body',330,994,7);path('cap',330,994,7,fill='#d7e1e7')
line(330,286,330,1095)
leader([(385,984),(520,984),(520,935)],'Ø15 neck / Ø12 passage',470,916)
leader([(425,704),(570,704)],'Ø28 front bore',474,680)
leader([(457,546),(585,546)],'Y64 closure shoulder',474,524)
leader([(421,582),(574,582)],'M30 × 1.5 / 6H–6g proposed',460,613)
leader([(444,549),(460,490)],'Face gland 1.6 wide × 0.78 deep',470,480)
leader([(383,360),(590,360)],'Ø2.5 sensor drill; offset 7.8',465,338)
leader([(360,401),(590,401)],'Ø11.1 motor pocket; fit TBD',465,379)
text(45,1138,'Whole shape preserved; turning envelopes show no thread teeth.',20,'muted')
text(840,134,'REAR JOINT / SECTION PERPENDICULAR TO RING GAP',22,weight='bold')
svg.append('<defs><clipPath id="rear"><rect x="830" y="178" width="810" height="330"/></clipPath></defs>')
for n,c in [('rear_tray','#80aaa1'),('rear_body','#c0c8ce'),('rear_ring','#c29a4d'),('rear_cuff','#b8a0c6')]:path(n,1195,360,15,-8,c,clip='rear')
leader([(1330,418),(1490,480)],'Ring Ø17 groove × 1.3',1305,518)
leader([(1355,350),(1535,270)],'Ø24 shoulder / 2 mm tray pad',1295,247)
leader([(1055,301),(945,227)],'Bonded silicone cuff',835,206)
text(845,555,'Ø18 spigot / Ø18.2 socket. Socket bond resists torque.',20)
text(845,589,'Ring captures axially. Cover screws close plastic only.',20)
text(840,655,'SENSOR DRILL / HOLDER CLEARANCE RESERVATION',22,weight='bold')
path('cap',1110,1045,8.5,54.75,fill='#d7e1e7');path('tool_holder',1110,1045,8.5,54.75,fill='#829ead');path('tool_bit',1110,1045,8.5,54.75,fill='#b58d49')
leader([(1178,818),(1458,818)],'12.5 mm cylindrical depth (5D)',1300,792)
leader([(1203,1000),(1268,1050)],'Holder envelope: Ø7 nose / 3° taper',1285,1059)
text(1280,883,'Guhring 6405 Ø2.5 / 4 mm shank',18)
text(1280,915,'Haimer 77.160.04 candidate',18)
text(1280,947,'25 mm proposed tool projection',18)
text(1280,980,f'Nominal holder margin: {r["sensor_tooling_candidate"]["minimum_holder_to_cap_mm"]:.2f} mm',18)
text(35,1180,'Sections derived from saved native geometry. Tool and ring shapes are reservations; no CAM, fixture or physical approval.',19,'muted')
text(35,1207,'Native SHA256: '+r['native_sha256'][:24]+'…',16,'muted')
svg.append('</svg>');out.write_text('\n'.join(svg)+'\n');doc=pymupdf.open(stream=out.read_bytes(),filetype='svg');doc[0].get_pixmap(matrix=pymupdf.Matrix(1.2,1.2)).save(str(out.with_suffix('.png')))
out.with_suffix('.json').write_text(json.dumps({'native_sha256':r['native_sha256'],'renderer_sha256':sha(Path(__file__)),'sections_sha256':sha(folder/'section-data.json'),'SVG_sha256':sha(out),'scope':'Native slice curves with nominal annotations. Not a fabrication drawing.'},indent=2)+'\n');print(out)
