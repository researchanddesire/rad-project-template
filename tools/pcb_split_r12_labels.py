"""Clone B to C and match existing reference/value visibility for two new headers."""
from pathlib import Path
import hashlib,json,shutil
import wx
APP=wx.App(False)
import pcbnew as K
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'hardware/pcb/split-r12'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not(P/'candidate-c').exists();shutil.copytree(P/'candidate-b',P/'candidate-c')
changes={}
def signature(board):
    return sorted((f.GetReference(),f.GetLayer(),round(f.GetOrientationDegrees(),6),
      f.GetPosition().x,f.GetPosition().y,
      tuple(sorted((p.GetNumber(),p.GetNetname(),p.GetPosition().x,p.GetPosition().y,p.GetSize().x,p.GetSize().y,p.GetDrillSize().x,p.GetDrillSize().y,str(p.GetLayerSet().FmtHex()))for p in f.Pads())))for f in board.GetFootprints())
for domain,ref in [('body','J6'),('flange','J7')]:
    path=P/'candidate-c'/(domain+'-r12.kicad_pcb');b=K.LoadBoard(str(path));before=signature(b)
    fp=next(f for f in b.GetFootprints()if f.GetReference()==ref)
    fp.Reference().SetVisible(False);fp.Value().SetVisible(False)
    K.SaveBoard(str(path),b);saved=K.LoadBoard(str(path));assert signature(saved)==before
    changes[domain]={'source_B_sha256':sha(P/'candidate-b'/path.name),'candidate_C_sha256':sha(path),
                     'change':'New connector reference/value visibility matches all existing source footprints; pin1silk/body/pads unchanged',
                     'native_pad_pose_signature_unchanged':True}
# Inherited B inspection/report hashes explicitly remain B snapshots, not C evidence.
(P/'candidate-c/label-change.json').write_text(json.dumps({'script_sha256':sha(Path(__file__)),'changes':changes,'scope':'Label visibility only. Reinspect C boards in fresh processes; copied B reports keep their original identities.'},indent=2)+'\n')
print('Created C; native electrical-pad/pose signatures unchanged')
