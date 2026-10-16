"""Run the external-filament picker checks by hand; no printer or app input.

    tools/cad-venv/bin/python tools/bambu-ui/test_filament_picker.py

Generated images and the native OCR test executable stay in .cache.
"""
from pathlib import Path
import json,subprocess,sys,tempfile
from PIL import Image,ImageDraw,ImageFont
root=Path(__file__).resolve().parents[2];cache=root/'.cache/printer-control/filament-picker-review'
cache.mkdir(parents=True,exist_ok=True)
source=(root/'tools/bambu-ui/main.swift').read_text().split('while let line = readLine()')[0]
source+='''
import ImageIO
let imageURL = URL(fileURLWithPath:CommandLine.arguments[1])
let imageSource = CGImageSourceCreateWithURL(imageURL as CFURL,nil)!
let image = CGImageSourceCreateImageAtIndex(imageSource,0,nil)!
do {
 let words = try recognizedText(image)
 let choice = try externalChoice(words,filament:"TPU")
 let data = try JSONSerialization.data(withJSONObject:["point":[choice.rect.midX,choice.rect.midY]])
 print(String(data:data,encoding:.utf8)!)
} catch {
 let data = try! JSONSerialization.data(withJSONObject:["error":(error as? Failure)?.message ?? error.localizedDescription])
 print(String(data:data,encoding:.utf8)!)
}
'''
(cache/'main.swift').write_text(source)
subprocess.run(['swiftc','-O',str(cache/'main.swift'),'-o',str(cache/'test-picker')],check=True)
font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',28)
small=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',25)
def fixture(name,position,scale=1,kind='TPU',duplicate=False):
 im=Image.new('RGB',(1600,1200),'#eaeaea');d=ImageDraw.Draw(im)
 # A mapped dialog tile and a matching AMS tray are distractors.
 d.rectangle((1100,650,1220,800),fill='black');d.text((1130,670),'Ext',font=small,fill='white');d.text((1130,710),'TPU',font=small,fill='white')
 d.text((250,120),'AMS',font=font,fill='black');d.rectangle((250,170,380,300),fill='#dddddd');d.text((275,205),'TPU',font=small,fill='black')
 def external(x,y):
  d.rectangle((x-20,y-20,x+350,y+185),fill='white',outline='#888888',width=2)
  d.text((x,y),'External',font=font,fill='black');d.rectangle((x,y+55,x+120,y+170),fill='black')
  d.text((x+36,y+70),'Ext',font=small,fill='white');d.text((x+30,y+115),kind,font=small,fill='white')
 external(*position)
 if duplicate:external(850,150)
 if scale!=1:im=im.resize((int(im.width*scale),int(im.height*scale)))
 path=cache/(name+'.png');im.save(path)
 result=json.loads(subprocess.check_output([str(cache/'test-picker'),str(path)],text=True))
 if kind!='TPU' or duplicate:assert 'error' in result,(name,result)
 else:
  x,y=result['point'];px,py=position;assert (px+30)*scale<x<(px+90)*scale and (py+60)*scale<y<(py+110)*scale,(name,result)
 return dict(name=name,result=result)
rows=[fixture('left-popover-below',(180,750)),fixture('right-popover-above-left',(500,340)),fixture('resized-window',(90,420),.7),fixture('retina-window',(500,340),2),fixture('wrong-external-type',(500,340),kind='PET-CF'),fixture('ambiguous-external',(160,520),duplicate=True)]
sys.path.insert(0,str(root/'tools'));import bambu_print as bp
# Two identical unresolved labels must still resolve to the correct column;
# dynamic tags and already-mapped external sources are independent of origin.
def nodes(left,right,dx=0,dy=0):
 rows=[('AXStaticText','Left Nozzle',[10,20,80,18]),('AXStaticText','Right Nozzle',[400,20,90,18]),('AXGroup',left,[10,60,94,61]),('AXGroup',right,[400,60,94,61]),('AXStaticText','Print Options',[10,200,100,18])]
 return [dict(id=i,parent=0,role=role,label=label,rect=[r[0]+dx,r[1]+dy,r[2],r[3]],enabled=True) for i,(role,label,r) in enumerate(rows)]
class UI:
 printer_busy=False
 def __init__(self):self.ns=nodes('? ?','? ?',230,170);self.calls=[]
 def wait(self,predicate,**kw):assert predicate(self.ns);return self.ns
 def call(self,command,**kw):
  self.calls.append((command,kw));assert command=='select_external';assert bp.matching(self.ns,kw['label'],'AXGroup')[kw['nth']] is self.ns[kw['nozzle']+1]
  self.ns[kw['nozzle']+1]['label']='Ext '+kw['filament']+(' R' if kw['nozzle']==2 else '')
  return {'clicked':'External > Ext '+kw['filament']}
u=UI();bp.map_external_spools(u,{'slots':{2:{'type':'TPU'}}});assert u.calls[0][1]['nth']==1
u=UI();bp.map_external_spools(u,{'slots':{1:{'type':'PET-CF'},2:{'type':'TPU'}}});assert len(u.calls)==2
bp.map_external_spools(u,{'slots':{1:{'type':'PET-CF'},2:{'type':'TPU'}}});assert len(u.calls)==2
for dx,dy in [(0,0),(500,200),(-300,60)]:
 ns=nodes('Ext PET-CF','Ext TPU R',dx,dy);assert bp.external_mapped(ns,1,{'type':'PET-CF'}) and bp.external_mapped(ns,2,{'type':'TPU'})
 assert not bp.external_mapped(ns,1,{'type':'TPU'})
record=dict(native_ocr_cases=rows,mapping_checks=['duplicate labels in two columns','both external nozzles','translated window','already-mapped source makes no click','wrong type rejected'],scope='Native Vision OCR on generated popover fixtures; mapping protocol exercised with AX fixtures. No printer job is submitted by these checks.')
(cache/'results.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))
