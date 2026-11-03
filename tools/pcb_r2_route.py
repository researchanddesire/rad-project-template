#!/usr/bin/env python3
"""Reproduce R2 routing from a frozen placement and explicit route sources.

Run with KiCad 7's bundled Python. In1.Cu is reserved for GND. This tool does
not change footprints, the circuit, or the audited R0 source. Native DRC and
actual-project rules decide whether the resulting candidate is connected.
"""
from __future__ import annotations
import argparse, hashlib, json, math, re
from pathlib import Path
import wx
APP = wx.App(False)
import pcbnew as k
ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / 'hardware/pcb/prototype-r2'
BOARD = PROJECT / 'buttplug-r2.kicad_pcb'
LAYERS = {'F.Cu': k.F_Cu, 'In2.Cu': k.In2_Cu, 'B.Cu': k.B_Cu}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, data):
    path.write_text(json.dumps(data, indent=2) + '\n')


def xy(x, y):
    return k.VECTOR2I(k.FromMM(100 + x), k.FromMM(130 - y))


def mech(point):
    return [round(k.ToMM(point.x)-100, 6), round(130-k.ToMM(point.y), 6)]


def apply_routes(board, records, locked=True):
    for route in records:
        if route['kind'] == 'via':
            item = k.PCB_VIA(board)
            item.SetPosition(xy(*route['position']))
            item.SetWidth(k.FromMM(route.get('diameter', .6)))
            item.SetDrill(k.FromMM(route.get('drill', .3)))
            item.SetViaType(k.VIATYPE_THROUGH)
            item.SetLayerPair(k.F_Cu, k.B_Cu)
        else:
            assert route['layer'] in LAYERS, 'In1 is reserved for GND'
            item = k.PCB_TRACK(board)
            item.SetStart(xy(*route['start'])); item.SetEnd(xy(*route['end']))
            item.SetWidth(k.FromMM(route['width']))
            item.SetLayer(LAYERS[route['layer']])
        net = board.FindNet(route['net'])
        assert net, route['net']
        item.SetNet(net); item.SetLocked(locked); board.Add(item)


def route_records(board):
    records = []
    for item in board.GetTracks():
        if isinstance(item, k.PCB_VIA):
            records.append({'kind': 'via', 'net': item.GetNetname(),
                'position': mech(item.GetPosition()),
                'diameter': k.ToMM(item.GetWidth()), 'drill': k.ToMM(item.GetDrillValue())})
        else:
            records.append({'kind': 'track', 'net': item.GetNetname(),
                'layer': k.LayerName(item.GetLayer()), 'start': mech(item.GetStart()),
                'end': mech(item.GetEnd()), 'width': k.ToMM(item.GetWidth())})
    return records


def fill_save(path):
    # A save/reload before filling avoids the KiCad 7 in-memory build crash.
    board = k.LoadBoard(str(path)); board.BuildConnectivity()
    filler = k.ZONE_FILLER(board); filler.Fill(board.Zones())
    k.SaveBoard(str(path), board)
    return board


def ground_planes(board, outline):
    for layer in (k.F_Cu, k.In1_Cu, k.In2_Cu, k.B_Cu):
        zone = k.ZONE(board); zone.SetLayer(layer); zone.SetNet(board.FindNet('GND'))
        zone.SetLocalClearance(k.FromMM(.1)); zone.SetMinThickness(k.FromMM(.2))
        zone.SetPadConnection(k.ZONE_CONNECTION_THERMAL)
        zone.SetThermalReliefGap(k.FromMM(.2)); zone.SetThermalReliefSpokeWidth(k.FromMM(.3))
        zone.SetIslandRemovalMode(k.ISLAND_REMOVAL_MODE_ALWAYS)
        poly = zone.Outline(); poly.NewOutline()
        for point in outline:
            p = xy(*point); poly.Append(p.x, p.y)
        board.Add(zone)


