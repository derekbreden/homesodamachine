"""Stream the exact native roads, retaining actual per-road height/width/tool."""
from pathlib import Path
import re
WORD=re.compile(r'([A-Z])([-+]?(?:\d+(?:\.\d*)?|\.\d+))')
MODEL={'Outer wall','Inner wall','Overhang wall','Bottom surface','Top surface','Internal solid infill','Sparse infill','Bridge','Gap infill'}
WALL={'Outer wall','Inner wall','Overhang wall'}
def layers(data):
 x=y=z=e=width=height=0.;tool=0;obj=None;feature='';layer=None;abs_xyz=True;rel_e=True;roads=[];commands=[]
 def finished():
  model=[r for r in roads if r[6]==1901 and r[7] in MODEL]
  walls=[r for r in model if r[7] in WALL]
  actual=walls[0][10] if walls else model[0][10] if model else height
  return layer,actual,roads,commands
 for lineno,raw in enumerate(data,1):
  line=raw.decode().strip() if isinstance(raw,bytes) else raw.strip()
  if line.startswith('; Z_HEIGHT:'):
   if layer is not None:yield finished()
   layer=float(line.split(':',1)[1]);obj=None;feature='';roads=[];commands=[]
  elif line.startswith('; LAYER_HEIGHT:'):height=float(line.split(':',1)[1])
  elif line.startswith('; OBJECT_ID:'):obj=int(line.split(':',1)[1]);feature=''
  elif line.startswith('; start printing object, unique label id:'):obj=int(line.rsplit(':',1)[1]);feature=''
  elif line.startswith('; stop printing object, unique label id:'):
   if int(line.rsplit(':',1)[1])==obj:obj=None;feature=''
  elif line.startswith('; FEATURE:'):feature=line.split(':',1)[1].strip()
  elif line.startswith('; LINE_WIDTH:'):width=float(line.split(':',1)[1])
  code=line.split(';',1)[0].strip()
  if not code:continue
  cmd=code.split()[0]
  if re.fullmatch('T[0-9]+',cmd):
   if layer is not None:commands.append({'line':lineno,'command':cmd})
   if cmd in ('T0','T1'):tool=int(cmd[1:])
  v={k:float(n) for k,n in WORD.findall(code)}
  if cmd in ('G90','G91'):abs_xyz=cmd=='G90'
  elif cmd in ('M82','M83'):rel_e=cmd=='M83'
  elif cmd=='G92':x,y,z,e=(v.get(k,old) for k,old in zip('XYZE',(x,y,z,e)))
  elif cmd in ('G0','G1','G2','G3'):
   nx,ny,nz=(v.get(k,old) if abs_xyz else old+v.get(k,0) for k,old in zip('XYZ',(x,y,z)))
   de=v.get('E',0) if rel_e else v.get('E',e)-e
   if obj is not None and layer is not None and de>1e-9 and (nx!=x or ny!=y):roads.append((x,y,nx,ny,width,tool,obj,feature,cmd,de,height,lineno))
   x,y,z=nx,ny,nz
   if 'E' in v:e=e+v['E'] if rel_e else v['E']
 if layer is not None:yield finished()
