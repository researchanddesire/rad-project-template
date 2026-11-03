"""Render editable engineering concept SVGs from the concept inputs."""
import html
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT/'developer-docs/docs/assets/concept-v1'
ASSETS.mkdir(parents=True, exist_ok=True)
layout = json.loads((ROOT/'hardware/cad/concepts/layout-v1.json').read_text())
results = json.loads((ROOT/'hardware/design/concept-results-v1.json').read_text())
INK, BLUE, GREEN, ORANGE, PURPLE = '#213047', '#176bc1', '#26755b', '#a15a08', '#7652ad'


class Drawing:
    def __init__(self, height, title):
        self.bits = [f'<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="{height}" viewBox="0 0 1400 {height}">',
                     f'<title>{html.escape(title)}</title>',
                     '<defs><marker id="arrow" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto-start-reverse"><path d="M0 0 L9 4.5 L0 9" fill="context-stroke"/></marker></defs>',
                     '<rect width="100%" height="100%" fill="#fff"/>']

    def rect(self, x,y,w,h,fill='#f5f7fa',stroke='#d8dfeb',radius=16,dash=False):
        self.bits.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="2"'+(' stroke-dasharray="7 5"' if dash else '')+'/>')

    def text(self,x,y,s,size=21,color=INK,weight='normal',anchor='start'):
        for i,line in enumerate(s.split('\n')):
            self.bits.append(f'<text x="{x}" y="{y+i*size*1.35}" font-family="Arial, sans-serif" font-size="{size}" font-weight="{weight}" fill="{color}" text-anchor="{anchor}">{html.escape(line)}</text>')

    def line(self,points,color=BLUE,arrow=False,dash=False):
        self.bits.append('<polyline points="'+' '.join(f'{x},{y}' for x,y in points)+f'" fill="none" stroke="{color}" stroke-width="2.5"'+(' marker-end="url(#arrow)"' if arrow else '')+(' stroke-dasharray="6 5"' if dash else '')+'/>')

    def circle(self,x,y,r,fill,stroke=INK):
        self.bits.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')

    def node(self,x,y,w,h,title,body,fill='#eaf3ff',color=BLUE):
        self.rect(x,y,w,h,fill,color)
        self.text(x+16,y+30,title,22,color,'bold')
        self.text(x+16,y+59,body,18)

    def save(self,path):
        path.write_text('\n'.join(self.bits+['</svg>'])+'\n')


d=Drawing(1000,'Concept 01 — compact T-handle packaging')
d.text(34,56,'Concept 01 / compact T-handle',39,INK,'bold')
d.text(36,94,'30 Oct 2026 · adjustable space reservations · no finished body geometry or physical fit claim',22,'#57657a')
d.rect(30,135,760,725)
d.text(56,176,'A  Stacked base — preferred',27,BLUE,'bold')
d.line([(170,225),(570,225)],INK)
d.line([(170,216),(170,231)],INK); d.line([(570,216),(570,231)],INK)
d.text(370,216,'80 mm starting envelope',17,INK,anchor='middle')
d.rect(170,238,400,130,'#eee8fa',PURPLE,24)
d.rect(187.5,255.5,365,95,'#fff',PURPLE,10)
d.rect(190,258,325,25,'#cee5ff',BLUE,4)
d.text(310,276,'PCB / 65 ×18 ×5',16,BLUE,anchor='middle')
d.rect(190,293,220,50,'#d7eee3',GREEN,7)
d.text(300,314,'Protected pack bay',17,GREEN,'bold',anchor='middle')
d.text(300,335,'44 ×22 ×10; cell/capacity TBD',14,GREEN,anchor='middle')
d.rect(437,255.5,112,95,'none',ORANGE,6,True)
d.text(493,309,'RF end',16,ORANGE,anchor='middle')
d.text(493,330,'reserve',16,ORANGE,anchor='middle')
d.circle(225,239,9,'#fff',BLUE);d.circle(267,239,9,'#fff',BLUE)
d.text(624,255,'Power + mode',18,BLUE)
d.text(624,278,'under silicone',18)
d.line([(612,260),(588,260),(267,239)],BLUE)
d.circle(220,365,6,'#d7eee3',GREEN);d.circle(245,365,6,'#d7eee3',GREEN)
d.text(60,396,'Charging contacts',18,GREEN)
d.text(60,420,'in opposite wing',18)
d.line([(222,393),(235,383),(245,365)],GREEN)
d.bits.append(f'<path d="M330 368 L330 410 C330 442 294 462 290 505 C282 568 295 665 329 714 Q370 760 411 714 C445 665 458 568 450 505 C446 462 410 442 410 410 L410 368" fill="#f5f0fb" stroke="{PURPLE}" stroke-width="2.5"/>')
d.line([(367,369),(367,440)],PURPLE)
d.rect(337.5,462,65,170,'#cee5ff',BLUE,18)
d.text(370,518,'MOTOR',17,BLUE,'bold',anchor='middle')
d.text(370,544,'SPACE',17,BLUE,anchor='middle')
d.text(370,572,'Ø13',17,BLUE,anchor='middle')
d.text(370,598,'×34',17,BLUE,anchor='middle')
d.rect(355,684,30,40,'#f5dba9',ORANGE,6)
d.line([(419,348),(424,440),(424,669),(385,704)],ORANGE,False,True)
d.text(62,487,'Motor sleeve',21,BLUE,'bold')
d.text(62,515,'Reference motor: Ø11 ×26',17)
d.text(62,540,'Mounting/wire allowance',17)
d.line([(273,518),(324,518),(337.5,530)],BLUE)
d.text(496,472,'Tip cable corridor',21,ORANGE,'bold')
d.text(496,501,'3.3 V / GND / SDA / SCL',17)
d.line([(490,489),(451,489),(424,540)],ORANGE)
d.text(70,690,'Sensor at distal tip',21,ORANGE,'bold')
d.text(70,718,'6 ×8 ×5 assembly space',17)
d.line([(285,710),(355,704)],ORANGE)
d.text(57,794,'Body contour is illustrative. Shape, neck, retention geometry,',19,'#57657a')
d.text(57,822,'thermal path and materials need a separate design review.',19,'#57657a')

