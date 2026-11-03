"""Review renders from stable, owner-exported R2 STL geometry.

Uses actual binary native mesh exports, including native section exports. No
triangle clipping, invented cut faces, assembly-clearance inference or image
generation is performed. Exploded translations are display offsets only.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import struct
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, PngImagePlugin

ROOT = Path(__file__).resolve().parents[1]
CAD = ROOT / 'hardware/cad/prototype-r2'
OUT = ROOT / 'developer-docs/docs/assets/prototype-r2'
FONT = '/System/Library/Fonts/Supplemental/Arial.ttf'
BOLD = '/System/Library/Fonts/Supplemental/Arial Bold.ttf'
INK = '#243449'
MUTED = '#5b6c7e'
AMBER = '#975d15'
LIGHT = np.array([-.4, .7, 1.0]); LIGHT /= np.linalg.norm(LIGHT)

ROLES = {
    'lower': 'MetalShellLower',
    'upper': 'MetalShellUpper',
    'cap': 'FemaleNoseCap',
    'bolt': 'RearClampBolt',
    'nut': 'RearClampNut',
    'core': 'PolymerFlangeCore',
    'bridge': 'PolymerCaptureBridge',
    'rubber': 'ElastomerFlangeCoverLower',
    'rubber_upper': 'ElastomerFlangeCoverUpper',
    'cover': 'ServiceCoverWithDockPorts',
    'carrier': 'CarrierWithTipStrainRelief',
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def label(draw, xy, value, size=22, bold=False, fill=INK):
    draw.multiline_text(xy, value,
                        font=ImageFont.truetype(BOLD if bold else FONT, size),
                        fill=fill, spacing=7)


def part_color(name):
    if name in (ROLES['lower'], ROLES['upper']): return (181, 192, 205)
    if name == ROLES['cap']: return (153, 170, 189)
    if name.startswith('ElastomerFlangeCover'): return (62, 82, 107)
    if name in (ROLES['core'], ROLES['bridge'], ROLES['cover']): return (86, 115, 144)
    if name in (ROLES['bolt'], ROLES['nut']): return (187, 145, 85)
    if any(s in name for s in ('TBoard', 'TipPCB', 'PlacedComponent')): return (54, 139, 93)
    if any(s in name for s in ('Gasket', 'Seal', 'Tape', 'Liner')): return (47, 141, 113)
    if any(s in name for s in ('Corridor', 'Lead', 'Splice', 'Wire')): return (85, 145, 155)
    if 'Motor' in name: return (211, 153, 64)
    if 'Pack' in name: return (84, 155, 192)
    if any(s in name for s in ('Carrier', 'CaptureFork')): return (211, 209, 186)
    if any(s in name for s in ('Tip', 'Temperature')): return (153, 109, 157)
    return (115, 126, 140)


class NativeMeshes:
    def __init__(self, cad, suffix='', report=None):
        self.cad = cad
        self.suffix = suffix
        self.cache = {}
        self.used = {}
        self.expected = {}
        self.empty_sections = set()
        if report:
            self.expected={v['path']:v['sha256'] for files in report['canonical_exports'].values() for v in files.values()}
            self.empty_sections={n for n,v in report.get('native_section_volumes_mm3',{}).items() if v <= 1e-9}

    def load(self, name, section=False, require_section=False):
        section_path = self.cad / (name + '-section' + self.suffix + '.stl')
        path = section_path if section and section_path.exists() else self.cad / (name + self.suffix + '.stl')
        if require_section and path != section_path:
            raise ValueError('Owner-exported native section is required: ' + str(section_path))
        if path not in self.cache:
            data = path.read_bytes()
            if self.expected:
                assert path.name in self.expected and hashlib.sha256(data).hexdigest()==self.expected[path.name], 'Canonical export mismatch: '+str(path)
            if len(data) < 84:
                raise ValueError('Expected native binary STL: ' + str(path))
            count = struct.unpack_from('<I', data, 80)[0]
            if len(data) != 84 + 50 * count or count == 0:
                raise ValueError('Empty or invalid native binary STL: ' + str(path))
            dtype = np.dtype([('normal', '<f4', (3,)), ('vertices', '<f4', (3, 3)), ('attr', '<u2')])
            triangles = np.frombuffer(data, dtype=dtype, offset=84)['vertices'].astype(float)
            if not np.isfinite(triangles).all():
                raise ValueError('Non-finite mesh vertices: ' + str(path))
            self.cache[path] = triangles
            self.used[path.name] = hashlib.sha256(data).hexdigest()
        return self.cache[path]

    def verify(self):
        assert all(sha(self.cad/name) == value for name,value in self.used.items()), 'Mesh export changed during rendering'


def camera_basis(camera):
    camera = np.array(camera, dtype=float); camera /= np.linalg.norm(camera)
    right = np.cross([0, 1, 0], camera)
    if np.linalg.norm(right) < 1e-8:
        right = np.cross([0, 0, 1], camera)
    right /= np.linalg.norm(right)
    up = np.cross(camera, right)
    return camera, right, up


def panel(canvas, box, title, subtitle, geometry, *, camera=(1.05, .16, 1.75),
          side_labels=False, focus_bounds=None):
    """Project unchanged source triangles, apart from explicit exploded offsets."""
    draw = ImageDraw.Draw(canvas); x, y, w, h = box
    draw.rounded_rectangle((x, y, x+w, y+h), radius=18,
                           fill='#f5f7fa', outline='#dbe3ec', width=2)
    label(draw, (x+24, y+20), title, 25, True)
    label(draw, (x+24, y+63), subtitle, 19, fill=MUTED)
    cam, right, up = camera_basis(camera)
    all_vertices = (np.array(list(itertools.product(*zip(*focus_bounds))))
                    if focus_bounds else np.concatenate([a.reshape(-1, 3) for _, a, _ in geometry]))
    u, v = all_vertices @ right, all_vertices @ up
    margin = 285 if side_labels else 40
    fit_w, fit_h = w-2*margin, h-155
    scale = min(fit_w / np.ptp(u), fit_h / np.ptp(v))
    cx = x+w/2-(u.max()+u.min())/2*scale
    cy = y+103+(h-125)/2+(v.max()+v.min())/2*scale
    faces = []; anchors = {}
    for name, triangles, role in geometry:
        normals = np.cross(triangles[:, 1]-triangles[:, 0], triangles[:, 2]-triangles[:, 0])
        lengths = np.linalg.norm(normals, axis=1)
        normals /= np.maximum(lengths[:, None], 1e-12)
        shade = .58+.42*np.maximum(normals @ LIGHT, 0)
        pts = np.stack((cx+triangles @ right*scale, cy-triangles @ up*scale), axis=-1)
        for i in np.flatnonzero(normals @ cam > 0):
            color = tuple(int(c*shade[i]) for c in part_color(name))
            faces.append((float(triangles[i].mean(axis=0) @ cam), pts[i], color))
        if role:
            flat = pts.reshape(-1, 2)
            center = (flat.max(axis=0)+flat.min(axis=0))/2
            # Anchor the callout to an actual source vertex, not empty cavity.
            anchors[role] = flat[np.argmin(np.linalg.norm(flat-center, axis=1))]
    # A viewport crop clips only the image, never source mesh vertices. This
    # supports honest close views without fabricating section surfaces.
    raster = Image.new('RGB', canvas.size, '#f5f7fa'); face_draw=ImageDraw.Draw(raster)
    for _, points, color in sorted(faces, key=lambda face: face[0]):
        face_draw.polygon([tuple(p) for p in points], fill=color)
    viewport = (x+6, y+106, x+w-6, y+h-24)
    canvas.paste(raster.crop(viewport), viewport[:2])
    return anchors


def callouts(canvas, anchors, box):
    x, y, w, h = box; draw = ImageDraw.Draw(canvas)
    descriptions = {
        'upper': 'Upper metal half', 'lower': 'Lower metal half',
        'cap': 'Female nose cap', 'core': 'Rigid polymer core',
        'bridge': 'Upper capture bridge', 'rubber': 'Elastomer cover study',
        'bolt': 'Rear clamp bolt', 'nut': 'Rear clamp nut',
        'carrier': 'Internal module\nUnselected battery bay',
    }
    # Fixed side assignments keep short, readable leaders outside the mesh area.
    sides = {'upper': 'left', 'lower': 'right', 'cap': 'right', 'core': 'right',
             'bridge': 'left', 'rubber': 'left', 'bolt': 'left', 'nut': 'right',
             'carrier': 'right'}
    for side in ('left', 'right'):
        roles = sorted((r for r in anchors if sides.get(r) == side), key=lambda r: anchors[r][1])
        ideal = [float(anchors[r][1]) for r in roles]
        low, high, separation = y+145, y+h-80, 103
        positions = []
        for target in ideal:
            positions.append(max(target, low if not positions else positions[-1]+separation))
        if positions and positions[-1] > high:
            positions = [p-(positions[-1]-high) for p in positions]
        if positions and positions[0] < low:
            positions = list(np.linspace(low, high, len(positions)))
        for role, ty in zip(roles, positions):
            tx = x+25 if side == 'left' else x+w-258
            edge_x = tx+238 if side == 'left' else tx-10
            a = tuple(float(v) for v in anchors[role])
            draw.line([a, (edge_x, ty+13)], fill='#6b7c8f', width=2)
            draw.ellipse((a[0]-3, a[1]-3, a[0]+3, a[1]+3), fill='#42586f')
            draw.rounded_rectangle((tx-5, ty-5, tx+237, ty+65), radius=5, fill='#f5f7fa')
            label(draw, (tx, ty), descriptions[role], 20, True)


def geometry(meshes, names, *, section=False, offsets=None):
    offsets = offsets or {}; values = []; roles_by_name = {v:k for k,v in ROLES.items()}
    for name in names:
        # Upper shell and service coverings are deliberately removed in the
        # internal view. All remaining cuts come from native section STL files.
        if section and name in (ROLES['upper'], ROLES['rubber'], ROLES['rubber_upper'], ROLES['cover']):
            continue
        use_section = section and name in (
            ROLES['lower'], ROLES['cap'], ROLES['core'], ROLES['bridge'], ROLES['carrier'])
        if use_section and name in meshes.empty_sections:
            continue
        triangles = meshes.load(name, use_section,
                               require_section=use_section and name in (ROLES['cap'], ROLES['core']))
        if name in offsets:
            triangles = triangles + np.asarray(offsets[name], dtype=float)
        values.append((name, triangles, roles_by_name.get(name)))
    return values


def dimension_line(parameters):
    items = []
    for key, title, suffix in [('body_length', 'Body', 'mm'),
                               ('body_max_diameter', 'max Ø', 'mm'),
                               ('neck_outer_diameter', 'neck Ø', 'mm'),
                               ('flange_depth', 'flange depth', 'mm')]:
        if key in parameters:
            value = float(parameters[key]); items.append(f'{title} {value:g} {suffix}')
    return ' · '.join(items)


def repack_line(parameters):
    status=(parameters.get('electronics_status','')+' '+parameters.get('release_state','')).lower()
    if any(word in status for word in ('incomplete','conflict','repack pending')):
        return 'Electrical repack is incomplete; internal boxes show relocation conflicts.'
    return 'Geometry reservations do not establish actual-part fit or a completed physical assembly.'


def save(canvas, path, meshes, report_path, parameters_path, native_path):
    meshes.verify()
    meta = PngImagePlugin.PngInfo()
    meta.add_text('Scope', 'Actual native STL geometry; development review only. Exploded positions are illustration offsets, not an assembly path.')
    meta.add_text('SourceHashes', json.dumps({
        'native_sha256': sha(native_path), 'geometry_report_sha256': sha(report_path),
        'parameters_sha256': sha(parameters_path), 'renderer_sha256': sha(Path(__file__)),
        'meshes_sha256': meshes.used}, sort_keys=True))
    canvas.save(path, pnginfo=meta)
    print(path)


def checkpoint(cad, expected_sha):
    """Exterior-only checkpoint; no absent fastener/thread/fit result is added."""
    report_path=cad/'exterior-checkpoint-report.json'
    parameters_path=cad/'exterior-checkpoint-parameters.json'
    native_path=cad/'exterior-checkpoint.FCStd'
    report=json.loads(report_path.read_text()); parameters=json.loads(parameters_path.read_text())
    assert sha(native_path)==expected_sha==report['native_sha256']
    assert sha(parameters_path)==report['parameters_sha256'], 'Checkpoint parameter snapshot differs from its report'
    waist=report['waist']; assert float(waist['target_od_mm'])==15
    names=list(report['parts'])
    assert all(part['valid'] for part in report['parts'].values())
    required=('MetalShellLower','MetalShellUpper','FemaleNoseCap','TBoardReservation')
    assert all(name in names for name in required)
    meshes=NativeMeshes(cad,'-exterior-checkpoint'); OUT.mkdir(parents=True,exist_ok=True)
    exterior=[n for n in names if n!='TBoardReservation']
    closed=geometry(meshes,exterior)
    ring_names=('MetalShellLower','MetalShellUpper','TBoardReservation')
    ring=[(n,meshes.load(n+'-waist'),None) for n in ring_names]
    all_ring=np.concatenate([a.reshape(-1,3) for _,a,_ in ring])
    ylo,yhi=all_ring[:,1].min(),all_ring[:,1].max()
    neck=float(waist['target_od_mm']); bore=float(waist['bore_mm']); board=float(waist['proposed_board_width_mm'])
    canvas=Image.new('RGB',(1800,1160),'white');draw=ImageDraw.Draw(canvas)
    label(draw,(36,25),'R2 / selected 15 mm neck checkpoint',37,True)
    label(draw,(37,83),'Actual native exterior meshes · split metal body · plain cap · joints and internal repack incomplete',23,fill=MUTED)
    panel(canvas,(30,140,855,770),'EXTERIOR / selected slimmer waist',
          'Plain cap reservation; thread and rear bolt not modeled',closed)
    panel(canvas,(915,140,855,770),'WAIST / actual native section',
          f'Y {ylo:g}–{yhi:g} mm · proposed bare centered PCB',ring,camera=(0,1,0))
    draw=ImageDraw.Draw(canvas)
    label(draw,(37,946),f'Selected neck Ø{neck:g} mm target · Ø{bore:g} mm study bore · {board:g} mm component-free PCB waist proposal',25,True)
    label(draw,(37,994),'Silver: actual shell section · green: bare-board proposal. Populated electrical fit is incomplete.',22,fill=MUTED)
    label(draw,(37,1042),'Thread, rear clamp, registration, sealing and strength are not established by this checkpoint.',23,True,fill=AMBER)
    label(draw,(37,1092),'A smaller waist does not establish comfort, anatomical fit or any safe wear duration.',22,fill=MUTED)
    save(canvas,OUT/'mechanical-r2-checkpoint.png',meshes,report_path,parameters_path,native_path)

    reach=max(neck*.9,10.0); end_y=float(waist['axial_span_y_mm'][1])
    focus=((-reach,-5,-reach),(reach,end_y+12,reach))
    canvas=Image.new('RGB',(1800,1120),'white');draw=ImageDraw.Draw(canvas)
    label(draw,(36,25),'R2 / selected 15 mm waist profile',37,True)
    label(draw,(37,83),'Actual exterior checkpoint meshes · orthographic camera crops · no replacement surface geometry',23,fill=MUTED)
    panel(canvas,(30,140,855,760),'FRONT / X–Y profile','Selected 15 mm neck target; root blend retained',
          closed,camera=(0,0,1),focus_bounds=focus)
    panel(canvas,(915,140,855,760),'SIDE / Z–Y profile','Selected 15 mm neck target; root blend retained',
          closed,camera=(1,0,0),focus_bounds=focus)
    draw=ImageDraw.Draw(canvas)
    label(draw,(37,936),f'Neck span Y {waist["axial_span_y_mm"][0]:g}–{end_y:g} mm · root blend R{waist["root_blend_radius_mm"]:g} mm · {board:g} mm bare-board waist proposal',25,True)
    label(draw,(37,986),'Exterior-only checkpoint: thread, rear bolt, seals and populated internal repack are incomplete.',23,True,fill=AMBER)
    label(draw,(37,1037),'No comfort, wear-duration, strength or sealing result follows from these views.',22,fill=MUTED)
    save(canvas,OUT/'mechanical-r2-checkpoint-neck.png',meshes,report_path,parameters_path,native_path)
    assert sha(native_path)==expected_sha and sha(parameters_path)==report['parameters_sha256']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cad', type=Path, default=CAD)
    parser.add_argument('--expected-native-sha', required=True,
                        help='Stable native SHA256 supplied by the geometry owner before rendering')
    parser.add_argument('--checkpoint',action='store_true',help='Render the frozen exterior-only checkpoint, without assuming full assembly parts')
    args = parser.parse_args(); cad = args.cad
    if args.checkpoint:
        checkpoint(cad,args.expected_native_sha); return
    report_path = cad/'geometry-report.json'; parameters_path = cad/'parameters.json'
    native_path = cad/'ButtplugPrototypeR2.FCStd'
    assert sha(native_path) == args.expected_native_sha, 'Native source changed; obtain a stable export snapshot first'
    report = json.loads(report_path.read_text()); parameters = json.loads(parameters_path.read_text())
    bay_note=' × '.join(f'{float(v):g}' for v in parameters['pack_reservation_xyz'])
    assert float(parameters['neck_outer_diameter']) == 15.0, 'R2 renderer expects the selected 15 mm neck target, not an older neck candidate'
    assert report['native_sha256'] == args.expected_native_sha, 'Report and native snapshot differ'
    assert sha(parameters_path) == report['source_inputs']['parameters_sha256'], 'Full-R2 parameters changed after export'
    names = report.get('visible_final_objects', report.get('native_view_state', {}).get('visible_final_objects'))
    assert names, 'No final native object inventory in report'
    assert all(n in report['parts'] for n in names)
    required = [ROLES[r] for r in ('lower','upper','cap','bolt','nut','core','bridge','rubber','rubber_upper','carrier')]
    assert all(n in names for n in required), 'Final R2 role names need coordination with the geometry owner'
    meshes = NativeMeshes(cad, report=report); OUT.mkdir(parents=True, exist_ok=True)

    closed = [n for n in names if n in [ROLES[r] for r in ('lower','upper','cap','rubber','rubber_upper','cover','bolt','nut')]
              or n in ('SiliconeButtonBootReservations','DockContactReservations','ButtonCaptureCollars')]
    canvas = Image.new('RGB', (1800, 1230), 'white'); draw = ImageDraw.Draw(canvas)
    label(draw, (36, 25), 'R2 / 15 mm neck — joint and carrier study', 35, True)
    label(draw, (37, 83), 'Actual native meshes · split shell / threaded cap / rear clamp · unqualified engineering geometry', 23, fill=MUTED)
    panel(canvas, (30, 140, 855, 800), 'CLOSED / exterior study',
          'Material and finished seam remain unqualified', geometry(meshes, closed))
    panel(canvas, (915, 140, 855, 800), 'SECTION / internal packaging',
          'Upper shell and service coverings removed', geometry(meshes, names, section=True))
    draw = ImageDraw.Draw(canvas)
    label(draw, (37, 974), dimension_line(parameters), 25, True)
    label(draw, (37, 1022), 'Green PCB · blue battery bay — unselected · gold motor · beige carrier · teal wire / seal reservations', 22, fill=MUTED)
    conflicts=report['static_screen_summary']['unintended_positive_intersection_count']
    groups=report['carrier']['solids']
    if conflicts:
        failure=f'{conflicts} reported static overlaps; lower carrier has {groups} solid groups.'
    else:
        module=report['parts'].get('RemovableMotorTipCarrier',{}).get('solids')
        failure=f'No reported static overlaps · lower carrier {groups} solid'
        if module is not None:
            failure+=f' · removable motor/tip module {module} solid'
        failure+='.'
    label(draw, (37, 1072), failure, 23, True, fill=AMBER)
    label(draw, (37, 1120), 'Thread fit, strength, sealing, materials, cleaning and body-contact use remain unqualified.', 23, True, fill=AMBER)
    save(canvas, OUT/'mechanical-r2.png', meshes, report_path, parameters_path, native_path)

    offsets = {
        ROLES['upper']: (0, 0, 30), ROLES['lower']: (0, 0, -29),
        ROLES['cap']: (0, 24, 0), ROLES['core']: (0, -22, 0),
        ROLES['bridge']: (0, -8, 44), ROLES['rubber']: (0, -53, -18),
        ROLES['rubber_upper']: (0, -53, 18),
        ROLES['bolt']: (0, 0, 57), ROLES['nut']: (0, 0, -52),
        ROLES['cover']: (0, -53, 0),
    }
    exploded_names = [n for n in names if not n.startswith(('CoverBolt','CoverNut'))]
    canvas = Image.new('RGB', (1800, 1350), 'white'); draw = ImageDraw.Draw(canvas)
    label(draw, (36, 25), 'R2 / development checkpoint — parts and supports', 35, True)
    label(draw, (37, 83), 'Actual exported parts · display offsets only; these positions do not prove an assembly motion', 23, fill=MUTED)
    box = (30, 140, 1740, 970)
    anchors = panel(canvas, box, 'EXPLODED / parts and reference contents',
                    'Two metal halves · female cap · rear bolt · rigid core / bridge · elastomer-cover study',
                    geometry(meshes, exploded_names, offsets=offsets), side_labels=True)
    callouts(canvas, anchors, box)
    draw = ImageDraw.Draw(canvas)
    label(draw, (37, 1142), 'Rear clamp and nose-cap retention geometry are modeled; load capacity and assembly remain unqualified.', 23)
    label(draw, (37, 1190), 'Unselected '+bay_note+' mm battery bay. '+failure, 20, fill=MUTED)
    label(draw, (37, 1240), 'Sealing, thread fit, strength, finishing and physical assembly remain unqualified.', 23, True, fill=AMBER)
    save(canvas, OUT/'mechanical-r2-exploded.png', meshes, report_path, parameters_path, native_path)

    # Orthographic views of the actual waist. The framing uses final parameter
    # values; no previous neck candidate or hand-drawn replacement is shown.
    neck=float(parameters['neck_outer_diameter']); neck_length=float(parameters['neck_length'])
    reach=max(neck*.9, 10.0)
    focus=((-reach,-5,-reach),(reach,neck_length+12,reach))
    canvas=Image.new('RGB',(1800,1120),'white'); draw=ImageDraw.Draw(canvas)
    label(draw,(36,25),'R2 / development waist inspection',37,True)
    waist=parameters.get('pcb_waist_width',parameters.get('pcb_neck_width'))
    board_note=f' · {float(waist):g} mm component-free PCB waist' if waist is not None else ''
    label(draw,(37,83),f'Selected neck Ø{neck:g} mm target{board_note} · actual native mesh geometry',23,fill=MUTED)
    closed_geometry=geometry(meshes,closed)
    panel(canvas,(30,140,855,760),'FRONT / X–Y profile','Camera crop only; complete source surfaces retained',
          closed_geometry,camera=(0,0,1),focus_bounds=focus)
    panel(canvas,(915,140,855,760),'SIDE / Z–Y profile','Camera crop only; complete source surfaces retained',
          closed_geometry,camera=(1,0,0),focus_bounds=focus)
    draw=ImageDraw.Draw(canvas)
    label(draw,(37,936),dimension_line(parameters),25,True)
    label(draw,(37,986),failure+' Fit, comfort and wear remain unvalidated.',23,True,fill=AMBER)
    label(draw,(37,1037),'No anatomy, pressure, sealing or thread-strength result is established by these views.',22,fill=MUTED)
    save(canvas,OUT/'mechanical-r2-neck.png',meshes,report_path,parameters_path,native_path)
    assert sha(native_path) == args.expected_native_sha, 'Native source changed during render; images need a stable rerun'


if __name__ == '__main__':
    main()
