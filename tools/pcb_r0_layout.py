#!/usr/bin/env python3
"""Generate the real R0 main-board placement from the circuit manifest.

Run with KiCad's bundled Python (pcbnew and wx). The manifest/netlist remain
schematic-owned; this script emits candidate field assignments for that owner.
The native board is a review source, never a fabrication approval.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

import wx

APP = wx.App(False)
import pcbnew as k

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "hardware/pcb/prototype-r0"
LIB = PROJECT / "PrototypeR0.pretty"
SYSTEM_LIB = Path("/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints")
BOARD = PROJECT / "buttplug-r0.kicad_pcb"
ORIGIN = (100.0, 130.0)

# Mechanical +Y points toward the tip. KiCad +Y points down on screen.
def xy(x, y):
    return k.VECTOR2I(k.FromMM(ORIGIN[0] + x), k.FromMM(ORIGIN[1] - y))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main_outline():
    """Clip unused FR4 at the module antenna feed region; keep the T topology."""
    source=json.loads((ROOT/'hardware/cad/prototype-r0/geometry-report.json').read_text())['pcb_outline_vertices_xy_mm']
    result=[];limit=31.6
    for a,b in zip(source[-1:]+source[:-1],source):
        inside_a=a[0]<=limit;inside_b=b[0]<=limit
        if inside_a!=inside_b:
            y=a[1]+(b[1]-a[1])*(limit-a[0])/(b[0]-a[0]);result.append([limit,round(y,6)])
        if inside_b:result.append(b)
    return result


def save_json(path, data):
    path.write_text(json.dumps(data, indent=2) + "\n")


def small_footprint(name, body, pads, source):
    """Make a two-terminal, nonpolar, manufacturer reflow-land candidate."""
    bw, bh = body
    pw, ph, center = pads
    cx = max(bw / 2, center + pw / 2) + 0.25
    cy = max(bh / 2, ph / 2) + 0.25
    s = [f'(footprint "{name}" (version 20221018) (generator pcb_r0_layout)',
         '(layer "F.Cu") (attr smd)', f'(descr "{source}")',
         '(fp_text reference "REF**" (at 0 -1.8) (layer "F.SilkS") (effects (font (size 0.6 0.6) (thickness 0.1))))',
         f'(fp_text value "{name}" (at 0 1.8) (layer "F.Fab") (effects (font (size 0.6 0.6) (thickness 0.1))))']
    for layer, x, y in [('F.Fab', bw / 2, bh / 2), ('F.CrtYd', cx, cy)]:
        s.append(f'(fp_rect (start {-x} {-y}) (end {x} {y}) (stroke (width 0.05) (type default)) (fill none) (layer "{layer}"))')
    for number, px in [(1, -center), (2, center)]:
        s.append(f'(pad "{number}" smd roundrect (at {px} 0) (size {pw} {ph}) (layers "F.Cu" "F.Paste" "F.Mask") (roundrect_rratio 0.1))')
    (LIB / (name + '.kicad_mod')).write_text('\n  '.join(s) + '\n)\n')


COPIES = [
    ('Inductor_SMD', 'L_Coilcraft_XxL4020'),
    ('Button_Switch_SMD', 'SW_SPST_B3U-1000P'),
    ('Fuse', 'Fuse_1206_3216Metric'),
    ('Connector_JST', 'JST_PH_S4B-PH-SM4-TB_1x04-1MP_P2.00mm_Horizontal'),
    ('Connector_JST', 'JST_SH_SM06B-SRSS-TB_1x06-1MP_P1.00mm_Horizontal'),
    ('Jumper', 'SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm'),
    ('Package_TO_SOT_SMD', 'SOT-23-5'),
    ('Package_TO_SOT_SMD', 'TSOT-23-6'),
    ('Package_TO_SOT_SMD', 'SOT-23'),
    ('Connector_JST', 'JST_SH_SM02B-SRSS-TB_1x02-1MP_P1.00mm_Horizontal'),
]


def prepare_library():
    LIB.mkdir(exist_ok=True)
    for library, name in COPIES:
        shutil.copyfile(SYSTEM_LIB / (library + '.pretty') / (name + '.kicad_mod'), LIB / (name + '.kicad_mod'))
    # Manufacturer IEC reflow alternatives from Vishay document 28950.
    small_footprint('Vishay_TNPW0603_IEC_Reflow', (1.6, .85), (.55, .90, .725),
                    'Vishay TNPW e3 doc28758; IEC reflow lands doc28950: G0.90 Y0.55 X0.90mm; local courtyard allowance')
    small_footprint('Vishay_TNPW0805_IEC_Reflow', (2.0, 1.25), (.65, 1.30, .875),
                    'Vishay TNPW e3 doc28758; IEC reflow lands doc28950: G1.10 Y0.65 X1.30mm; local courtyard allowance')
    # Reflow dimensions within Murata's published GRM-family land ranges.
    for name, body, pads in [
        ('Murata_GRM18_0603_Reflow', (1.6, .8), (.65, .8, .675)),
        ('Murata_GRM21_0805_Reflow', (2., 1.25), (.70, 1.3, .95)),
        ('Murata_GRM31_1206_Reflow', (3.2, 1.6), (1.05, 1.7, 1.475)),
        ('Murata_GRM32_1210_Reflow', (3.2, 2.5), (1.10, 2.3, 1.65)),
    ]:
        small_footprint(name, body, pads,
                        'Murata GRM reference-sheet reflow land ranges; chosen midpoint pattern, local courtyard allowance; verify exact part and assembler process')
    small_footprint('TDK_C1608_0603_Reflow', (1.6, .8), (.65, .8, .675),
                    'TDK C1608X7R1E105K080AB recommended reflow PA PB PC each 0.6 to 0.8mm; local courtyard allowance')
    # The generic circuit symbol is A=1,K=2. Stock KiCad diode is K=1,A=2.
    src = SYSTEM_LIB / 'Diode_SMD.pretty/D_SOD-123.kicad_mod'
    text = src.read_text()
    text = re.sub(r'\(pad ("?)([12])\1 ', lambda m: '(pad "' + ('2' if m[2] == '1' else '1') + '" ', text)
    text = text.replace('D_SOD-123', 'Diodes_B140HW_SOD123_A1_K2')
    text = text.replace('Diode_SMD.3dshapes/Diodes_B140HW_SOD123_A1_K2.wrl','Diode_SMD.3dshapes/D_SOD-123.wrl')
    text = text.replace('(descr ', '(descr "Renumbered A1 K2 to match R0 circuit symbol. Cathode bar remains on pad2. " )\n  (descr ', 1)
    # Keep one description field for native compatibility.
    text = re.sub(r'\(descr "Renumbered[^\n]+\n  \(descr [^\n]+',
                  '(descr "Diodes B140HW SOD123; derived KiCad pattern; R0 A1 K2 numbering, cathode bar on pad2; primary DS30670")', text)
    (LIB / 'Diodes_B140HW_SOD123_A1_K2.kicad_mod').write_text(text)


MURATA_REF = 'https://search.murata.co.jp/Ceramy/image/img/A01X/G101/ENG/GRM188R71C104KA01-01.pdf'
CAPS = {
    '100nF': ('GRM188R71C104KA01D', 'Murata_GRM18_0603_Reflow', .9, '100 nF, 16 V, X7R, 10%'),
    '1uF': ('C1608X7R1E105K080AB', 'TDK_C1608_0603_Reflow', .9, '1 uF, 25 V, X7R, 10%'),
    '4.7uF': ('GRM21BR71A475KA73L', 'Murata_GRM21_0805_Reflow', 1.4, '4.7 uF, 10 V, X7R, 10%'),
    '10uF': ('GRM21BR61A106KE19L', 'Murata_GRM21_0805_Reflow', 1.35, '10 uF, 10 V, X5R, 10%'),
    '22uF': ('GRM31CR71A226KE15L', 'Murata_GRM31_1206_Reflow', 2.7, '22 uF, 10 V, X7R, 10%'),
    '47uF': ('GRM32ER61A476KE20L', 'Murata_GRM32_1210_Reflow', 2.7, '47 uF, 10 V, X5R, 10%'),
}
RESISTOR_CODES = {'10.0k': '10K0', '8.87k': '8K87', '3.24k': '3K24', '10k': '10K0', '100k': '100K',
                  '312k': '312K', '362k': '362K', '4.7k': '4K70', '11k': '11K0', '1.00M': '1M00', '715k': '715K', '110k': '110K', '200k': '200K', '1k': '1K00'}


def selection(part):
    ref, value = part['ref'], part['value']
    if ref.startswith('R'):
        token = value.split()[0]
        if token not in RESISTOR_CODES:
            raise ValueError(f'New resistor needs explicit candidate selection: {ref}={value}')
        size = '0805' if token in ('362k', '715k', '1.00M') else '0603'
        return dict(mpn=f'TNPW{size}{RESISTOR_CODES[token]}BEEA', manufacturer='Vishay',
                    footprint='Vishay_TNPW' + size + '_IEC_Reflow', height_mm=.55,
                    source='https://www.vishay.com/docs/28758/tnpw_e3.pdf',
                    land_source='https://www.vishay.com/doc?28950',
                    note='0.1%, 25 ppm/K family candidate; E192 supported. Procurement and actual lot are unverified.')
    if ref.startswith('C'):
        if ref in ('C51','C52','C53','C54'):
            return dict(mpn='C1608X5R1A106K080AC', manufacturer='TDK', footprint='TDK_C1608_0603_Reflow', height_mm=.9,
                        source='https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=C1608X5R1A106K080AC',
                        land_source='https://product.tdk.com/system/files/dam/doc/product/capacitor/ceramic/mlcc/charasheet/c1608x5r1a106k080ac.pdf',
                        note='10 uF, 10 V, X5R, 10%; production version. Local HF bypass from TI reference circuit; effective capacitance, voltage margin and loop behavior remain to be verified.')
        for token, (mpn, footprint, height, desc) in CAPS.items():
            if value.startswith(token):
                if token == '1uF':
                    return dict(mpn=mpn, manufacturer='TDK', footprint=footprint, height_mm=height,
                                source='https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=C1608X7R1E105K080AB',
                                land_source='https://product.tdk.com/system/files/dam/doc/product/capacitor/ceramic/mlcc/charasheet/c1608x7r1e105k080ab.pdf',
                                note=desc + '; production status shown by manufacturer. Effective capacitance in this circuit remains unverified.')
                return dict(mpn=mpn, manufacturer='Murata', footprint=footprint, height_mm=height,
                            source='https://www.murata.com/en-global/api/pdfdownloadapi?cate=luCeramicCapacitorsSMD&partno=' + mpn[:-1] + '%23',
                            land_source=MURATA_REF, note=desc + '; DC-bias, temperature, tolerance and effective capacitance need verification in this circuit.')
        raise ValueError(f'New capacitor needs explicit candidate selection: {ref}={value}')
    if ref in ('L1', 'L2'):
        return dict(mpn='XFL4020-152MEC', manufacturer='Coilcraft', footprint='L_Coilcraft_XxL4020', height_mm=2.1,
                    source='https://www.coilcraft.com/pdfs/xfl4020.pdf', note='1.5 uH, 20%; 4.1 A saturation at 10% inductance drop, 25 C. Published land pattern matches library. Peak-current and thermal qualification remain open.')
    if ref.startswith('SW'):
        return dict(mpn='B3U-1000P', manufacturer='Omron', footprint='SW_SPST_B3U-1000P', height_mm=1.75,
                    source='https://omronfs.omron.com/en_US/ecb/products/pdf/en-b3u.pdf',
                    note='Top-actuated SPST-NO; no boss or ground terminal. Two contacts are electrically interchangeable. Silicone actuator, force, travel and sealing remain unvalidated.')
    choices = {
        'F1': ('1206L050YR', 'Littelfuse', 'Fuse_1206_3216Metric', .75,
               'https://www.littelfuse.com/assetdocs/resettable-ptcs-1206l-datasheet?assetguid=2b6a1515-d4ee-4c83-8bd4-152b4901b8f5',
               '0.5 A hold at 20 C, 6 V family candidate; not a precision current limiter. Exact YR ordering suffix from manufacturer packaging table; resistance and enclosed temperature derating still require review.'),
        'D1': ('B140HW-7', 'Diodes Inc.', 'Diodes_B140HW_SOD123_A1_K2', 1.35,
               'https://www.diodes.com/datasheet/download/B140HW.pdf', '1 A / 40 V Schottky candidate. Local footprint explicitly maps A=1,K=2 to the R0 symbol; stock KiCad polarity numbering would be wrong.'),
        'J1': ('S2B-PH-SM4-TB', 'JST', 'JST_PH_S2B-PH-SM4-TB_1x02-1MP_P2.00mm_Horizontal', 4.8,
               'https://www.jst-mfg.com/product/pdf/eng/ePH.pdf', 'Internal dock harness header only; exposed magnetic contacts, seals, polarity and pigtail remain separate mechanical work.'),
        'J2': ('S4B-PH-SM4-TB', 'JST', 'JST_PH_S4B-PH-SM4-TB_1x04-1MP_P2.00mm_Horizontal', 4.8,
               'https://www.jst-mfg.com/product/pdf/eng/ePH.pdf', 'Four-wire protected pack adapter: PACK_P,GND,PACK_NTC,PACK_GUARD. Actual pack lead order and two cell-coupled NTC attachments require review.'),
        'J3': ('SM02B-SRSS-TB', 'JST', 'JST_SH_SM02B-SRSS-TB_1x02-1MP_P1.00mm_Horizontal', 2.95,
               'https://www.jst-mfg.com/product/pdf/eng/eSH.pdf', 'Motor OUT1/OUT2; pin2 is not ground. Connector headline rating does not qualify measured startup/stall or actual wire/crimp path.'),
        'J4': ('SM06B-SRSS-TB', 'JST', 'JST_SH_SM06B-SRSS-TB_1x06-1MP_P1.00mm_Horizontal', 2.95,
               'https://www.jst-mfg.com/product/pdf/eng/eSH.pdf', 'Self-powered native USB/debug harness. No USB VBUS on this connector. Harness impedance, ESD and fixture remain open.'),
        'J5': ('SM04B-SRSS-TB', 'JST', 'JST_SH_SM04B-SRSS-TB_1x04-1MP_P1.00mm_Horizontal', 2.95,
               'https://www.jst-mfg.com/product/pdf/eng/eSH.pdf', 'Tip harness1=3V3,2=GND,3=SDA,4=SCL. Connector/mating-plug and bend envelope need mechanical validation.'),
        'JP1': ('PCB solder jumper / open', 'PCB feature', 'SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm', 0,
                'https://gitlab.com/kicad/libraries/kicad-footprints/', 'Fabricated open copper feature; charging permit remains open by default. Not a purchased shorting cap.'),
    }
    if ref in choices:
        mpn, maker, footprint, height, source, note = choices[ref]
        if ref=='J2' and len(part['pins'])==3:
            mpn='S3B-PH-SM4-TB'
            footprint='JST_PH_S3B-PH-SM4-TB_1x03-1MP_P2.00mm_Horizontal'
            note='Current three-wire schematic snapshot only. Charge-guard revision is expected to change this to four pins; do not freeze this header.'
        return dict(mpn=mpn, manufacturer=maker, footprint=footprint, height_mm=height, source=source, note=note)
    ic = {'U1': ('BQ24074RGT', 'TI_RGT0016C_3x3mm_BQ24074_EP1.68mm', 1.0),
          'U2': ('TPS63070RNM', 'TI_RNM0015A_2.5x3mm_TPS63070', 1.0),
          'U3': ('TPS63070RNM', 'TI_RNM0015A_2.5x3mm_TPS63070', 1.0),
          'U4': ('SN74LVC1G11DBVR', 'SOT-23-6', 1.45),
          'U5': ('DRV8212DSGR', 'WSON-8-1EP_2x2mm_P0.5mm_EP0.9x1.6mm', .8),
          'U6': ('ESP32-C3-MINI-1-N4X', 'Espressif_ESP32-C3-MINI-1_53Pads', 2.55),
          'U7': ('MC3635', 'MEMSIC_MC3635_LGA10_1.6x1.6mm_P0.4mm', 1.0),
          'U8': ('TPS3700DDCR', 'TSOT-23-6', 1.1),
          'U9': ('TPS3808G33DBVR', 'SOT-23-6', 1.45),
          'Q1': ('AO3400A', 'SOT-23', 1.25)}
    if ref in ic:
        mpn, footprint, height = ic[ref]
        return dict(mpn=mpn, manufacturer='Alpha and Omega Semiconductor' if ref == 'Q1' else ('MEMSIC' if ref == 'U7' else ('Espressif' if ref == 'U6' else 'Texas Instruments')),
                    footprint=footprint, height_mm=height,
                    source={'U8':'https://www.ti.com/lit/ds/symlink/tps3700.pdf',
                            'U9':'https://www.ti.com/lit/ds/symlink/tps3808.pdf',
                            'Q1':'https://www.aosmd.com/sites/default/files/res/datasheets/AO3400A.pdf'}.get(ref,'See footprint-register-r0.json'),
                    land_source={'U8':'https://www.ti.com/lit/ml/mpds124i/mpds124i.pdf',
                                 'U9':'https://www.ti.com/lit/ds/symlink/tps3808.pdf',
                                 'Q1':'https://www.aosmd.com/sites/default/files/res/package/SOT23.pdf'}.get(ref,'See footprint-register-r0.json'),
                    note='Candidate IC; package and assembly-process boundaries remain in the footprint/charge review.' + (' MC3635 nominal contact-sized 0.30x0.20mm lands; device-specific stencil/process acceptance remains open.' if ref == 'U7' else ''))
    raise ValueError(f'No explicit candidate for {ref}={value}')


# Mechanical XY in millimetres; angle is native KiCad before side flip.
PLACEMENT = {
 'U6': (26,-17.75,-90,'F'), 'SW1':(-30,-12,0,'F'), 'SW2':(-20,-12,0,'F'),
 'SW3':(8,-12,0,'F'), 'SW4':(14,-12,0,'F'), 'J1':(-30,-21,0,'F'),
 'J2':(-10,-17.5,180,'F'), 'J4':(8,-21,0,'F'),
 'U1':(-24,-18,0,'B'), 'F1':(-31,-24,0,'B'), 'D1':(-26,-24,0,'B'),
 'C1':(-24.75,-14.3,90,'B'), 'C2':(-20,-17.5,180,'B'), 'C3':(-28,-19,0,'B'),
 'R1':(-27.5,-15.5,90,'B'), 'R2':(-30.5,-18,90,'B'), 'R3':(-30,-11,0,'B'),
 'R4':(-17,-13,0,'B'), 'R5':(-17,-15.5,0,'B'), 'JP1':(-8,-11,0,'B'),
 'U2':(1.65,10,0,'B'), 'L1':(-2.5,10,-90,'B'),
 'C11':(3.65,14,90,'B'), 'C12':(0,14.9,0,'B'),
 'C13':(-3,4.3,-90,'B'), 'C14':(0,.8,0,'B'), 'C15':(3,4.3,-90,'B'),
 'C51':(1.2,12.9,0,'B'), 'C52':(1.2,7.3,0,'B'),
 'C16':(4.1,9.7,90,'B'), 'R11':(3,7,0,'F'), 'R12':(3,9,0,'F'),
 'R13':(-3.3,14,90,'B'),
 'U3':(1.7,40,0,'B'), 'L2':(-2.6,40,-90,'B'),
 'C21':(4.6,44.1,90,'B'), 'C22':(0,45.5,0,'B'),
 'C23':(-4,34.1,-90,'B'), 'C24':(0,33.5,0,'B'), 'C25':(3.5,33.7,-90,'B'),
 'C53':(1.1,42.9,0,'B'), 'C54':(1.1,37,0,'B'),
 'C26':(4.35,39.9,90,'B'), 'R21':(6,37.8,90,'B'), 'R22':(6,41,90,'B'),
 'R26':(-4.5,44.4,90,'B'), 'U5':(0,49,0,'B'),
 'C28':(2.6,50.5,90,'B'), 'C29':(-2.6,50.5,90,'B'), 'C30':(0,54,0,'B'),
 'U4':(4.4,55.9,90,'B'), 'C27':(4.5,59.3,0,'B'),
 'R23':(4.5,61.3,0,'B'), 'R24':(4.5,63.3,0,'B'), 'R25':(4.5,65.3,0,'B'),
 'J3':(-2.4,62,180,'B'), 'J5':(0,73,180,'B'),
 'U7':(0,66.8,0,'B'), 'C41':(-2.4,67.6,90,'B'), 'C42':(2.4,67.6,90,'B'),
 'R41':(0,69,0,'B'),
 'C31':(28.4,-15.75,0,'B'), 'C32':(28.4,-13.15,0,'B'), 'C33':(15.5,-15.5,90,'B'),
 'R31':(17,-12,0,'B'), 'R32':(17,-23.5,0,'B'), 'R33':(14,-23.5,0,'B'),
 'R34':(11,-23.5,0,'B'), 'R35':(-30,-15,0,'B'), 'R36':(-17,-20,0,'B'),
 'R37':(3,-5.2,0,'B'), 'R38':(3,-7.2,0,'B'),
 'U8':(-12,-21,0,'B'), 'U9':(-6.5,-21,0,'B'), 'Q1':(-3,-17,0,'B'),
 'R42':(-13,-12,0,'B'), 'R43':(-13,-15,90,'B'), 'R44':(-10,-15,90,'B'),
 'R45':(-7,-15,90,'B'), 'R46':(-2,-23.5,0,'B'), 'R47':(-3,-13,90,'B'),
 'R48':(0,-17,90,'B'), 'C43':(-15,-21,90,'B'), 'C44':(-9.25,-21,90,'B'),
 'R39':(-3.8,-3,90,'B'), 'R40':(-3.8,0,90,'B'), 'C34':(-1,-1.8,90,'B'),
}


def critical_routes(board):
    """Short, locked converter/decoupling routes; remaining nets use review routing."""
    footprints={f.GetReference():f for f in board.GetFootprints()}
    def pad(ref, number):
        return next(p for p in footprints[ref].Pads() if p.GetNumber()==str(number))
    def point(p):
        v=p.GetPosition();return (k.ToMM(v.x)-ORIGIN[0],ORIGIN[1]-k.ToMM(v.y))
    def path(net, points, width=.3, layer=k.B_Cu):
        points=[point(v) if isinstance(v,k.PAD) else v for v in points]
        for a,b in zip(points,points[1:]):
            if a==b:continue
            t=k.PCB_TRACK(board);t.SetStart(xy(*a));t.SetEnd(xy(*b));t.SetWidth(k.FromMM(width));t.SetLayer(layer);t.SetNet(board.FindNet(net));t.SetLocked(True);board.Add(t)
    def via(net,x,y):
        v=k.PCB_VIA(board);v.SetPosition(xy(x,y));v.SetWidth(k.FromMM(.6));v.SetDrill(k.FromMM(.3));v.SetViaType(k.VIATYPE_THROUGH);v.SetLayerPair(k.F_Cu,k.B_Cu);v.SetNet(board.FindNet(net));v.SetLocked(True);board.Add(v)
    for n,origin_x,origin_y in [(1,1.65,10),(2,1.7,40)]:
        u='U'+str(n+1);ind='L'+str(n)
        p11=pad(u,11);p9=pad(u,9);p10=pad(u,10)
        x11,y11=point(p11);x9,y9=point(p9);x10,y10=point(p10)
        # Escape parallel to the three exposed strips before widening toward L.
        path(f'REG{n}_L1',[p11,(-.3,y11+.15)],.25)
        path(f'REG{n}_L1',[(-.3,y11+.15),(-.6,y11+.4),pad(ind,1)],.5)
        path(f'REG{n}_L2',[p9,(-.3,y9-.15)],.25)
        path(f'REG{n}_L2',[(-.3,y9-.15),(-.6,y9-.4),pad(ind,2)],.5)
        via('GND',-.35,y10);path('GND',[p10,(-.35,y10)],.25)
        path('GND',[pad(u,4),(origin_x+.15,origin_y-.25),(origin_x+.15,origin_y),p10],.15)
        p15=pad(u,15);x15,y15=point(p15);via('GND',x15+.725,y15+.4);path('GND',[p15,(x15+.725,y15+.4)],.15)
        aux='C16' if n==1 else 'C26'
        path(f'REG{n}_AUX',[pad(u,3),pad(aux,1)],.15)
        # VIN/EN and the nearest input bypass; output capacitors form a short bus.
        cin1='C11' if n==1 else 'C21';cin2='C12' if n==1 else 'C22'
        vin=pad(u,13);xvin,yvin=point(vin);xc,yc=point(pad(cin1,1))
        path('SYS',[vin,(xvin,yvin+.8),(xvin+yc-yvin-.8,yc),pad(cin1,1)],.3)
        path('SYS',[pad(cin1,1),pad(cin2,1)],.6)
        cout1='C13' if n==1 else 'C23';cout2='C14' if n==1 else 'C24';cout3='C15' if n==1 else 'C25'
        rail='3V3' if n==1 else 'MOTOR_3V7';vout=pad(u,7)
        xo,yo=point(vout);xc,yc=point(pad(cout3,1));bus_y=point(pad(cout1,1))[1]
        path(rail,[vout,(xo,yo-.7),(xo+yo-.7-bus_y,bus_y),(xc,bus_y),pad(cout3,1)],.3)
        path(rail,[pad(cout1,1),(xc,bus_y),pad(cout3,1)],.6)
        xb,yb=point(pad(cout2,1));path(rail,[(xb,bus_y),pad(cout2,1)],.6)
        hf_in='C51' if n==1 else 'C53';hf_out='C52' if n==1 else 'C54'
        path('SYS',[vin,(xvin,yvin+.8),pad(hf_in,1)],.25)
        path(rail,[vout,(xo,yo-.7),pad(hf_out,1)],.25)
        for cap in (hf_in,hf_out):
            gx,gy=point(pad(cap,2));via('GND',gx-.725,gy);path('GND',[pad(cap,2),(gx-.725,gy)],.25)
        for cap in [cin1,cin2,cout1,cout2,cout3]:
            p=pad(cap,2);gx,gy=point(p)
            vx=gx+(1.15 if gx>0 else -1.15)
            if n==1 and vx>4.4:vx=4.4
            vy=gy
            if cap=='C11':vx=4.4;vy=gy
            via('GND',vx,vy);path('GND',[p,(vx,vy)],.35)
    # Logic feedback uses two small top-face resistors outside the pack region.
    via('REG1_FB',3.1,8.1);path('REG1_FB',[pad('U2',5),(3.1,8.1)],.15)
    path('REG1_FB',[(3.1,8.1),pad('R11',2)],.2,k.F_Cu)
    path('REG1_FB',[(3.1,8.1),pad('R12',1)],.2,k.F_Cu)
    via('3V3',2.275,6.5);path('3V3',[pad('R11',1),(2.275,6.5)],.2,k.F_Cu)
    path('3V3',[(2.275,6.5),(2.275,5.775)],.3)
    path('REG2_FB',[pad('U3',5),pad('R21',2),pad('R22',1)],.15)
    # Bridge supply bypasses exit away from its output pads.
    path('MOTOR_3V7',[pad('U5',1),pad('C28',1)],.25)
    path('3V3',[pad('U5',8),pad('C29',1)],.25)
    for cap,dx in [('C28',-1.05),('C29',1.05)]:
        gx,gy=point(pad(cap,2));via('GND',gx+dx,gy);path('GND',[pad(cap,2),(gx+dx,gy)],.25)
    path('MOTOR_3V7',[pad('C28',1),(3.6,50.3),(3.6,53.3),pad('C30',1)],.6)
    via('GND',-.3,49);path('GND',[pad('U5',9),(-.3,49)],.3)
    # Narrow device escapes widen outside the fine-pitch packages.
    for net,number,x,y in [('MOTOR_P',2,3.7,49.25),('MOTOR_N',3,3.7,48.25)]:
        path(net,[pad('U5',number),(x,y)],.25);via(net,x,y)
    # The BQ ground land is enclosed by fine-pitch leads. This central via
    # requires a filled/capped via-in-pad and stencil review before release.
    via('GND',-24,-18)
    path('VBUS_CHG',[pad('U1',6),(-23.75,-20.5)],.25);via('VBUS_CHG',-23.75,-20.5)
    path('VBUS_CHG',[pad('U1',13),pad('C1',1),(-26,-15.25)],.25);via('VBUS_CHG',-26,-15.25)
    path('PACK_P',[pad('U1',2),pad('U1',3),pad('C2',1)],.3)
    path('SYS',[pad('U1',11),pad('U1',10),(-26.2,-18.25)],.25)
    path('SYS',[(-26.2,-18.25),pad('C3',1)],.3)
    for cap,dx,dy in [('C1',1.05,0),('C2',1.05,0),('C3',0,-1.05)]:
        gx,gy=point(pad(cap,2));via('GND',gx+dx,gy+dy);path('GND',[pad(cap,2),(gx+dx,gy+dy)],.3)
    path('3V3',[pad('U7',6),pad('U7',7)],.15)
    # Module's local 3V3 bypass is on the opposite face, directly below pin 3.
    via('3V3',28.4,-12.45);path('3V3',[pad('U6',3),(28.4,-12.45)],.3,k.F_Cu)
    path('3V3',[(28.4,-12.45),pad('C32',1),pad('C31',1)],.4)
    for x,y in [(22,-14.55),(30,-20.95),(24.5,-14.45),(26,-17.75),(-3,18),(3,25),(-4,47),(0,57),(3,70)]:via('GND',x,y)
    # Coupled bench USB route on F.Cu over the reserved inner ground plane.
    # Width/spacing/stackup still require fabricator impedance approval.
    path('USB_DM',[pad('J4',2),(6.5,-17.5),(12.8,-17.5),(17.3,-22),(17.3,-24.8),(22.8,-24.8),pad('U6',26)],.2,k.F_Cu)
    path('USB_DP',[pad('J4',3),(7.5,-18),(12.6,-18),(16.8,-22.2),(16.8,-25.3),(23.6,-25.3),pad('U6',27)],.2,k.F_Cu)


def ground_planes(board,outline):
    for layer in [k.F_Cu,k.In1_Cu,k.In2_Cu,k.B_Cu]:
        z=k.ZONE(board);z.SetLayer(layer);z.SetNet(board.FindNet('GND'));z.SetLocalClearance(k.FromMM(.1));z.SetMinThickness(k.FromMM(.2))
        z.SetPadConnection(k.ZONE_CONNECTION_THERMAL);z.SetThermalReliefGap(k.FromMM(.2));z.SetThermalReliefSpokeWidth(k.FromMM(.3))
        poly=z.Outline();poly.NewOutline()
        for x,y in outline:
            p=xy(x,y);poly.Append(p.x,p.y)
        board.Add(z)
    board.BuildConnectivity()


def ensure_stackup():
    """KiCad 7's STEP exporter requires explicit layers, not only general thickness."""
    s=BOARD.read_text()
    if '(stackup' not in s:
        stack='''(stackup
      (layer "F.SilkS" (type "Top Silk Screen"))
      (layer "F.Paste" (type "Top Solder Paste"))
      (layer "F.Mask" (type "Top Solder Mask") (thickness 0.01))
      (layer "F.Cu" (type "copper") (thickness 0.035))
      (layer "dielectric 1" (type "prepreg") (thickness 0.1) (material "FR4") (epsilon_r 4.5) (loss_tangent 0.02))
      (layer "In1.Cu" (type "copper") (thickness 0.0175))
      (layer "dielectric 2" (type "core") (thickness 0.675) (material "FR4") (epsilon_r 4.5) (loss_tangent 0.02))
      (layer "In2.Cu" (type "copper") (thickness 0.0175))
      (layer "dielectric 3" (type "prepreg") (thickness 0.1) (material "FR4") (epsilon_r 4.5) (loss_tangent 0.02))
      (layer "B.Cu" (type "copper") (thickness 0.035))
      (layer "B.Mask" (type "Bottom Solder Mask") (thickness 0.01))
      (layer "B.Paste" (type "Bottom Solder Paste"))
      (layer "B.SilkS" (type "Bottom Silk Screen"))
      (copper_finish "None")
      (dielectric_constraints no)
    )'''
        s=s.replace('(setup\n','(setup\n    '+stack+'\n',1)
        BOARD.write_text(s)


