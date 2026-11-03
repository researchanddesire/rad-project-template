"""One-board native DRC with immutable source identity, not a routing pass."""
from pathlib import Path
import argparse,hashlib,json,re
import wx
APP=wx.App(False)
import pcbnew as K
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ap=argparse.ArgumentParser();ap.add_argument('directory',type=Path);ap.add_argument('domain',choices=['body','flange']);a=ap.parse_args();P=a.directory.resolve()/a.domain
f=P/(a.domain+'-r14.kicad_pcb');before=sha(f);b=K.LoadBoard(str(f));b.BuildConnectivity();report=P/'fresh-native-drc.txt';K.WriteDRCReport(b,str(report),K.EDA_UNITS_MILLIMETRES,True);t=report.read_text()
counts={n:int(re.search(rx,t).group(1))for n,rx in [('violations',r'\*\* Found (\d+) DRC violations'),('unconnected',r'\*\* Found (\d+) unconnected pads'),('footprint_errors',r'\*\* Found (\d+) Footprint errors')]}
assert sha(f)==before
r={'native_board_sha256':before,'project_sha256':sha(P/(a.domain+'-r14.kicad_pro')),'reviewer_sha256':sha(Path(__file__)),'native_report_sha256':sha(report),'counts':counts,'scope':'Fresh native KiCad7 DRC in a one-board process. UNROUTED; missing connections are findings and are not waived. Separate from full-system ERC and physical/process qualification.'}
(P/'native-drc.json').write_text(json.dumps(r,indent=2)+'\n');print(a.domain,counts)
