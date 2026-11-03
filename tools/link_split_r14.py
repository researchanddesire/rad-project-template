"""Copy R12 native boards and bind footprint instances to R14 schematics.

No placement, copper, pads, pin nets, stackup or mechanical geometry change.
"""
from pathlib import Path
import argparse,hashlib,json,re,xml.etree.ElementTree as E
import wx
APP=wx.App(False)
import pcbnew as K
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/'hardware/pcb/split-r12/candidate-i';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ap=argparse.ArgumentParser();ap.add_argument('directory',type=Path);ap.add_argument('domain',choices=['body','flange']);ap.add_argument('--verify-existing',action='store_true');args=ap.parse_args();P=args.directory.resolve();domain=args.domain
bindings=json.loads((P/'partition-source.json').read_text())['board_instances'];f=SOURCE/(domain+'-r12.kicad_pcb');before=sha(f);b=K.LoadBoard(str(f));out=P/domain/(domain+'-r14.kicad_pcb');assert out.exists()if args.verify_existing else not out.exists()
def geometry(b):
 return {'thickness_nm':b.GetDesignSettings().GetBoardThickness(),'layers':b.GetCopperLayerCount(),'tracks':len(list(b.GetTracks())),'board_zones':len(list(b.Zones())),
 'drawings':sorted([str(o.GetShape()),o.GetLayer(),o.GetStart().x,o.GetStart().y,o.GetEnd().x,o.GetEnd().y,o.GetWidth()]for o in b.GetDrawings()if isinstance(o,K.PCB_SHAPE)),
 'footprints':sorted([fp.GetReference(),str(fp.GetFPID().GetLibNickname())+':'+str(fp.GetFPID().GetLibItemName()),fp.GetPosition().x,fp.GetPosition().y,fp.GetOrientationDegrees(),fp.GetLayer(),
  sorted([p.GetNumber(),p.GetNetname(),p.GetPosition().x,p.GetPosition().y,p.GetSize().x,p.GetSize().y,p.GetDrillSize().x,p.GetDrillSize().y,p.GetShape(),p.GetOrientationDegrees()]for p in fp.Pads())]for fp in b.GetFootprints())}
oldgeometry=geometry(b);paths=[]
xml=E.parse(P/domain/(domain+'-native.xml')).getroot();components={c.get('ref'):c for c in xml.findall('components/comp')}
for fp in b.GetFootprints():
 ref=fp.GetReference();bind=bindings[ref];assert bind['domain']==domain
 c=components[ref];tail=c.find('sheetpath').get('tstamps')+c.findtext('tstamps');assert bind['path'].endswith(tail),ref
 oldpath=fp.GetPath().AsString();path=K.KIID_PATH(bind['path']);fp.SetPath(path)
 paths.append({'ref':ref,'old_path':oldpath,'new_path':bind['path']})
if not args.verify_existing:K.SaveBoard(str(out),b)
saved=K.LoadBoard(str(out));newgeometry=geometry(saved);assert newgeometry==oldgeometry
for fp in saved.GetFootprints():assert fp.GetPath().AsString()==bindings[fp.GetReference()]['path']
neutral=lambda path:re.sub(r'(?m)^[ \t]*\(path "[^"\n]*"\)\n','',path.read_text())
assert neutral(f)==neutral(out),'Every native field except schematic instance path must remain byte-identical'
assert sha(f)==before
r={'date':'2026-11-01','linker_sha256':sha(Path(__file__)),'source_R12_board_sha256':before,'native_board_sha256':sha(out),'new_schematic_instances':paths,
 'mechanical_and_electrical_signature_sha256':hashlib.sha256(json.dumps(newgeometry,sort_keys=True).encode()).hexdigest(),'native_geometry_pin_nets_stackup_unchanged':True,'source_native_XML_sha256':sha(P/domain/(domain+'-native.xml')),
 'whole_native_text_equal_except_instance_paths':True,'path_neutral_native_text_sha256':hashlib.sha256(neutral(out).encode()).hexdigest(),
 'scope':'Path-only board instance binding to actual standalone native schematic export. Placement/pads/netnames/drills/outline/stackup conserved; board remains UNROUTED. No Update-PCB GUI import, ERC or physical/process acceptance follows.'}
(P/domain/'instance-link.json').write_text(json.dumps(r,indent=2)+'\n');print(domain,len(paths),'native instances linked; geometry unchanged')