def build():
    prepare_library()
    manifest_path = PROJECT/'candidate-pin-manifest.json'
    allparts = json.loads(manifest_path.read_text())['parts']
    parts = [p for p in allparts if p['assembly_domain'] == 'MAIN_T' and not p['ref'].startswith('#')]
    candidates = {p['ref']: selection(p) for p in parts}
    assignments = {ref: 'PrototypeR0:' + v['footprint'] for ref, v in candidates.items()}
    save_json(PROJECT/'footprint-assignments-r0.json', {'status':'Candidate fields only; main T-board', 'assignments':assignments})
    save_json(PROJECT/'layout-candidates-r0.json', {'date':'2026-10-30','status':'Assembly candidates, not the human-owned BOM or procurement authorization','parts':candidates})
    missing = sorted(set(candidates)-set(PLACEMENT))
    if missing:
        raise ValueError('Placement needed for new circuit refs: '+', '.join(missing))
    xml = ET.parse(PROJECT/'buttplug-r0.xml')
    components = {n.attrib['ref']:n for n in xml.findall('./components/comp')}
    root_uuid = re.search(r'\(uuid ([0-9a-f-]+)\)', (PROJECT/'buttplug-r0.kicad_sch').read_text())[1]
    board = k.BOARD()
    settings = board.GetDesignSettings()
    settings.SetBoardThickness(k.FromMM(1.0)); settings.SetCopperLayerCount(4)
    settings.m_MinClearance=k.FromMM(.1); settings.m_TrackMinWidth=k.FromMM(.15)
    settings.m_ViasMinSize=k.FromMM(.6); settings.m_MinThroughDrill=k.FromMM(.3)
    settings.m_CopperEdgeClearance=k.FromMM(.3)
    default = settings.m_NetSettings.m_DefaultNetClass
    default.SetClearance(k.FromMM(.1)); default.SetTrackWidth(k.FromMM(.2))
    default.SetViaDiameter(k.FromMM(.6)); default.SetViaDrill(k.FromMM(.3))
    nets = {n for p in parts for v in p['pins'].values() if (n:=v['net'])}
    netitems = {}
    for name in sorted(nets):
        n=k.NETINFO_ITEM(board,name);board.Add(n);netitems[name]=n
    outline=main_outline()
    for a,b in zip(outline,outline[1:]+outline[:1]):
        line=k.PCB_SHAPE();line.SetShape(k.SHAPE_T_SEGMENT);line.SetStart(xy(*a));line.SetEnd(xy(*b));line.SetLayer(k.Edge_Cuts);line.SetWidth(k.FromMM(.05));board.Add(line)
    for part in parts:
        ref=part['ref'];c=candidates[ref];x,y,angle,side=PLACEMENT[ref]
        fp=k.FootprintLoad(str(LIB),c['footprint']);assert fp,c['footprint']
        fp.SetReference(ref);fp.SetValue(c['mpn']);fp.SetFPID(k.LIB_ID('PrototypeR0',c['footprint']))
        board.Add(fp)  # KiCad 7 Flip needs the parent board for layer mapping.
        fp.SetPosition(xy(x,y));fp.SetOrientationDegrees(angle)
        if side=='B':fp.Flip(fp.GetPosition(),True)
        fp.Value().SetVisible(False)
        fp.Reference().SetVisible(False)
        fp.SetProperty('DesignStatus','CANDIDATE / REVIEW ONLY')
        fp.SetProperty('Manufacturer',c['manufacturer']);fp.SetProperty('MPN',c['mpn'])
        fp.SetProperty('CandidateHeight_mm',str(c['height_mm']))
        fp.SetProperty('AssemblyDomain','MAIN_T')
        if ref=='U7':fp.SetProperty('OpenLandPatternReview','Nominal contact-sized 0.30x0.20mm lands; device-specific stencil/process acceptance remains open')
        comp=components[ref];path=k.KIID_PATH()
        for uid in [root_uuid]+[v for v in comp.find('sheetpath').attrib['tstamps'].split('/') if v]+[comp.findtext('tstamps')]:path.push_back(k.KIID(uid))
        fp.SetPath(path)
        electrical={p.GetNumber() for p in fp.Pads() if p.GetNumber() not in ('','MP')}
        assert electrical==set(part['pins']),(ref,electrical,set(part['pins']))
        for pad in fp.Pads():
            entry=part['pins'].get(pad.GetNumber())
            if entry and entry['net']:pad.SetNet(netitems[entry['net']])
            if ref=='U6' and pad.GetNumber()=='49':
                pad.SetZoneConnection(k.ZONE_CONNECTION_FULL)
    # Board text is kept away from component courtyards and RF copper keepout.
    for value,x,y,layer,size in [('R0 CIRCUIT REVIEW / NOT FAB',0,-29,k.Dwgs_User,1),('TIP +Y',10,80,k.Dwgs_User,1),('POWER',-30,-9.8,k.F_SilkS,.8),('MODE',-20,-9.8,k.F_SilkS,.8)]:
        t=k.PCB_TEXT(board);t.SetText(value);t.SetPosition(xy(x,y));t.SetLayer(layer);t.SetTextSize(k.VECTOR2I(k.FromMM(size),k.FromMM(size)));t.SetTextThickness(k.FromMM(.1));board.Add(t)
    critical_routes(board)
    ground_planes(board,outline)
    board.BuildConnectivity();k.SaveBoard(str(BOARD),board)
    ensure_stackup()
    # Loading normalizes the just-created board before the native zone filler.
    board=k.LoadBoard(str(BOARD));board.BuildConnectivity()
    filler=k.ZONE_FILLER(board);filler.Fill(board.Zones());k.SaveBoard(str(BOARD),board)
    report(board,candidates,manifest_path)
    print(f'Saved true net-connected placement: {len(parts)} main footprints, {len(nets)} nets. Remote-tip and power flags excluded.')


