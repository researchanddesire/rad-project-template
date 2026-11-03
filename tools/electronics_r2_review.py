"""Run a read-only native KiCad DRC for an explicitly hashed R2 snapshot.

Use KiCad's bundled Python. The board's matching adjacent project and local
footprint table must remain present. This does not fill zones or save a board.
"""
from pathlib import Path
import argparse
import hashlib
import os
import re
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("board", type=Path)
    parser.add_argument("expected_sha256")
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    board_path = args.board.resolve()
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    assert sha(board_path) == args.expected_sha256, "Board snapshot changed"
    project = board_path.with_suffix(".kicad_pro")
    assert project.is_file(), "Matching project is required"
    project_hash = sha(project)

    import wx
    app = wx.App(False)
    import pcbnew as k
    board = k.LoadBoard(str(board_path))
    board.BuildConnectivity()
    args.report.parent.mkdir(parents=True, exist_ok=True)
    k.WriteDRCReport(board, str(args.report.resolve()), k.EDA_UNITS_MILLIMETRES, True)
    report = args.report.read_text()
    assert "** End of Report **" in report, "Native report is incomplete"
    counts = [int(x) for x in re.findall(r"\*\* Found (\d+) ", report)]
    assert counts == [0, 0, 0], f"Native DRC findings: {counts}"
    assert sha(board_path) == args.expected_sha256, "Board changed during review"
    assert sha(project) == project_hash, "Project changed during review"
    print(f"KiCad {k.Version()}: {counts}; source and project unchanged")
    # KiCad 7/wx can hang while destroying a headless application on macOS.
    # Exit only after native report completion and source-preservation checks.
    # No board/project save is performed, and a preceding exception exits 1.
    sys.stdout.flush()
    os._exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        import traceback
        traceback.print_exc()
        sys.stderr.flush()
        os._exit(1)
