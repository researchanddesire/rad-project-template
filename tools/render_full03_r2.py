"""Source-hashed review figures from the integrated full-03 native exports."""
import json, hashlib
from pathlib import Path
from PIL import Image, ImageDraw, PngImagePlugin
import render_mechanical_r2 as draw

ROOT=Path(__file__).resolve().parents[1]
CAD=ROOT/'hardware/cad/prototype-r2/full-03'
OUT=ROOT/'developer-docs/docs/assets/prototype-r2'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report_path=CAD/'geometry-report.json'
r=json.loads(report_path.read_text());native=CAD/'ButtplugPrototypeR2Full03.FCStd'
assert sha(native)==r['native_sha256']=='7af6a14eac216deea59afedd104ce50ceb06e60d1b60af08f7411618024ac014'
base_color=draw.part_color
def color(n):
    if n in ['Full03UpperCoreCut7','IntegratedPolymerFlangeCore','LocalServiceCover']:return (86,115,144)
    if n=='IntegratedElastomerFlangeCoverUpper':return (62,82,107)
    if n.startswith('SW'):
        return (160,100,170) if 'Plunger' in n or 'BlockingStop' in n else (202,175,124)
    if n=='RigidContactInsert':return (76,160,168)
    if 'ContactReference' in n:return (199,155,65)
    if 'Magnet' in n:return (132,112,160)
    return base_color(n)
draw.part_color=color
m=draw.NativeMeshes(CAD)
m.expected={n+suffix:entry[key] for n,entry in r['exports'].items()
            for key,suffix in [('stl_sha256','.stl'),('section_stl_sha256','-section.stl')] if key in entry}
def geom(names,section=False):
    values=[]
    for n in names:
        use=section and n in ['MetalShellLower','FemaleNoseCap','IntegratedPolymerFlangeCore','CarrierWithTipStrainRelief']
        values.append((n,m.load(n,use,require_section=use),None))
    return values
closed=['MetalShellLower','MetalShellUpper','FemaleNoseCap','ElastomerFlangeCoverLower',
        'IntegratedElastomerFlangeCoverUpper','LocalServiceCover','GroundContactReference','PositiveContactReference']
omit={'MetalShellUpper','ElastomerFlangeCoverLower','IntegratedElastomerFlangeCoverUpper',
      'Full03UpperCoreCut7','LocalServiceCover'}
internal=[n for n in r['parts'] if n not in omit and not any(s in n for s in
          ['SealPath','EncapsulationPath','SolderTerminationSpace','StrainReliefSpace'])]
im=Image.new('RGB',(1800,1210),'white');d=ImageDraw.Draw(im)
draw.label(d,(36,25),'R2 / full-03 integrated engineering candidate',37,True)
draw.label(d,(37,85),'15 mm neck · single T-board · blocked control cartridges · charging insert and magnet keepers',23,fill=draw.MUTED)
draw.panel(im,(30,140,855,795),'EXTERIOR / unchanged contour budget',
           'Split tube closed by the separate threaded cap',geom(closed))
draw.panel(im,(915,140,855,795),'INTERNALS / controls and dock included',
           'Upper shell/core/skin and service cover removed',geom(internal,True))
d=ImageDraw.Draw(im)
draw.label(d,(37,972),'87 valid final roles · no reported unintended static intersections · 15 mm neck / 8 mm bare PCB waist',24,True)
draw.label(d,(37,1020),'Purple: blocked plungers · blue: unselected battery bay · gold: motor · teal: wire-space studies',23,fill=draw.MUTED)
draw.label(d,(37,1068),'Native source and listed assembly checks are separate from actual-part and continuous-wire fit.',23,fill=draw.MUTED)
draw.label(d,(37,1118),'Controls fastening/travel, continuous seals, materials and physical assembly remain unfinished.',23,True,fill=draw.AMBER)
m.verify();assert sha(native)==r['native_sha256']
meta={'native_sha256':sha(native),'geometry_report_sha256':sha(report_path),'renderer_sha256':sha(Path(__file__)),
      'mesh_sha256':m.used,'scope':'Actual native geometry. Upper source coverings removed; sections come from owner-exported native cuts. No physical fit, operating controls, sealing or wear proof.'}
png=PngImagePlugin.PngInfo();png.add_text('SourceHashes',json.dumps(meta,sort_keys=True))
target=OUT/'mechanical-r2-full03.png';im.save(target,pnginfo=png)
(OUT/'mechanical-r2-full03-source.json').write_text(json.dumps(meta,indent=2)+'\n')
print(target)
