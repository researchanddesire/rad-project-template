"""Frame cropped native interboard schematic plots with checked source counts."""
from pathlib import Path
import hashlib,json,xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'hardware/pcb/split-r14/candidate-b';OUT=ROOT/'developer-docs/docs/assets/prototype-r2';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
erc=json.loads((P/'native-erc.json').read_text());parity=json.loads((P/'native-netlist-parity.json').read_text())
assert erc['violations']==0 and sha(P/erc['native_report'])==erc['native_report_sha256']
for f,h in erc['source_schematics_sha256'].items():assert sha(P/f)==h
images=[];used={}
for i,domain in enumerate(['Body','Flange']):
    f=P/'native-svg'/('system-r14-'+domain+' electronics-Interboard connection.svg');r=E.parse(f).getroot()
    r.set('x',str(55+i*730));r.set('y','230');r.set('width','660');r.set('height','530');r.set('viewBox','40 40 100 85');r.attrib.pop('version',None)
    images.append(E.tostring(r,encoding='unicode'));used[str(f.relative_to(P))]=sha(f)
body=f'''<svg xmlns="http://www.w3.org/2000/svg" width="1530" height="1060" viewBox="0 0 1530 1060"><rect width="1530" height="1060" fill="white"/>
<g font-family="Arial,sans-serif" fill="#243449">
<text x="35" y="58" font-size="35" font-weight="700">Separate circuits / explicit body-to-flange connection</text>
<text x="35" y="104" font-size="23">R14 candidate B · editable native body, flange and complete-device circuit projects</text>
<rect x="30" y="145" width="710" height="650" rx="14" fill="#f5f7fa" stroke="#d7e0ea"/>
<rect x="770" y="145" width="730" height="650" rx="14" fill="#f5f7fa" stroke="#d7e0ea"/>
<text x="55" y="188" font-size="25" font-weight="700">BODY / J6</text><text x="795" y="188" font-size="25" font-weight="700">FLANGE / J7</text>
{''.join(images)}
<text x="35" y="840" font-size="25" font-weight="700">Full-device native ERC: 0 errors / 0 warnings · saved report covers all 13 sheets</text>
<text x="35" y="883" font-size="23">318 original pin/net connections preserved + 20 new header connections. No electrical exclusions added.</text>
<text x="35" y="925" font-size="23">67 body / 22 flange footprints linked to the new schematics; PCB placement and pad nets are unchanged.</text>
<text x="35" y="967" font-size="22" fill="#975d15">UNROUTED: 165 / 81 connections remain. Cable construction, current/fault/return/RF checks remain open.</text>
<text x="35" y="1009" font-size="21">Schematic numbering shown; physical keyed-mate orientation is a separate harness drawing. SPICE models untested.</text>
</g></svg>'''
target=OUT/'split-circuit-r14.svg';target.write_text(body)
(OUT/'split-circuit-r14-source.json').write_text(json.dumps({'method':'Native KiCad SVG schematic crops; framing only, no redrawn wires or pin numbering','native_plot_sha256':used,'ERC_record_sha256':sha(P/'native-erc.json'),'native_netlist_parity_sha256':sha(P/'native-netlist-parity.json'),'renderer_sha256':sha(Path(__file__)),'figure_sha256':sha(target),'scope':'Full-system ERC and circuit partition only; boards remain unrouted and physical harness not accepted.'},indent=2)+'\n')
print(target)