d.rect(820,135,550,295)
d.text(846,177,'B  Split wings — comparison',25,INK,'bold')
d.text(846,210,'100 ×30 ×22 mm starting base envelope',21)
d.rect(850,245,490,104,'#eee8fa',PURPLE,20)
d.rect(866,263,203,65,'#d7eee3',GREEN,8)
d.text(967,301,'Pack bay',19,GREEN,'bold',anchor='middle')
d.rect(1090,263,185,65,'#cee5ff',BLUE,8)
d.text(1183,301,'PCB 40 ×18',18,BLUE,'bold',anchor='middle')
d.rect(1287,263,35,65,'none',ORANGE,4,True)
d.text(846,388,'Thinner base; wider crossbar and less PCB area.',20)
d.text(846,413,'Schematic comparison; rectangles not to scale.',16,'#57657a')

d.rect(820,455,550,405)
d.text(846,498,'A  Space budget',26,INK,'bold')
items=[('Outside base','80 ×30 ×26 mm'),('Skin / rigid wall','2 / 1.5 mm each side'),('Inside box','73 ×23 ×19 mm'),('PCB populated allocation','65 ×18 ×5 mm'),('Protected-pack bay','44 ×22 ×10 mm'),('Stack separator','2 mm'),('Height left in box','2 mm before detail design')]
for i,(label,value) in enumerate(items):
    yy=540+i*36
    d.text(846,yy,label,18,'#57657a')
    d.text(1130,yy,value,18)
d.text(846,820,'RF exclusion, corners, leads and fasteners remain open.',16,ORANGE)
d.rect(30,890,1340,78,'#fff5e6','#efcf98')
d.text(52,922,'Battery bay ≠ chosen battery. Neither a 500 mAh nor a 1000 mAh pack is asserted to fit.',22,ORANGE,'bold')
d.text(52,950,'Next mechanical artifact: inert sectional fit model, after the base envelope and real motor are agreed.',19)
mech=ROOT/'hardware/cad/concepts/layout-v1.svg';d.save(mech)

