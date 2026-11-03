"""Six-layer body study: preserve W copper/parts and the 1 mm mechanical stack.

In2/In4 are ground; F/In1/In3/B are signal. B-to-ground dielectric remains
.1 mm. This is a provisional fabricator-review stackup, not an order release.
"""
from pathlib import Path
from collections import Counter
import sys,json,shutil
import pcb_r2_route as R
import kicad_sexp as S
K=R.k;ROOT=Path(__file__).resolve().parents[1]
source=Path(sys.argv[1]).resolve();P=Path(sys.argv[2]).resolve()
bp=source/'body/body-r19.kicad_pcb';sourcehash=R.sha(bp)
P.mkdir(parents=True,exist_ok=True);assert not any(P.iterdir())
metadata={'global-release-r19.json','local-ground-rework-r19.json','fp-lib-table','sym-lib-table','body-seed.json','local-power.json','power-refinement.json','local-interfaces.json','compact-driver.json','signal-first-seed.json','signal-ports.json','signal-application.json','ground-plan.json','ground-application.json','ground-rework.json','fresh-fill.json','local-seed-final.json','dock-port-rework.json','signal-repack.json','local-seed-conservation.json','board-width.json','via-process.json'}
for p in source.rglob('*'):
    if not p.is_file():continue
    if p.suffix not in ['.kicad_pro','.kicad_sch','.kicad_sym','.kicad_mod','.kicad_pcb']and p.name not in metadata:continue
    relative=str(p.relative_to(source));relative=relative.replace('-r19','-r23')if p.suffix in ['.kicad_pro','.kicad_sch','.kicad_pcb']else relative;q=P/relative;q.parent.mkdir(parents=True,exist_ok=True)
    if p.suffix=='.kicad_sch':q.write_text(p.read_text().replace('-r19','-r23'))
    elif p.suffix=='.kicad_pro':
        d=json.loads(p.read_text());d['meta']['filename']=q.name;R.write(q,d)
    else:shutil.copyfile(p,q)
target=P/'body/body-r23.kicad_pcb';tree=S.parse(target.read_text());layers=S.child(tree,'layers')
assert [(n[0].value,n[1].value)for n in layers[1:]if int(n[0].value)<32]==[('0','F.Cu'),('1','In1.Cu'),('2','In2.Cu'),('31','B.Cu')]
at=next(i for i,n in enumerate(layers)if isinstance(n,list)and n[0].value=='31')
layers[at:at]=[S.parse('(3 "In3.Cu" signal)'),S.parse('(4 "In4.Cu" signal)')]
setup=S.child(tree,'setup');stack=S.child(setup,'stackup');assert S.value(S.child(tree,'general'),'thickness')=='1'
old_stack=S.dump(stack)
stacktext='''(stackup
 (layer "F.SilkS" (type "Top Silk Screen"))
 (layer "F.Paste" (type "Top Solder Paste"))
 (layer "F.Mask" (type "Top Solder Mask") (thickness 0.01))
 (layer "F.Cu" (type "copper") (thickness 0.035))
 (layer "dielectric 1" (type "prepreg") (thickness 0.1) (material "FR4") (epsilon_r 4.5) (loss_tangent 0.02))
 (layer "In1.Cu" (type "copper") (thickness 0.0175))
 (layer "dielectric 2" (type "core") (thickness 0.1) (material "FR4") (epsilon_r 4.5) (loss_tangent 0.02))
 (layer "In2.Cu" (type "copper") (thickness 0.0175))
 (layer "dielectric 3" (type "prepreg") (thickness 0.44) (material "FR4") (epsilon_r 4.5) (loss_tangent 0.02))
 (layer "In3.Cu" (type "copper") (thickness 0.0175))
 (layer "dielectric 4" (type "core") (thickness 0.1) (material "FR4") (epsilon_r 4.5) (loss_tangent 0.02))
 (layer "In4.Cu" (type "copper") (thickness 0.0175))
 (layer "dielectric 5" (type "prepreg") (thickness 0.1) (material "FR4") (epsilon_r 4.5) (loss_tangent 0.02))
 (layer "B.Cu" (type "copper") (thickness 0.035))
 (layer "B.Mask" (type "Bottom Solder Mask") (thickness 0.01))
 (layer "B.Paste" (type "Bottom Solder Paste"))
 (layer "B.SilkS" (type "Bottom Silk Screen"))
 (copper_finish "None") (dielectric_constraints no))'''