def refresh_candidates():
    """Refresh metadata/pad nets without discarding review routing.

    A changed net on a routed pad is deliberately not repaired here. Native DRC
    must expose and resolve the stale branch before that board can be complete.
    """
    prepare_library()
    parts=[p for p in json.loads((PROJECT/'candidate-pin-manifest.json').read_text())['parts']
           if p['assembly_domain']=='MAIN_T' and not p['ref'].startswith('#')]
    candidates={p['ref']:selection(p) for p in parts}
    save_json(PROJECT/'footprint-assignments-r0.json', {'status':'Candidate fields only; main T-board',
              'assignments':{ref:'PrototypeR0:'+c['footprint'] for ref,c in candidates.items()}})
    save_json(PROJECT/'layout-candidates-r0.json', {'date':'2026-10-30','status':'Assembly candidates, not the human-owned BOM or procurement authorization','parts':candidates})
    board=k.LoadBoard(str(BOARD));fps={f.GetReference():f for f in board.GetFootprints()}
    assert set(fps)==set(candidates)
    changes=[]
    for part in parts:
        fp=fps[part['ref']];c=candidates[part['ref']]
        fp.SetValue(c['mpn']);fp.SetFPID(k.LIB_ID('PrototypeR0',c['footprint']))
        fp.SetProperty('Manufacturer',c['manufacturer']);fp.SetProperty('MPN',c['mpn'])
        for pad in fp.Pads():
            entry=part['pins'].get(pad.GetNumber())
            if entry and entry['net'] and pad.GetNetname()!=entry['net']:
                changes.append((part['ref'],pad.GetNumber(),pad.GetNetname(),entry['net']))
                pad.SetNet(board.FindNet(entry['net']))
    k.SaveBoard(str(BOARD),board);ensure_stackup()
    print('Refreshed candidate metadata; changed pad nets:',changes)


