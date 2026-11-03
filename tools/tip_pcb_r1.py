"""Generate the six-by-four millimetre TMP117 remote tip PCB with KiCad 7.

Run using KiCad's bundled Python. This board implements the REMOTE_TIP domain
of the main schematic; it does not add parts to the human-owned product BOM.
"""
from pathlib import Path
import hashlib
import json
import math
import re
import shutil
import uuid
import xml.etree.ElementTree as ET
import wx
import pcbnew as k

APP = wx.App(False)
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'hardware/pcb/tip-r1'
LIB = OUT / 'TipR1.pretty'
LIB.mkdir(parents=True, exist_ok=True)
SHARED = Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport')
BOARD_PATH = OUT / 'buttplug-tip-r1.kicad_pcb'
NS = uuid.UUID('e4b48ad1-5826-446b-8253-9c89897960fc')

def uid(s): return str(uuid.uuid5(NS, s))
def mm(x): return k.FromMM(x)
def v(p): return k.VECTOR2I(mm(p[0]), mm(p[1]))
def scalar(x): return k.ToMM(x)
def point(p): return [scalar(p.x), scalar(p.y)]

pads = {1:(-.975,-.65),2:(-.975,0),3:(-.975,.65),4:(.975,.65),5:(.975,0),6:(.975,-.65)}
footprint = '''(footprint "TI_TMP117_DRV0006B_NoEP" (version 20221018) (generator pcbnew)
 (layer "F.Cu") (attr smd)
 (descr "TI TMP117 DRV0006B, 4223922/A 09/2017, RevD pages40-42. Six 0.45x0.30 lands at 1.95 row spacing/0.65 pitch. No central copper/paste: rigid PCB thermal pad intentionally unsoldered, TI sections9/10.")
 (tags "TMP117 WSON6 DRV0006B unsoldered thermal pad")
 (solder_mask_margin 0.07)
 (fp_text reference "U101" (at 0 -1.6) (layer "F.Fab") (effects (font (size 0.5 0.5) (thickness 0.08))))
 (fp_text value "TMP117AIDRVR" (at 0 1.6) (layer "F.Fab") (effects (font (size 0.5 0.5) (thickness 0.08))))
'''
for a,b in [((-1,-.5),(-.5,-1)),((-.5,-1),(1,-1)),((1,-1),(1,1)),((1,1),(-1,1)),((-1,1),(-1,-.5))]:
 footprint += f' (fp_line (start {a[0]} {a[1]}) (end {b[0]} {b[1]}) (layer "F.Fab") (width 0.1))\n'
for a,b in [((-1.45,-1.35),(1.45,-1.35)),((1.45,-1.35),(1.45,1.35)),((1.45,1.35),(-1.45,1.35)),((-1.45,1.35),(-1.45,-1.35))]:
 footprint += f' (fp_line (start {a[0]} {a[1]}) (end {b[0]} {b[1]}) (layer "F.CrtYd") (width 0.05))\n'
for n,(x,y) in pads.items():
 footprint += f' (pad "{n}" smd roundrect (at {x} {y}) (size .45 .30) (layers "F.Cu" "F.Paste" "F.Mask") (roundrect_rratio 0.166666667))\n'
footprint += ')\n'
(LIB/'TI_TMP117_DRV0006B_NoEP.kicad_mod').write_text(footprint)
wire = '''(footprint "TipWire4_P1.4mm" (version 20221018) (generator pcbnew)
 (layer "F.Cu") (attr smd)
 (descr "Four direct-wire solder pads, pin1=3V3 pin2=GND pin3=SDA pin4=SCL, left to right viewed from component side")
 (fp_text reference "J101" (at 0 0) (layer "F.Fab") (effects (font (size .5 .5) (thickness .08))))
 (fp_text value "TIP_WIRE4" (at 0 0) (layer "F.Fab") hide (effects (font (size .5 .5) (thickness .08))))
'''
for n,x in enumerate((-2.1,-.7,.7,2.1),1):
 wire += f' (pad "{n}" smd roundrect (at {x} 0) (size .70 .85) (layers "F.Cu" "F.Mask") (roundrect_rratio .15))\n'
for a,b in [((-2.6,-.6),(2.6,-.6)),((2.6,-.6),(2.6,.6)),((2.6,.6),(-2.6,.6)),((-2.6,.6),(-2.6,-.6))]:
 wire += f' (fp_line (start {a[0]} {a[1]}) (end {b[0]} {b[1]}) (layer "F.CrtYd") (width .05))\n'
