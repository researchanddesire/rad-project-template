"""Check actual KiCad-exported connectivity against the candidate pin manifest.

This is a netlist export check, not a replacement for KiCad GUI ERC, hardware
review, simulation, footprint checks or bench testing.
"""
from pathlib import Path
import hashlib
import json
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'hardware/pcb/prototype-r0'


def main():
    manifest = json.loads((OUT/'candidate-pin-manifest.json').read_text())
    root = ET.parse(OUT/'buttplug-r0.xml').getroot()
    actual = {}
    for net in root.find('nets'):
        for node in net.findall('node'):
            actual[(node.attrib['ref'], node.attrib['pin'])] = net.attrib['name']
    issues = []
    checked = 0
    for part in manifest['parts']:
        if part['assembly_domain'] == 'ANNOTATION':
            continue
        for number, pin in part['pins'].items():
            wanted = pin['net']
            found = actual.get((part['ref'], number))
            if wanted is None:
                if found is not None and not found.startswith('unconnected-'):
                    issues.append(f'{part["ref"]}.{number} expected NC, exported {found}')
            elif wanted != found:
                issues.append(f'{part["ref"]}.{number} expected {wanted}, exported {found}')
            checked += 1
    nets = {name: sorted(f'{ref}.{pin}' for (ref,pin), n in actual.items() if n == name)
            for name in ('SYS','3V3','PACK_P','PACK_NTC','PACK_GUARD','CHARGE_TEMP_OK','CHARGE_PERMIT','CHARGE_GATE','CHARGE_CE_N','MOTOR_3V7','MOTOR_PWM','MOTOR_ARM','MOTOR_IN1',
                         'MOTOR_P','MOTOR_N','DOCK_PRESENT_N','I2C_SDA','I2C_SCL','ACCEL_INT_N')}
    assert actual.get(('U6','20')) == 'MOTOR_PWM'
    assert actual.get(('U6','21')) == 'MOTOR_ARM'
    assert actual.get(('U1','7')) == actual.get(('U4','6')) == actual.get(('U6','30')) == 'DOCK_PRESENT_N'
    assert actual.get(('U5','5')) == actual.get(('U5','7')) == 'GND'
    assert actual.get(('J3','2')) == actual.get(('U5','3')) == 'MOTOR_N'
    assert actual.get(('J3','2')) != 'GND'
    for pin, net in {'1':'3V3','2':'GND','3':'I2C_SDA','4':'I2C_SCL'}.items():
        assert actual.get(('J5',pin)) == actual.get(('J101',pin)) == net
    assert actual.get(('U8','1')) == actual.get(('U8','6')) == actual.get(('U9','1')) == actual.get(('JP1','1')) == 'CHARGE_TEMP_OK'
    assert actual.get(('JP1','2')) == actual.get(('R47','1')) == 'CHARGE_PERMIT'
    assert actual.get(('Q1','1')) == actual.get(('R47','2')) == actual.get(('R48','1')) == 'CHARGE_GATE'
    assert actual.get(('Q1','3')) == actual.get(('U1','4')) == 'CHARGE_CE_N'
    assert actual.get(('J2','4')) == actual.get(('TH2','1')) == 'PACK_GUARD'
    assert actual.get(('U101','1')) == 'I2C_SCL' and actual.get(('U101','6')) == 'I2C_SDA'
    assert actual.get(('U2','14')) == actual.get(('U2','1')) == actual.get(('R13','2')) == 'REG1_PS'
    assert actual.get(('U2','14')) != 'SYS'
    for ref, net in {'C51':'SYS','C52':'3V3','C53':'SYS','C54':'MOTOR_3V7'}.items():
        assert actual.get((ref,'1')) == net and actual.get((ref,'2')) == 'GND'
    hashes = {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.glob('*.kicad_sch'))}
    result = {'check':'KiCad XML export versus candidate pin manifest, not ERC',
              'kicad_tool':root.findtext('design/tool'), 'pins_checked':checked,
              'issues':issues, 'key_nets':nets,'schematic_sha256':hashes,
              'assembly_partition':{domain:sorted(p['ref'] for p in manifest['parts'] if p['assembly_domain']==domain)
                                    for domain in ('MAIN_T','REMOTE_TIP','EXTERNAL_PACK','ANNOTATION')}}
    (OUT/'netlist-review.json').write_text(json.dumps(result,indent=2)+'\n')
    print(f'Checked {checked} exported pins; {len(issues)} mismatches. Not an ERC or physical validation.')
    if issues:
        raise SystemExit('\n'.join(issues))


if __name__ == '__main__':
    main()