def import_route_session(path):
    """Import routed additions; KiCad 7's exposed SES importer is GUI-only.

    The accepted subset is explicit SES wire paths and through vias. Existing
    locked routes and all component placements stay intact. Native DRC checks
    the imported copper rather than trusting the router's score.
    """
    tokens=re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',path.read_text())
    stack=[];root=None
    for token in tokens:
        if token=='(':
            node=[]
            if stack:stack[-1].append(node)
            stack.append(node)
        elif token==')':
            node=stack.pop()
            if not stack:root=node
        else:stack[-1].append(json.loads(token) if token.startswith('"') else token)
    assert root and not stack and root[0]=='session'
    routes=next(n for n in root if isinstance(n,list) and n[0]=='routes')
    resolution=next(n for n in routes if isinstance(n,list) and n[0]=='resolution')
    assert resolution==['resolution','um','10'],resolution
    network=next(n for n in routes if isinstance(n,list) and n[0]=='network_out')
    board=k.LoadBoard(str(BOARD));added=0
    # SES replaces the router-owned copper; locked manual power routes survive.
    for track in list(board.GetTracks()):
        if not track.IsLocked():board.Delete(track)
    def point(x,y):return k.VECTOR2I(k.FromMM(float(x)/10000),k.FromMM(-float(y)/10000))
    for net in network[1:]:
        assert net[0]=='net';item=board.FindNet(net[1]);assert item,net[1]
        for feature in net[2:]:
            if feature[0]=='wire':
                route=feature[1];layers={'F.Cu':k.F_Cu,'In2.Cu':k.In2_Cu,'B.Cu':k.B_Cu}
                assert route[0]=='path' and route[1] in layers,route[:3]
                pts=[point(x,y) for x,y in zip(route[3::2],route[4::2])]
                for a,b in zip(pts,pts[1:]):
                    track=k.PCB_TRACK(board);track.SetStart(a);track.SetEnd(b);track.SetWidth(k.FromMM(float(route[2])/10000));track.SetLayer(layers[route[1]]);track.SetNet(item);board.Add(track);added+=1
            elif feature[0]=='via':
                dims=re.fullmatch(r'Via\[0-[13]\]_(\d+):(\d+)_um',feature[1]);assert dims,feature
                via=k.PCB_VIA(board);via.SetPosition(point(feature[2],feature[3]));via.SetWidth(k.FromMM(float(dims[1])/1000));via.SetDrill(k.FromMM(float(dims[2])/1000));via.SetViaType(k.VIATYPE_THROUGH);via.SetLayerPair(k.F_Cu,k.B_Cu);via.SetNet(item);board.Add(via);added+=1
            else:raise ValueError('Unsupported SES feature: '+str(feature))
    k.SaveBoard(str(BOARD),board)
    board=k.LoadBoard(str(BOARD));board.BuildConnectivity();filler=k.ZONE_FILLER(board);filler.Fill(board.Zones());k.SaveBoard(str(BOARD),board);report(board)
    print('Imported SES additions:',added)


