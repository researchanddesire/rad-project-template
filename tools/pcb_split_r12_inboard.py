"""D variant: point the underside interboard connector toward the wing interior."""
from pathlib import Path
import hashlib,json,shutil
import wx
APP=wx.App(False)
import pcbnew as K
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'hardware/pcb/split-r12';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not(P/'candidate-d').exists();shutil.copytree(P/'candidate-c',P/'candidate-d')
path=P/'candidate-d/flange-r12.kicad_pcb';b=K.LoadBoard(str(path));f=next(f for f in b.GetFootprints()if f.GetReference()=='J7')
before={p.GetNumber():p.GetNetname()for p in f.Pads()}
f.SetOrientationDegrees(270);K.SaveBoard(str(path),b)
saved=K.LoadBoard(str(path));fp=next(f for f in saved.GetFootprints()if f.GetReference()=='J7')
assert{p.GetNumber():p.GetNetname()for p in fp.Pads()}==before
(P/'candidate-d/inboard-change.json').write_text(json.dumps({'script_sha256':sha(Path(__file__)),'source_C_flange_sha256':sha(P/'candidate-c/flange-r12.kicad_pcb'),'D_flange_sha256':sha(path),'change':'Rotate underside J7 fromnative90to270. ActualMP/contact row inspection showedBside90exitsoutward;270exitsinboard. No net reassignment.','source_reports':'Copied C/B files retain sourcehashes; fresh D inspections are current evidence.','pad_net_map_unchanged':True},indent=2)+'\n')
print('D:undersideJ7rotatedinward;pin/netmap preserved')
