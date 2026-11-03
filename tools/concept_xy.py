"""Create the Concept 02 XY silhouette board, DXF and review drawing."""
from pathlib import Path
import html
import json
import math
import shutil
import uuid

ROOT = Path(__file__).resolve().parents[1]
C = json.loads((ROOT/'hardware/cad/concepts/layout-v2.json').read_text())
BOARD_DIR = ROOT/'hardware/pcb/concepts'
ASSETS = ROOT/'developer-docs/docs/assets/concept-v2'
ASSETS.mkdir(parents=True, exist_ok=True)
INK, BLUE, GREEN, ORANGE, PURPLE = '#213047', '#176bc1', '#26755b', '#b56612', '#7652ad'


def add(a,b): return (a[0]+b[0],a[1]+b[1])
def sub(a,b): return (a[0]-b[0],a[1]-b[1])
def mul(a,n): return (a[0]*n,a[1]*n)
def unit(a): return mul(a,1/math.hypot(*a))


def rounded_segments(vertices, radius):
    corners=[]
    for i,raw in enumerate(vertices):
        v=tuple(raw); before=tuple(vertices[i-1]); after=tuple(vertices[(i+1)%len(vertices)])
        u=unit(sub(before,v)); w=unit(sub(after,v))
        theta=math.acos(max(-1,min(1,u[0]*w[0]+u[1]*w[1])))
        trim=min(radius/math.tan(theta/2),math.dist(before,v)/3,math.dist(after,v)/3)
        actual_r=trim*math.tan(theta/2)
        center=add(v,mul(unit(add(u,w)),actual_r/math.sin(theta/2)))
        start=add(v,mul(u,trim)); end=add(v,mul(w,trim))
        midpoint=add(center,mul(unit(add(sub(start,center),sub(end,center))),actual_r))
        corners.append((start,midpoint,end,center,actual_r))
    segments=[]
    for i,(start,mid,end,center,r) in enumerate(corners):
        segments.append({'type':'line','start':corners[i-1][2],'end':start})
        segments.append({'type':'arc','start':start,'mid':mid,'end':end,'center':center,'radius':r})
    return segments


vertices=C['pcb']['outline_vertices_xy_mm']
x_bounds=[min(p[0] for p in vertices),max(p[0] for p in vertices)]
y_bounds=[min(p[1] for p in vertices),max(p[1] for p in vertices)]
assert math.isclose(x_bounds[1]-x_bounds[0],C['pcb']['crossbar_x_mm']), 'Crossbar dimension and vertices disagree'
assert math.isclose(y_bounds[1]-y_bounds[0],C['pcb']['overall_y_mm']), 'Overall Y dimension and vertices disagree'
assert math.isclose(C['pcb']['board_thickness_z_mm'],1), 'Update illustration Z positions when changing board thickness'
assert C['motor']['reserved_diameter_mm']==13 and C['motor']['pcb_gap_z_mm']==2, 'Update section geometry for changed motor reservation'
assert C['battery']['protected_pack_bay_xyz_mm']==[44,22,10] and C['battery']['pcb_gap_z_mm']==2 and C['battery']['populated_pcb_allocation_z_mm']==5, 'Update section geometry for changed pack reservation'
S=rounded_segments(vertices,C['pcb']['corner_radius_mm'])
for i,s in enumerate(S):
    assert math.dist(s['end'],S[(i+1)%len(S)]['start'])<1e-9, 'Unclosed outline'
    if s['type']=='arc':
        assert all(abs(math.dist(s[k],s['center'])-s['radius'])<1e-8 for k in ['start','mid','end'])


def fmt(p,offset=(0,0)):
    return f'{p[0]+offset[0]:.6f} {p[1]+offset[1]:.6f}'


