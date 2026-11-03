"""Source-bound native wire and unchanged board/cradle review figure."""
from pathlib import Path
import sys,json,hashlib
from PIL import Image,ImageDraw,PngImagePlugin
import render_mechanical_r2 as draw
ROOT=Path(__file__).resolve().parents[1];P=Path(sys.argv[1]).resolve();SRC=ROOT/'hardware/cad/flange-controls-r27/candidate-d';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();r=json.loads((P/'geometry-report.json').read_text());v=json.loads((P/'saved-review.json').read_text());old=json.loads((SRC/'geometry-report.json').read_text());assert sha(P/'InterboardR29.FCStd')==r['native_sha256']==v['native_sha256']and not v['unexpected_intersections'];assert sha(SRC/'FlangeCradleR27.FCStd')==r['source_R27_native_sha256']
a=draw.NativeMeshes(P);a.expected=v['wire_review_meshes_sha256'];b=draw.NativeMeshes(SRC);b.expected=old['review_meshes_sha256'];palette=[(175,71,55),(219,139,47),(102,145,58),(34,137,124),(48,123,170),(98,97,172),(167,83,148),(203,117,120),(118,133,60),(75,136,152)];orig=draw.part_color

def colour(n):
 if n.startswith('InterboardWireR29_'):return palette[int(n.rsplit('_',1)[1])-1]
 if n in ['FlangeSupportHubR27','FlangeEndKeeperR27']:return(128,156,164)
 if n.startswith('R17Mate_'):return(161,178,192)
 if n.startswith('R17_')or n in ['FlangePCB_R17','BodyPCB_R17']:return(57,134,91)
 return orig(n)
draw.part_color=colour
wires=[q['role']for q in r['individual_wires']]
def geom(names,flange_only=False):
 out=[]
 for n in names:
  mesh=(a if n in wires else b).load(n)
  if flange_only and n in wires:mesh=mesh[(mesh[:,:,1]<-8).all(axis=1)]
  out.append((n,mesh,None))
 return out
im=Image.new('RGB',(1740,1100),'white');d=ImageDraw.Draw(im);draw.label(d,(32,24),'Ten-wire body-to-flange route',36,True);draw.label(d,(33,79),'R29E / current native boards and exterior preserved / 0.60 mm wire allowances',23,fill=draw.MUTED)
context=['BodyPCB_R17','R17_J6','R17Mate_J6','FlangePCB_R17','R17_J7','R17Mate_J7','FlangeSupportHubR27','HubRight']
draw.panel(im,(25,125,820,640),'INSTALLED ROUTE','Metal body and covers omitted; wires remain unrestrained',geom(context+wires),camera=(.6,-.7,1.25))
close=['FlangePCB_R17','R17_J7','R17Mate_J7','R17_U6','FlangeSupportHubR27','FlangeEndKeeperR27','FlangeKeeperScrewEnvelopeR27']
draw.panel(im,(870,125,845,640),'FLANGE LOOP','All ten wires; colours identify pins, not supplied jackets',geom(close+wires,flange_only=True),camera=(.65,-1.8,.65))
d=ImageDraw.Draw(im);minimum=min(q['native_surface_distance_mm']for q in v['native_wire_surface_gaps']);lengths=[q['native_path_length_mm']for q in r['individual_wires']]
draw.label(d,(33,798),f'Fresh saved review: {v["forced_new_pairs_tested"]} new-wire pairs / zero intersections; minimum wire surface gap {minimum:.3f} mm.',23,True)
draw.label(d,(33,842),f'Installed paths: {min(lengths):.2f}–{max(lengths):.2f} mm. Guarded curvature and separation checks accompany the exact paths.',22)
draw.label(d,(33,886),'All 141 source roles conserved. No PCB, motor mount, neck or exterior change is made for this route.',23)
draw.label(d,(33,930),'Candidate exits and wire OD remain assumptions. Add supports and check connected assembly/service movement.',22,fill=draw.AMBER)
draw.label(d,(33,974),'120 mm starting blanks are trimmed on a fixture; actual crimps, final lengths, current/heat and physical fit remain open.',22,fill=draw.MUTED)
draw.label(d,(33,1020),'Battery choice stays open. This is an internal wiring checkpoint; the complete prototype build proposal is unfinished.',22,fill=draw.MUTED)
a.verify();b.verify();meta={'native_sha256':r['native_sha256'],'geometry_report_sha256':sha(P/'geometry-report.json'),'saved_review_sha256':sha(P/'saved-review.json'),'source_R27_native_sha256':r['source_R27_native_sha256'],'source_meshes_sha256':b.used,'wire_meshes_sha256':a.used,'renderer_sha256':sha(Path(__file__)),'render_library_sha256':sha(ROOT/'tools/render_mechanical_r2.py'),'display_translations':{},'flange_panel_wire_triangle_filter':'All vertices Y<-8mm; open crop without invented cap surfaces.','scope':'Actual native meshes in saved positions; body/covers omitted. Pin colours illustrative. No supported harness, physical or moving-assembly acceptance.'};out=ROOT/'developer-docs/docs/assets/prototype-r2/interboard-r29-e.png';info=PngImagePlugin.PngInfo();info.add_text('SourceHashes',json.dumps(meta,sort_keys=True));im.save(out,pnginfo=info);out.with_name(out.stem+'-source.json').write_text(json.dumps(meta,indent=2)+'\n');print(out,flush=True)