newstack=S.parse(stacktext);total=sum(float(S.value(n,'thickness')or 0)for n in S.children(newstack,'layer'));assert abs(total-1)<1e-12
setup[setup.index(stack)]=newstack;S.write(target,tree)
b=K.LoadBoard(str(target));assert b.GetCopperLayerCount()==6 and K.ToMM(b.GetDesignSettings().GetBoardThickness())==1
before=R.route_records(b);g=json.loads((source/'body-native-geometry-all-layers.json').read_text());assert g['board_sha256']==sourcehash and before==g['routes']
planes=[]
base=next(z for z in b.Zones()if not z.GetIsRuleArea()and z.GetLayerSet().Contains(K.In2_Cu));outline=base.Outline().COutline(0)
for layer in [K.In3_Cu,K.In4_Cu]:
    z=K.ZONE(b);z.SetLayer(layer);z.SetNet(b.FindNet('GND'));z.SetLocalClearance(K.FromMM(.1));z.SetMinThickness(K.FromMM(.2));z.SetPadConnection(K.ZONE_CONNECTION_THERMAL);z.SetThermalReliefGap(K.FromMM(.2));z.SetThermalReliefSpokeWidth(K.FromMM(.3));z.SetIslandRemovalMode(K.ISLAND_REMOVAL_MODE_ALWAYS)
    poly=z.Outline();poly.NewOutline()
    for i in range(outline.PointCount()):p=outline.CPoint(i);poly.Append(p.x,p.y)
    b.Add(z);planes.append(K.LayerName(layer))
rules=[]
for z in b.Zones():
    if z.GetIsRuleArea()and z.GetLayerSet().Contains(K.In1_Cu):
        old=[K.LayerName(i)for i in range(32)if z.GetLayerSet().Contains(i)];ls=z.GetLayerSet();ls.AddLayer(K.In3_Cu);z.SetLayerSet(ls);rules.append({'before_layers':old,'after_layers':old+['In3.Cu'],'reason':'Extend the existing MEMS signal/via keepout to the new signal layer.'})
assert len(rules)==1
K.SaveBoard(str(target),b);saved=R.fill_save(target);canon=lambda t:json.dumps(t,sort_keys=True);assert Counter(map(canon,before))==Counter(map(canon,R.route_records(saved)))
assert R.sha(P/'flange/flange-r23.kicad_pcb')==R.sha(source/'flange/flange-r19.kicad_pcb')
R.write(P/'stackup-r23.json',{'date':'2026-11-01','builder_sha256':R.sha(Path(__file__)),'source_directory':str(source.relative_to(ROOT)),'source_board_sha256':sourcehash,'source_geometry_sha256':R.sha(source/'body-native-geometry-all-layers.json'),'native_board_sha256':R.sha(target),'old_copper_layers':4,'new_copper_layers':6,'total_thickness_with_mask_mm':total,'outer_Cu_mm':.035,'inner_Cu_mm':.0175,'dielectric_sequence_mm':[.1,.1,.44,.1,.1],'B_adjacent_ground_layer':'In4.Cu','B_adjacent_ground_dielectric_mm':.1,'reserved_ground_layers':['In2.Cu','In4.Cu'],'signal_layers':['F.Cu','In1.Cu','In3.Cu','B.Cu'],'all_W_track_via_records_preserved':len(before),'additional_GND_zones':planes,'extended_rule_areas':rules,'old_stackup_S_expression':old_stack,'proposed_stackup_S_expression':stacktext,'scope':'Same body outline/thickness/parts/pad nets and all2373W records. Two added copper layers; adjacent B ground spacing preserved. Provisional six-layer stackup needs fabricator review. Circuit/name conservation and fresh native checks required; no fabrication release.'})
assert R.sha(bp)==sourcehash;print(P,'six layers; all',len(before),'copper records retained',flush=True)
