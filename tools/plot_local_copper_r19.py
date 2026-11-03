"""Read-only layer diagnostic from actual saved copper polygons/records."""
from pathlib import Path
import sys,json,hashlib,html
p=Path(sys.argv[1]);g=json.loads(p.read_text());out=Path(sys.argv[2]);colors={'GND':'#77818a','SYS':'#e2a400','MOTOR_N':'#ab25a5','MOTOR_P':'#dc4560','MOTOR_3V7':'#e17a33','3V3':'#15804d'};s=['<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="1160" viewBox="0 0 1800 1160"><rect width="1800" height="1160" fill="white"/>'];s.append('<text x="25" y="30" font-family="sans-serif" font-size="22">R19 local power seed · actual native coordinates · zones omitted</text>')
for row,(xmin,xmax,ymin,ymax,title)in enumerate([(2,9,38,46,'SYS / motor output area'),(-8,6,25,35,'header / sensor logic area')]):
 for col,layer in enumerate(['F.Cu','In1.Cu','B.Cu']):
  ox=25+col*590;oy=90+row*520;scale=min(540/(xmax-xmin),430/(ymax-ymin));w=(xmax-xmin)*scale;h=(ymax-ymin)*scale
  def xy(pt):return(ox+(pt[0]-xmin)*scale,oy+(ymax-pt[1])*scale)
  s.append(f'<text x="{ox}" y="{oy-18}" font-family="sans-serif" font-size="18">{html.escape(title)} / {layer}</text><rect x="{ox}" y="{oy}" width="{w}" height="{h}" fill="#f6f8fb" stroke="#cbd2dc"/>')
  s.append(f'<clipPath id="c{row}{col}"><rect x="{ox}" y="{oy}" width="{w}" height="{h}"/></clipPath><g clip-path="url(#c{row}{col})">')
  for i in range(int(xmin*2),int(xmax*2)+1):
   x,_=xy([i/2,ymin]);s.append(f'<path d="M{x},{oy}v{h}" stroke="#dde4eb" stroke-width=".5"/>')
  for i in range(int(ymin*2),int(ymax*2)+1):
   _,y=xy([xmin,i/2]);s.append(f'<path d="M{ox},{y}h{w}" stroke="#dde4eb" stroke-width=".5"/>')
  for pad in g['pads']:
   if layer not in pad['layers']:continue
   for poly in pad['polygons']:
    pts=' '.join(f'{a},{b}'for a,b in map(xy,poly));s.append(f'<polygon points="{pts}" fill="{colors.get(pad["net"],"#9fb3ca")}" opacity=".65"/>')
  for t in g['routes']:
   color=colors.get(t['net'],'#7894b3')
   if t['kind']=='track'and t['layer']==layer:
    a,b=xy(t['start']),xy(t['end']);s.append(f'<path d="M{a[0]},{a[1]} L{b[0]},{b[1]}" stroke="{color}" stroke-width="{t["width"]*scale}" stroke-linecap="round"/>')
   elif t['kind']=='via':
    a,b=xy(t['position']);s.append(f'<circle cx="{a}" cy="{b}" r="{t["diameter"]*scale/2}" fill="{color}"/><circle cx="{a}" cy="{b}" r="{t["drill"]*scale/2}" fill="white"/>')
    if xmin<=t['position'][0]<=xmax and ymin<=t['position'][1]<=ymax:
     label={'MOTOR_N':'N','MOTOR_P':'P','SYS':'S','GND':'G','3V3':'3','MOTOR_3V7':'M'}.get(t['net'],'');s.append(f'<text x="{a+5}" y="{b-7}" font-family="sans-serif" font-size="11" fill="#202b39">{label}</text>')
  s.append('</g>')
  s.append(f'<text x="{ox}" y="{oy+h+18}" font-family="sans-serif" font-size="12">X {xmin}…{xmax} mm / Y {ymin}…{ymax} mm; 0.5 mm grid</text>')
s.append(f'<text x="25" y="1130" font-family="sans-serif" font-size="12">Board SHA256 {g["board_sha256"]} · geometry SHA256 {hashlib.sha256(p.read_bytes()).hexdigest()}</text></svg>');out.write_text('\n'.join(s))
