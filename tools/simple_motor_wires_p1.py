"""Two conditional motor lead allowances and plug access, without a new keeper."""
import FreeCAD as App
import Part


def build(doc, active_names):
    wires = []
    paths = []
    hits = []
    omitted = {'MotorLeadFlareAllowanceR21', 'TipStrainReliefProcessAllowanceR26'}

    def overlap(a, b):
        aa, bb = a.BoundBox, b.BoundBox
        if any(min(getattr(aa, k+'Max'), getattr(bb, k+'Max')) <=
               max(getattr(aa, k+'Min'), getattr(bb, k+'Min')) + 1e-7 for k in 'XYZ'):
            return 0.
        return a.copy().common(b.copy()).Volume

    for pin, x, end_x in [(1, -3.9, .5), (2, -4.9, -.5)]:
        points = [(x, 54.975, 2.1), (x, 58.475, 2.1),
                  (end_x, 58.5, 3.5), (end_x, 62., 3.5)]
        curve = Part.BezierCurve()
        curve.setPoles([App.Vector(*p) for p in points])
        edge = curve.toShape()
        spine = doc.addObject('Part::Feature', 'P1MotorPath'+str(pin))
        spine.Shape = Part.Wire([edge])
        profile = doc.addObject('Part::Feature', 'P1MotorProfile'+str(pin))
        profile.Shape = Part.Wire([Part.makeCircle(.3, App.Vector(*points[0]), App.Vector(0, 1, 0))])
        obj = doc.addObject('Part::Sweep', 'P1MotorWire'+str(pin))
        obj.Sections, obj.Spine, obj.Solid, obj.Frenet = [profile], spine, True, False
        obj.Label = 'J3.'+str(pin)+' / '+('MOTOR_P' if pin == 1 else 'MOTOR_N, NOT GND')+' / OD0.60 lead allowance'
        doc.recompute()
        assert obj.Shape.isValid() and len(obj.Shape.Solids) == 1
        radii = [1/edge.curvatureAt(u/200) for u in range(201) if edge.curvatureAt(u/200) > 1e-9]
        paths.append({'pin': pin, 'role': obj.Name, 'bezier_poles_xyz_mm': points,
                      'path_length_mm': edge.Length, 'OD_allowance_mm': .6,
                      'sampled_minimum_radius_mm': min(radii),
                      'net': 'MOTOR_P' if pin == 1 else 'MOTOR_N'})
        wires.append(obj)
        for name in active_names:
            if name in omitted:
                continue
            v = overlap(obj.Shape, doc.getObject(name).Shape)
            if v > 1e-5:
                hits.append({'wire': obj.Name, 'fixed': name, 'intersection_mm3': v})
    v = overlap(wires[0].Shape, wires[1].Shape)
    if v > 1e-5:
        hits.append({'wire': wires[0].Name, 'fixed': wires[1].Name, 'intersection_mm3': v})
    # Plug comes from the open nose with motor seated and tip/cap waiting.
    waiting = {'MotorSeatCapR25', 'TipPCB', 'TipComponentEnvelope',
               'StationaryTipCarrierR26', 'StationaryPickupShoeR26',
               'TipClipFittedEnvelopeR26', 'TipDielectricBondR26', 'TipCapThermalGelR26'}
    poses = []
    mate = doc.getObject('R17Mate_J3').Shape
    for offset in (4., 3., 2., 1., .5, 0.):
        s = mate.copy()
        s.translate(App.Vector(0, offset, 0))
        bad = []
        for name in active_names:
            if name in waiting | omitted | {'R17Mate_J3'} or name.startswith(('TipWire', 'TipBare', 'TipSolder')):
                continue
            v = overlap(s, doc.getObject(name).Shape)
            if v > 1e-5:
                bad.append({'fixed': name, 'intersection_mm3': v})
        poses.append({'offset_Y_mm': offset, 'hits': bad})
    print('P1 motor lead collisions', hits, 'plug access', poses, flush=True)
    return {'objects': wires, 'construction': [doc.getObject('P1MotorPath'+str(i)) for i in (1, 2)] +
            [doc.getObject('P1MotorProfile'+str(i)) for i in (1, 2)],
            'review': {'paths': paths, 'unexpected_intersections': hits,
                       'motor_mate_listed_poses': poses,
                       'scope': 'Nominal OD0.60 jackets and assumed capsule lead exits only. Current J3 pin-axis mapping follows native footprint rotation. Actual OEM lead OD, bend limits, termination and slack/assembly movement need fit trial. Finite plug poses omit the still-waiting tip/cap; no continuous flexible-wire proof.'}}
