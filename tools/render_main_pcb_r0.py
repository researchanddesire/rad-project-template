"""Frame read-only native KiCad SVG layer plots for the R0 layout review.

Input: front/back page-size-mode2 plots and the native validation register.
This file does not route the board or change its native project.
"""
from pathlib import Path
import hashlib,json,sys,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'developer-docs/docs/assets/prototype-r1';OUT.mkdir(parents=True,exist_ok=True)
v=json.loads((ROOT/'hardware/pcb/prototype-r0/layout-validation-r0.json').read_text())
board=ROOT/'hardware/pcb/prototype-r0/buttplug-r0.kicad_pcb'
assert hashlib.sha256(board.read_bytes()).hexdigest()==v['board_sha256'], 'Native validation is stale'
def artwork(path,x):
 svg=ET.parse(path).getroot()
 svg.set('x',str(x));svg.set('y','190');svg.set('width','660');svg.set('height','720')
 svg.attrib.pop('version',None)
 return ET.tostring(svg,encoding='unicode')
front=artwork(sys.argv[1],70);back=artwork(sys.argv[2],860)
c=v.get('counts',{})
svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1120" viewBox="0 0 1600 1120">
<metadata>Native board SHA256: {v['board_sha256']}</metadata>
<rect width="1600" height="1120" fill="white"/>
<g font-family="Arial,sans-serif" fill="#243449">
<text x="40" y="62" font-size="36" font-weight="700">T-shaped main PCB · native layout R0</text>
<text x="40" y="106" font-size="23" fill="#5b6c7e">Single XY board · 4 copper layers · 1.0 mm finished reservation · engineering review candidate</text>
<rect x="30" y="140" width="750" height="790" rx="18" fill="#172333"/>
<rect x="820" y="140" width="750" height="790" rx="18" fill="#172333"/>
<text x="60" y="180" font-size="23" fill="white">FRONT / component face +Z</text>
<text x="850" y="180" font-size="23" fill="white">BACK / component face −Z</text>
{front}{back}
<text x="40" y="980" font-size="26" font-weight="700">87 footprints · 48 nets · antenna-end FR4 cutback · separate wired tip island</text>
<text x="40" y="1028" font-size="23">Native check: {c.get('drc_violations','see report')} DRC violations · {c.get('unconnected_items','see report')} unconnected items</text>
<text x="40" y="1073" font-size="22" fill="#975d15">Actual stackup, RF, via/paste process, provisional lands and physical assembly remain to qualify.</text>
</g></svg>'''
(OUT/'main-pcb-r0.svg').write_text(svg)
print(OUT/'main-pcb-r0.svg')