def complete_routes(session_path):
    """Apply reviewed local repairs to the preserved automatic route session.

    This is a deterministic post-import step, not another autorouter. It moves
    two drilled escapes off passive pads, repairs the boundary path, and adds
    explicit local control/ground links. Only a fresh build/import may use it.
    """
    board = k.LoadBoard(str(BOARD))
    patch = json.loads((PROJECT/'route-refinements-r0.json').read_text())
    assert digest(session_path) == patch['session_sha256'], 'Route session differs from reviewed local additions'
    def point(p):
        return (round(k.ToMM(p.x)-100, 6), round(130-k.ToMM(p.y), 6))
    def close(p, q):
        return all(abs(a-b) < .00006 for a, b in zip(p, q))
    # The old MC3635 ground detour blocked its power/clock escapes. Replace it
    # with the off-pad ground stitches recorded in the local route source.
    remove = [((.5953,67.4453),(.1977,67.8428)),
              ((.1977,67.8428),(-.9845,67.8428)),
              ((-.9845,67.8428),(-1.9678,67.8428)),
              ((-1.9678,67.8428),(-2.4,68.275)),
              ((-.9845,67.8428),(-.9845,67.2386)),
              ((-.9845,67.2386),(-.7956,67.0497)),
              ((-.7956,67.0497),(-.5996,67.0497)),
              ((-.5996,67.0497),(-.5996,67.0496)),
              ((-.5996,67.0496),(-.55,67))]
    for t in list(board.GetTracks()):
        net = t.GetNetname(); a = point(t.GetStart()); b = point(t.GetEnd())
        isvia = isinstance(t, k.PCB_VIA)
        delete = net == 'MOTOR_PWM' and not t.IsLocked()
        if (not isvia and net == 'ACCEL_INT_N' and t.GetLayer() == k.In2_Cu
                and (a[1] > 63 or b[1] > 63)):
            delete = True  # Replace the old under-U7 leg with an external path.
        for n, p in [('3V3',(2.275,6.5)), ('GND',(4.4,14.95))]:
            if net == n and ((isvia and close(a,p)) or
                             (t.IsLocked() and (close(a,p) or close(b,p)))):
                delete = True
        if net == 'GND' and not isvia and any(
                (close(a,p) and close(b,q)) or (close(a,q) and close(b,p))
                for p,q in remove):
            delete = True
        if delete:
            board.Delete(t); continue
        if not isvia and t.GetWidth() < k.FromMM(.15):
            t.SetWidth(k.FromMM(.15))
        points = [(t.SetPosition,t.GetPosition())] if isvia else [
                  (t.SetStart,t.GetStart()), (t.SetEnd,t.GetEnd())]
        for setter, p in points:
            x,y = point(p)
            if close((x,y),(-17.1731,-25.4155)):
                setter(xy(x,-25.3755))  # Keep dock-present via inside edge rule.
            if (not isvia and net == 'TEMP_COLD_IN' and t.GetLayer() == k.F_Cu
                    and abs(x+9.7637) < .00005 and -21.12 <= y <= -17.30):
                setter(xy(-10.3137,y))
        if not isvia and net == 'TEMP_COLD_IN' and t.GetLayer() == k.F_Cu:
            t.SetWidth(k.FromMM(.15))
    for route in patch['routes']:
        if route['kind'] == 'via':
            t=k.PCB_VIA(board); t.SetPosition(xy(*route['position']))
            t.SetWidth(k.FromMM(.6)); t.SetDrill(k.FromMM(.3))
            t.SetViaType(k.VIATYPE_THROUGH); t.SetLayerPair(k.F_Cu,k.B_Cu)
        else:
            t=k.PCB_TRACK(board); t.SetStart(xy(*route['start']))
            t.SetEnd(xy(*route['end'])); t.SetWidth(k.FromMM(route['width']))
            t.SetLayer({'F.Cu':k.F_Cu,'In2.Cu':k.In2_Cu,'B.Cu':k.B_Cu}[route['layer']])
        t.SetNet(board.FindNet(route['net'])); t.SetLocked(True); board.Add(t)
    for zone in board.Zones():
        if zone.GetNetname() == 'GND':
            zone.SetIslandRemovalMode(k.ISLAND_REMOVAL_MODE_ALWAYS)
    k.SaveBoard(str(BOARD),board)
    board=k.LoadBoard(str(BOARD)); board.BuildConnectivity()
    filler=k.ZONE_FILLER(board); filler.Fill(board.Zones())
    k.SaveBoard(str(BOARD),board)
    print('Applied reviewed local route additions:',len(patch['routes']))


