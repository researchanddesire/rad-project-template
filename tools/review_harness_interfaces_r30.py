"""Source-material witnesses at the keeper boss and retained rail region."""
from pathlib import Path
import sys,json,hashlib
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A
import Part
ROOT=Path(__file__).resolve().parents[1];P=Path(sys.argv[1]).resolve();SRC=ROOT/'hardware/cad/interboard-r29/candidate-e';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();nf=P/'HarnessSupportR30.FCStd';before=sha(nf);r=json.loads((P/'geometry-report.json').read_text());assert before==r['native_sha256'];D=A.openDocument(str(nf));S=A.openDocument(str(SRC/'InterboardR29.FCStd'));old=S.getObject('FlangeSupportHubR27').Shape;new=D.getObject('HarnessLeftHubR30').Shape;removed=old.copy().cut(new.copy());boss=S.getObject('FlangeKeeperBossR27').Shape.copy();railbox=Part.makeBox(23.2,6.5125,.8875,A.Vector(-35.5,-20.0125,7.7125));rail=old.copy().common(railbox.copy());regions={'keeper_screw_boss':boss,'upper_rail_below_Z8_6':rail};rows={}
for name,s in regions.items():
 assert s.Volume>1;lost=s.copy().cut(new.copy()).Volume;assert abs(lost)<1e-5,(name,lost);rows[name]={'source_witness_volume_mm3':s.Volume,'source_material_lost_mm3':lost}
print(rows,flush=True);out={'native_sha256':before,'source_R29_native_sha256':sha(SRC/'InterboardR29.FCStd'),'reviewer_sha256':sha(Path(__file__)),'witnesses':rows,'scope':'Actual source boss and nonempty source upper-rail subset belowZ8.6 retain all material at1e-5mm3 screen. No thread/bearing/stiffness/creep or physical load acceptance.'};(P/'mechanical-interface-review.json').write_text(json.dumps(out,indent=2)+'\n');A.closeDocument(S.Name);A.closeDocument(D.Name);assert sha(nf)==before
