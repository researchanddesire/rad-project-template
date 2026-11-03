"""Review figure from source-bound full-04 native mesh/section exports."""
import hashlib, json
from pathlib import Path
from PIL import Image, ImageDraw, PngImagePlugin
import render_mechanical_r2 as draw

root = Path(__file__).resolve().parents[1]
cad = root/'hardware/cad/prototype-r2/full-04'
out = root/'developer-docs/docs/assets/prototype-r2'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
r = json.loads((cad/'geometry-report.json').read_text())
index = json.loads((cad/'review-meshes/mesh-index.json').read_text())
native = cad/'ButtplugPrototypeR2Full04.FCStd'
assert sha(native) == r['native_sha256'] == index['native_sha256']
assert sha(cad/'geometry-report.json') == index['geometry_report_sha256']
assert len(r['parts']) == 97 and not r['unintended_intersections']
old_color = draw.part_color
def color(name):
    if name in ['NewMetalLower', 'NewMetalUpper']: return (181,192,205)
    if name in ['RAMCombinedLowerCore', 'RAMCombinedUpperCore', 'LocalServiceCover']: return (86,115,144)
    if name == 'IntegratedElastomerFlangeCoverUpper': return (62,82,107)
    if name.startswith(('R3_SW', 'SW')):
        return (160,100,170) if any(s in name for s in ['Plunger','BlockingStop','LockKey']) else (202,175,124)
    if name.startswith('RearM2'): return (187,145,85)
    if name == 'RigidContactInsert': return (76,160,168)
    if 'ContactReference' in name: return (199,155,65)
    if 'Magnet' in name: return (132,112,160)
    return old_color(name)
draw.part_color = color
m = draw.NativeMeshes(cad/'review-meshes')
m.expected = {name: h for v in index['roles'].values() for name,h in v['exports'].items()}
def geometry(names, section=False):
    values=[]
    for name in names:
        cut = section and 'section_volume_mm3' in index['roles'][name]
        values.append((name,m.load(name,cut,require_section=cut),None))
    return values
closed = ['NewMetalLower','NewMetalUpper','FemaleNoseCap','ElastomerFlangeCoverLower',
          'IntegratedElastomerFlangeCoverUpper','LocalServiceCover','GroundContactReference','PositiveContactReference']
omit = {'NewMetalUpper','ElastomerFlangeCoverLower','IntegratedElastomerFlangeCoverUpper',
        'RAMCombinedUpperCore','LocalServiceCover'}
internal = [n for n in r['logical_to_native_role'] if n not in omit and not any(s in n for s in
            ['SealPath','EncapsulationPath','SolderTerminationSpace','StrainReliefSpace'])]
im = Image.new('RGB',(1800,1250),'white'); d=ImageDraw.Draw(im)
draw.label(d,(36,25),'R2 / full-04 integrated engineering candidate',37,True)
draw.label(d,(37,85),'15 mm neck · open-ended metal tube and closing cap · retained, blocked controls · underside rear bolt',23,fill=draw.MUTED)
draw.panel(im,(30,140,855,795),'EXTERIOR / contour retained',
           'The threaded cap supplies the external nose wall',geometry(closed))
draw.panel(im,(915,140,855,795),'INTERNALS / R4 joint and R3 controls',
           'Upper shell/core and covers removed; native sections',geometry(internal,True))
d=ImageDraw.Draw(im)
draw.label(d,(37,970),'97 valid final roles · no reported unintended static intersections · parts remain at assembly poses',24,True)
draw.label(d,(37,1018),'Purple: blocked plungers and lock keys · blue: unselected battery bay · teal: wire-space studies',23,fill=draw.MUTED)
draw.label(d,(37,1066),'Rear bolt/key entries clear in the stated stages. Captured core-join nut loading remains unresolved.',23,fill=draw.MUTED)
draw.label(d,(37,1114),'Button assembly clearance, working travel, dock holding, continuous seals and physical fit remain open.',23,True,fill=draw.AMBER)
draw.label(d,(37,1162),'Source-bound CAD review · no fabrication, assembly, electrical or wear acceptance',23,fill=draw.MUTED)
m.verify(); assert sha(native) == r['native_sha256']
meta={'native_sha256':sha(native),'geometry_report_sha256':sha(cad/'geometry-report.json'),
      'mesh_index_sha256':sha(cad/'review-meshes/mesh-index.json'),
      'renderer_sha256':sha(Path(__file__)),'render_library_sha256':sha(root/'tools/render_mechanical_r2.py'),
      'mesh_sha256':m.used,'scope':index['scope']}
png=PngImagePlugin.PngInfo();png.add_text('SourceHashes',json.dumps(meta,sort_keys=True))
target=out/'mechanical-r2-full04.png';im.save(target,pnginfo=png)
(out/'mechanical-r2-full04-source.json').write_text(json.dumps(meta,indent=2)+'\n')
print(target)