def u7_rule_area(board):
    """Keep inner signals/through-via annuli out of the nominal MEMS body.

    This is a bounded engineering precaution, not package-process acceptance.
    F terminal escapes and the In1 GND reference remain available.
    """
    footprint=next(f for f in board.GetFootprints() if f.GetReference()=='U7')
    x,y=mech(footprint.GetPosition())
    zone=k.ZONE(board); zone.SetIsRuleArea(True)
    layers=k.LSET(); layers.AddLayer(k.In2_Cu); layers.AddLayer(k.B_Cu)
    zone.SetLayerSet(layers); zone.SetDoNotAllowTracks(True)
    zone.SetDoNotAllowVias(True); zone.SetDoNotAllowCopperPour(False)
    zone.SetDoNotAllowPads(False); zone.SetDoNotAllowFootprints(False)
    poly=zone.Outline(); poly.NewOutline()
    for a,b in [(x-.8,y-.8),(x+.8,y-.8),(x+.8,y+.8),(x-.8,y+.8)]:
        point=xy(a,b); poly.Append(point.x,point.y)
    board.Add(zone)


def usb_via_rule_areas(board):
    """Prevent later through vias from perforating the pair's reference corridor.

    The strips allow plane copper and tracks. Native DRC tests the via annulus,
    providing a conservative margin around each 0.2 mm signal. Actual impedance
    still depends on a supplier-approved stackup and process.
    """
    for track in list(board.GetTracks()):
        if isinstance(track,k.PCB_VIA) or track.GetNetname() not in ('USB_DM','USB_DP'):
            continue
        a,b=map(mech,(track.GetStart(),track.GetEnd()))
        dx,dy=b[0]-a[0],b[1]-a[1]; length=math.hypot(dx,dy)
        if length==0:continue
        ux,uy=dx/length,dy/length; nx,ny=-uy*.2,ux*.2
        points=[[a[0]-ux*.2+nx,a[1]-uy*.2+ny],
                [b[0]+ux*.2+nx,b[1]+uy*.2+ny],
                [b[0]+ux*.2-nx,b[1]+uy*.2-ny],
                [a[0]-ux*.2-nx,a[1]-uy*.2-ny]]
        zone=k.ZONE(board);zone.SetIsRuleArea(True);zone.SetLayer(k.In1_Cu)
        zone.SetDoNotAllowVias(True);zone.SetDoNotAllowTracks(False)
        zone.SetDoNotAllowCopperPour(False);zone.SetDoNotAllowPads(False)
        zone.SetDoNotAllowFootprints(False)
        poly=zone.Outline();poly.NewOutline()
        for point in points:
            p=xy(*point);poly.Append(p.x,p.y)
        board.Add(zone)


def build(source_path, routes_path, output):
    source = json.loads(source_path.read_text())
    placement = source_path.parent / source['placement_file']
    assert sha(placement) == source['placement_sha256'], 'Frozen placement changed'
    board = k.LoadBoard(str(placement))
    assert not list(board.GetTracks()), 'Placement source must be unrouted'
    for fp in board.GetFootprints():
        override=source.get('pose_overrides',{}).get(fp.GetReference())
        if override:
            assert ('B' if fp.GetLayer()==k.B_Cu else 'F')==override['side']
            fp.SetOrientationDegrees(override['native_angle_deg'])
            fp.SetPosition(xy(*override['xy_mm']))
    for fp in board.GetFootprints():
        fp.SetProperty('PlacementStatus','R2 ROUTED ENGINEERING CANDIDATE / NOT FAB')
    for item in board.GetDrawings():
        if isinstance(item,k.PCB_TEXT) and 'R2 PLACEMENT ONLY' in item.GetText():
            item.SetText('R2 ROUTED ENGINEERING CANDIDATE / NOT FAB')
    routes = json.loads(routes_path.read_text())
    assert routes['placement_sha256'] == source['placement_sha256']
    apply_routes(board, routes['routes'])
    for fp in board.GetFootprints():
        if fp.GetReference() in ('U1','U2','U3','U4','U5'):
            for pad in fp.Pads():
                if pad.GetNetname()=='GND': pad.SetZoneConnection(k.ZONE_CONNECTION_FULL)
    u7_rule_area(board)
    usb_via_rule_areas(board)
    ground_planes(board, source['pcb_outline_vertices_xy_mm'])
    k.SaveBoard(str(output), board)
    fill_save(output)


