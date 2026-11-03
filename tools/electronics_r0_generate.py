"""Generate the review-only native KiCad 7 R0 schematic and pin manifest.

The human-owned hardware/bom.csv is deliberately not read or written. These
files are a new candidate design, not a reconstruction of Lucy/Gaby's image.
"""
from pathlib import Path
import json
import math
import re
import uuid

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'hardware/pcb/prototype-r0'
NS = uuid.UUID('fb8fd0f0-ef48-49d3-b032-b2b387560f05')
PROJECT = 'buttplug-r0'
LIB = {}
PARTS = []


def uid(name):
    return str(uuid.uuid5(NS, name))


def q(s):
    return json.dumps(str(s), ensure_ascii=False)


def effects(size=1.27, extra=''):
    return f'(effects (font (size {size} {size})) {extra})'


def ic(name, left, right, source, description, hidden=()):
    """Pin tuples are (number, name, electrical_type); zero pins are not invented."""
    rows = max(len(left), len(right), 2)
    half = (rows + 1) * 2.54
    w = 15.24
    pins = []
    for group, x, angle in [(left, -w - 5.08, 0), (right, w + 5.08, 180)]:
        for index, (number, label, kind) in enumerate(group):
            pins.append(dict(number=str(number), name=label, kind=kind,
                             x=x, y=(rows - 1) * 2.54 - index * 5.08,
                             angle=angle, hide=False))
    # Hidden stacked ground/power pins follow normal KiCad library convention.
    for number, label, kind, stacked_number in hidden:
        pin = next(p for p in pins if p['number'] == str(stacked_number)).copy()
        pin.update(number=str(number), name=label, kind=kind, hide=True)
        pins.append(pin)
    body = f'''(symbol {q(name)} (pin_names (offset 0.762)) (in_bom yes) (on_board yes)
      (property "Reference" "U" (at 0 {half + 5.08} 0) {effects()})
      (property "Value" {q(name)} (at 0 {half + 2.54} 0) {effects()})
      (property "Footprint" "" (at 0 0 0) {effects(extra='hide')})
      (property "Datasheet" {q(source)} (at 0 0 0) {effects(extra='hide')})
      (property "ki_description" {q(description)} (at 0 0 0) {effects(extra='hide')})
      (symbol {q(name + '_0_1')}
        (rectangle (start {-w} {half}) (end {w} {-half})
          (stroke (width 0.254) (type default)) (fill (type background))))
      (symbol {q(name + '_1_1')}
    '''
    for p in pins:
        body += f'''(pin {p['kind']} line (at {p['x']} {p['y']} {p['angle']})
          (length 5.08) {'hide' if p['hide'] else ''}
          (name {q(p['name'])} {effects(1.016)})
          (number {q(p['number'])} {effects(1.016)}))\n'''
    body += '))'
    LIB[name] = dict(text=body, pins=pins, source=source, half=half)


def passive(name, kind='R'):
    if kind in ('R', 'F'):
        draw = '(rectangle (start -1.27 3.81) (end 1.27 -3.81) (stroke (width 0.254) (type default)) (fill (type none)))'
    elif kind == 'C':
        draw = '\n'.join(f'(polyline (pts (xy -2.54 {y}) (xy 2.54 {y})) (stroke (width 0.3) (type default)) (fill (type none)))' for y in (0.762, -0.762))
        draw += '\n' + '\n'.join(f'(polyline (pts (xy 0 {a}) (xy 0 {b})) (stroke (width 0.254) (type default)) (fill (type none)))' for a, b in ((3.81, 0.762), (-0.762, -3.81)))
    elif kind == 'L':
        draw = '(polyline (pts (xy 0 3.81) (xy -1.27 2.54) (xy 1.27 1.27) (xy -1.27 0) (xy 1.27 -1.27) (xy -1.27 -2.54) (xy 0 -3.81)) (stroke (width 0.3) (type default)) (fill (type none)))'
    elif kind == 'D':
        draw = '(polyline (pts (xy -2.54 2.54) (xy 2.54 2.54) (xy 0 -2.54) (xy -2.54 2.54)) (stroke (width 0.254) (type default)) (fill (type none))) (polyline (pts (xy -2.54 -2.54) (xy 2.54 -2.54)) (stroke (width 0.3) (type default)) (fill (type none)))'
        draw += '(polyline (pts (xy 0 3.81) (xy 0 2.54)) (stroke (width 0.254) (type default)) (fill (type none))) (polyline (pts (xy 0 -2.54) (xy 0 -3.81)) (stroke (width 0.254) (type default)) (fill (type none)))'
    else:
        draw = '(polyline (pts (xy 0 3.81) (xy 1.27 -2.54)) (stroke (width 0.254) (type default)) (fill (type none))) (circle (center 0 -3.81) (radius 0.4) (stroke (width 0.254) (type default)) (fill (type none)))'
    text = f'''(symbol {q(name)} (pin_names hide) (in_bom yes) (on_board yes)
      (property "Reference" {q(kind)} (at 3.81 1.27 0) {effects()})
      (property "Value" {q(name)} (at 3.81 -1.27 0) {effects()})
      (property "Footprint" "" (at 0 0 0) {effects(extra='hide')})
      (property "Datasheet" "" (at 0 0 0) {effects(extra='hide')})
      (symbol {q(name + '_0_1')} {draw})
      (symbol {q(name + '_1_1')}
        (pin passive line (at 0 5.08 270) (length 1.27) (name "1" {effects()}) (number "1" {effects(1.016)}))
        (pin passive line (at 0 -5.08 90) (length 1.27) (name "2" {effects()}) (number "2" {effects(1.016)}))))'''
    LIB[name] = dict(text=text, source='', half=5.08,
                     pins=[dict(number='1', name='1', kind='passive', x=0, y=5.08, angle=270, hide=False),
                           dict(number='2', name='2', kind='passive', x=0, y=-5.08, angle=90, hide=False)])


