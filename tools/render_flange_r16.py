"""Frame actual native PCB SVGs; do not redraw copper or alter poses."""
from pathlib import Path
import json,hashlib,xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'hardware/pcb/route-r16/candidate-u';OUT=ROOT/'developer-docs/docs/assets/prototype-r2';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();audit=json.loads((P/'saved-copper-audit.json').read_text());inv=json.loads((P/'drill-paste-inventory.json').read_text());assert audit['DRC']=={'violations':0,'unconnected':0,'footprint_errors':0}and inv['counts']['vias_drilling_SMD_copper']==0
images=[];bindings={}
for i,name in enumerate(['front','back']):
 f=P/('native-'+name+'.svg');r=E.parse(f).getroot();r.set('x',str(35+i*780));r.set('y','190');r.set('width','730');r.set('height','560');images.append(E.tostring(r,encoding='unicode'));bindings[f.name]=sha(f)
svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1070" viewBox="0 0 1600 1070"><rect width="1600" height="1070" fill="white"/>
<g font-family="Arial,sans-serif" fill="#243449"><text x="35" y="55" font-size="35" font-weight="700">Flange board routed / R16 candidate U</text>
<text x="35" y="101" font-size="23">24 parts · same 23.5 × 15 mm substrate · user buttons and radio orientation preserved</text>
<rect x="25" y="135" width="760" height="620" rx="14" fill="#f5f7fa" stroke="#d7e0ea"/><rect x="805" y="135" width="770" height="620" rx="14" fill="#f5f7fa" stroke="#d7e0ea"/>
<text x="45" y="176" font-size="24" font-weight="700">FRONT COPPER + ACTUAL FOOTPRINT OUTLINES</text><text x="825" y="176" font-size="24" font-weight="700">BACK COPPER · SAME TOP COORDINATES</text>
{''.join(images)}
<text x="35" y="803" font-size="25" font-weight="700">Native DRC: 0 violations / 0 missing connections / 0 footprint errors</text>
<text x="35" y="847" font-size="23">USB: 17.63553 mm each · 0 signal vias · 1,173 ground-reference samples present</text>
<text x="35" y="890" font-size="23">All 39 vias / 125 copper or paste shapes checked: no nominal drill overlap with SMD copper or paste.</text>
<text x="35" y="933" font-size="23">F1 / D1 now protect the body feed from the flange; outward service plug clears them.</text>
<text x="35" y="976" font-size="22" fill="#975d15">Body board still has 163 open connections. This is a routing review checkpoint, not fabrication data.</text>
<text x="35" y="1019" font-size="21">Stackup / impedance, RF, current, assembly process and physical fit remain unqualified. Fresh R16 GUI ERC pending.</text>
</g></svg>'''
f=OUT/'flange-routing-r16.svg';f.write_text(svg)
(OUT/'flange-routing-r16-source.json').write_text(json.dumps({'native_board_sha256':audit['native_board_sha256'],'native_plot_sha256':bindings,'copper_audit_sha256':sha(P/'saved-copper-audit.json'),'drill_inventory_sha256':sha(P/'drill-paste-inventory.json'),'renderer_sha256':sha(Path(__file__)),'figure_sha256':sha(f),'method':'Actual native SVG plots framed without moving footprints/copper. Back copper is shown in the same top-coordinate frame; not a mirrored assembly drawing.'},indent=2)+'\n');print(f)
