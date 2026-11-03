"""Frame actual native SVG copper/Fab plots with current saved-check evidence."""
from pathlib import Path
import sys,json,hashlib,xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1];P=Path(sys.argv[1]).resolve();OUT=ROOT/'developer-docs/docs/assets/prototype-r2';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
a=json.loads((P/'saved-circuit-review.json').read_text());assert all(q['DRC']=={'drc_violations':0,'unconnected_items':0,'footprint_errors':0}for q in a['domains'].values())
assert sha(P/'flange/flange-r28.kicad_pcb')==a['domains']['flange']['native_board_sha256']
inv=json.loads((P/'flange/drill-paste-review.json').read_text());assert inv['vias_drilling_SMD_copper']==inv['vias_drilling_paste']==0
images=[];bindings={}
for i,name in enumerate(['front','back']):
 f=P/'flange'/('native-'+name+'.svg');r=E.parse(f).getroot();r.set('x',str(35+i*780));r.set('y','190');r.set('width','730');r.set('height','560');images.append(E.tostring(r,encoding='unicode'));bindings[f.name]=sha(f)
svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1070" viewBox="0 0 1600 1070"><rect width="1600" height="1070" fill="white"/>
<g font-family="Arial,sans-serif" fill="#243449"><text x="35" y="55" font-size="35" font-weight="700">Flange routing repaired / R28 candidate S</text>
<text x="35" y="101" font-size="23">J1 / J7 now face board edges; same 24 parts and 23.5 x 15 mm substrate</text>
<rect x="25" y="135" width="760" height="620" rx="14" fill="#f5f7fa" stroke="#d7e0ea"/><rect x="805" y="135" width="770" height="620" rx="14" fill="#f5f7fa" stroke="#d7e0ea"/>
<text x="45" y="176" font-size="24" font-weight="700">FRONT COPPER + NATIVE FOOTPRINT OUTLINES</text><text x="825" y="176" font-size="24" font-weight="700">BACK COPPER / SAME TOP COORDINATES</text>
{''.join(images)}
<text x="35" y="803" font-size="25" font-weight="700">Body and flange: zero native DRC / missing connections / footprint findings</text>
<text x="35" y="847" font-size="23">94 circuit components / 338 nodes conserved. Body copper and USB pair preserved.</text>
<text x="35" y="890" font-size="23">41 flange drills / 125 pad shapes: no SMD copper or paste drill overlaps.</text>
<text x="35" y="933" font-size="23">Input / charging paths remain 0.6 mm; original 0.65 mm radio trunk retained.</text>
<text x="35" y="976" font-size="22" fill="#975d15">Same component envelopes as R27D cradle. Actual wires, buttons, seals and physical fit remain open.</text>
<text x="35" y="1019" font-size="21">Review source only; fresh GUI ERC, supplier stackup/current CAM and electrical/RF/physical acceptance pending.</text>
</g></svg>'''
f=OUT/'flange-routing-r28-s.svg';f.write_text(svg)
meta={'native_boards_sha256':{k:v['native_board_sha256']for k,v in a['domains'].items()},'native_plot_sha256':bindings,'saved_circuit_review_sha256':sha(P/'saved-circuit-review.json'),'drill_review_sha256':sha(P/'flange/drill-paste-review.json'),'renderer_sha256':sha(Path(__file__)),'figure_sha256':sha(f),'method':'Actual native SVG plots framed without moving copper/footprints. Back is shown in the same top-coordinate frame, not a mirrored assembly drawing.'};f.with_name(f.stem+'-source.json').write_text(json.dumps(meta,indent=2)+'\n');print(f,flush=True)