def export_dsn(board_path, output):
    board = k.LoadBoard(str(board_path))
    # The reference plane remains a plane; outer pours are not treated as ideal
    # connections that might hide final ground islands from the router.
    for zone in list(board.Zones()):
        if not zone.GetIsRuleArea() and not zone.GetLayerSet().Contains(k.In1_Cu):
            board.Delete(zone)
    assert k.ExportSpecctraDSN(board, str(output))
    dsn = output.read_text()
    power = ['SYS','PACK_P','DOCK_5V','DOCK_FUSED','VBUS_CHG','MOTOR_3V7','MOTOR_P','MOTOR_N']
    begin = dsn.index('(class kicad_default'); end = dsn.index('(circuit', begin)
    header = dsn[begin:end]
    for net in power + ['3V3']:
        header = re.sub(r'(?<!\S)' + re.escape(net) + r'(?=\s)', '', header)
    dsn = dsn[:begin] + header + dsn[end:]
    insert = dsn.rfind('\n  )', 0, dsn.index('\n  (wiring'))
    classes = '\n    (class PowerRails ' + ' '.join(power) + '\n      (circuit (use_via Via[0-3]_600:300_um))\n      (rule (width 600) (clearance 100.1))\n    )'
    classes += '\n    (class DigitalSupply 3V3\n      (circuit (use_via Via[0-3]_600:300_um))\n      (rule (width 300) (clearance 100.1))\n    )'
    output.write_text(dsn[:insert] + classes + dsn[insert:])


def parse_ses(path):
    tokens = re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+', path.read_text())
    stack=[]; root=None
    for token in tokens:
        if token == '(':
            node=[]
            if stack: stack[-1].append(node)
            stack.append(node)
        elif token == ')':
            node=stack.pop()
            if not stack: root=node
        else:
            stack[-1].append(json.loads(token) if token.startswith('"') else token)
    assert root and not stack and root[0] == 'session'
    routes=next(n for n in root if isinstance(n,list) and n[0]=='routes')
    assert next(n for n in routes if isinstance(n,list) and n[0]=='resolution') == ['resolution','um','10']
    network=next(n for n in routes if isinstance(n,list) and n[0]=='network_out')
    def point(x,y):
        return [round(float(x)/10000-100, 6), round(130+float(y)/10000, 6)]
    result=[]
    for net in network[1:]:
        assert net[0] == 'net'
        for feature in net[2:]:
            if feature[0] == 'wire':
                route=feature[1]; assert route[0]=='path' and route[1] in LAYERS
                points=[point(x,y) for x,y in zip(route[3::2],route[4::2])]
                for a,b in zip(points,points[1:]):
                    result.append({'kind':'track','net':net[1],'layer':route[1],
                        'start':a,'end':b,'width':float(route[2])/10000})
            elif feature[0] == 'via':
                dims=re.fullmatch(r'Via\[0-[13]\]_(\d+):(\d+)_um',feature[1]); assert dims, feature
                result.append({'kind':'via','net':net[1],'position':point(feature[2],feature[3]),
                    'diameter':float(dims[1])/1000,'drill':float(dims[2])/1000})
            else:
                raise ValueError('Unsupported SES feature: '+str(feature))
    return result


def import_session(board_path, session_path):
    board=k.LoadBoard(str(board_path))
    for item in list(board.GetTracks()):
        if not item.IsLocked(): board.Delete(item)
    apply_routes(board, parse_ses(session_path), locked=False)
    k.SaveBoard(str(board_path),board); fill_save(board_path)


def refine_routes(board_path, patch_path, session_path):
    """Apply explicit local route repairs only to the matching route session."""
    patch=json.loads(patch_path.read_text())
    assert sha(session_path)==patch['session_sha256'], 'SES differs from reviewed repairs'
    board=k.LoadBoard(str(board_path))
    def signature(record):
        if record['kind']=='via':
            return ('via',record['net'],tuple(record['position']))
        return ('track',record['net'],record['layer'],
                tuple(sorted((tuple(record['start']),tuple(record['end'])))))
    remove={signature(r) for r in patch.get('remove',[])}
    for item,record in zip(list(board.GetTracks()),route_records(board)):
        if signature(record) in remove:board.Delete(item)
        elif not isinstance(item,k.PCB_VIA) and item.GetWidth()<k.FromMM(.15):
            item.SetWidth(k.FromMM(.15))
    apply_routes(board,patch.get('routes',[]))
    k.SaveBoard(str(board_path),board);fill_save(board_path)


