"""Frame native KiCad front/back SVG plots without changing the board.

Export plots from an isolated copy with KiCad's board-area page mode. The
back plot is a mirrored bottom view. This only composes existing vectors.
"""
from pathlib import Path
import argparse
import hashlib
import json
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
PCB = ROOT / "hardware/pcb/prototype-r2"
OUT = ROOT / "developer-docs/docs/assets/prototype-r2"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def artwork(path, x):
    svg = ET.parse(path).getroot()
    svg.set("x", str(x))
    svg.set("y", "190")
    svg.set("width", "660")
    svg.set("height", "720")
    svg.attrib.pop("version", None)
    return ET.tostring(svg, encoding="unicode")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("front", type=Path)
    parser.add_argument("back", type=Path)
    args = parser.parse_args()
    vpath = PCB / "layout-validation-r2.json"
    v = json.loads(vpath.read_text())
    board = PCB / "buttplug-r2.kicad_pcb"
    project = PCB / "buttplug-r2.kicad_pro"
    assert sha(board) == v["board_sha256"], "Native validation is stale"
    assert sha(project) == v["project_sha256"], "Project validation is stale"
    c = v["counts"]
    front, back = artwork(args.front, 70), artwork(args.back, 860)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1120" viewBox="0 0 1600 1120">
<metadata>Native board SHA256: {v['board_sha256']}</metadata>
<rect width="1600" height="1120" fill="white"/>
<g font-family="Arial,sans-serif" fill="#243449">
<text x="40" y="62" font-size="36" font-weight="700">R2 main PCB · narrow-waist routing candidate</text>
<text x="40" y="106" font-size="23" fill="#5b6c7e">8 mm component-free waist · shortened T tongue · 4 copper layers · 1 mm finished study</text>
<rect x="30" y="140" width="750" height="790" rx="18" fill="#172333"/>
<rect x="820" y="140" width="750" height="790" rx="18" fill="#172333"/>
<text x="60" y="180" font-size="23" fill="white">FRONT / component face +Z</text>
<text x="850" y="180" font-size="23" fill="white">BACK / mirrored bottom view, −Z</text>
{front}{back}
<text x="40" y="980" font-size="26" font-weight="700">{v['main_footprints']} footprints · {v['nets']} nets · {v['main_pad_entries_checked']} pad/net entries matched to the circuit</text>
<text x="40" y="1028" font-size="23">Native: {c['drc_violations']} rule violations · {c['unconnected_items']} unconnected items · {c['footprint_errors']} footprint errors</text>
<text x="40" y="1073" font-size="22" fill="#975d15">Stackup, via/paste process, component lands, actual loads and mechanical assembly remain to qualify.</text>
</g></svg>'''
    OUT.mkdir(parents=True, exist_ok=True)
    out = OUT / "main-pcb-r2.svg"
    out.write_text(svg)
    record = {
        "method": "Framed read-only native KiCad SVG plots exported sequentially from an isolated board/project copy; no invented copper or footprint geometry",
        "board_sha256": sha(board),
        "project_sha256": sha(project),
        "native_validation_sha256": sha(vpath),
        "front_plot_sha256": sha(args.front),
        "back_plot_sha256": sha(args.back),
        "front_layers": ["F.Cu", "F.Silkscreen", "F.Fab", "Edge.Cuts"],
        "back_layers": ["B.Cu", "B.Silkscreen", "B.Fab", "Edge.Cuts"],
        "back_mirrored": True,
        "generator_sha256": sha(Path(__file__)),
        "framed_svg_sha256": sha(out),
        "scope": "Native source review only; not fabrication, electrical operation or assembly release",
    }
    (OUT / "main-pcb-r2-source.json").write_text(json.dumps(record, indent=2) + "\n")
    assert sha(board) == v["board_sha256"] and sha(project) == v["project_sha256"]
    print(out)


if __name__ == "__main__":
    main()
