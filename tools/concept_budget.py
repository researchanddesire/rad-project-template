"""Reproduce the concept's unit-aware power and box-envelope calculations."""
from pathlib import Path
import argparse
import json
import math
import unittest

ROOT = Path(__file__).resolve().parents[1]


def power_row(settings, case):
    hours = float(settings['target_hours'])
    usable = float(settings['usable_capacity_fraction'])
    efficiency = float(settings['motor_supply_efficiency'])
    voltage = float(settings['battery_nominal_voltage_v'])
    motor_v = float(settings['motor_voltage_v'])
    current = float(settings['motor_current_ma'])
    base = float(case['base_average_battery_ma'])
    minutes = float(case['motor_minutes_per_target'])
    values = [hours, usable, efficiency, voltage, motor_v, current, base, minutes]
    if not all(math.isfinite(v) for v in values):
        raise ValueError('Inputs must be finite')
    if hours <= 0 or voltage <= 0 or motor_v <= 0:
        raise ValueError('Hours and voltages must be positive')
    if not 0 < usable <= 1 or not 0 < efficiency <= 1:
        raise ValueError('Fractions must be in (0, 1]')
    if min(current, base, minutes) < 0 or minutes > hours * 60:
        raise ValueError('Currents must be nonnegative; motor time must fit the period')
    # mA * V * h = mWh; divide by battery V and conversion efficiency for mAh.
    motor_mah = motor_v * current * (minutes / 60) / (voltage * efficiency)
    base_mah = base * hours
    charge_mah = base_mah + motor_mah
    return {'name': case['name'], 'base_mah': round(base_mah, 2),
            'motor_mah': round(motor_mah, 2),
            'required_mah': round(charge_mah, 2),
            'required_nameplate_mah': round(charge_mah / usable, 2),
            'meets_capacity_study': {str(c): charge_mah <= float(c) * usable
                                     for c in settings['hypothetical_cell_capacities_mah']}}


def envelope_report(layout):
    allowance = 2 * (layout['skin_allowance_each_side'] +
                     layout['core_wall_allowance_each_side'])
    a = layout['stacked_t_base']
    b = layout['split_wings']
    a_inner = [d - allowance for d in a['outer_base_wdh']]
    a_stack = a['protected_pack_bay_wdh'][2] + a['populated_pcb_wdh'][2] + layout['stack_separator']
    b_inner = [d - allowance for d in b['outer_base_wdh']]
    b_width = b['protected_pack_bay_wdh'][0] + b['populated_pcb_wdh'][0] + b['inter_bay_gap']
    return {'status': 'Axis-aligned box arithmetic, not a fit or strength validation',
            'stacked': {'inner_wdh_mm': a_inner, 'stack_height_mm': a_stack,
                        'remaining_height_mm': a_inner[2] - a_stack,
                        'reservations_inside_box': max(a['protected_pack_bay_wdh'][0], a['populated_pcb_wdh'][0]) <= a_inner[0]
                        and max(a['protected_pack_bay_wdh'][1], a['populated_pcb_wdh'][1]) <= a_inner[1] and a_stack <= a_inner[2]},
            'split': {'inner_wdh_mm': b_inner, 'side_by_side_width_mm': b_width,
                      'remaining_width_mm': b_inner[0] - b_width,
                      'reservations_inside_box': b_width <= b_inner[0]
                      and max(b['protected_pack_bay_wdh'][1], b['populated_pcb_wdh'][1]) <= b_inner[1]
                      and max(b['protected_pack_bay_wdh'][2], b['populated_pcb_wdh'][2]) <= b_inner[2]}}


class UnitChecks(unittest.TestCase):
    def setUp(self):
        self.cfg = {'target_hours': 24, 'usable_capacity_fraction': 0.8,
                    'motor_supply_efficiency': 1, 'battery_nominal_voltage_v': 3.7,
                    'motor_voltage_v': 3.7, 'motor_current_ma': 450,
                    'hypothetical_cell_capacities_mah': [1000]}

    def test_no_motor_one_day_at_50ma_needs_1500mah_nameplate(self):
        r = power_row(self.cfg, {'name': 'idle', 'base_average_battery_ma': 50, 'motor_minutes_per_target': 0})
        self.assertEqual(r['required_mah'], 1200)
        self.assertEqual(r['required_nameplate_mah'], 1500)
        self.assertFalse(r['meets_capacity_study']['1000'])

    def test_one_hour_motor_at_same_voltage_uses_450mah(self):
        r = power_row(self.cfg, {'name': 'motor', 'base_average_battery_ma': 0, 'motor_minutes_per_target': 60})
        self.assertEqual(r['required_mah'], 450)
        self.cfg['motor_supply_efficiency'] = 0.9
        r = power_row(self.cfg, {'name': 'motor', 'base_average_battery_ma': 0, 'motor_minutes_per_target': 60})
        self.assertEqual(r['required_mah'], 500)

    def test_impossible_duration_and_zero_efficiency_rejected(self):
        with self.assertRaises(ValueError):
            power_row(self.cfg, {'name': 'invalid', 'base_average_battery_ma': 0, 'motor_minutes_per_target': 1441})
        self.cfg['motor_supply_efficiency'] = 0
        with self.assertRaises(ValueError):
            power_row(self.cfg, {'name': 'invalid', 'base_average_battery_ma': 0, 'motor_minutes_per_target': 1})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-test', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.self_test:
        unittest.main(argv=['concept_budget.py'])
    settings = json.loads((ROOT/'hardware/design/power-scenarios-v1.json').read_text())
    layout = json.loads((ROOT/'hardware/cad/concepts/layout-v1.json').read_text())
    result = {'power': [power_row(settings, c) for c in settings['scenarios']],
              'packaging': envelope_report(layout)}
    encoded = json.dumps(result, indent=2) + '\n'
    if args.output:
        args.output.write_text(encoded)
    else:
        print(encoded, end='')
