"""Local pack-interface variant: five solder lands, four original logical nets.

All other footprints/routes retained. Header copper lands1-4 keep centres;
second pin2 land supplies a separate external NTC return. Human BOM untouched.
"""
from pathlib import Path
import sys,json,shutil,math,collections
import pcb_r2_route as R
import kicad_sexp as S
K=R.k;ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'hardware/pcb/flange-access-r28/candidate-s';OUT=Path(sys.argv[1]).resolve();OUT.mkdir(parents=True,exist_ok=True);assert not any(OUT.iterdir());sha=R.sha
for p in SRC.rglob('*'):
 if not p.is_file()or p.suffix not in ['.kicad_sch','.kicad_pro','.kicad_sym']and p.name not in ['fp-lib-table','sym-lib-table']:continue
 rel=str(p.relative_to(SRC)).replace('-r28','-r35');q=OUT/rel;q.parent.mkdir(parents=True,exist_ok=True)
 if p.suffix=='.kicad_sch':
  t=S.parse(p.read_text().replace('-r28','-r35'));relative=p.relative_to(SRC)
  if relative==Path('body/01-power.kicad_sch'):
   j=next(n for n in S.children(t,'symbol')if S.prop(n,'Reference')=='J2')
   for prop in S.children(j,'property'):
    key=prop[1].value
    if key=='Value':prop[2]=S.string('PACK_PIGTAIL_4NET_5LAND')
    if key=='Footprint':prop[2]=S.string('PackPigtailR35:Pack_Pigtail_4Net_5Land')
    if key=='Datasheet':prop[2]=S.string('')
    if key=='ReviewNote':prop[2]=S.string('Copper-only hand-solder interface; do not populate the former Pico-Lock header. Original logical pins1PACK_P,2GND,3PACK_NTC,4PACK_GUARD preserved. Two distinct pad2 lands: original2P power return; new2S at mechanicalXY[-2.2,41.9] for separate NTC return. Join returns only on body PCB. Actual wire, solder/strain relief/loading qualification required; batteryOPEN.')
   bom=S.child(j,'in_bom');assert bom;bom[1]=S.atom('no')
  S.write(q,t)
 elif p.suffix=='.kicad_pro':
  o=json.loads(p.read_text())
  if 'meta'in o and 'filename'in o['meta']:o['meta']['filename']=q.name
  q.write_text(json.dumps(o,indent=2)+'\n')
 else:shutil.copyfile(p,q)
name='Pack_Pigtail_4Net_5Land';lib=OUT/'body/PackPigtailR35.pretty';lib.mkdir();pads=[]
for n,x,y,w,h in [('1',-2.25,-2.795,.6,1.),('2',-.75,-2.795,.6,1.),('3',.75,-2.795,.6,1.),('4',2.25,-2.795,.6,1.),('2',-1.4,-2.58,.5,.5)]:pads.append('(pad "'+n+'" smd roundrect (at '+str(x)+' '+str(y)+') (size '+str(w)+' '+str(h)+') (layers "F.Cu" "F.Mask") (roundrect_rratio 0.25)'+(' (zone_connect 2)'if n=='2'and x==-1.4 else'')+')')
lines=[]
for a,b in [((-2.8,-3.545),(2.8,-3.545)),((2.8,-3.545),(2.8,.37)),((2.8,.37),(-2.8,.37)),((-2.8,.37),(-2.8,-3.545))]:lines.append('(fp_line (start '+str(a[0])+' '+str(a[1])+') (end '+str(b[0])+' '+str(b[1])+') (layer "F.CrtYd") (width 0.05))')
text='(footprint "'+name+'" (version 20211014) (generator pcbnew) (layer "F.Cu") (attr smd exclude_from_bom) (descr "Four-net five-land soldered pack interface; two distinct GND pad2 lands; no populated header or paste")\n(fp_text reference "REF**" (at 0 1.4) (layer "F.Fab") (effects (font (size 1 1) (thickness .15))))\n(fp_text value "'+name+'" (at 0 2.8) (layer "F.Fab") (effects (font (size 1 1) (thickness .15))))\n(fp_text user "SG" (at 0 1.2 90) (layer "F.SilkS") (effects (font (size .8 .8) (thickness .12))))\n'+'\n'.join(lines+pads)+'\n)\n';(lib/(name+'.kicad_mod')).write_text(text)
for p,uri in [(OUT/'fp-lib-table','${KIPRJMOD}/body/PackPigtailR35.pretty'),(OUT/'body/fp-lib-table','${KIPRJMOD}/PackPigtailR35.pretty')]:
 t=S.parse(p.read_text());t.append([S.atom('lib'),[S.atom('name'),S.string('PackPigtailR35')],[S.atom('type'),S.string('KiCad')],[S.atom('uri'),S.string(uri)],[S.atom('options'),S.string('')],[S.atom('descr'),S.string('Copper-only prototype solder lands')]]);S.write(p,t)