wire += ')\n'
(LIB/'TipWire4_P1.4mm.kicad_mod').write_text(wire)
shutil.copyfile(SHARED/'footprints/Capacitor_SMD.pretty/C_0402_1005Metric.kicad_mod',LIB/'C_0402_1005Metric.kicad_mod')
shutil.copyfile(ROOT/'hardware/pcb/prototype-r0/PrototypeR0.pretty/LICENSE.md',LIB/'LICENSE.md')
(OUT/'fp-lib-table').write_text('(fp_lib_table (lib (name "TipR1")(type "KiCad")(uri "${KIPRJMOD}/TipR1.pretty")(options "")(descr "Project-local remote sensor land patterns")))\n')

pro = {
 'meta':{'filename':'buttplug-tip-r1.kicad_pro','version':1},
 'board':{'design_settings':{'rules':{'min_clearance':.15,'min_track_width':.15,'min_copper_edge_clearance':.2,'min_via_diameter':.45,'min_through_hole_diameter':.2,'min_via_annular_width':.1}}},
 'net_settings':{'classes':[{'name':'Default','description':'Tip I2C/low-current supply','clearance':.15,'track_width':.15,'via_diameter':.45,'via_drill':.2,'microvia_diameter':.3,'microvia_drill':.1,'bus_width':12,'wire_width':6,'diff_pair_width':.15,'diff_pair_gap':.15,'diff_pair_via_gap':.25}],'meta':{'version':3}}
}
PRO_PATH=OUT/'buttplug-tip-r1.kicad_pro'
PRO_PATH.write_text(json.dumps(pro,indent=2)+'\n')
b=k.BOARD();b.SetFileName(str(BOARD_PATH))
def apply_rules(board):
 s=board.GetDesignSettings();s.SetBoardThickness(mm(.62))
 s.m_MinClearance=mm(.15);s.m_TrackMinWidth=mm(.15)
 s.m_ViasMinSize=mm(.45);s.m_MinThroughDrill=mm(.2)
 s.m_ViasMinAnnularWidth=mm(.1);s.m_CopperEdgeClearance=mm(.2)
 s.m_HoleClearance=mm(.2)
 default=s.m_NetSettings.m_DefaultNetClass
 default.SetClearance(mm(.15));default.SetTrackWidth(mm(.15))
 default.SetViaDiameter(mm(.45));default.SetViaDrill(mm(.2))
apply_rules(b)
nets={}
for name in ['3V3','GND','I2C_SDA','I2C_SCL']:
 net=k.NETINFO_ITEM(b,name);b.Add(net);nets[name]=net

def load(name,ref,value,xy,angle,pin_nets):
 fp=k.FootprintLoad(str(LIB),name)
 if fp is None:raise RuntimeError(name)
 b.Add(fp); fp.SetReference(ref);fp.SetValue(value);fp.SetPosition(v(xy));fp.SetOrientationDegrees(angle)
 fp.Reference().SetVisible(False);fp.Value().SetVisible(False)
 fp.SetFPID(k.LIB_ID('TipR1',name))
 for p in fp.Pads():
  n=p.GetNumber()
  if n in pin_nets:p.SetNet(nets[pin_nets[n]])
 return fp
u=load('TI_TMP117_DRV0006B_NoEP','U101','TMP117AIDRVR',(0,-.65),180,{'1':'I2C_SCL','2':'GND','4':'GND','5':'3V3','6':'I2C_SDA'})
c=load('C_0402_1005Metric','C101','GRM155R71C104KA88D',(-2,-.5),90,{'1':'3V3','2':'GND'})
j=load('TipWire4_P1.4mm','J101','TIP_WIRE4',(0,1.35),0,{'1':'3V3','2':'GND','3':'I2C_SDA','4':'I2C_SCL'})
for p in u.Pads():
 if p.GetNumber()=='3':p.SetPadName('3')

# Rounded outline, six by four mm, R0.3 corners. Coordinates are board-local.
r=.3
lines=[((-2.7,-2),(2.7,-2)),((3,-1.7),(3,1.7)),((2.7,2),(-2.7,2)),((-3,1.7),(-3,-1.7))]
for a,z in lines:
 s=k.PCB_SHAPE(b);s.SetShape(k.SHAPE_T_SEGMENT);s.SetStart(v(a));s.SetEnd(v(z));s.SetWidth(mm(.05));s.SetLayer(k.Edge_Cuts);b.Add(s)
