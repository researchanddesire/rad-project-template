"""Finite rigid loading checks for the P1 kit; real wire forming stays manual."""
from pathlib import Path
import hashlib
import json
import sys

sys.path.insert(0, '/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as App
import Part
from simple_charging_wires_p1 import overlap


def main():
    folder = Path(sys.argv[1]).resolve()
    manifest = json.loads((folder / 'kit-manifest.json').read_text())
    native = folder / 'P1DryFitKit.FCStd'
    assert hashlib.sha256(native.read_bytes()).hexdigest() == manifest['native_sha256']
    doc = App.openDocument(str(native))
    shapes = {o.Name: o.Shape for o in doc.Objects if hasattr(o, 'Shape') and not o.Shape.isNull()}
    core = ['BodyCarrier', 'BodyBoardGauge', 'BodyBoardKeeper', 'PlugGauge_J3',
            'PlugGauge_J5', 'PlugGauge_J6']
    stages = [
        ('core_through_open_nose', core, ['Body'], (0, 1, 0), [100, 70, 50, 30, 20, 10, 5, 2, 1, 0]),
        ('flange_board_unplugged', ['FlangeBoardGauge'],
         ['Body', 'LeftHub', 'RightHub']+core, (-1, 0, 0), [50, 30, 20, 10, 5, 2, 1, 0]),
        ('independent_motor_mount', ['MotorMount', 'MotorGauge'],
         ['Body']+core, (0, 1, 0), [30, 20, 10, 5, 2, 1, 0]),
    ]
    results = []
    for name, moving, fixed, axis, distances in stages:
        poses = []
        for distance in distances:
            hits = []
            for a in moving:
                shape = shapes[a].copy()
                shape.translate(App.Vector(*axis)*distance)
                for b in fixed:
                    volume = overlap(shape, shapes[b])
                    if volume > 1e-5:
                        hits.append({'moving': a, 'fixed': b, 'intersection_mm3': volume})
            poses.append({'distance_mm': distance, 'hits': hits})
        print(name, 'hits', [(p['distance_mm'], p['hits']) for p in poses if p['hits']], flush=True)
        results.append({'stage': name, 'moving': moving, 'fixed': fixed,
                        'translation_axis': axis, 'samples': poses})
    passed = not any(p['hits'] for stage in results for p in stage['samples'])
    result = {'kit_native_sha256': manifest['native_sha256'],
              'checker_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'all_listed_samples_clear': passed, 'stages': results,
              'scope': 'Finite rigid part/gauge samples only. Flange board loads before its plugs; cap/tip/skins wait during core and motor loading. No continuous collision, flexible-wire travel, cap-thread motion, hands/tools, physical fitting, finish or seal proof. Complete connected assembly/service remains the dry-fit worksheet task.'}
    (folder / 'loading-check.json').write_text(json.dumps(result, indent=2)+'\n')
    assert passed, 'Resolve reported rigid loading interference before presenting the kit'


if __name__ == '__main__':
    main()
