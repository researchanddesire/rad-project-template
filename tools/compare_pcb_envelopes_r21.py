"""Bind a current PCB checkpoint to the retained native R21 part envelopes."""
from pathlib import Path
import sys,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
P,S,PCB=[Path(x).resolve()for x in sys.argv[1:4]]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((P/'geometry-report.json').read_text());source=json.loads((S/'geometry-report.json').read_text())
assert sha(P/'MotorRetentionR21.FCStd')==r['native_sha256']
assert sha(S/'geometry-report.json')==r['source_R20_report_sha256']
oldfile=ROOT/source['PCB_directory']/'layout-inspection.json'
assert sha(oldfile)==source['PCB_inspection_sha256']
newfile=PCB/'layout-inspection.json';old=json.loads(oldfile.read_text());new=json.loads(newfile.read_text())
numeric_delta=[]
def compare(a,b,path):
    if isinstance(a,dict):
        assert set(a)==set(b),path
        for k in a:
            if k!='native_board_sha256':compare(a[k],b[k],path+'.'+k)
    elif isinstance(a,list):
        assert len(a)==len(b),path
        for i,(u,v)in enumerate(zip(a,b)):compare(u,v,path+'.'+str(i))
    elif isinstance(a,(int,float)):
        d=abs(a-b);assert d<1e-5,(path,a,b);numeric_delta.append(d)
    else:assert a==b,(path,a,b)
parts=[];native={}
for domain,board in new['boards'].items():
    before=old['boards'][domain]
    compare({k:v for k,v in before.items()if k!='placements'},{k:v for k,v in board.items()if k!='placements'},domain)
    aa={q['ref']:q for q in before['placements']};bb={q['ref']:q for q in board['placements']}
    compare(aa,bb,domain+'.placements')
    bp=next((PCB/domain).glob(domain+'-r*.kicad_pcb'))
    assert sha(bp)==board['native_board_sha256'];native[domain]=sha(bp)
    for q in board['placements']:
        if not q['body_xy_mm']:continue
        a,b,c,d=q['body_xy_mm'];z,w=q['z_bounds_mm'];bounds=[a,b,z,c,d,w]
        got=r['parts']['R17_'+q['ref']]['bounds_xyz_mm']
        delta=max(abs(u-v)for u,v in zip(bounds,got));assert delta<1e-5,q['ref']
        parts.append({'ref':q['ref'],'maximum_CAD_bounds_delta_mm':delta})
out={'native_R21_sha256':r['native_sha256'],'R20_source_report_sha256':sha(S/'geometry-report.json'),'original_PCB_inspection_sha256':sha(oldfile),'current_PCB_inspection_sha256':sha(newfile),'current_native_PCB_sha256':native,'comparator_sha256':sha(Path(__file__)),'all_89_part_and_pad_records_equal_original_inspection':True,'outline_thickness_and_nominal_mates_equal_original_inspection':True,'maximum_numeric_delta':max(numeric_delta),'actual_Fab_height_envelopes_checked':parts,'scope':'Current native PCB/source inspection parity with the source-bound R20 inspection, plus retained R21 actual Fab/height boxes. Does not model copper, drilled holes, real mates/wires, tolerances or strength.'}
output=Path(sys.argv[4]).resolve()if len(sys.argv)>4 else P/('pcb-'+PCB.name+'-envelopes.json');output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(out,indent=2)+'\n')
print(len(parts),'CAD Fab-height bounds;89part/pad records; outlines and nominal mates equal',flush=True)