def report(board=None,candidates=None,manifest_path=None):
    board=board or k.LoadBoard(str(BOARD))
    candidates=candidates or json.loads((PROJECT/'layout-candidates-r0.json').read_text())['parts']
    manifest_path=manifest_path or PROJECT/'candidate-pin-manifest.json'
    boxes=[]
    for fp in board.GetFootprints():
        ref=fp.GetReference();shapes=[s for s in fp.GraphicalItems() if isinstance(s,k.PCB_SHAPE) and s.GetLayer() in (k.F_Fab,k.B_Fab)]
        bounds=[s.GetBoundingBox() for s in shapes]
        if not bounds:bounds=[fp.GetBoundingBox(False,False)]
        xmin=min(b.GetLeft() for b in bounds);xmax=max(b.GetRight() for b in bounds)
        ymin=min(b.GetTop() for b in bounds);ymax=max(b.GetBottom() for b in bounds)
        height=candidates[ref]['height_mm'];bottom=fp.GetLayer()==k.B_Cu
        boxes.append({'ref':ref,'mpn':candidates[ref]['mpn'],'side':'negative_Z/B.Cu' if bottom else 'positive_Z/F.Cu',
                      'xy_bounds_mm':[round(k.ToMM(xmin)-ORIGIN[0],4),round(ORIGIN[1]-k.ToMM(ymax),4),round(k.ToMM(xmax)-ORIGIN[0],4),round(ORIGIN[1]-k.ToMM(ymin),4)],
                      'z_bounds_mm':[-6.5-height,-6.5] if bottom else [-5.5,-5.5+height],
                      'scope':'Conservative body projection from F.Fab plus nominal/candidate height; excludes mating plugs, wires, solder and tolerances.'})
    save_json(PROJECT/'placement-report-r0.json',{'date':'2026-10-30','status':'Actual circuit placement development; not physical fit proof','mechanical_to_KiCad':{'x_offset':ORIGIN[0],'y_offset':ORIGIN[1],'invert_Y':True,'board_z_mm':[-6.5,-5.5]},'pcb_outline_vertices_xy_mm':main_outline(),'copper_layers':board.GetCopperLayerCount(),'manifest_sha256':digest(manifest_path),'board_sha256':digest(BOARD),'footprints':len(list(board.GetFootprints())),'nets':board.GetNetCount()-1,'tracks':len(list(board.GetTracks())),'component_boxes':boxes})


