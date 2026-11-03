"""Fresh one-board KiCad DRC, without altering the board or project."""
from pathlib import Path
import sys,json,re
import pcb_r2_route as R
P=Path(sys.argv[1]).resolve();bp=next((P/'body').glob('body-r*.kicad_pcb'));before=R.sha(bp)
b=R.k.LoadBoard(str(bp));b.BuildConnectivity();report=P/'body/fresh-native-drc.txt'
R.k.WriteDRCReport(b,str(report),R.k.EDA_UNITS_MILLIMETRES,True)
t=report.read_text();counts={n:int(re.search(rx,t).group(1))for n,rx in [('violations',r'\*\* Found (\d+) DRC violations'),('unconnected',r'\*\* Found (\d+) unconnected pads'),('footprint_errors',r'\*\* Found (\d+) Footprint errors')]}
assert R.sha(bp)==before
R.write(P/'body/native-drc.json',{'native_board_sha256':before,'project_sha256':R.sha(bp.with_suffix('.kicad_pro')),'reviewer_sha256':R.sha(Path(__file__)),'native_report_sha256':R.sha(report),'counts':counts,'scope':'Fresh native KiCad 7 DRC. Findings are not waived; no electrical, thermal or physical qualification inferred.'})
print(counts,flush=True)