thickness=float(C['pcb']['board_thickness_z_mm'])
assert thickness>0.07
pcb=['(kicad_pcb (version 20221018) (generator "codex_concept_xy")',
     f'  (general (thickness {thickness:.6f}))','  (paper "A4")',
     '  (layers (0 "F.Cu" signal) (31 "B.Cu" signal) (36 "B.SilkS" user "b.silkscreen") (37 "F.SilkS" user "f.silkscreen") (40 "Dwgs.User" user "user.drawings") (44 "Edge.Cuts" user))',
     '  (setup (stackup (layer "F.Cu" (type "copper") (thickness 0.035)) '
     f'(layer "dielectric 1" (type "core") (thickness {thickness-0.07:.6f}) (material "FR4")) '
     '(layer "B.Cu" (type "copper") (thickness 0.035))) (pad_to_mask_clearance 0))']
for i,s in enumerate(S):
    geometry=f'(start {fmt(s["start"],(100,50))}) '
    if s['type']=='arc': geometry+=f'(mid {fmt(s["mid"],(100,50))}) '
    geometry+=f'(end {fmt(s["end"],(100,50))})'
    stamp=uuid.uuid5(uuid.NAMESPACE_URL,f'buttplug-concept02-edge-{i}')
    pcb.append(f'  (gr_{s["type"]} {geometry} (stroke (width 0.05) (type default)) (layer "Edge.Cuts") (tstamp {stamp}))')
for i,(value,y) in enumerate([('CONCEPT 02 - XY OUTLINE ONLY',42),('DIMENSIONS UNAPPROVED - NO ELECTRICAL LAYOUT',46),('X = HANDLE / Y = TIP / Z = BOARD NORMAL',139)]):
    stamp=uuid.uuid5(uuid.NAMESPACE_URL,f'buttplug-concept02-note-{i}')
    pcb.append(f'  (gr_text "{value}" (at 100 {y}) (layer "Dwgs.User") (tstamp {stamp}) (effects (font (size 1 1) (thickness 0.15))))')
pcb.append(')')
(BOARD_DIR/'xy-outline-concept.kicad_pcb').write_text('\n'.join(pcb)+'\n')

dxf=['0','SECTION','2','HEADER','9','$ACADVER','1','AC1015','9','$INSUNITS','70','4','0','ENDSEC','0','SECTION','2','ENTITIES']
for s in S:
    if s['type']=='line':
        dxf+=['0','LINE','8','PCB_OUTLINE','10',str(s['start'][0]),'20',str(s['start'][1]),'30','0','11',str(s['end'][0]),'21',str(s['end'][1]),'31','0']
    else:
        def angle(p): return math.degrees(math.atan2(p[1]-s['center'][1],p[0]-s['center'][0]))%360
        a,b,m=angle(s['start']),angle(s['end']),angle(s['mid'])
        if (m-a)%360>(b-a)%360: a,b=b,a
        dxf+=['0','ARC','8','PCB_OUTLINE','10',str(s['center'][0]),'20',str(s['center'][1]),'30','0','40',str(s['radius']),'50',str(a),'51',str(b)]
dxf+=['0','ENDSEC','0','EOF']
(BOARD_DIR/'xy-outline-concept.dxf').write_text('\n'.join(dxf)+'\n')

bits=['<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="1040" viewBox="0 0 1400 1040">',
      '<title>Concept 02 — one T-shaped PCB in the toy XY plane</title>',
      '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto-start-reverse"><path d="M0 0 L8 4 L0 8" fill="context-stroke"/></marker></defs>',
      '<rect width="1400" height="1040" fill="white"/>']


def text(x,y,s,size=21,color=INK,weight='normal',anchor='start'):
    for i,line in enumerate(s.split('\n')):
        bits.append(f'<text x="{x}" y="{y+i*size*1.35}" font-family="Arial, sans-serif" font-size="{size}" fill="{color}" font-weight="{weight}" text-anchor="{anchor}">{html.escape(line)}</text>')


def rect(x,y,w,h,fill='#f5f7fa',stroke='#d8dfeb',r=15,dash=False,opacity=1):
    bits.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" fill-opacity="{opacity}" stroke="{stroke}" stroke-width="2"'+(' stroke-dasharray="7 5"' if dash else '')+'/>')