def geometry_export(board_path, output):
    """Conservative native copper geometry for local route-search studies."""
    board=k.LoadBoard(str(board_path));pads=[]
    for footprint in board.GetFootprints():
        for pad in footprint.Pads():
            bounds=pad.GetBoundingBox()
            pads.append({'ref':footprint.GetReference(),'number':pad.GetNumber(),
                'net':pad.GetNetname(),'position':mech(pad.GetPosition()),
                'bounds':[round(k.ToMM(bounds.GetLeft())-100,6),round(130-k.ToMM(bounds.GetBottom()),6),
                          round(k.ToMM(bounds.GetRight())-100,6),round(130-k.ToMM(bounds.GetTop()),6)],
                'layers':[name for name,layer in LAYERS.items() if pad.GetLayerSet().Contains(layer)]})
    routes=route_records(board)
    for route in routes:
        if route['kind']=='via':route['radius']=route['diameter']/2
    source=json.loads((PROJECT/'routing-source-r2.json').read_text())
    write(output,{'outline':source['pcb_outline_vertices_xy_mm'],'tracks':routes,'pads':pads})


def drc(board_path, report_path):
    board=k.LoadBoard(str(board_path)); board.BuildConnectivity()
    assert k.WriteDRCReport(board,str(report_path),k.EDA_UNITS_MILLIMETRES,True)
    text=report_path.read_text()
    return {key:int(re.search(r'\*\* Found (\d+) '+name,text)[1]) for key,name in
        [('drc_violations','DRC violations'),('unconnected_items','unconnected pads'),('footprint_errors','Footprint errors')]}


def audit(board_path, drc_path, output):
    board=k.LoadBoard(str(board_path))
    manifest=PROJECT/'candidate-pin-manifest.json'
    parts={p['ref']:p for p in json.loads(manifest.read_text())['parts'] if p['assembly_domain']=='MAIN_T' and not p['ref'].startswith('#')}
    footprints={f.GetReference():f for f in board.GetFootprints()}; mismatches=[]; pinsets=[]; count=0
    for ref,part in parts.items():
        actual={p.GetNumber() for p in footprints[ref].Pads() if p.GetNumber() not in ('','MP')}
        if actual!=set(part['pins']): pinsets.append([ref,sorted(actual),sorted(part['pins'])])
        for pad in footprints[ref].Pads():
            entry=part['pins'].get(pad.GetNumber())
            if entry:
                count+=1
                if pad.GetNetname() != (entry['net'] or ''):
                    mismatches.append([ref,pad.GetNumber(),pad.GetNetname(),entry['net']])
    ground=next(z for z in board.Zones() if not z.GetIsRuleArea() and z.GetLayerSet().Contains(k.In1_Cu))
    usb={}
    for net in ('USB_DM','USB_DP'):
        tracks=[t for t in board.GetTracks() if t.GetNetname()==net]; samples=missing=0
        for track in tracks:
            if isinstance(track,k.PCB_VIA): continue
            a,b=track.GetStart(),track.GetEnd(); dx,dy=b.x-a.x,b.y-a.y
            length=math.hypot(dx,dy)
            if length==0: continue
            steps=max(1,math.ceil(k.ToMM(length)/.1))
            for i in range(steps+1):
                for offset in (-.1,0,.1):
                    point=k.VECTOR2I(round(a.x+dx*i/steps-dy/length*k.FromMM(offset)),round(a.y+dy*i/steps+dx/length*k.FromMM(offset)))
                    samples+=1
                    if not ground.HitTestFilledArea(k.In1_Cu,point): missing+=1
        usb[net]={'length_mm':round(sum(k.ToMM(t.GetLength()) for t in tracks if not isinstance(t,k.PCB_VIA)),6),
            'vias':sum(isinstance(t,k.PCB_VIA) for t in tracks),
            'widths_mm':sorted({k.ToMM(t.GetWidth()) for t in tracks if not isinstance(t,k.PCB_VIA)}),
            'layers':sorted({k.LayerName(t.GetLayer()) for t in tracks if not isinstance(t,k.PCB_VIA)}),
            'reference_samples':samples,'samples_without_In1_ground':missing}
    result={'board_sha256':sha(board_path),'project_sha256':sha(board_path.with_suffix('.kicad_pro')),
        'manifest_sha256':sha(manifest),'drc_report_sha256':sha(drc_path),
        'counts':{key:int(re.search(r'\*\* Found (\d+) '+name,drc_path.read_text())[1]) for key,name in [('drc_violations','DRC violations'),('unconnected_items','unconnected pads'),('footprint_errors','Footprint errors')]},'main_footprints':len(footprints),'nets':board.GetNetCount()-1,
        'main_pad_entries_checked':count,'pad_net_mismatches':mismatches,'pinset_mismatches':pinsets,
        'board_only_refs':sorted(set(footprints)-set(parts)),'manifest_only_refs':sorted(set(parts)-set(footprints)),
        'copper_layers':board.GetCopperLayerCount(),
        'In1_signal_tracks':sum(not isinstance(t,k.PCB_VIA) and t.GetLayer()==k.In1_Cu for t in board.GetTracks()),
        'usb':usb,'limits':['Geometric connectivity checks do not establish actual-part fit, current, thermal, RF, endurance or physical validation.','Fabricator stackup/impedance, via-in-pad/stencil and U7 package-specific assembly acceptance remain open.']}
    # DRC can save project settings; capture the final files after it completes.
    result['board_sha256']=sha(board_path); result['project_sha256']=sha(board_path.with_suffix('.kicad_pro'))
    result['drc_report_sha256']=sha(drc_path)
    write(output,result); print(json.dumps(result,indent=2))


