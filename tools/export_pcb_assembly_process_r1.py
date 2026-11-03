"""Read-only KiCad pad/paste/drill details for the R2 assembly-process review.

Run with KiCad's bundled Python. This never saves or changes the source board.
The output is review geometry, not fabrication plots or a process approval.
"""
import hashlib
import json
from pathlib import Path

import pcbnew

ROOT = Path(__file__).resolve().parents[1]
BOARD = ROOT / "hardware/pcb/prototype-r2/buttplug-r2.kicad_pcb"
PROJECT = BOARD.with_suffix(".kicad_pro")
INVENTORY = ROOT / "hardware/pcb/prototype-r2/reviews/independent-via-process-inventory-r2.json"
OUT = ROOT / "hardware/pcb/prototype-r2/assembly-review"
EXPECTED = "5ba844fad77f58a8a5dfcb67f50e9070cf021048c29ed45a2751a9b8067f0bd4"
REFS = ["U1", "U5", "U6", "U7"]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def xy(p):
    return [pcbnew.ToMM(p.x) - 100, 130 - pcbnew.ToMM(p.y)]


def polygons(pad, layer):
    if layer in [pcbnew.F_Paste, pcbnew.B_Paste]:
        margin = pad.GetSolderPasteMargin()
        assert margin.x == 0 and margin.y == 0, "Nonzero paste margin needs separate polygon handling"
    poly = pad.GetEffectivePolygon()
    assert all(poly.HoleCount(i) == 0 for i in range(poly.OutlineCount())), "Unexpected pad polygon hole needs explicit handling"
    return [
        [xy(poly.COutline(i).CPoint(j)) for j in range(poly.COutline(i).PointCount())]
        for i in range(poly.OutlineCount())
    ]


def area(polys):
    return sum(abs(sum(
        p[i][0] * p[(i + 1) % len(p)][1] - p[(i + 1) % len(p)][0] * p[i][1]
        for i in range(len(p))
    )) / 2 for p in polys)


def main():
    assert sha(BOARD) == EXPECTED
    project_hash = sha(PROJECT)
    inventory = json.loads(INVENTORY.read_text())
    assert inventory["board_sha256"] == EXPECTED
    board = pcbnew.LoadBoard(str(BOARD))
    vias = [t for t in board.GetTracks() if isinstance(t, pcbnew.PCB_VIA)]
    assert len(vias) == inventory["counts"]["all_vias_examined"]
    fp_by_ref = {fp.GetReference(): fp for fp in board.GetFootprints()}
    details = {}
    for ref in REFS:
        fp = fp_by_ref[ref]
        cu = pcbnew.B_Cu if fp.IsFlipped() else pcbnew.F_Cu
        paste = pcbnew.B_Paste if fp.IsFlipped() else pcbnew.F_Paste
        pads = []
        for pad in fp.Pads():
            if not (pad.IsOnLayer(cu) or pad.IsOnLayer(paste)):
                continue
            copper_polys = polygons(pad, cu) if pad.IsOnLayer(cu) else []
            paste_polys = polygons(pad, paste) if pad.IsOnLayer(paste) else []
            margin = pad.GetSolderPasteMargin()
            pads.append({
                "number": pad.GetNumber(), "net": pad.GetNetname(),
                "center_xy_mm": xy(pad.GetPosition()),
                "native_size_mm": [pcbnew.ToMM(pad.GetSize().x), pcbnew.ToMM(pad.GetSize().y)],
                "native_paste_margin_xy_mm": [pcbnew.ToMM(margin.x), pcbnew.ToMM(margin.y)],
                "copper_polygons_xy_mm": copper_polys,
                "paste_polygons_xy_mm": paste_polys,
                "polygon_copper_area_mm2": area(copper_polys),
                "polygon_paste_area_mm2": area(paste_polys),
            })
        drill_refs = [o for o in inventory["overlaps"] if o["reference"] == ref and o["drill_overlaps_copper"]]
        drills = []
        for observed in drill_refs:
            found = [v for v in vias if str(v.m_Uuid.AsString()) == observed["via_uuid"]]
            assert len(found) == 1
            v = found[0]
            pos = xy(v.GetPosition())
            assert max(abs(a-b) for a,b in zip(pos,observed["mechanical_xy_mm"])) < 1e-8
            assert abs(pcbnew.ToMM(v.GetDrillValue()) - observed["via_drill_mm"]) < 1e-8
            drills.append({"via_uuid": observed["via_uuid"], "center_xy_mm": pos,
                           "drill_mm": pcbnew.ToMM(v.GetDrillValue()),
                           "copper_diameter_mm": pcbnew.ToMM(v.GetWidth()),
                           "net": v.GetNetname(), "pad": observed["pad"],
                           "paste_overlap_source": observed["other_paste_pad_shapes_overlapping_drill"]})
        details[ref] = {"footprint": str(fp.GetFPID().GetLibItemName()),
                        "center_xy_mm": xy(fp.GetPosition()),
                        "side": "B" if fp.IsFlipped() else "F",
                        "native_angle_deg": fp.GetOrientationDegrees(),
                        "pads": pads, "drill_in_pad": drills}
    record = {
        "status": "Read-only source geometry for four assembly-process details; no approval",
        "board": str(BOARD.relative_to(ROOT)), "board_sha256": EXPECTED,
        "project_sha256": project_hash, "inventory_sha256": sha(INVENTORY),
        "extractor_sha256": sha(Path(__file__)), "KiCad": pcbnew.Version(),
        "coordinates": "Mechanical top-coordinate plan: X=KiCadX-100, Y=130-KiCadY; back copper is not mirrored into a bottom view",
        "polygon_method": "Native PAD.GetEffectivePolygon with actual component-side copper/paste layer membership. Every plotted paste pad has native effective XY margins zero, asserted before reusing its effective shape. Curves use KiCad's native polygon approximation for review plotting, not Gerbers or a manufacturing tolerance.",
        "details": details,
        "limits": "Existing full inventory owns all149vias/320SMD overlaps. This extract checks their three actual drill identities/positions against unchanged native and plots four source footprints; no new all-board process, mask-tenting/fill, thermal, assembly-yield or electrical acceptance.",
    }
    assert sum(len(v["drill_in_pad"]) for v in details.values()) == 3
    assert sha(BOARD) == EXPECTED and sha(PROJECT) == project_hash
    OUT.mkdir(exist_ok=True)
    (OUT / "native-pad-details.json").write_text(json.dumps(record, indent=2) + "\n")
    print(OUT / "native-pad-details.json")


if __name__ == "__main__":
    main()