for start,mid,end in [((2.7,-2),(2.912132,-1.912132),(3,-1.7)),((3,1.7),(2.912132,1.912132),(2.7,2)),((-2.7,2),(-2.912132,1.912132),(-3,1.7)),((-3,-1.7),(-2.912132,-1.912132),(-2.7,-2))]:
 s=k.PCB_SHAPE(b);s.SetShape(k.SHAPE_T_ARC);s.SetArcGeometry(v(start),v(mid),v(end));s.SetWidth(mm(.05));s.SetLayer(k.Edge_Cuts);b.Add(s)

track_log=[]
def route(net,layer,points,width=.15):
 for a,z in zip(points,points[1:]):
  t=k.PCB_TRACK(b);t.SetStart(v(a));t.SetEnd(v(z));t.SetWidth(mm(width));t.SetLayer(layer);t.SetNet(nets[net]);b.Add(t)
  track_log.append({'net':net,'layer':k.LayerName(layer),'start_mm':list(a),'end_mm':list(z),'width_mm':width})
def via(net,xy):
 t=k.PCB_VIA(b);t.SetPosition(v(xy));t.SetWidth(mm(.45));t.SetDrill(mm(.2));t.SetViaType(k.VIATYPE_THROUGH);t.SetLayerPair(k.F_Cu,k.B_Cu);t.SetNet(nets[net]);b.Add(t)

# Physical pad positions are deliberately read after native rotation.
pos={(f.GetReference(),p.GetNumber()):tuple(point(p.GetPosition())) for f in (u,c,j) for p in f.Pads()}
route('I2C_SCL',k.F_Cu,[pos['J101','4'],(2.1,.85),(1.4,.7),pos['U101','1']])
route('3V3',k.F_Cu,[pos['J101','1'],(-2.1,.65),pos['C101','1']])
route('3V3',k.F_Cu,[pos['C101','1'],(-1.45,-.02),(-1.45,-.65),pos['U101','5']])
route('I2C_SDA',k.F_Cu,[pos['U101','6'],(-1.25,.5)])
via('I2C_SDA',(-1.25,.5));via('I2C_SDA',(.7,.65))
route('I2C_SDA',k.B_Cu,[(-1.25,.5),(-1.25,-.6),(.7,-.6),(.7,.65)])
route('I2C_SDA',k.F_Cu,[(.7,.65),pos['J101','3']])
for pin,xy in [('2',(1.6,-.65)),('4',(-1.6,-1.3))]:
 route('GND',k.F_Cu,[pos['U101',pin],xy]);via('GND',xy)
route('GND',k.F_Cu,[pos['C101','2'],(-1.6,-1.3)])
route('GND',k.F_Cu,[pos['J101','2'],(-.1,.7)]);via('GND',(-.1,.7))

zone=k.ZONE(b);zone.SetLayer(k.B_Cu);zone.SetNet(nets['GND']);zone.SetLocalClearance(mm(.15));zone.SetPadConnection(k.ZONE_CONNECTION_FULL)
zone.SetThermalReliefGap(mm(.15));zone.SetThermalReliefSpokeWidth(mm(.2));zone.SetMinThickness(mm(.15))
poly=zone.Outline();poly.NewOutline()
for x,y in [(-2.7,-1.7),(2.7,-1.7),(2.7,1.7),(-2.7,1.7)]:poly.Append(mm(x),mm(y))
b.Add(zone)
# Backside plane remains solder-mask covered. Dielectric thermal bonding is
# still mandatory; the mask alone is not an insulation qualification.
# Tiny-board wire numbering belongs in the assembly drawing, not unreadable silk.
b.BuildConnectivity();k.SaveBoard(str(BOARD_PATH),b)
# KiCad7's STEP exporter otherwise synthesizes a1.6mm default, despite the
# general thickness field. This is a0.60mm clad-board /0.62mm masked study;
# fabrication tolerances/materials still need the board supplier's approval.
stackup='''
    (stackup
      (layer "F.SilkS" (type "Top Silk Screen"))
      (layer "F.Paste" (type "Top Solder Paste"))
      (layer "F.Mask" (type "Top Solder Mask") (thickness 0.01))
      (layer "F.Cu" (type "copper") (thickness 0.035))
      (layer "dielectric 1" (type "core") (thickness 0.53) (material "FR4") (epsilon_r 4.5) (loss_tangent 0.02))
      (layer "B.Cu" (type "copper") (thickness 0.035))
      (layer "B.Mask" (type "Bottom Solder Mask") (thickness 0.01))
      (layer "B.Paste" (type "Bottom Solder Paste"))
      (layer "B.SilkS" (type "Bottom Silk Screen"))
      (copper_finish "ENIG") (dielectric_constraints no)
    )'''