def derive_manual(placement_path, output):
    """Bootstrap explicit R2 copper from the checked R0 local layout geometry.

    The resulting JSON is the reviewable route source. Its affine transforms
    preserve complete converter bays; independently moved feedback/input caps
    are connected from actual R2 pad coordinates rather than old positions.
    Native DRC still checks the derived paths and drill clearances.
    """
    import importlib.util
    module_path=ROOT/'tools/pcb_r0_layout.py'
    spec=importlib.util.spec_from_file_location('r0_review_source',module_path)
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    old=k.LoadBoard(str(ROOT/'hardware/pcb/prototype-r0/buttplug-r0.kicad_pcb'))
    for item in list(old.GetTracks()): old.Delete(item)
    module.critical_routes(old)
    source_records=route_records(old)
    current=k.LoadBoard(str(placement_path))
    fps={f.GetReference():f for f in current.GetFootprints()}
    def pad(ref,n):
        return mech(next(p for p in fps[ref].Pads() if p.GetNumber()==str(n)).GetPosition())
    result=[]
    def path(net,points,width=.3,layer='B.Cu'):
        for a,b in zip(points,points[1:]):
            if a!=b:result.append({'kind':'track','net':net,'start':a,'end':b,'width':width,'layer':layer})
    def via(net,p):
        result.append({'kind':'via','net':net,'position':p,'diameter':.6,'drill':.3})
    def same(a,b):return math.dist(a,b)<.0001
    oldfps={f.GetReference():f for f in old.GetFootprints()}
    def oldpad(ref,n):return mech(next(p for p in oldfps[ref].Pads() if p.GetNumber()==str(n)).GetPosition())
    old_c22=[oldpad('C22',1),oldpad('C22',2)]
    for source in source_records:
        route=dict(source)
        pts=[route['position']] if route['kind']=='via' else [route['start'],route['end']]
        net=route['net']; transform=None; layer=None
        if net in ('USB_DM','USB_DP'):
            transform=lambda p:p
        elif all(p[0]<-20 and -23<p[1]<-13 for p in pts):
            transform=lambda p:p
        elif all(p[0]>20 and -26<p[1]<-10 for p in pts):
            transform=lambda p:p
        elif all(-7<p[0]<7 and 5<p[1]<16.5 for p in pts):
            # Feedback is now wholly on B; old F escapes are deliberately omitted.
            if net=='REG1_FB' or (route['kind']=='track' and route['layer']!='B.Cu'):
                continue
            if net=='3V3' and any(same(p,[2.275,6.5]) for p in pts):continue
            # R0's later reviewed refinement moved this drilled escape off C11.
            pts=[[4.95,p[1]] if same(p,[4.4,14.95]) else p for p in pts]
            transform=lambda p:[round(p[1]-.2625,6),round(-19-p[0],6)]
        elif all(-7<p[0]<7 and 34<p[1]<46.6 for p in pts):
            if any(same(p,c) for p in pts for c in old_c22):continue
            # This ground via belonged to the independently relocated C22.
            if route['kind']=='via' and any(same(pts[0],[c[0]+(1.15 if c[0]>0 else -1.15),c[1]]) for c in old_c22[1:]):continue
            transform=lambda p:[-p[0],p[1]];layer='F.Cu'
        elif all(-7<p[0]<7 and 47<p[1]<55.5 for p in pts):
            transform=lambda p:[-p[0],round(p[1]-3.6,6)];layer='F.Cu'
        if transform is None:continue
        if route['kind']=='via':route['position']=transform(pts[0])
        else:
            route['start'],route['end']=map(transform,pts)
            if layer:route['layer']=layer
        result.append(route)
    # Relocated feedback is left to the short local route stage rather than
    # dragging the old opposite-face fanout through new output copper.
    path('SYS',[pad('C21',1),[-4.6,43.8],[2.7,43.8],pad('C22',1)],.6,'F.Cu')
    # Motion's tied supplies and local bypass have moved to the handle.
    path('3V3',[pad('U7',6),pad('U7',7)],.15,'F.Cu')
    # The moved bay sits below the service header; remove three old ground
    # stitches that now intersect its front pads. Plane/short stitches are
    # restored from the actual free geometry during route completion.
    blocked_ground=[[7.0375,-18.8],[9.7375,-18.65],[11.5375,-22.1],[3.85,44.95]]
    revised=[]
    for route in result:
        pts=[route['position']] if route['kind']=='via' else [route['start'],route['end']]
        if route['net']=='GND' and any(same(p,q) for p in pts for q in blocked_ground):continue
        if route['net']=='VBUS_CHG' and any(same(p,[-23.75,-20.5]) for p in pts):continue
        for p in pts:
            if route['net']=='VBUS_CHG' and same(p,[-23.75,-20.5]):
                p[:]=[-24.5,-20.9]
            if route['net'] in ('MOTOR_P','MOTOR_N') and abs(p[0]+3.7)<.0001:
                p[0]=-1.8
        revised.append(route)
    result=revised
    record={'status':'Derived manual routing candidate; native DRC and placement review required',
        'placement_sha256':sha(placement_path),'baseline_board_sha256':sha(ROOT/'hardware/pcb/prototype-r0/buttplug-r0.kicad_pcb'),
        'bootstrap_generator_sha256':sha(module_path),'routes':result,
        'limits':['Widths and stackup are engineering candidates, not validated current or impedance ratings.','Ground drill-in-pad inventory and package-specific process acceptance remain required.']}
    write(output,record)


