"""Source-bound R36 connected sensor and separated bare-lap figure."""
from pathlib import Path
import hashlib,json,sys
import numpy as np
from PIL import Image,ImageDraw,PngImagePlugin
import render_mechanical_r2 as draw
ROOT=Path(__file__).resolve().parents[1];P=Path(sys.argv[1]).resolve();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((P/'geometry-report.json').read_text());v=json.loads((P/'saved-review.json').read_text());c=json.loads((P/'display-context.json').read_text());assert sha(P/'ConnectedPackSensorsR36.FCStd')==r['native_sha256']==v['native_sha256']==c['native_sha256'];assert r['all_static_screens_clear']and v['all_reviewed_screens_clear']
a=draw.NativeMeshes(P);a.expected=dict(c['wiring_meshes_sha256'],**c['lap_meshes_sha256']);rot=np.array([[1,0,0],[0,0,1],[0,-1,0]])
def colour(n):
 if n.startswith('PackPublished'):return(119,174,196)
 if n.startswith('PackNTCHead'):return(156,100,157)
 if n.startswith('NTCSplice')or n.startswith('SensorReturnYJoint'):return(96,109,127)
 if n.startswith('FactoryNTCWire'):return(199,150,65)
 if n.startswith('FactoryLapBare'):return(191,123,74)
 if n.startswith('PackAdapterBare'):return(224,156,89)
 if n.startswith('PackConnectedWireR36_1'):return(196,80,65)
 if n.startswith('PackConnectedWireR36_3'):return(90,99,113)
 if n.startswith('PackConnectedWireR36_4'):return(176,134,39)
 if n.startswith('PackConnectedWireR36_5'):return(144,91,168)
 return(66,118,174)
draw.part_color=colour
geometry=lambda files:[(f.removesuffix('.stl'),a.load(f.removesuffix('.stl'))@rot.T,None)for f in files]
im=Image.new('RGB',(1800,1120),'white');d=ImageDraw.Draw(im);draw.label(d,(32,25),'The two pack sensors now have complete lead and joint paths',34,True);draw.label(d,(32,80),'R36H / sensor circuit connected to R35F lands / protected-pack power mate and restraints remain unfinished',23,fill=draw.MUTED)
draw.panel(im,(25,125,1025,610),'PACK FRONT / NATIVE WIRING VIEW','Hub and covers omitted; blue block is the unchanged pack-size reference.',geometry(c['wiring_meshes_sha256']),camera=(.18,.16,-2.5))
draw.panel(im,(1080,125,695,610),'ONE LAP / BARE PATHS SEPARATED','Sleeve and solder omitted; these are process targets.',geometry(c['lap_meshes_sha256']),camera=(.1,2.5,.25))
d=ImageDraw.Draw(im);draw.label(d,(33,775),'Two heads move 10 mm outward. Four full factory leads fan into separate insulated lap-joint targets.',23,True);draw.label(d,(33,820),'The sensor return branches at one junction; the long power return stays separate until the body PCB.',23);draw.label(d,(33,865),'Native static wiring, moved-sensor, source-material and sizing-reservation checks pass their recorded scopes.',23);draw.label(d,(33,910),'The bare ends have distinct paths; the proposed solder bridge touches both within the sleeve-size budget.',23);draw.label(d,(33,955),'Factory leads remain at least 4.5 mm straight at the heads; minimum factory bend centerline is R6.6 mm.',23);draw.label(d,(33,1000),'Joint/insulation materials, force bypass, connected loading, power mate and physical tests remain open.',23,fill=draw.AMBER);draw.label(d,(33,1045),'No battery selected or connected. This is an editable prototype-development checkpoint.',23,fill=draw.MUTED)
a.verify();meta={'native_sha256':r['native_sha256'],'geometry_report_sha256':sha(P/'geometry-report.json'),'saved_review_sha256':sha(P/'saved-review.json'),'context_sha256':sha(P/'display-context.json'),'renderer_sha256':sha(Path(__file__)),'render_library_sha256':sha(ROOT/'tools/render_mechanical_r2.py'),'meshes_sha256':a.used,'display_transform':'(x,y,z)->(x,z,-y), no relative transforms','scope':c['scope']};out=ROOT/'developer-docs/docs/assets/prototype-r2/pack-sensor-r36-h.png';info=PngImagePlugin.PngInfo();info.add_text('SourceHashes',json.dumps(meta,sort_keys=True));im.save(out,pnginfo=info);out.with_name(out.stem+'-source.json').write_text(json.dumps(meta,indent=2)+'\n');print(out,flush=True)
