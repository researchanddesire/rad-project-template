"""Read-only saved six-layer dimensions, plane roles and evidence binding."""
from pathlib import Path
import sys,json,hashlib
import kicad_sexp as S
P=Path(sys.argv[1]).resolve();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();bp=P/'body/body-r23.kicad_pcb';before=sha(bp);tree=S.parse(bp.read_text())
layers=[(int(n[0].value),n[1].value)for n in S.child(tree,'layers')[1:]if int(n[0].value)<32];assert layers==[(0,'F.Cu'),(1,'In1.Cu'),(2,'In2.Cu'),(3,'In3.Cu'),(4,'In4.Cu'),(31,'B.Cu')]
rows=[]
for n in S.children(S.child(S.child(tree,'setup'),'stackup'),'layer'):
    if S.value(n,'thickness')is None:continue
    rows.append({'layer':n[1].value,'type':S.value(n,'type'),'thickness_mm':float(S.value(n,'thickness'))})
total=sum(n['thickness_mm']for n in rows);assert abs(total-1)<1e-9 and float(S.value(S.child(tree,'general'),'thickness'))==1
cu=[n for n in rows if n['type']=='copper'];assert [n['layer']for n in cu]==[n for i,n in layers]
assert all(n['thickness_mm']==(.035 if n['layer']in ['F.Cu','B.Cu']else .0175)for n in cu)
die=[n['thickness_mm']for n in rows if n['type']in ['prepreg','core']];assert die==[.1,.1,.44,.1,.1]
bottom=next(i for i,n in enumerate(rows)if n['layer']=='B.Cu');assert rows[bottom-1]['layer']=='dielectric 5'and rows[bottom-2]['layer']=='In4.Cu'and rows[bottom-1]['thickness_mm']==.1
zones={S.value(z,'layer'):S.value(z,'net_name')for z in S.children(tree,'zone')if S.child(z,'keepout')is None};assert zones['In2.Cu']==zones['In4.Cu']=='GND'
dr=json.loads((P/'body/native-drc.json').read_text());audit=json.loads((P/'saved-body-copper-audit.json').read_text());geom=json.loads((P/'body-native-geometry-all-layers.json').read_text());circuit=json.loads((P/'circuit-conservation.json').read_text())
assert before==dr['native_board_sha256']==audit['native_board_sha256']==geom['board_sha256'];assert dr['counts']=={'violations':0,'unconnected':0,'footprint_errors':0}
assert audit['copper_layers']==6 and audit['local_B_power_reference']['samples_without_filled_In2_GND']==0 and audit['local_B_power_adjacent_ground_reference']['samples_without_filled_adjacent_GND']==0
assert not any(t['kind']=='track'and t['layer']in ['In2.Cu','In4.Cu']and t['net']!='GND'for t in geom['routes'])
assert len(geom['rules'])==1 and set(geom['rules'][0]['layers'])=={'F.Cu','In1.Cu','In3.Cu'}and geom['rules'][0]['no_tracks']and geom['rules'][0]['no_vias']
assert circuit['all_338_nodes_equal_R16U']and circuit['flange_board_byte_identical_to_R16U']
out={'native_board_sha256':before,'reviewer_sha256':sha(Path(__file__)),'saved_Cu_layer_sequence':layers,'saved_stackup_rows':rows,'total_finished_nominal_thickness_mm':total,'B_adjacent_ground_layer':'In4.Cu','B_adjacent_ground_dielectric_mm':.1,'native_DRC_record_sha256':sha(P/'body/native-drc.json'),'dual_reference_audit_sha256':sha(P/'saved-body-copper-audit.json'),'full_circuit_conservation_sha256':sha(P/'circuit-conservation.json'),'scope':'Saved six-layer stack/plane role and native evidence binding. Provisional stackup needs supplier review; no physical thickness, electrical/RF/thermal/assembly qualification.'}
(P/'saved-stackup-review.json').write_text(json.dumps(out,indent=2)+'\n');assert sha(bp)==before;print('Saved6layers/1mm; B-to-In4GND .1mm; dual1260point references; DRC0/0/0',flush=True)