d=Drawing(930,'Concept 01 — proposed electrical architecture')
d.text(34,56,'Concept 01 / electronics architecture',39,INK,'bold')
d.text(36,95,'New candidates for review; this is a block diagram, not a completed schematic or netlist.',22,'#57657a')
d.node(40,170,240,110,'Magnetic dock input','5 V proposal\nInput protection TBD')
d.node(360,170,260,110,'BQ24074 candidate','Charging + system path\nInput / charge limits TBD','#e9f5ed',GREEN)
d.node(750,170,230,110,'3.3 V buck-boost','Part selection open\n≥500 mA rail capability','#e9f5ed',GREEN)
d.node(1100,170,250,110,'ESP32-C3-MINI-1','N4X candidate\nWiFi + Bluetooth LE')
d.line([(280,225),(360,225)],GREEN,True)
d.line([(620,225),(750,225)],GREEN,True)
d.text(648,210,'SYS',17,GREEN)
d.line([(980,225),(1100,225)],GREEN,True)
d.node(360,365,260,110,'Protected 1S pack','Actual pack + NTC TBD\nPack protection required','#e9f5ed',GREEN)
d.line([(490,365),(490,280)],GREEN,True)
d.line([(520,280),(520,365)],GREEN,True)
d.text(42,355,'Battery NTC → charger TS',20,GREEN,'bold')
d.text(42,386,'Separate from the tip sensor.',18)
d.line([(360,420),(320,420),(320,260),(360,260)],GREEN,True)
d.node(360,595,260,110,'Motor voltage solution','Drive voltage not selected\nBench reference: 3.7 V','#fff5e6',ORANGE)
d.line([(660,225),(680,225),(680,540),(330,540),(330,650),(360,650)],GREEN,True)
d.node(750,595,230,110,'DRV8212 candidate','PWM + output disable\nMode / package TBD')
d.line([(620,650),(750,650)],GREEN,True)
d.node(1100,595,250,110,'2-pin motor output','NFP-E1015 vs “N20” open\nStartup/stall not measured')
d.line([(980,650),(1100,650)],GREEN,True)
d.node(1100,365,250,110,'Tip MAX31875','Small PCB / flex at tip\nWired 3.3 V I²C')
d.line([(1225,280),(1225,365)],BLUE,True)
d.node(750,365,230,110,'MC3635','Main PCB; shared I²C\nInterrupt + purpose TBD')
d.line([(980,420),(1030,420),(1030,250),(1100,250)],BLUE,True)
d.line([(1140,280),(1065,310),(1065,520),(850,520),(850,595)],BLUE,True)
d.text(760,510,'PWM / motor inhibit',19,BLUE)
d.rect(40,443,260,71,'#fff5e6','#efcf98')
d.text(53,470,'Do not connect motor directly',17,ORANGE,'bold')
d.text(53,495,'to an unverified 4.2 / 4.4 V rail.',17,ORANGE)
d.node(750,765,230,85,'Power + mode','Silicone-covered buttons')
d.line([(980,810),(1380,810),(1380,225),(1350,225)],BLUE,True)
d.text(42,790,'Proposed first-prototype behavior',23,INK,'bold')
d.text(42,824,'Motor off at boot, docked, or fault. Local stop has priority.',20)
d.text(42,856,'Power-off vs sleep still needs a circuit decision.',20)
d.text(38,900,'SYS is nominally 4.4 V on external power; full cell is 4.2 V. Motor rating: 3.7 V. Sources in the design proposal.',18,'#57657a')
elec=ROOT/'hardware/pcb/concepts/architecture-v1.svg';d.save(elec)

d=Drawing(560,'Concept 01 — illustrative 24-hour battery-charge scenarios')
d.text(34,53,'24-hour charge budget / scenario study',37,INK,'bold')
d.text(36,90,'Assumed battery-side base current + motor branch; 20% cell capacity allowance. No measured runtime.',21,'#57657a')
origin,scale=400,0.63
for cap,color in [(500,BLUE),(1000,GREEN)]:
    x=origin+cap*0.8*scale
    d.line([(x,146),(x,465)],color,False,True)
    d.text(x,132,f'{cap} mAh cell: {cap*0.8:.0f} usable',16,color,anchor='middle')
for i,row in enumerate(results['power']):
    y=171+i*60
    d.text(36,y+23,row['name'],20)
    a=row['base_mah']*scale;b=row['motor_mah']*scale
    d.rect(origin,y,a,32,'#b8d5f5',BLUE,0)
    d.rect(origin+a,y,b,32,'#b4dec9',GREEN,0)
    d.text(origin+a+b+14,y+23,f"{row['required_mah']:g} mAh",18)
d.rect(38,492,22,22,'#b8d5f5',BLUE,0);d.text(70,511,'Base load',18)
d.rect(240,492,22,22,'#b4dec9',GREEN,0);d.text(272,511,'Motor branch',18)
d.text(550,511,'500/1000 mAh are hypothetical capacities; packaging is unconfirmed.',18,ORANGE)
power=ROOT/'hardware/design/power-budget-v1.svg';d.save(power)
for source in [mech,elec,power]:
    shutil.copy2(source,ASSETS/source.name)
print('Wrote three editable SVG concept drawings and docs copies.')