def placement_report(board_path, output):
    """Current routed poses for CAD, kept separate from frozen placement input."""
    import importlib.util
    spec=importlib.util.spec_from_file_location('r2_placement_source',ROOT/'tools/electronics_r2_place.py')
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    board=k.LoadBoard(str(board_path)); result=json.loads((PROJECT/'placement-report-r2.json').read_text())
    baseline={p['ref']:p for p in result['placements']}; boxes=[]; placements=[]; delta=[]
    candidates=json.loads((PROJECT/'layout-candidates-r0.json').read_text())['parts']
    for fp in board.GetFootprints():
        r=fp.GetReference();side='B' if fp.GetLayer()==k.B_Cu else 'F';height=candidates[r]['height_mm']
        pose={'ref':r,'xy_mm':mech(fp.GetPosition()),'native_angle_deg':fp.GetOrientationDegrees(),
              'side':side,'footprint':str(fp.GetFPID().GetLibItemName()),'height_mm':height}
        old=baseline[r]
        if any(pose[key]!=old[key] for key in ('xy_mm','native_angle_deg','side')):
            delta.append({'ref':r,'frozen_placement':{key:old[key] for key in ('xy_mm','native_angle_deg','side')},
                          'current_routed_pose':{key:pose[key] for key in ('xy_mm','native_angle_deg','side')}})
        placements.append(pose)
        boxes.append({'ref':r,'mpn':candidates[r]['mpn'],'side':side,
            'xy_bounds_mm':module.bbox(fp,[k.F_Fab,k.B_Fab]),
            'courtyard_xy_bounds_mm':module.bbox(fp,[k.F_CrtYd,k.B_CrtYd]),
            'z_bounds_mm':[-.5-height,-.5] if side=='B' else [.5,.5+height],
            'scope':'Conservative Fab/body projection and candidate height; excludes wires/solder/tolerances'})
    mates=[]
    for r,n in [('J1',2),('J3',2),('J5',4)]:
        fp=next(f for f in board.GetFootprints() if f.GetReference()==r)
        mp=[mech(p.GetPosition()) for p in fp.Pads() if p.GetNumber()=='MP']
        sg=[mech(p.GetPosition()) for p in fp.Pads() if p.GetNumber() not in ('','MP')]
        v=[sum(p[j] for p in mp)/len(mp)-sum(p[j] for p in sg)/len(sg) for j in [0,1]]
        length=math.hypot(*v);v=[round(z/length,6) for z in v];u=[-v[1],v[0]]
        x,y=mech(fp.GetPosition())
        if r=='J1':
            body=module.bbox(fp,[k.F_Fab,k.B_Fab]);center=[(body[0]+body[2])/2,(body[1]+body[3])/2]
            edge=max(a*v[0]+b*v[1] for a in [body[0],body[2]] for b in [body[1],body[3]])
            distance=edge-center[0]*v[0]-center[1]*v[1]
            mouth=[center[0]+distance*v[0],center[1]+distance*v[1]]
            points=[[mouth[0]+v[0]*a+u[0]*c,mouth[1]+v[1]*a+u[1]*c] for a in [0,2] for c in [-2.9,2.9]]
            zb=[.5,6.0];source='JST ePH.pdf; nominal 5.8 mm width and 2 mm extension beyond actual native Fab mouth edge'
        else:
            width=1.5 if n==2 else 2.5
            points=[[x+v[0]*a+u[0]*c,y+v[1]*a+u[1]*c] for a in [2.625,4.575] for c in [-width,width]]
            zb=[.5,3.45];source='JST eSH.pdf plus frozen placement candidate dimensions'
        mates.append({'ref':r,'mating_direction_xy':v,
            'plug_extension_xy_bounds_mm':[min(p[0] for p in points),min(p[1] for p in points),max(p[0] for p in points),max(p[1] for p in points)],
            'z_bounds_mm':zb,'source':source,
            'scope':'Conservative candidate mate; excludes wire bend and tolerances'})
    result.update({'status':'Current routed-candidate poses for mechanical review; routing DRC is recorded separately',
        'frozen_placement_sha256':sha(PROJECT/'placement-source-r2.kicad_pcb'),
        'board_sha256':sha(board_path),'project_sha256':sha(board_path.with_suffix('.kicad_pro')),
        'component_boxes':boxes,'placements':placements,'mated_connectors':mates,
        'placement_delta_from_frozen':delta,'tracks_and_vias':len(list(board.GetTracks()))})
    result.pop('native_DRC',None); result.pop('conservative_same_side_overlap_screen',None)
    write(output,result)
    write(PROJECT/'routed-placement-delta-r2.json',{'frozen_placement_sha256':result['frozen_placement_sha256'],
        'board_sha256':result['board_sha256'],'delta':delta,
        'reasons':json.loads((PROJECT/'routing-source-r2.json').read_text()).get('pose_override_reasons',{})})


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--board',type=Path,default=BOARD)
    parser.add_argument('--build',action='store_true')
    parser.add_argument('--derive-manual',type=Path,help='Read a frozen placement and write explicit manual-route JSON')
    parser.add_argument('--source',type=Path,default=PROJECT/'routing-source-r2.json')
    parser.add_argument('--manual',type=Path,default=PROJECT/'manual-routing-r2.json')
    parser.add_argument('--export-dsn',type=Path)
    parser.add_argument('--import-ses',type=Path)
    parser.add_argument('--drc',type=Path)
    parser.add_argument('--refine',type=Path)
    parser.add_argument('--geometry',type=Path)
    parser.add_argument('--report',type=Path)
    parser.add_argument('--audit',type=Path)
    args=parser.parse_args()
    if args.derive_manual: derive_manual(args.derive_manual,args.manual)
    if args.audit and not args.drc: parser.error('--audit requires --drc')
    if args.refine and not (args.build and args.import_ses): parser.error('--refine requires a fresh --build and --import-ses')
    if args.build: build(args.source,args.manual,args.board)
    if args.export_dsn: export_dsn(args.board,args.export_dsn)
    if args.import_ses: import_session(args.board,args.import_ses)
    if args.refine: refine_routes(args.board,args.refine,args.import_ses)
    if args.geometry: geometry_export(args.board,args.geometry)
    if args.drc: print(drc(args.board,args.drc))
    if args.audit: audit(args.board,args.drc,args.audit)
    if args.report: placement_report(args.board,args.report)

if __name__=='__main__': main()