def line(points,color=INK,arrow=False,dash=False):
    bits.append('<polyline points="'+' '.join(f'{x},{y}' for x,y in points)+f'" fill="none" stroke="{color}" stroke-width="2"'+(' marker-end="url(#arrow)"' if arrow else '')+(' stroke-dasharray="6 5"' if dash else '')+'/>')


def profile_path(ox,oy,scale):
    def p(t): return f'{ox+t[0]*scale:.4f},{oy+t[1]*scale:.4f}'
    out=[f'M{p(S[0]["start"])}']
    for s in S:
        if s['type']=='line': out.append(f'L{p(s["end"])}')
        else:
            a=sub(s['start'],s['center']);b=sub(s['end'],s['center'])
            sweep=1 if a[0]*b[1]-a[1]*b[0]>0 else 0
            out.append(f'A{s["radius"]*scale:.4f},{s["radius"]*scale:.4f} 0 0 {sweep} {p(s["end"])}')
    return ' '.join(out)+' Z'


text(34,56,'Concept 02 / PCB follows the toy’s XY silhouette',36,INK,'bold')
text(36,95,'One continuous T-shaped board · X across the handle · Y toward the tip · Z normal to the board',21,'#57657a')
rect(30,135,690,730);rect(750,135,620,730)
text(55,178,'XY plan — look along Z',26,BLUE,'bold')
text(776,178,'YZ section — look along X',26,BLUE,'bold')
text(776,208,'Board, pack and motor occupy separate Z volumes.',18)

ox,oy,scale=330,260,5
# The outer contour is illustrative and intentionally carries no product dimensions.
toy=[(-40,-5),(40,-5),(40,23),(10,23),(10,34),(18,48),(18,74),(8,95),(-8,95),(-18,74),(-18,48),(-10,34),(-10,23),(-40,23)]
bits.append('<polygon points="'+' '.join(f'{ox+x*scale},{oy+y*scale}' for x,y in toy)+f'" fill="#f4effa" stroke="{PURPLE}" stroke-width="2" stroke-dasharray="7 5"/>')
bits.append(f'<path d="{profile_path(ox,oy,scale)}" fill="#c6e1ff" stroke="{BLUE}" stroke-width="3"/>')
bx,by=C['battery']['projection_min_xy_mm'];bw,bh,bz=C['battery']['protected_pack_bay_xyz_mm']
rect(ox+bx*scale,oy+by*scale,bw*scale,bh*scale,'#b3dfc8',GREEN,7,True,0.48)
text(300,306,'PACK IN +Z',17,GREEN,'bold',anchor='middle')
rect(ox+20*scale,oy,12.5*scale,18*scale,'none',ORANGE,5,True)
text(461,302,'RF',18,ORANGE,'bold')
my=C['motor']['projection_start_y_mm'];md=C['motor']['reserved_diameter_mm'];ml=C['motor']['reserved_y_mm']
rect(ox-md*scale/2,oy+my*scale,md*scale,ml*scale,'#f5cca0',ORANGE,16,True,0.38)
text(330,555,'MOTOR',15,ORANGE,'bold',anchor='middle')
text(330,578,'IN +Z',15,ORANGE,anchor='middle')
sx,sy=C['tip_sensor']['projection_min_xy_mm']
rect(ox+sx*scale,oy+sy*scale,30,40,'#f5dba9',ORANGE,4)
line([(330,675),(338,684),(323,689),(330,690)],ORANGE)
text(534,274,'Crossbar',20,BLUE,'bold');text(534,301,'Radio, power,',17);text(534,324,'controls',17)
line([(493,285),(522,285)],BLUE)
text(534,400,'Supported neck',19,BLUE,'bold');text(534,425,'10 mm study width',16)
line([(356,390),(519,390)],BLUE)
text(534,502,'Motor projection',18,ORANGE,'bold');text(534,526,'Above the PCB in Z',16)
line([(364,500),(521,500)],ORANGE)
text(534,606,'Blue = PCB tongue',18,BLUE,'bold');text(534,631,'No motor cutout',16)
line([(379,605),(520,605)],BLUE)
text(534,716,'Wired tip island',18,ORANGE,'bold');line([(347,710),(520,710)],ORANGE)
line([(167.5,225),(492.5,225)],INK);line([(167.5,218),(167.5,231)],INK);line([(492.5,218),(492.5,231)],INK)
text(330,216,f'{C["pcb"]["crossbar_x_mm"]:g} mm PCB crossbar — provisional',16,anchor='middle')
line([(108,260),(108,675)],INK);line([(101,260),(115,260)],INK);line([(101,675),(115,675)],INK)
text(64,470,f'{C["pcb"]["overall_y_mm"]:g} mm',16,anchor='middle');text(64,494,'PCB length',14,anchor='middle')
text(55,789,'Dashed green/orange shapes are projections of parts in +Z.',17,'#57657a')
text(55,817,'Purple contour is illustrative; it is not a released toy outline.',17,'#57657a')