def audit(drc_path):
    """Record exact current-file connectivity and footprint-source evidence."""
    board=k.LoadBoard(str(BOARD));manifest=PROJECT/'candidate-pin-manifest.json'
    parts={p['ref']:p for p in json.loads(manifest.read_text())['parts']
           if p['assembly_domain']=='MAIN_T' and not p['ref'].startswith('#')}
    footprints={f.GetReference():f for f in board.GetFootprints()};mismatches=[];count=0
    for ref,part in parts.items():
        for pad in footprints[ref].Pads():
            entry=part['pins'].get(pad.GetNumber())
            if entry:
                count+=1
                if pad.GetNetname()!=(entry['net'] or ''):mismatches.append([ref,pad.GetNumber(),pad.GetNetname(),entry['net']])
    register_path=PROJECT/'layout-candidates-r0.json';register=json.loads(register_path.read_text());unique={}
    for candidate in register['parts'].values():
        name=candidate['footprint'];path=LIB/(name+'.kicad_mod')
        if name not in unique:
            fp=k.FootprintLoad(str(LIB),name)
            unique[name]={'sha256':digest(path),'native_load':bool(fp),'sources':[],
                          'pads':[{'number':p.GetNumber(),'size_mm':[k.ToMM(p.GetSize().x),k.ToMM(p.GetSize().y)],
                                   'position_mm':[k.ToMM(p.GetPosition().x),k.ToMM(p.GetPosition().y)]} for p in fp.Pads()]}
        for key in ('source','land_source'):
            if candidate.get(key) and candidate[key] not in unique[name]['sources']:unique[name]['sources'].append(candidate[key])
    register['footprints']=unique
    register['verification_scope']='Native load and explicit pad geometry/source hashes. Package/land comparison boundaries are documented; this is not independent assembler approval.'
    save_json(register_path,register)
    text=drc_path.read_text()
    counts={key:int(re.search(r'\*\* Found (\d+) '+pattern,text)[1]) for key,pattern in
            [('drc_violations','DRC violations'),('unconnected_items','unconnected pads'),('footprint_errors','Footprint errors')]}
    ground = next(z for z in board.Zones() if z.GetLayerSet().Contains(k.In1_Cu))
    usb = {}
    for net in ('USB_DM','USB_DP'):
        tracks = [t for t in board.GetTracks() if t.GetNetname() == net]
        samples = missing = 0
        for t in tracks:
            if isinstance(t,k.PCB_VIA): continue
            a,b = t.GetStart(),t.GetEnd(); dx=b.x-a.x; dy=b.y-a.y
            length=math.hypot(dx,dy); steps=max(1,math.ceil(k.ToMM(length)/.1))
            for i in range(steps+1):
                for offset in (-.1,0,.1):
                    p=k.VECTOR2I(round(a.x+dx*i/steps-dy/length*k.FromMM(offset)),
                                 round(a.y+dy*i/steps+dx/length*k.FromMM(offset)))
                    samples+=1
                    if not ground.HitTestFilledArea(k.In1_Cu,p): missing+=1
        usb[net]={'length_mm':round(sum(k.ToMM(t.GetLength()) for t in tracks if not isinstance(t,k.PCB_VIA)),6),
                  'vias':sum(isinstance(t,k.PCB_VIA) for t in tracks),
                  'widths_mm':sorted({k.ToMM(t.GetWidth()) for t in tracks if not isinstance(t,k.PCB_VIA)}),
                  'layers':sorted({k.LayerName(t.GetLayer()) for t in tracks if not isinstance(t,k.PCB_VIA)}),
                  'reference_samples':samples,'samples_without_In1_ground':missing}
    result={'date':'2026-10-30','board_sha256':digest(BOARD),'manifest_sha256':digest(manifest),
            'project_sha256':digest(PROJECT/'buttplug-r0.kicad_pro'),'drc_report_sha256':digest(drc_path),
            'counts':counts,'main_footprints':len(footprints),'main_pad_entries_checked':count,'pad_net_mismatches':mismatches,
            'board_only_refs':sorted(set(footprints)-set(parts)),'manifest_only_refs':sorted(set(parts)-set(footprints)),
            'copper_layers':board.GetCopperLayerCount(),
            'In1_signal_tracks':sum(not isinstance(t,k.PCB_VIA) and t.GetLayer()==k.In1_Cu for t in board.GetTracks()),
            'In1_ground_filled_outlines':ground.GetFilledPolysList(k.In1_Cu).OutlineCount(),
            'usb':usb,
            'limits':['Native geometric and connectivity checks are not current, thermal, RF, assembly or physical validation.',
                      'U7 manufacturer land/stencil acceptance remains open.']}
    save_json(PROJECT/'layout-validation-r0.json',result);print(json.dumps(result,indent=2))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--build',action='store_true');p.add_argument('--export-dsn',type=Path)
    p.add_argument('--import-ses',type=Path);p.add_argument('--drc',type=Path);p.add_argument('--report',action='store_true')
    p.add_argument('--refresh-candidates',action='store_true')
    p.add_argument('--complete-routes',action='store_true',help='Fresh-build only: apply reviewed local additions after matching SES import')
    p.add_argument('--audit',type=Path,help='Audit the saved board against the current manifest and this native DRC report')
    args=p.parse_args()
    if args.complete_routes and not (args.build and args.import_ses):
        p.error('--complete-routes requires --build and --import-ses in the same call')
    if args.build:build()
    if args.refresh_candidates:refresh_candidates()
    if args.export_dsn:
        board=k.LoadBoard(str(BOARD))
        # Export explicit ground connectivity. An ideal plane in DSN hides
        # the real islands that signal routes can create in a filled zone.
        for zone in list(board.Zones()):
            if not zone.GetIsRuleArea() and not zone.GetLayerSet().Contains(k.In1_Cu):board.Delete(zone)
        assert k.ExportSpecctraDSN(board,str(args.export_dsn))
        # Broad rail routing is distinct from signal escapes. Locked switch-node
        # necks remain as manually reviewed above; these class widths are still
        # engineering candidates, not validated current/thermal limits.
        dsn=args.export_dsn.read_text()
        railnets=['SYS','PACK_P','DOCK_5V','DOCK_FUSED','VBUS_CHG','MOTOR_3V7','MOTOR_P','MOTOR_N']
        begin=dsn.index('(class kicad_default');end=dsn.index('(circuit',begin)
        header=dsn[begin:end]
        for net in railnets+['3V3']:header=re.sub(r'(?<!\S)'+re.escape(net)+r'(?=\s)','',header)
        dsn=dsn[:begin]+header+dsn[end:]
        network_end=dsn.index('\n  (wiring')
        insert=dsn.rfind('\n  )',0,network_end)
        via_name='Via[0-3]_600:300_um'
        power='\n    (class PowerRails '+ ' '.join(railnets)+'\n      (circuit (use_via '+via_name+'))\n      (rule (width 600) (clearance 100.1))\n    )'
        power+='\n    (class DigitalSupply 3V3\n      (circuit (use_via '+via_name+'))\n      (rule (width 300) (clearance 100.1))\n    )'
        dsn=dsn[:insert]+power+dsn[insert:]
        args.export_dsn.write_text(dsn)
    if args.import_ses:
        import_route_session(args.import_ses)
    if args.complete_routes:complete_routes(args.import_ses)
    if args.drc:
        board=k.LoadBoard(str(BOARD));board.BuildConnectivity();assert k.WriteDRCReport(board,str(args.drc),k.EDA_UNITS_MILLIMETRES,True)
    if args.report:report()
    if args.audit:audit(args.audit)


if __name__=='__main__':main()
