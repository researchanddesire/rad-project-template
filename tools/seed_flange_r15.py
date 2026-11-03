"""Lock a matched F USB pair and local supply/return routes before autoroute.

Uses R15B actual pads. Widths/stackup are engineering studies; no impedance,
current, thermal or fabrication acceptance is inferred from geometry.
"""
from pathlib import Path
import argparse,hashlib,json,math,shutil
import pcb_r2_route as R
import pcb_split_r12 as G
K=R.k;ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/'hardware/pcb/route-r15/candidate-b';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ap=argparse.ArgumentParser();ap.add_argument('directory',type=Path);a=ap.parse_args();OUT=a.directory.resolve();OUT.mkdir(parents=True,exist_ok=True);assert not any(OUT.rglob('*.kicad_pcb'))
for f in SOURCE.rglob('*'):
 if f.is_file()and(f.suffix in ['.kicad_pcb','.kicad_pro','.kicad_sch','.kicad_sym','.kicad_mod']or f.name in ['fp-lib-table','sym-lib-table']):
  q=OUT/f.relative_to(SOURCE);q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,q)
source=SOURCE/'flange/flange-r15.kicad_pcb';before=sha(source);board=OUT/'flange/flange-r15.kicad_pcb';shutil.copyfile(source,OUT/'flange/source-placement.kicad_pcb');b=K.LoadBoard(str(board));assert not list(b.GetTracks());fps={f.GetReference():f for f in b.GetFootprints()}
def physical():return{r:[G.mech(f.GetPosition()),f.GetOrientationDegrees(),f.GetLayer(),G.rect(f,[K.F_Fab,K.B_Fab]),[(p.GetNumber(),p.GetNetname(),G.mech(p.GetPosition()))for p in f.Pads()]]for r,f in fps.items()}
pose_signature=physical()
def pad(ref,n):return G.mech(next(p for p in fps[ref].Pads()if p.GetNumber()==str(n)).GetPosition())
routes=[]
def path(net,pts,width=.2,layer='F.Cu'):
 for p,q in zip(pts,pts[1:]):
  if math.dist(p,q)>1e-8:routes.append({'kind':'track','net':net,'start':p,'end':q,'width':width,'layer':layer})
def via(net,p):routes.append({'kind':'via','net':net,'position':p,'diameter':.6,'drill':.3})
dm=[pad('U6',26),[-28.5,-12.3],[-28.1,-11.9],[-26.25,-11.9],[-25.95,-12.2],[-25.95,-24.9],[-25.3,-25.55],[-18.45,-25.55],[-17.9,-25.0],pad('J4',2)]
offset=.45*math.sqrt(2)
def positive(rise):return[pad('U6',27),[-29.3,-12.6+rise],[-28.15-rise,-11.45],[-26.7+offset,-11.45],[-25.5,-12.65+offset],[-25.5,-25.35+offset],[-25.75+offset,-25.1],[-19,-25.1],[-18.9,-25.0],pad('J4',3)]
length=lambda points:sum(math.dist(p,q)for p,q in zip(points,points[1:]))
low,high=.25,.9
for _ in range(60):
 middle=(low+high)/2
 if length(positive(middle))<length(dm):low=middle
 else:high=middle
dp=positive((low+high)/2);assert abs(length(dm)-length(dp))<1e-7
path('USB_DM',dm);path('USB_DP',dp)

# Wide common feed and two vias at each layer handoff; terminal fanout/local
# capacitor branches are narrower. These are not current/thermal ratings.
path('3V3',[pad('U6',3),[-34.1,-24.95],[-34.5,-25.35],[-35.4,-25.35]],.65)
for point in [[-34.6,-25.35],[-35.4,-25.35],[-28,-14.3],[-28.8,-14.3]]:via('3V3',point)
path('3V3',[pad('J7',3),[-27.5,-13.8],[-28,-14.3],[-28.8,-14.3]],.65,'B.Cu')
path('3V3',[[-28.8,-14.3],[-28,-14.3],[-28,-22],[-29.5,-23.5],[-32.75,-23.5],[-34.6,-25.35],[-35.4,-25.35]],.65,'In2.Cu')
path('3V3',[[-35.4,-25.35],[-35.725,-25.35],pad('C32',1)],.3,'B.Cu')
path('3V3',[[-34.6,-25.35],[-34.6,-22.45],pad('C31',1)],.4,'B.Cu')