raw=BOARD_PATH.read_text();assert '(stackup' not in raw
BOARD_PATH.write_text(raw.replace('  (setup','  (setup'+stackup,1))
# DRC must read the written board/project, not only in-memory assumptions.
b=k.LoadBoard(str(BOARD_PATH));apply_rules(b);b.BuildConnectivity()
filler=k.ZONE_FILLER(b);filler.Fill(b.Zones());k.SaveBoard(str(BOARD_PATH),b)
report=OUT/'drc-tip-r1.rpt';k.WriteDRCReport(b,str(report),k.EDA_UNITS_MILLIMETRES,True)
main_xml=ROOT/'hardware/pcb/prototype-r0/buttplug-r0.xml'
expected={}
for net in ET.parse(main_xml).findall('./nets/net'):
 for node in net.findall('node'):
  if node.attrib['ref'] in ('U101','C101','J101'):
   expected[node.attrib['ref'],node.attrib['pin']]='' if net.attrib['name'].startswith('unconnected-') else net.attrib['name']
actual={(f.GetReference(),p.GetNumber()):p.GetNetname() for f in b.GetFootprints() for p in f.Pads()}
for key,net in actual.items():
 assert net==expected.get(key,''),(key,net,expected.get(key,''))
validation={
 'status':'Connected and routed remote-tip review board; physical and process qualification pending',
 'tool':k.Version(),'units':'mm','pcb_size_mm':[6,4,.62],'structural_clad_thickness_mm':.6,'corner_radius_mm':.3,
 'circuit_domain':'REMOTE_TIP','main_board_connector':'J5 pins1=3V3,2=GND,3=SDA,4=SCL',
 'schematic_parity':{'source':str(main_xml.relative_to(ROOT)),'sha256':hashlib.sha256(main_xml.read_bytes()).hexdigest(),'pad_count':len(actual),'net_mismatches':0},
 'physical_candidates':{
  'U101':{'mpn':'TMP117AIDRVR','source':'https://www.ti.com/lit/ds/symlink/tmp117.pdf','land_pattern':'TI4223922/A,09/2017, sixlands with unsoldered EP'},
  'C101':{'mpn':'GRM155R71C104KA88D','source':'https://www.murata.com/en-global/api/pdfdownloadapi?cate=luCeramicCapacitorsSMD&partno=GRM155R71C104KA88%23','value':'100nF16VX7R10%0402','body_max_xyz_mm':[1.05,.55,.55],'boundary':'Current lot, availability and generic KiCad0402land-pattern acceptance need review; no purchase'}
 },
 'footprints':{f.GetReference():{'value':f.GetValue(),'xy_mm':point(f.GetPosition()),'rotation_deg':f.GetOrientationDegrees(),'pad_nets':{p.GetNumber():p.GetNetname() for p in f.Pads()}} for f in b.GetFootprints()},
 'unconnected_from_native_connectivity':b.GetConnectivity().GetUnconnectedCount(False),
 'drc_report':str(report.relative_to(ROOT)), 'tracks':track_log,
 'component_envelopes':[
  {'ref':'U101','xy_center_mm':[0,-.65],'body_max_xyz_mm':[2.1,2.1,.8],'front_assembly_height_reservation_mm':.9},
  {'ref':'C101','xy_center_mm':[-2,-.5],'body_max_xyz_mm':[.55,1.05,.55],'front_assembly_height_reservation_mm':.65}
 ],
 'thermal_pad':'Package EP7 intentionally unsoldered, no central solder land or paste; front vias tented by process requirement. Backside masked GND plane needs a qualified dielectric thermal bond to metal.',
 'wire_interface':'Direct-wire pads; no paste openings. Gauge/insulation, strain relief and installed lengths remain to qualify.',
 'manufacturing_open_items':['Independent layout review and current circuit parity','Assembler panelization/handling of6x4mm board','0.2mm drill/0.45mm via, mask registration and tenting','0.6mm stackup, finish, reflow profile and inspection','Dielectric thermal bond and installed response/calibration','Physical cable/strain relief and final tip carrier fit'],
 'source_sha256':{}
}
for p in [Path(__file__),*LIB.glob('*.kicad_mod'),BOARD_PATH,PRO_PATH]:validation['source_sha256'][str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
(OUT/'validation-tip-r1.json').write_text(json.dumps(validation,indent=2)+'\n')
print('Saved',BOARD_PATH)
print('Native unconnected:',validation['unconnected_from_native_connectivity'])
print(report.read_text())
