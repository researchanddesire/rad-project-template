"""Enforce proposed .6mm input-power width after router import/package."""
from pathlib import Path
import sys,json,shutil
import pcb_r2_route as R
P=Path(sys.argv[1]).resolve();bp=P/'flange/flange-r28.kicad_pcb';before=R.sha(bp);package=json.loads((P/'project-package.json').read_text());assert before==package['flange_native_sha256']
archive=P/'before-power-width-repair';archive.mkdir(exist_ok=False)
for rel in ['saved-circuit-review.json','layout-inspection.json','flange/routed-native-drc.txt','flange/drc-status.json','flange/route-geometry.json','flange/drill-paste-review.json']:
 src=P/rel;dest=archive/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dest)
b=R.k.LoadBoard(str(bp));changes=[]
for t,q in zip(b.GetTracks(),R.route_records(b)):
 if not isinstance(t,R.k.PCB_VIA)and t.GetNetname()in ['DOCK_5V','DOCK_FUSED','VBUS_CHG']and R.k.ToMM(t.GetWidth())<.6:changes.append(q);t.SetWidth(R.k.FromMM(.6))
assert changes;R.k.SaveBoard(str(bp),b);R.fill_save(bp)
R.write(P/'power-width-repair.json',{'source_packaged_board_sha256':before,'native_board_sha256':R.sha(bp),'builder_sha256':R.sha(Path(__file__)),'changed_source_records':changes,'target_minimum_mm':.6,'scope':'Remove remaining .45mm router power necks to retain the proposed .6mm charging/input path. Native min/rules remain unchanged. Prior native0DRC snapshot retained; fresh native DRC/geometry/plane/process audit required.'})
package['current_flange_native_sha256']=R.sha(bp);package['post_package_power_width_repair_sha256']=R.sha(P/'power-width-repair.json');R.write(P/'project-package.json',package);print(len(changes),'power necks widened to.6mm',flush=True)
