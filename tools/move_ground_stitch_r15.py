"""Move one R15 ground stitch away from the native module copper land."""
from pathlib import Path
import sys,shutil,json,math
import pcb_r2_route as R
S=R.ROOT/'hardware/pcb/route-r15/candidate-r';P=Path(sys.argv[1]).resolve();P.mkdir(parents=True,exist_ok=True);assert not any(P.iterdir())
for f in S.rglob('*'):
 if f.is_file()and(f.suffix in ['.kicad_pcb','.kicad_pro','.kicad_sch','.kicad_sym','.kicad_mod']or f.name in ['fp-lib-table','sym-lib-table']):
  q=P/f.relative_to(S);q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,q)
bp=P/'flange/flange-r15.kicad_pcb';b=R.k.LoadBoard(str(bp));old=[-34.5,-18.5];new=[-34.7,-18.5];moved=[];ends=[]
for t in b.GetTracks():
 if t.GetNetname()!='GND':continue
 if isinstance(t,R.k.PCB_VIA):
  if math.dist(R.mech(t.GetPosition()),old)<.00001:t.SetPosition(R.xy(*new));moved.append(str(t.m_Uuid.AsString()))
 else:
  for get,set in [(t.GetStart,t.SetStart),(t.GetEnd,t.SetEnd)]:
   if math.dist(R.mech(get()),old)<.00001:set(R.xy(*new));ends.append(str(t.m_Uuid.AsString()))
assert len(moved)==1 and len(ends)==2
R.k.SaveBoard(str(bp),b);R.fill_save(bp)
(P/'ground-stitch-repair.json').write_text(json.dumps({'tool_sha256':R.sha(Path(__file__)),'source_R_board_sha256':R.sha(S/'flange/flange-r15.kicad_pcb'),'native_board_sha256':R.sha(bp),'old_xy':old,'new_xy':new,'via_UUID':moved,'connected_track_UUIDs':ends,'reason':'Move local ground stitch .2mm away from U6 copper49 edge; preserve same short return with no nominal drill-in-SMD-copper. Fresh DRC and all-via inventory own result.'},indent=2)+'\n')