# Local ground returns; holes kept outside SMD lands where possible. A fresh
# all-pad drill/paste inventory still owns process acceptance.
grounds=[[-35.3,-23.55],[-34.5,-14.5],[-34.5,-18.5],[-34.5,-21],[-29.3,-25.35],[-16.9,-25.3],[-22.5,-16],[-14.8,-16]]
for point in grounds:via('GND',point)
path('GND',[pad('U6',48),[-35.55,-23.3],[-35.3,-23.55]],.3)
path('GND',[pad('U6',37),[-34.5,-14.5]],.3)
path('GND',[pad('U6',42),[-34.5,-18.5]],.3)
path('GND',[pad('U6',45),[-34.6,-20.9],[-34.5,-21]],.3)
path('GND',[pad('C32',2),[-35.475,-23.725],[-35.3,-23.55]],.3,'B.Cu')
path('GND',[pad('C31',2),[-34.95,-20.55],[-34.5,-21]],.3,'B.Cu')
path('GND',[pad('C33',2),[-29.425,-25.225],[-29.3,-25.35]],.3,'B.Cu')
path('GND',[pad('J4',1),[-16.9,-25.3]],.3)
path('GND',[pad('J1',2),[-18,-24.4],[-17.1,-25.3],[-16.9,-25.3]],.3,'B.Cu')
via('MCU_EN',[-30.1,-25.35]);path('MCU_EN',[pad('U6',8),[-30.1,-25.35]])
path('MCU_EN',[[-30.1,-25.35],[-30.775,-24.675],pad('C33',1)],.2,'B.Cu')
R.apply_routes(b,routes,locked=True)
for fp in fps.values():
 fp.SetProperty('PlacementStatus','R15 USB/power seed / other routing incomplete / not fabrication')
 if fp.GetReference()=='U6':
  for p in fp.Pads():
   if p.GetNetname()=='GND':p.SetZoneConnection(K.ZONE_CONNECTION_FULL)
R.usb_via_rule_areas(b);outline=[[-37.3,-26],[-13.8,-26],[-13.8,-11],[-37.3,-11]];R.ground_planes(b,outline)
assert physical()==pose_signature
K.SaveBoard(str(board),b);filled=R.fill_save(board)
saved=R.route_records(filled);usb={}
for net in ['USB_DM','USB_DP']:
 tracks=[t for t in saved if t['net']==net];assert all(t['kind']=='track'and t['layer']=='F.Cu'and t['width']==.2 for t in tracks)
 usb[net]={'length_mm':sum(math.dist(t['start'],t['end'])for t in tracks),'vias':0,'track_count':len(tracks),'width_mm':.2,'layer':'F.Cu'}
assert abs(usb['USB_DM']['length_mm']-usb['USB_DP']['length_mm'])<.00001
assert sha(source)==before
r={'date':'2026-11-01','builder_sha256':sha(Path(__file__)),'source_placement_sha256':before,'native_board_sha256':sha(board),'project_sha256':sha(OUT/'flange/flange-r15.kicad_pro'),'physical_pose_and_pad_nets_unchanged':True,'manual_source_routes':routes,'actual_saved_USB':usb,'USB_skew_mm':abs(usb['USB_DM']['length_mm']-usb['USB_DP']['length_mm']),
 'scope':'Partial routed seed with locked matched F USB, local capacitor supply/reset/ground paths, via keepouts and four GND fills. Fresh native DRC/reference/paste/drill review and all remaining routing required. .2mm/.25mm USB geometry does not prove90ohm impedance; supplier stackup, near-edge fields and fixture need review.'}
(OUT/'manual-seed.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'USB':usb,'skew_mm':r['USB_skew_mm'],'manual_records':len(routes),'board':str(board)},indent=2),flush=True)
