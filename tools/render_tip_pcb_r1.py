"""Frame a native KiCad SVG plot with the verified remote-tip interface map.

Input is a KiCad F.Cu,F.Mask,F.Fab,Edge.Cuts SVG plot, page-size-mode2.
The board artwork is native geometry, not an illustrative replacement.
"""
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'developer-docs/docs/assets/prototype-r1'
OUT.mkdir(parents=True,exist_ok=True)
board=ET.parse(sys.argv[1]).getroot()
board.set('x','75');board.set('y','180');board.set('width','680');board.set('height','455')
board.attrib.pop('version',None)
art=ET.tostring(board,encoding='unicode')
labels=''
for x,n,net in [(177,1,'3V3'),(334,2,'GND'),(491,3,'SDA'),(648,4,'SCL')]:
 labels+=f'<path d="M{x},625 v38" stroke="#556578"/><text x="{x}" y="695" text-anchor="middle" font-size="23" font-weight="600">{n} · {net}</text>'
svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900">
<rect width="1600" height="900" fill="white"/>
<g font-family="Arial,sans-serif" fill="#243449">
<text x="55" y="65" font-size="36" font-weight="700">Wired tip sensor · native PCB R1</text>
<text x="55" y="108" font-size="23" fill="#5b6c7e">Connected review board · 30 October 2026 · physical qualification pending</text>
<rect x="45" y="145" width="740" height="500" rx="18" fill="#172333"/>
{art}
<g fill="#243449">{labels}</g>
<text x="850" y="205" font-size="28" font-weight="700">6 × 4 mm tip island</text>
<text x="850" y="250" font-size="23">0.60 mm clad board / 0.62 mm with mask</text>
<text x="850" y="290" font-size="23">TMP117AIDRVR + 100 nF bypass</text>
<text x="850" y="330" font-size="23">0.9 mm front component reservation</text>
<text x="850" y="395" font-size="26" font-weight="700">Interface matches main J5</text>
<text x="850" y="440" font-size="23">Component-side view; direct-wire pads</text>
<text x="850" y="480" font-size="23">ADD0 grounded · I2C address 0x48</text>
<text x="850" y="545" font-size="26" font-weight="700">Thermal coupling still to qualify</text>
<text x="850" y="590" font-size="23">Package exposed pad left unsoldered</text>
<text x="850" y="630" font-size="23">Masked backside plane + dielectric bond</text>
<text x="850" y="670" font-size="23">No direct electrical contact with shell</text>
<text x="55" y="800" font-size="25" fill="#27745f" font-weight="700">Native check: 0 DRC violations · 0 unconnected pads</text>
<text x="55" y="845" font-size="22" fill="#5b6c7e">Study rules: 0.15 mm track / clearance · 0.45 / 0.20 mm vias · panelization, wiring and thermal response untested</text>
</g></svg>'''
(OUT/'tip-pcb-r1.svg').write_text(svg)
print(OUT/'tip-pcb-r1.svg')