# Z=0 is the board midplane. Y matches the plan view.
z0,y0=918,260
rect(z0-2.5,y0,5,83*5,'#c6e1ff',BLUE,0)
rect(z0-22.5,y0,20,18*5,'#9ac4ef',BLUE,2)
rect(z0+12.5,y0-2*5,10*5,22*5,'#b3dfc8',GREEN,6)
rect(z0+12.5,y0+my*5,md*5,ml*5,'#f5cca0',ORANGE,17)
line([(z0,232),(z0+140,232)],INK,True);text(z0+146,238,'+Z',18)
line([(z0,260),(z0,744)],BLUE,False,True)
text(1050,280,'Battery bay',22,GREEN,'bold')
text(778,286,'4 mm parts',17,BLUE,'bold');text(778,311,'on −Z side',16)
line([(873,295),(893,295)],BLUE)
text(1050,309,'10 mm in Z',19);text(1050,336,'2 mm gap to board',18)
line([(981,300),(1035,300)],GREEN)
text(1050,470,'Motor sleeve',22,ORANGE,'bold')
text(1050,499,'Ø13 mm reservation',18);text(1050,526,'2 mm separation',18)
line([(997,520),(1035,520)],ORANGE)
text(780,645,'1 mm PCB',18,BLUE,'bold');line([(890,638),(914,638)],BLUE)
text(776,721,'Motor overlap:',20,INK,'bold')
text(776,750,'13 motor + 2 gap + 1 PCB = 16 mm internal Z',19)
text(776,792,'Base overlap:',20,INK,'bold')
text(776,821,'10 pack + 2 gap + 5 PCB assembly = 17 mm',19)
rect(30,892,1340,114,'#fff5e6','#efcf98')
text(54,925,'The board follows an inward-offset carrier cavity, not the outer silicone skin.',23,ORANGE,'bold')
text(54,955,'All dimensions are study inputs. Z totals exclude carrier, silicone, adhesives, tolerances and actual part clearances.',19)
text(54,983,'KiCad / DXF outputs contain a rounded board outline only. No electrical layout, fit or fabrication validation.',19)
bits.append('</svg>')
svg=ROOT/'hardware/cad/concepts/layout-v2.svg'
svg.write_text('\n'.join(bits)+'\n')
shutil.copy2(svg,ASSETS/svg.name)

report={'revision':'concept-02', 'outline_segments':len(S), 'outline_closed_analytically':True,
        'board_nominal_bounds_xy_mm':{'x':x_bounds,'y':y_bounds},
        'motor_internal_z_mm':C['motor']['reserved_diameter_mm']+C['motor']['pcb_gap_z_mm']+C['pcb']['board_thickness_z_mm'],
        'battery_internal_z_mm':C['battery']['protected_pack_bay_xyz_mm'][2]+C['battery']['pcb_gap_z_mm']+C['battery']['populated_pcb_allocation_z_mm'],
        'status':'Local stack and profile arithmetic only; no fit, circuit or product validation'}
(ROOT/'hardware/design/concept-results-v2.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
