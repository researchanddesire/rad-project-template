"""Review figure from source-bound Full05 native mesh/section exports."""
import hashlib, json
from pathlib import Path
from PIL import Image, ImageDraw, PngImagePlugin
import render_mechanical_r2 as draw

root = Path(__file__).resolve().parents[1]
cad = root/'hardware/cad/prototype-r2/full-05'
out = root/'developer-docs/docs/assets/prototype-r2'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
r = json.loads((cad/'geometry-report.json').read_text())
index = json.loads((cad/'review-meshes/mesh-index.json').read_text())
native = cad/'ButtplugPrototypeR2Full05.FCStd'
assert sha(native) == r['native_sha256'] == index['native_sha256']
assert sha(cad/'geometry-report.json') == index['geometry_report_sha256']
assert len(r['parts']) == 103 and not r['unintended_intersections']
base_color = draw.part_color
def color(name):
    if name in ['NewMetalLower','NewMetalUpper']: return (181,192,205)
    if name in ['Full04PolymerFlangeCore','R5WithR4PortCut1','LocalServiceCover']: return (86,115,144)
    if name=='IntegratedElastomerFlangeCoverUpper': return (62,82,107)
    if name=='MotorNut1ForwardPortApplied': return base_color('CarrierWithTipStrainRelief')
    if '_SW' in name:
        return (160,100,170) if any(s in name for s in ['Plunger','BlockingStop','LockKey']) else (202,175,124)
    if name.startswith(('RearM2','R5_')): return (187,145,85)
    if name=='RigidContactInsert': return (76,160,168)
    if 'ContactReference' in name:return (199,155,65)
    if 'Magnet' in name:return (132,112,160)
    return base_color(name)
draw.part_color=color
meshes=draw.NativeMeshes(cad/'review-meshes')
meshes.expected={name:h for v in index['roles'].values() for name,h in v['exports'].items()}
def geometry(names, section=False):
    values=[]
    for name in names:
        cut=section and 'section_volume_mm3' in index['roles'][name]
        values.append((name,meshes.load(name,cut,require_section=cut),None))
    return values
closed=['NewMetalLower','NewMetalUpper','FemaleNoseCap','ElastomerFlangeCoverLower',
        'IntegratedElastomerFlangeCoverUpper','LocalServiceCover','GroundContactReference','PositiveContactReference']
omit={'NewMetalUpper','ElastomerFlangeCoverLower','IntegratedElastomerFlangeCoverUpper',
      'R5WithR4PortCut1','LocalServiceCover'}
internal=[n for n in r['parts'] if n not in omit and not any(s in n for s in
          ['SealPath','EncapsulationPath','SolderTerminationSpace','StrainReliefSpace'])]
im=Image.new('RGB',(1800,1230),'white');d=ImageDraw.Draw(im)
draw.label(d,(36,25),'Full05 / integrated prototype candidate',37,True)
draw.label(d,(37,85),'15 mm neck · open tube and closing cap · R4 controls · R5 nut keepers · R6 carrier loading ports',23,fill=draw.MUTED)
draw.panel(im,(30,140,855,795),'EXTERIOR / contour retained',
           'The threaded cap supplies the external nose wall',geometry(closed))
draw.panel(im,(915,140,855,795),'INTERNALS / current saved parts',
           'Upper shell/core and covers removed; native sections',geometry(internal,True))
d=ImageDraw.Draw(im)
draw.label(d,(37,970),'103 valid final roles · 210 STEP solids · 5,460 fresh pairs · zero unintended static intersections',24,True)
draw.label(d,(37,1018),'Purple: blocked plungers/keys · blue: unselected battery bay · teal: carrier and wire-space studies',23,fill=draw.MUTED)
draw.label(d,(37,1066),'Parts stay at assembly poses. Source identity and static fit do not establish the complete assembly route.',23,fill=draw.MUTED)
draw.label(d,(37,1114),'Working buttons, fastener profiles, wires, continuous seals and physical fit remain open.',23,True,fill=draw.AMBER)
draw.label(d,(37,1162),'Source-bound CAD review · no fabrication, assembly, electrical or wear acceptance',23,fill=draw.MUTED)
meshes.verify();assert sha(native)==r['native_sha256']
meta={'native_sha256':sha(native),'geometry_report_sha256':sha(cad/'geometry-report.json'),
      'mesh_index_sha256':sha(cad/'review-meshes/mesh-index.json'),
      'renderer_sha256':sha(Path(__file__)),'render_library_sha256':sha(root/'tools/render_mechanical_r2.py'),
      'mesh_sha256':meshes.used,'scope':index['scope']}
png=PngImagePlugin.PngInfo();png.add_text('SourceHashes',json.dumps(meta,sort_keys=True))
target=out/'mechanical-r2-full05.png';im.save(target,pnginfo=png)
(out/'mechanical-r2-full05-source.json').write_text(json.dumps(meta,indent=2)+'\n')
print(target)