source=SRC/'body/body-r28.kicad_pcb';assert sha(source)=='19f0c9b20d4b6e6c43636076531297af3eab12effb196b8ce46c807de477491b';b=K.LoadBoard(str(source));oldroutes=R.route_records(b);old=next(f for f in b.GetFootprints()if f.GetReference()=='J2');oldpads={p.GetNumber():{'xy_mm':R.mech(p.GetPosition()),'net':p.GetNetname(),'size_mm':[K.ToMM(p.GetSize().x),K.ToMM(p.GetSize().y)]}for p in old.Pads()if p.GetNumber()not in ['','MP']};oldposition=old.GetPosition();oldangle=old.GetOrientationDegrees();oldpath=old.GetPath();oldref=old.Reference().IsVisible();all_other={f.GetReference():str(f.GetFPID())for f in b.GetFootprints()if f.GetReference()!='J2'}
fp=K.FootprintLoad(str(lib),name);assert fp;fp.SetReference('J2');fp.SetValue('PACK_PIGTAIL_4NET_5LAND');fp.SetFPID(K.LIB_ID('PackPigtailR35',name));b.Add(fp);fp.SetPosition(oldposition);fp.SetOrientationDegrees(oldangle);fp.SetPath(oldpath);fp.Reference().SetVisible(oldref);fp.Value().SetVisible(False);fp.SetProperty('DesignStatus','CANDIDATE / NOT FABRICATION RELEASE');fp.SetProperty('AssemblyDomain','MAIN_T');fp.SetProperty('CandidateHeight_mm','0');fp.SetProperty('AssemblyInterface','Copper-only; no header. Pad2P original GND, pad2S new isolated landing tied to body GND; external sensor return separate from power return.');fp.SetProperty('Manufacturer','R+D prototype copper');fp.SetProperty('MPN','NO PURCHASED COMPONENT')
padrows=[]
for pad in fp.Pads():
 n=pad.GetNumber();pad.SetNet(b.FindNet(oldpads[n]['net']));xy=R.mech(pad.GetPosition());padrows.append({'number':n,'xy_mm':xy,'net':pad.GetNetname(),'size_local_mm':[K.ToMM(pad.GetSize().x),K.ToMM(pad.GetSize().y)],'paste_present':pad.GetLayerSet().Contains(K.F_Paste)})
newpad=next(p for p in padrows if p['number']=='2'and max(abs(x-y)for x,y in zip(p['xy_mm'],[-2.2,41.9]))<1e-6)
for n,q in oldpads.items():assert any(p['number']==n and p['net']==q['net']and max(abs(x-y)for x,y in zip(p['xy_mm'],q['xy_mm']))<1e-6 for p in padrows),(n,q,padrows)
b.Remove(old)
for a,c in [((-2.2,41.9),(-1.985,41.25))]:
 t=K.PCB_TRACK(b);t.SetStart(R.xy(*a));t.SetEnd(R.xy(*c));t.SetWidth(K.FromMM(.3));t.SetLayer(K.F_Cu);t.SetNet(b.FindNet('GND'));t.SetLocked(True);b.Add(t)
bp=OUT/'body/body-r35.kicad_pcb';K.SaveBoard(str(bp),b);b=K.LoadBoard(str(bp));b.BuildConnectivity();K.ZONE_FILLER(b).Fill(b.Zones());K.SaveBoard(str(bp),b)
now=R.route_records(K.LoadBoard(str(bp)));canon=lambda x:collections.Counter(json.dumps(q,sort_keys=True)for q in x);assert not canon(oldroutes)-canon(now);assert sum((canon(now)-canon(oldroutes)).values())==1
flange=OUT/'flange/flange-r35.kicad_pcb';shutil.copyfile(SRC/'flange/flange-r28.kicad_pcb',flange)
report={'builder_sha256':sha(Path(__file__)),'source_R28_body_sha256':sha(source),'native_body_sha256':sha(bp),'flange_byte_identical_to_R28':sha(flange)==sha(SRC/'flange/flange-r28.kicad_pcb'),'source_J2_original_pad_rows':oldpads,'current_J2_pad_rows':padrows,'J2_position_mm':R.mech(oldposition),'J2_angle_deg':oldangle,'physical_lands':5,'logical_pins':4,'all_original_J2_electrical_pad_centres_and_nets_retained':True,'original_route_count':len(oldroutes),'added_GND_tracks':list((canon(now)-canon(oldroutes)).elements()),'all_other_footprint_IDs_before':all_other,'native_library_sha256':sha(lib/(name+'.kicad_mod')),'source_rules_changed':False,'scope':'Local hand-solder interface variant only: header removed, four original electrical lands retained without paste, two unnetted MP lands removed, one second pad2 GND land plus one0.3mm GND track added. Header is not DNP hardware; J2 now represents copper lands and is excluded from component BOM. Existing circuit topology intended unchanged; fresh native netlist/DRC/footprint/pose/copper and solder/process/strain relief/loading checks still required. BatteryOPEN and humanBOMunchanged.'};R.write(OUT/'interface-change.json',report);print('saved R35 body, pad rows',padrows,'all source routes retained;1GNDsegment added; flange byte-identical',flush=True)