def connector(name, count):
    ic(name, [(i, str(i), 'passive') for i in range(1, count + 1)], [], '',
       'Logical connector pin numbering; physical connector and footprint not selected')


class Sheet:
    def __init__(self, name, title):
        self.name = name
        self.title = title
        self.id = uid(name)
        self.content = []
        self.used = set()
        self.paper = 'A3'
        self.sheet_path = '/' + uid(PROJECT) + '/' + uid('sheet-' + name)

    def note(self, text, x, y, size=1.524):
        self.content.append(f'(text {q(text)} (at {x} {y} 0) {effects(size, "(justify left top)")} (uuid {uid(self.name + text)}))')

    def label(self, name, x, y, angle=0):
        align = 'right' if angle == 180 else 'left'
        self.content.append(f'(global_label {q(name)} (shape input) (at {x} {y} {angle}) {effects(1.016, "(justify " + align + ")")} (uuid {uid(self.name + name + str((x,y)))}))')

    def part(self, lib, ref, value, x, y, nets, footprint='', note='', domain=None):
        spec = LIB[lib]
        self.used.add(lib)
        part_id = uid(ref)
        prefix = ref.rstrip('0123456789')
        digits = ''.join(ch for ch in ref if ch.isdigit())
        domain = domain or ('REMOTE_TIP' if digits and int(digits) >= 101 else 'MAIN_T')
        assignments_path = OUT / 'footprint-assignments-r0.json'
        if assignments_path.exists() and domain == 'MAIN_T':
            footprint = json.loads(assignments_path.read_text())['assignments'].get(ref, footprint)
        if ref == 'J2':
            footprint = 'PrototypeR0:JST_PH_S4B-PH-SM4-TB_1x04-1MP_P2.00mm_Horizontal'
        if lib == 'PWR_FLAG':
            domain = 'ANNOTATION'
        r_y = y - spec['half'] - 5.08
        v_y = r_y + 2.54
        if lib in ('R', 'C', 'L', 'F', 'D', 'SW', 'NTC'):
            r_x, r_y, v_y = x + 8.89, y - 1.27, y + 1.27
        else:
            r_x = x
        property_alignment = '(justify left)' if lib in ('R', 'C', 'L', 'F', 'D', 'SW', 'NTC') else ''
        item = f'''(symbol (lib_id {q('PrototypeR0:' + lib)}) (at {x} {y} 0) (unit 1)
          (in_bom {'no' if lib == 'PWR_FLAG' else 'yes'}) (on_board {'no' if domain != 'MAIN_T' else 'yes'}) (dnp no) (uuid {part_id})
          (property "Reference" {q(ref)} (at {r_x} {r_y} 0) {effects(1.27,property_alignment)})
          (property "Value" {q(value)} (at {r_x} {v_y} 0) {effects(1.016,property_alignment)})
          (property "Footprint" {q(footprint)} (at {x} {y} 0) {effects(extra='hide')})
          (property "Datasheet" {q(spec['source'])} (at {x} {y} 0) {effects(extra='hide')})
          (property "DesignStatus" "CANDIDATE — NOT RELEASED" (at {x} {y} 0) {effects(extra='hide')})
          (property "AssemblyDomain" {q(domain)} (at {x} {y} 0) {effects(extra='hide')})
          (property "ReviewNote" {q(note)} (at {x} {y} 0) {effects(extra='hide')})
        '''
        for p in spec['pins']:
            item += f'(pin {q(p["number"])} (uuid {uid(ref + "." + p["number"])}))\n'
        item += f'''(instances (project {q(PROJECT)}
          (path {q(self.sheet_path)} (reference {q(ref)}) (unit 1)))))'''
        self.content.append(item)
        manifest = dict(ref=ref, value=value, symbol=lib, sheet=self.name,
                        source=spec['source'], footprint=footprint, assembly_domain=domain,
                        on_main_board=domain == 'MAIN_T', note=note, pins={})
        attached = set()
        for p in spec['pins']:
            net = nets.get(p['number'])
            manifest['pins'][p['number']] = dict(name=p['name'], net=net)
            if p['hide']:
                continue
            px, py = round(x + p['x'], 4), round(y - p['y'], 4)
            if net is None:
                if p['kind'] != 'no_connect':
                    self.content.append(f'(no_connect (at {px} {py}) (uuid {uid(ref + ".nc." + p["number"])}))')
                continue
            if (px, py) in attached:
                continue
            attached.add((px, py))
            theta = math.radians(p['angle'])
            # Pin angle points inward; wire extends in the opposite direction.
            ex = round(px - 5.08 * math.cos(theta), 4)
            ey = round(py + 5.08 * math.sin(theta), 4)
            self.content.append(f'(wire (pts (xy {px} {py}) (xy {ex} {ey})) (stroke (width 0) (type default)) (uuid {uid(ref + ".wire." + p["number"])}))')
            self.label(net, ex, ey, 180 if p['angle'] == 0 else 0)
        PARTS.append(manifest)

    def save(self):
        libraries = []
        for name in sorted(self.used):
            libraries.append(LIB[name]['text'].replace('(symbol ' + q(name), '(symbol ' + q('PrototypeR0:' + name), 1))
        text = f'''(kicad_sch (version 20230121) (generator electronics_r0_generate)
          (uuid {self.id}) (paper {q(self.paper)})
          (title_block (title {q(self.title)}) (date "2026-10-30") (rev "R0 candidate")
            (company "Research and Desire") (comment 1 "BENCH DEVELOPMENT — NOT FABRICATION OR WEAR RELEASE"))
          (lib_symbols {''.join(libraries)})
          {''.join(self.content)}
          (sheet_instances (path "/" (page "1"))))\n'''
        (OUT / f'{self.name}.kicad_sch').write_text(text)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for kind in ('R', 'C', 'L', 'F', 'D', 'SW'):
        passive(kind, kind)
    passive('NTC', 'R')
    LIB['NTC']['source'] = 'https://www.vishay.com/docs/29078/ntcle413.pdf'
    LIB['NTC']['text'] = LIB['NTC']['text'].replace('(property "Datasheet" ""', '(property "Datasheet" "https://www.vishay.com/docs/29078/ntcle413.pdf"')
    LIB['PWR_FLAG'] = dict(half=1.27, source='', pins=[dict(number='1',name='pwr',kind='power_out',x=0,y=0,angle=90,hide=False)],
        text=f'''(symbol "PWR_FLAG" (power) (pin_names hide) (in_bom no) (on_board no)
          (property "Reference" "#FLG" (at 0 5.08 0) {effects(extra='hide')})
          (property "Value" "PWR_FLAG" (at 0 3.81 0) {effects()})
          (property "Footprint" "" (at 0 0 0) {effects(extra='hide')})
          (property "Datasheet" "" (at 0 0 0) {effects(extra='hide')})
          (symbol "PWR_FLAG_0_1" (polyline (pts (xy 0 0) (xy 0 1.27) (xy -1.27 1.905) (xy 0 2.54) (xy 1.27 1.905) (xy 0 1.27))
            (stroke (width 0.254) (type default)) (fill (type none))))
          (symbol "PWR_FLAG_1_1" (pin power_out line (at 0 0 90) (length 0)
            (name "pwr" {effects()}) (number "1" {effects()}))))''')
    for count in (2, 3, 4, 6):
        connector('Conn' + str(count), count)
    ic('BQ24074RGT',
       [(13, 'IN', 'power_in'), (6, 'EN1', 'input'), (5, 'EN2', 'input'), (4, '~{CE}', 'input'),
        (12, 'ILIM', 'input'), (16, 'ISET', 'passive'), (15, 'ITERM', 'input'), (14, 'TMR', 'input')],
       [(10, 'OUT', 'power_out'), (2, 'BAT', 'power_out'), (1, 'TS', 'input'), (7, '~{PGOOD}', 'open_collector'),
        (9, '~{CHG}', 'open_collector'), (8, 'VSS', 'power_in')],
       'https://www.ti.com/lit/ds/symlink/bq24074.pdf', '1S 4.2V charger with power path; not a substitute for pack protection',
       [(11, 'OUT', 'passive', 10), (3, 'BAT', 'passive', 2), (17, 'EP', 'passive', 8)])
    ic('TPS63070RNM',
       [(12, 'VIN', 'power_in'), (14, 'EN', 'input'), (1, 'PS_SYNC', 'input'), (15, 'VSEL', 'input'),
        (11, 'L1', 'passive'), (9, 'L2', 'passive')],
       [(7, 'VOUT', 'power_out'), (5, 'FB', 'input'), (6, 'FB2', 'open_collector'), (3, 'VAUX', 'passive'),
        (2, 'PG', 'open_collector'), (4, 'GND', 'power_in'), (10, 'PGND', 'power_in')],
       'https://www.ti.com/lit/ds/symlink/tps63070.pdf', 'Adjustable buck boost; 3.6A switch is not guaranteed motor current',
       [(13, 'VIN', 'passive', 12), (8, 'VOUT', 'passive', 7)])
    ic('DRV8212DSG', [(1, 'VM', 'power_in'), (8, 'VCC', 'power_in'), (6, 'IN1_PH', 'input'),
                     (5, 'IN2_EN', 'input'), (7, 'MODE', 'input')],
       [(2, 'OUT1', 'output'), (3, 'OUT2', 'output'), (4, 'GND', 'power_in')],
       'https://www.ti.com/lit/ds/symlink/drv8212.pdf', 'DSG package; PWM mode MODE=0; both inputs0 coast/autosleep',
       [(9, 'EP', 'passive', 4)])
    ic('SN74LVC1G11DBV', [(1, 'A', 'input'), (3, 'B', 'input'), (6, 'C', 'input')],
       [(4, 'Y', 'output'), (5, 'VCC', 'power_in'), (2, 'GND', 'power_in')],
       'https://www.ti.com/lit/ds/symlink/sn74lvc1g11.pdf', 'Hardware motor PWM AND arm AND valid-input-absent')
    gpio = [(12, 'GPIO0_ADC', 'bidirectional'), (13, 'GPIO1', 'bidirectional'), (6, 'GPIO3', 'bidirectional'),
            (18, 'GPIO4', 'bidirectional'), (19, 'GPIO5', 'bidirectional'), (20, 'GPIO6', 'bidirectional'),
            (21, 'GPIO7', 'bidirectional'), (16, 'GPIO10', 'bidirectional'), (30, 'GPIO20_RXD', 'bidirectional')]
    other = [(3, '3V3', 'power_in'), (8, 'EN', 'input'), (5, 'GPIO2_STRAP', 'bidirectional'),
             (22, 'GPIO8_STRAP', 'bidirectional'), (23, 'GPIO9_BOOT', 'bidirectional'),
             (26, 'GPIO18_USB_D-', 'bidirectional'), (27, 'GPIO19_USB_D+', 'bidirectional'),
             (31, 'GPIO21_TXD', 'bidirectional'), (1, 'GND', 'power_in')]
    grounds = [2, 11, 14] + list(range(36, 54))
    nc = [4, 7, 9, 10, 15, 17, 24, 25, 28, 29, 32, 33, 34, 35]
    # All module pads are represented. NC pads are separate hidden pins and unconnected.
    ic('ESP32_C3_MINI_1_N4X', gpio, other,
       'https://documentation.espressif.com/esp32-c3-mini-1_datasheet_en.html',
       '53-pad module; antenna lives in outward polymer flange; exact land pattern review required',
       [(n, 'GND', 'passive', 1) for n in grounds])
    spec = LIB['ESP32_C3_MINI_1_N4X']
    for index, n in enumerate(nc):
        nc_y = (index + 1) * 1.27
        p = dict(number=str(n), name='NC', kind='no_connect', x=0, y=nc_y, angle=0, hide=True)
        spec['pins'].append(p)
        pin = f'(pin no_connect line (at 0 {nc_y} 0) (length 0) hide (name "NC" {effects()}) (number "{n}" {effects()}))'
        spec['text'] = spec['text'][:-2] + pin + '))'
    ic('MC3635', [(1, 'DOUT_A1', 'input'), (2, 'DIN_SDA', 'bidirectional'), (10, 'SCK_SCL', 'input'),
                  (9, 'CSN', 'input'), (4, 'VPP', 'power_in')],
       [(6, 'VDDIO', 'power_in'), (7, 'VDD', 'power_in'), (5, 'INTN', 'open_collector'),
        (8, 'GND', 'power_in'), (3, 'NC', 'no_connect')],
       'https://www.memsic.com/Public/Uploads/uploadfile/files/20220119/MC3635Datasheet.pdf',
       'I2C address0x4C; VPP grounded; CSN high; configure active-low open-drain INTN')
    ic('TMP117AIDRVR', [(1, 'SCL', 'input'), (6, 'SDA', 'bidirectional'), (4, 'ADD0', 'input')],
       [(5, 'V+', 'power_in'), (2, 'GND', 'power_in'), (3, 'ALERT', 'open_collector')],
       'https://www.ti.com/lit/ds/symlink/tmp117.pdf',
       'TMP117 WSON6; address0x48 ADD0=GND. Mechanical thermal pad is unsoldered, no copper/paste; not an electrical seventh pin')
    ic('TPS3700DDCR', [(3, 'INA+', 'input'), (4, 'INB-', 'input')],
       [(1, 'OUTA', 'open_collector'), (6, 'OUTB', 'open_collector'), (5, 'VDD', 'power_in'), (2, 'GND', 'power_in')],
       'https://www.ti.com/lit/ds/symlink/tps3700.pdf',
       'Independent NTC window: OUTA low on hot/undervoltage; OUTB low on cold/overvoltage')
    ic('TPS3808G33DBVR', [(5, 'SENSE', 'input'), (3, '~{MR}', 'input'), (4, 'CT', 'passive')],
       [(1, '~{RESET}', 'open_collector'), (6, 'VDD', 'power_in'), (2, 'GND', 'power_in')],
       'https://www.ti.com/lit/ds/symlink/tps3808.pdf',
       'Dock-powered 3V3 monitor; G33 3.07V threshold +/-1.5%; CT open gives12..28ms reset delay')
    ic('AO3400A', [(1, 'G', 'input')], [(3, 'D', 'passive'), (2, 'S', 'passive')],
       'https://www.aosmd.com/sites/default/files/res/datasheets/AO3400A.pdf',
       'Charge-enable sink, not a power-path switch. SOT23 gate1 source2 drain3; candidate requires board-temperature off-state qualification')

    p = Sheet('01-power', 'R0 / charging and regulated rails')
    p.paper = 'A2'
    p.note('CANDIDATE POWER DESIGN / protected 1S pack required / charging disabled by default', 15.24, 15.24, 2.032)
    p.part('Conn2', 'J1', 'MAGNETIC_DOCK_5V', 55.88, 50.8, {'1':'DOCK_5V', '2':'GND'}, note='Logical contacts only; polarity, mechanical dock and exposed-contact fault review open')
    p.part('F', 'F1', 'PTC 500mA candidate', 81.28, 38.1, {'1':'DOCK_5V', '2':'DOCK_FUSED'}, note='PTC is not a precise current limiter; bench supply must be current limited')
    p.part('D', 'D1', 'Schottky 1A/20V candidate', 119.38, 38.1, {'1':'DOCK_FUSED', '2':'VBUS_CHG'}, note='Generic symbol pin1 anode, pin2 cathode; select manufacturer part and map its package pads before PCB transfer')
    p.part('C', 'C1', '4.7uF 10V X7R', 157.48, 38.1, {'1':'VBUS_CHG', '2':'GND'})
    p.part('PWR_FLAG', '#FLG01', 'EXTERNAL_DC_INPUT', 355.6, 38.1, {'1':'VBUS_CHG'}, note='External current-limited dock source after passive input path')
    p.part('PWR_FLAG', '#FLG02', 'EXTERNAL_0V_RETURN', 393.7, 38.1, {'1':'GND'}, note='External supply/pack0V reference; no chassis/metal-shell bond selected')
    p.part('BQ24074RGT', 'U1', 'BQ24074RGT candidate', 121.92, 101.6,
           {'13':'VBUS_CHG', '6':'VBUS_CHG', '5':'GND', '4':'CHARGE_CE_N', '12':'CHG_ILIM', '16':'CHG_ISET',
            '15':None, '14':None, '10':'SYS', '11':'SYS', '2':'PACK_P', '3':'PACK_P', '1':'PACK_NTC',
            '7':'DOCK_PRESENT_N', '9':'CHARGE_STATUS_N', '8':'GND', '17':'GND'},
           footprint='PrototypeR0:TI_RGT0016C_3x3mm_BQ24074_EP1.68mm',
           note='EN1=1 EN2=0 USB500 input limit; TMR/ITERM intentionally open for factory defaults; CE high disables charge')
    p.part('Conn4', 'J2', 'PROTECTED_PACK_DUAL_NTC', 228.6, 76.2, {'1':'PACK_P', '2':'GND', '3':'PACK_NTC', '4':'PACK_GUARD'},
           note='Protected pack output plus two separate real cell-coupled NTCs; two-wire OEM pack needs adapter. Pin3 native TS, pin4 independent hardware guard. Not bare-cell pads')
    p.part('R', 'R1', '8.87k 1% / ~100mA', 40.64, 114.3, {'1':'CHG_ISET', '2':'GND'})
    p.part('R', 'R2', '3.24k 1%', 40.64, 147.32, {'1':'CHG_ILIM', '2':'GND'}, note='ILIM resistor required; fixed USB500 mode selected by EN pins')
    p.part('R', 'R3', '10k', 228.6, 114.3, {'1':'VBUS_CHG', '2':'CHARGE_CE_N'})
    for ref, x, net, val in [('C2',279.4,'PACK_P','4.7uF 10V'), ('C3',317.5,'SYS','10uF 10V')]:
        p.part('C',ref,val,x,88.9,{'1':net,'2':'GND'})
    p.part('R','R4','10k',279.4,139.7,{'1':'3V3','2':'DOCK_PRESENT_N'})
    p.part('R','R5','10k',317.5,139.7,{'1':'3V3','2':'CHARGE_STATUS_N'})
    p.note('PGOOD is low only for a VALID powered input, not physical dock presence.\nCHG is a status signal; it does not independently qualify the pack for charging.\nInput TVS/ESD, true dock detection and pack/protection limits remain review items.\nNo fixed resistor substitutes for the battery NTC.',15.24,175.26)

    def regulator(sheet, ref, x, y, out, enable, top, bottom, group):
        sheet.part('TPS63070RNM',ref,'TPS63070RNM candidate',x,y,
                   {'12':'SYS','13':'SYS','14':enable,'1':group+'_PS','15':'GND','11':group+'_L1','9':group+'_L2',
                    '7':out,'8':out,'5':group+'_FB','6':None,'3':group+'_AUX','2':None,'4':'GND','10':'GND'},
                   footprint='PrototypeR0:TI_RNM0015A_2.5x3mm_TPS63070',
                   note='PS/SYNC high enables PFM; FB2 open, VSEL low. RNM15 candidate land pattern reviewed; common7/8 and12/13 copper pairs share nets; layout not released')
        sheet.part('L','L'+group[-1],'1.5uH / Isat>=4A candidate',x-66.04,y-20.32,{'1':group+'_L1','2':group+'_L2'},note='Select vendor part and validate saturation, DCR and converter transient response')
        n=int(group[-1])*10
        sheet.part('C','C'+str(n+1),'10uF 10V',x-66.04,y+20.32,{'1':'SYS','2':'GND'},note='Paired input capacitors give2x10uF nominal total')
        sheet.part('C','C'+str(n+2),'10uF 10V',x-27.94,y+60.96,{'1':'SYS','2':'GND'})
        for j in range(3):
            sheet.part('C','C'+str(n+3+j),'22uF 10V X7R',x+50.8+j*35.56,y+20.32,{'1':out,'2':'GND'},note='66uF nominal total; effective DC-biased output capacitance must meet TI requirements')
        sheet.part('C','C'+str(n+6),'100nF 10V',x+50.8,y-27.94,{'1':group+'_AUX','2':'GND'})
        sheet.part('R','R'+str(n+1),top,x+88.9,y-27.94,{'1':out,'2':group+'_FB'})
        sheet.part('R','R'+str(n+2),bottom,x+124.46,y-27.94,{'1':group+'_FB','2':'GND'})
        sheet.part('R','R13' if group == 'REG1' else 'R26','10k',355.6,y,{'1':'SYS','2':group+'_PS'},note='10k supply tie per TPS63070 §11; U2 EN shares REG1_PS after R13. U3 EN is GPIO-driven separately. High permits power save')
        hf_start = 51 if group == 'REG1' else 53
        for cap_ref, cx, cap_net in [(hf_start,335.28,'SYS'),(hf_start+1,370.84,out)]:
            sheet.part('C','C'+str(cap_ref),'10uF 10V X5R 0603 HF',cx,y+39.37,
                       {'1':cap_net,'2':'GND'},footprint='PrototypeR0:TDK_C1608_0603_Reflow',
                       note='TDK C1608X5R1A106K080AC production candidate; 10uF10VX5R10%. Separate small-case HF bypass per TI§11; place directly VIN/PGND or VOUT/PGND. DC bias/effective C and mounted loop need review.')

    p.note('3.3V LOGIC RAIL / two regulator channels share one part family for R0; not a minimum-size design',15.24,208.28)
    regulator(p,'U2',121.92,251.46,'3V3','REG1_PS','312k 0.1%','100k 0.1%','REG1')
    p.save()

    g = Sheet('05-charge-guard', 'R0 / independent pack-temperature charge permission')
    g.note('INDEPENDENT PACK CHARGE GUARD / JP1 OPEN UNTIL BENCH ACCEPTANCE',15.24,15.24,2.032)
    g.part('TPS3700DDCR','U8','TPS3700DDCR',106.68,78.74,
           {'3':'TEMP_HOT_IN','4':'TEMP_COLD_IN','1':'CHARGE_TEMP_OK','6':'CHARGE_TEMP_OK','5':'3V3','2':'GND'},
           footprint='Package_TO_SOT_SMD:SOT-23-6', note='DDC thin-SOT23-6 package; compare exact land drawing before release. Both fault outputs wired AND with supervisor RESET')
    g.part('TPS3808G33DBVR','U9','TPS3808G33DBVR',292.1,78.74,
           {'5':'3V3','3':'VBUS_CHG','4':None,'1':'CHARGE_TEMP_OK','6':'VBUS_CHG','2':'GND'},
           footprint='Package_TO_SOT_SMD:SOT-23-6', note='VDD from dock, not monitored rail. MR high. CT deliberately open: minimum12ms exceeds TPS3700 maximum450us startup. Overvoltage above3.6V is not covered')
    for ref,x,y,value,nets,note in [
        ('R42',40.64,134.62,'10.0k 0.1%',{'1':'3V3','2':'PACK_GUARD'},'TNPW060310K0BEEA; independent NTC bias'),
        ('R43',106.68,134.62,'715k 0.1%',{'1':'PACK_GUARD','2':'TEMP_HOT_IN'},'TNPW0805715KBEEA;0805 because0603 family max332k'),
        ('R44',172.72,134.62,'110k 0.1%',{'1':'TEMP_HOT_IN','2':'TEMP_COLD_IN'},'TNPW0603110KBEEA'),
        ('R45',238.76,134.62,'200k 0.1%',{'1':'TEMP_COLD_IN','2':'GND'},'TNPW0603200KBEEA'),
        ('R46',304.8,134.62,'11k 1%',{'1':'VBUS_CHG','2':'CHARGE_TEMP_OK'},'Dock pullup avoids undocked3V3 drain. Minimum10.89k respects TPS3808>=10k guidance; outputs independently sink permission'),
        ('R47',172.72,208.28,'1k 1%',{'1':'CHARGE_PERMIT','2':'CHARGE_GATE'},'Gate series resistor'),
        ('R48',238.76,208.28,'100k 1%',{'1':'CHARGE_GATE','2':'GND'},'External gate pulldown defaults charge disabled when JP1 open')]:
        g.part('R',ref,value,x,y,nets,note=note)
    g.part('Conn2','JP1','CHARGE_PERMISSION / OPEN',55.88,208.28,{'1':'CHARGE_TEMP_OK','2':'CHARGE_PERMIT'},
           note='Series permission only. Closing cannot bypass temperature/supply guard; leave open until documented bench acceptance')
    g.part('AO3400A','Q1','AO3400A',327.66,208.28,{'1':'CHARGE_GATE','2':'GND','3':'CHARGE_CE_N'},
           footprint='Package_TO_SOT_SMD:SOT-23', note='At25C RDSon<=48mOhm atVGS2.5V. Fault VGS<=0.4V below25C minimumthreshold0.65V; all-temperature residual current requires bench qualification, not inferred from threshold typical plot')
    for ref,x,net in [('C43',40.64,'3V3'),('C44',106.68,'VBUS_CHG')]:
        g.part('C',ref,'100nF',x,259.08,{'1':net,'2':'GND'})
    g.note('NTC full published resistance bounds, comparator leakage,3.0..3.6V rail and resistor +/-0.5% budget:\nAt0C INB minimum0.41335V > maximum cold trip0.404V.\nAt45C INA maximum0.37282V < minimum hot trip0.387V.\nThis bounds SENSOR temperature only. Cell bond gradients/lag and MOSFET off-state need bench acceptance.\nOpen thermistor => cold fault; short => hot fault. MCU has no charge-enable bypass.',15.24,292.1)
    g.paper='A2'
    g.part('NTC','TH1','NTCLE413E2103F524A',40.64,350.52,{'1':'PACK_NTC','2':'GND'},
           domain='EXTERNAL_PACK',note='External dry sealed-cavity cell-mounted10k1% sensor. Native BQ TS backup, not sole0..45C guard; no immersion/hardpotting/overmolding per Vishay')
    g.part('NTC','TH2','NTCLE413E2103F524A',238.76,350.52,{'1':'PACK_GUARD','2':'GND'},
           domain='EXTERNAL_PACK',note='Second independent cell-mounted sensor; published full Rmin/Rmax curve used. Same mechanical restrictions and physical bond review as TH1')
    g.save()

    m=Sheet('02-motor','R0 / regulated motor drive and dock inhibit')
    m.note('CANDIDATE MOTOR CHANNEL / current-limited bench characterization before motor or pack approval',15.24,15.24,2.032)
    regulator(m,'U3',121.92,76.2,'MOTOR_3V7','MOTOR_ARM','362k 0.1%','100k 0.1%','REG2')
    m.note('Nominal Vmotor=0.8*(1+362k/100k)=3.696V.\nRegulator accuracy and motor tolerance need review. Startup/stall are unknown.\nNo claim of a2A motor capability is made from the converter headline rating.',15.24,152.4)
    m.part('SN74LVC1G11DBV','U4','SN74LVC1G11DBV candidate',76.2,200.66,
           {'1':'MOTOR_PWM','3':'MOTOR_ARM','6':'DOCK_PRESENT_N','4':'MOTOR_IN1','5':'3V3','2':'GND'},
           footprint='Package_TO_SOT_SMD:SOT-23-6')
    m.part('DRV8212DSG','U5','DRV8212DSG candidate',228.6,203.2,
           {'1':'MOTOR_3V7','8':'3V3','6':'MOTOR_IN1','5':'GND','7':'GND','2':'MOTOR_P','3':'MOTOR_N','4':'GND','9':'GND'},
           footprint='PrototypeR0:WSON-8-1EP_2x2mm_P0.5mm_EP0.9x1.6mm',
           note='PWM mode, IN2 low. IN1 low=>coast/HiZ/autosleep; high=>forward. No fault/status output or adjustable motor-current limit')
    m.part('Conn2','J3','MOTOR_2PIN',342.9,195.58,{'1':'MOTOR_P','2':'MOTOR_N'},note='Motor part/polarity, connector, wire gauge and startup/stall behavior unconfirmed')
    for ref,x,net,val in [('C27',40.64,'3V3','100nF'),('C28',177.8,'MOTOR_3V7','100nF'),('C29',215.9,'3V3','100nF'),('C30',254,'MOTOR_3V7','47uF 10V')]:
        m.part('C',ref,val,x,259.08,{'1':net,'2':'GND'})
    m.part('R','R23','100k',76.2,259.08,{'1':'MOTOR_ARM','2':'GND'})
    m.part('R','R24','100k',114.3,259.08,{'1':'MOTOR_PWM','2':'GND'})
    m.part('R','R25','100k',152.4,259.08,{'1':'MOTOR_IN1','2':'GND'})
    m.note('Hardware: PWM AND ARM AND DOCK_PRESENT_N. Reset pulldowns force off; valid dock power forces coast.\nA physically attached but unpowered/invalid dock is not detected by PGOOD.\nNo independent thermal cutoff, current telemetry or stalled-motor qualification is provided by this sheet.',15.24,233.68)
    m.save()

    c=Sheet('03-control','R0 / module, buttons, boot and debug')
    c.note('CANDIDATE MCU PIN MAP / WiFi+BLE via integrated antenna in outward whole-polymer flange',15.24,15.24,2.032)
    nets={'12':'VBAT_ADC','13':'POWER_N','6':'MODE_N','18':'I2C_SDA','19':'I2C_SCL','20':'MOTOR_PWM','21':'MOTOR_ARM',
          '16':'ACCEL_INT_N','30':'DOCK_PRESENT_N','3':'3V3','8':'MCU_EN','5':'STRAP2','22':'STRAP8','23':'BOOT_N',
          '26':'USB_DM','27':'USB_DP','31':'UART_TX','1':'GND'}
    nets.update({str(n):'GND' for n in grounds})
    c.part('ESP32_C3_MINI_1_N4X','U6','ESP32-C3-MINI-1-N4X candidate',127,88.9,nets,
           footprint='PrototypeR0:Espressif_ESP32-C3-MINI-1_53Pads',
           note='Full module53pads represented; NC intentionally isolated. Official-dimension candidate footprint; EPAD solder/paste, vias, RF clearances and assembly process remain review items.')
    for ref,x,net,val in [('C31',228.6,'3V3','10uF 10V'),('C32',266.7,'3V3','100nF'),('C33',304.8,'MCU_EN','1uF')]:
        c.part('C',ref,val,x,50.8,{'1':net,'2':'GND'})
    for ref,x,net in [('R31',228.6,'MCU_EN'),('R32',266.7,'STRAP2'),('R33',304.8,'STRAP8'),('R34',342.9,'BOOT_N')]:
        c.part('R',ref,'10k',x,96.52,{'1':'3V3','2':net})
    c.part('SW','SW1','POWER / momentary',40.64,180.34,{'1':'POWER_N','2':'GND'},note='Local silicone actuation. Soft off/deep sleep only; not battery isolation.')
    c.part('SW','SW2','MODE / momentary',81.28,180.34,{'1':'MODE_N','2':'GND'})
    c.part('SW','SW3','RESET / service',121.92,180.34,{'1':'MCU_EN','2':'GND'})
    c.part('SW','SW4','BOOT / service',162.56,180.34,{'1':'BOOT_N','2':'GND'})
    for ref,x,net in [('R35',40.64,'POWER_N'),('R36',81.28,'MODE_N'),('R37',121.92,'I2C_SDA'),('R38',162.56,'I2C_SCL')]:
        c.part('R',ref,'4.7k' if ref in ('R37','R38') else '10k',x,226.06,{'1':'3V3','2':net})
    c.part('R','R39','1.00M 1%',228.6,175.26,{'1':'PACK_P','2':'VBAT_ADC'})
    c.part('R','R40','1.00M 1%',266.7,175.26,{'1':'VBAT_ADC','2':'GND'})
    c.part('C','C34','100nF',304.8,175.26,{'1':'VBAT_ADC','2':'GND'},note='DividerThevenin500k; RC50ms. Firmware acquisition/calibration required.')
    c.part('Conn6','J4','SERVICE_USB_BOOT',266.7,251.46,
           {'1':'GND','2':'USB_DM','3':'USB_DP','4':'MCU_EN','5':'BOOT_N','6':'UART_TX'},
           note='Self-powered debug interface; no USB VBUS input. Actual connector/ESD and flashing fixture open.')
    c.note('POWER_N uses GPIO1 wake/deep-sleep semantics; mechanical latching off is not selected.\nGPIO2/8/9 reserved for boot. GPIO18/19 reserved for USB. 0V USB reference is GND.\nVBAT ADC=PACK_P/2; this is telemetry, not the independent pack protector.\nI2C pullups4.7k at main board; measure with actual tip harness and motor noise.',15.24,269.24)
    c.save()

    s=Sheet('04-sensors','R0 / onboard motion and wired tip sensor')
    s.note('MC3635 ON THE MAIN T BOARD / TMP117 ON REMOTE TIP INTERPOSER',15.24,15.24,2.032)
    s.part('MC3635','U7','MC3635 candidate /0x4C',101.6,78.74,
           {'1':'GND','2':'I2C_SDA','10':'I2C_SCL','9':'3V3','4':'GND','6':'3V3','7':'3V3','5':'ACCEL_INT_N','8':'GND','3':None},
           note='Firmware must perform required startup writes; INT polarity/open-drain configurable, default not assumed')
    s.part('R','R41','4.7k',177.8,55.88,{'1':'3V3','2':'ACCEL_INT_N'})
    s.part('C','C41','100nF',215.9,55.88,{'1':'3V3','2':'GND'},note='Local VDD bypass; place at U7')
    s.part('C','C42','100nF',254,55.88,{'1':'3V3','2':'GND'},note='Local VDDIO bypass; place at U7')
    s.part('Conn4','J5','MAIN_TIP_HARNESS',50.8,162.56,{'1':'3V3','2':'GND','3':'I2C_SDA','4':'I2C_SCL'},note='Physical connector and cable specification open; pin numbering matches remoteJ101')
    s.part('Conn4','J101','REMOTE_TIP_HARNESS',177.8,162.56,{'1':'3V3','2':'GND','3':'I2C_SDA','4':'I2C_SCL'},note='Remote tip assembly; not another rigid main-board topology')
    s.part('TMP117AIDRVR','U101','TMP117AIDRVR /0x48',292.1,162.56,
           {'1':'I2C_SCL','6':'I2C_SDA','4':'GND','5':'3V3','2':'GND','3':None},
           footprint='TipR1:TI_TMP117_DRV0006B_NoEP',
           note='Six electrical pins; mechanical thermal pad deliberately unsoldered with no copper/paste per TI rigid-PCB accuracy guidance. Remote board is separate; physical thermal bond unqualified')
    s.part('C','C101','100nF',355.6,162.56,{'1':'3V3','2':'GND'},note='Place directly at remote sensor supply pins')
    s.note('One shared100kHz bus is a starting configuration; no tip-cable length/capacitance is approved.\nSensor is coupled locally at tip; final shell thermal path and electronics heating must be characterized.\nShell/local sensor temperature is not validated tissue/core temperature. PackNTC is a separate circuit.\nTip interposer sealing, electrical insulation from metal, strain relief and exact footprint remain open.',15.24,218.44)
    s.save()

    root_id=uid(PROJECT)
    content=[]
    for i,sh in enumerate((p,m,c,s,g)):
        xx=38.1+(i%2)*177.8; yy=76.2+(i//2)*76.2
        content.append(f'''(sheet (at {xx} {yy}) (size 132.08 45.72)
          (stroke (width 0.254) (type default)) (fill (color 0 0 0 0)) (uuid {uid('sheet-'+sh.name)})
          (property "Sheetname" {q(sh.title)} (at {xx} {yy-2.54} 0) {effects(1.524,'(justify left)')})
          (property "Sheetfile" {q(sh.name+'.kicad_sch')} (at {xx} {yy+48.26} 0) {effects(1.27,'(justify left)')})
          (instances (project {q(PROJECT)} (path {q('/'+root_id)} (page {q(i+2)})))))''')
    root=f'''(kicad_sch (version 20230121) (generator electronics_r0_generate)
      (uuid {root_id}) (paper "A3")
      (title_block (title "Buttplug / native electronics R0") (date "2026-10-30") (rev "CANDIDATE")
        (company "Research and Desire") (comment 1 "New proposed design, not recovered Lucy/Gaby source; no fabrication release"))
      (lib_symbols)
      (text "NATIVE ELECTRICAL DESIGN / R0 REVIEW CANDIDATE" (at 25.4 25.4 0) {effects(2.54,'(justify left)')} (uuid {uid('root-title')}))
      (text "Five connected sheets use global net labels. Full T-shaped XY main-board topology is preserved; PCB placement/routing remains open.\\nActual protected cell, motor startup/stall, dock/NTC/thermal limits and footprints are not approved. Charge permission jumper starts OPEN.\\nBench assembly only after electrical review. No wear, casting, fabrication, radio or battery-runtime validation is claimed."
        (at 25.4 40.64 0) {effects(1.524,'(justify left top)')} (uuid {uid('root-note')}))
      {''.join(content)}
      (sheet_instances (path "/" (page "1"))))\n'''
    (OUT/f'{PROJECT}.kicad_sch').write_text(root)
    (OUT/'PrototypeR0.kicad_sym').write_text('(kicad_symbol_lib (version 20211014) (generator electronics_r0_generate)\n'+ '\n'.join(v['text'] for v in LIB.values())+'\n)\n')
    (OUT/'sym-lib-table').write_text('(sym_lib_table (lib (name "PrototypeR0")(type "KiCad")(uri "${KIPRJMOD}/PrototypeR0.kicad_sym")(options "")(descr "R0 candidate pin-checked project symbols")))\n')
    (OUT/'fp-lib-table').write_text('(fp_lib_table (lib (name "PrototypeR0")(type "KiCad")(uri "${KIPRJMOD}/PrototypeR0.pretty")(options "")(descr "R0 candidate footprints; review register before use")) (lib (name "TipR1")(type "KiCad")(uri "${KIPRJMOD}/../tip-r1/TipR1.pretty")(options "")(descr "Separate TMP117 remote tip assembly")))\n')
    # PCB API/GUI saves add useful board defaults and rule severities. Preserve
    # those fields instead of replacing a sibling agent's layout settings.
    project_path = OUT/f'{PROJECT}.kicad_pro'
    project = json.loads(project_path.read_text()) if project_path.exists() else {}
    project['meta'] = {'filename':PROJECT+'.kicad_pro','version':1}
    project.setdefault('board',{}).setdefault('design_settings',{}).setdefault('rules',{}).update({
        'min_clearance':0.10,'min_track_width':0.15,'min_via_diameter':0.60,
        'min_through_hole_diameter':0.30,'min_copper_edge_clearance':0.30})
    classes = project.setdefault('net_settings',{}).setdefault('classes',[])
    default = next((c for c in classes if c.get('name') == 'Default'),None)
    if default is None:
        default = {'name':'Default'}
        classes.append(default)
    default.update({'clearance':0.10,'track_width':0.20,'via_diameter':0.6,'via_drill':0.3,
        'microvia_diameter':0.3,'microvia_drill':0.1,'diff_pair_width':0.2,
        'diff_pair_gap':0.25,'diff_pair_via_gap':0.25})
    project.setdefault('erc',{})['erc_exclusions'] = []
    project_path.write_text(json.dumps(project,indent=2)+'\n')
    (OUT/'candidate-pin-manifest.json').write_text(json.dumps({'status':'Candidate schematic interfaces, not approved product BOM','date':'2026-10-30','parts':PARTS},indent=2)+'\n')
    print(f'Wrote 6 native schematic sheets and {len(PARTS)} symbol instances to {OUT}')


if __name__ == '__main__':
    main()
