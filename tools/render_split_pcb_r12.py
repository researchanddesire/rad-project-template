"""Frame four actual native KiCad placement plots; no invented copper."""
from pathlib import Path
import hashlib,json,xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'hardware/pcb/split-r12/candidate-i';OUT=ROOT/'developer-docs/docs/assets/prototype-r2';OUT.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();used={};art=[]
for i,(domain,side)in enumerate([('body','front'),('body','back'),('flange','front'),('flange','back')]):
    f=P/(domain+'-'+side+'.svg');r=E.parse(f).getroot();x=45+i*438
    r.set('x',str(x+12));r.set('y','245');r.set('width','394');r.set('height','570');r.attrib.pop('version',None)
    art.append(f'<rect x="{x}" y="180" width="416" height="660" rx="16" fill="#172333"/><text x="{x+16}" y="219" font-size="22" fill="white">{domain.upper()} / {side.upper()}{" (mirrored)"if side=="back"else""}</text>'+E.tostring(r,encoding='unicode'))
    used[f.name]=sha(f)
boards={}
for domain in ['body','flange']:
    r=json.loads((P/(domain+'-native-inspection.json')).read_text());assert sha(P/(domain+'-r12.kicad_pcb'))==r['board_sha256']
    boards[domain]={'board_sha256':r['board_sha256'],'inspection_sha256':sha(P/(domain+'-native-inspection.json')),'counts':r['native_DRC_counts']}
s=f'''<svg xmlns="http://www.w3.org/2000/svg" width="1840" height="1080" viewBox="0 0 1840 1080">
<rect width="1840" height="1080" fill="white"/><g font-family="Arial,sans-serif" fill="#243449">
<text x="45" y="63" font-size="38" font-weight="700">Separate body + flange boards / native placement draft</text>
<text x="45" y="110" font-size="25">R12 candidate I · 87 source footprints retained + 2 proposed interboard headers · 1 mm substrates</text>
<text x="45" y="149" font-size="22" fill="#975d15">UNROUTED: 165 body and 81 flange connections remain. Plots show pads and footprint geometry only.</text>
{''.join(art)}
<text x="45" y="893" font-size="27" font-weight="700">67 body footprints / 22 flange footprints · pad/net parity and native placement checks pass</text>
<text x="45" y="940" font-size="23">Body: 14→18 mm taper × 28 mm · Flange FR4: 23.5 × 15 mm; antenna overhangs its outer edge</text>
<text x="45" y="986" font-size="23">Battery and tip headers face inward to clear the existing carrier. Flange link header sits on the underside.</text>
<text x="45" y="1032" font-size="22" fill="#975d15">Schematic split, routing, RF, supported wiring, working controls, wing retention and physical fit remain open.</text>
</g></svg>'''
target=OUT/'split-pcb-r12.svg';target.write_text(s)
(OUT/'split-pcb-r12-source.json').write_text(json.dumps({'method':'Read-only native KiCad SVG layer plots, framed without geometry edits','candidate':'I','boards':boards,'plots_sha256':used,'back_mirrored':True,'renderer_sha256':sha(Path(__file__)),'figure_sha256':sha(target),'scope':'Unrouted placement review; not electrical or fabrication acceptance.'},indent=2)+'\n')
print(target)
