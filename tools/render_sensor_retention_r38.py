"""Source-bound drawing of the R38 shared sensor-joint retention study."""
from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image,ImageDraw,PngImagePlugin
import render_mechanical_r2 as draw
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'hardware/cad/joint-retention-r38/sensor-c';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();r=json.loads((P/'geometry-report.json').read_text());v=json.loads((P/'loading-review.json').read_text());c=json.loads((P/'display/display-context.json').read_text());assert r['native_sha256']==v['native_sha256']==c['native_sha256']==sha(P/'RetainedSensorJointsR38.FCStd');assert r['all_static_screens_clear']and v['all_listed_loading_and_tool_poses_clear']and v['all_joint_six_direction_samples_blocked_within_2mm']and v['all_key_rotation_samples_blocked_within_2degrees']
a=draw.NativeMeshes(P/'display');a.expected={n:h for q in c['panels'].values()for n,h in q['meshes_sha256'].items()};rot=np.array([[1,0,0],[0,0,1],[0,-1,0]])
def colour(n):
 if n.startswith('JointRetainingHub'):return(157,165,173)
 if n.startswith('SensorJointComb'):return(71,132,177)
 if n.startswith('ReturnJointDrop'):return(114,157,192)
 if 'SoftPad'in n:return(108,183,147)
 if n.startswith('JointCombScrew'):return(87,98,111)
 if n.startswith(('NTCSplice','SensorReturnYJoint')):return(204,154,69)
 if n.startswith('PackNTCHead'):return(153,106,155)
 return(172,134,84)
draw.part_color=colour
def geometry(label):return[(n.removesuffix('.stl'),a.load(n.removesuffix('.stl'))@rot.T,None)for n in c['panels'][label]['meshes_sha256']]
im=Image.new('RGB',(1800,1080),'white');d=ImageDraw.Draw(im);draw.label(d,(32,25),'Five sensor joints share one comb and one screw',34,True);draw.label(d,(32,80),'R38C / separate top-loaded return plug / keyed comb / unchanged wire paths, boards and exterior',23,fill=draw.MUTED)
draw.panel(im,(25,125,1075,600),'INSTALLED RETAINER / NATIVE GEOMETRY','Hub, pack, covers and boards omitted; blue comb captures the separate return plug.',geometry('context'),camera=(.35,.1,2.5))
draw.panel(im,(1125,125,650,600),'FOUR LAPS / X19.8 SECTION','Gray hub; blue comb; green pad; amber joint budgets.',geometry('section'),camera=(-2.5,0,0))
d=ImageDraw.Draw(im)
for y,t in [(765,'Install return pad/plug from above, then slide the comb and four pad targets in from the front.'),(810,'An integral tab locates the comb; one M1.6 x4 candidate screw holds it against its post.'),(855,'Listed loading/tool samples clear; all five joint budgets meet hard retainers in six sampled directions.'),(900,'Pad contact is nominal. Qualify actual joint insulation, preload, key/pilot fit, torque and creep.'),(945,'Power connector/lap retention and the full connected loading, covers, harnesses and seals remain open.')]:draw.label(d,(33,y),t,23,fill=draw.AMBER if y>=900 else draw.INK)
draw.label(d,(33,1010),'Battery OPEN. Editable prototype development; no physical fit, strength, thermal or wear result.',23,fill=draw.MUTED)
a.verify();meta={'native_sha256':r['native_sha256'],'geometry_report_sha256':sha(P/'geometry-report.json'),'loading_review_sha256':sha(P/'loading-review.json'),'display_context_sha256':sha(P/'display/display-context.json'),'renderer_sha256':sha(Path(__file__)),'render_library_sha256':sha(ROOT/'tools/render_mechanical_r2.py'),'meshes_sha256':a.used,'display_transform':'(x,y,z)->(x,z,-y); no relative transforms','scope':c['scope']};out=ROOT/'developer-docs/docs/assets/prototype-r2/sensor-retention-r38-c.png';info=PngImagePlugin.PngInfo();info.add_text('SourceHashes',json.dumps(meta,sort_keys=True));im.save(out,pnginfo=info);out.with_name(out.stem+'-source.json').write_text(json.dumps(meta,indent=2)+'\n');print(out,flush=True)
