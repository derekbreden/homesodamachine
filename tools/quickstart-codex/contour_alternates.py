#!/usr/bin/env python3
"""Compare three contour colors and collect their complete quick-start sheets."""
from pathlib import Path
import io
import json
import shutil
import subprocess
import sys

from PIL import Image
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from contours import Contours, PAD

ROOT = Path(__file__).resolve().parents[2]
DIR = ROOT/'hardware/quickstart-codex'
OUT = DIR/'out/contours'
W,H = 1368,936
INK = '#1a1a2e'
MUTED = '#656473'
for style in ('Regular','Semibold','Bold'):
    pdfmetrics.registerFont(TTFont(style,str(DIR/'fonts'/f'Plex-{style}.ttf')))

variants = [
    ('Original B gray','#75828a',OUT/'original-gray.pdf','Same gray as the B study.'),
    ('Darker slate','#46515b',DIR/'quick-start-codex.pdf','Recommended. Applied to the guide.'),
    ('Near-black','#242c36',OUT/'near-black.pdf','The strongest of these three contours.'),
]


def main():
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer,pagesize=(W,H),pageCompression=1)
    queues=[]
    def text(s,x,y,size=13,font='Regular',color=INK):
        c.setFillColor(HexColor(color));c.setFont(font,size);c.drawString(x,H-y-size*.8,s)
    def line(x,y,w):
        c.setStrokeColor(HexColor('#dcdfe1'));c.setLineWidth(.6);c.line(x,H-y,x+w,H-y)
    def picture(renderer,source,x,y,w,h):
        im=Image.open(source)
        a,b,cc,d=im.getchannel('A').getbbox()
        scale=min(w/(cc-a),h/(d-b))
        iw,ih=(cc-a)*scale,(d-b)*scale
        path,(pw,ph)=renderer.picture(source,(a,b,cc,d),iw,ih)
        ox,oy=x+(w-iw)/2,y+(h-ih)/2
        if path.exists():
            c.drawImage(str(path),ox-PAD,H-oy-ih-PAD,width=pw,height=ph,mask='auto')
    c.setFillColor(HexColor('#ffffff'));c.rect(0,0,W,H,fill=1,stroke=0)
    text('HOME SODA MACHINE / CONTOUR ALTERNATES',36,22,9,'Semibold',MUTED)
    text('Fine contour, across the whole guide.',36,47,31,'Semibold')
    text('Three colors. The same fine line. Each complete 19 x 13 in sheet follows this comparison.',36,92,13,'Regular',MUTED)
    line(36,121,1296)
    for index,(title,color,pdf,note) in enumerate(variants):
        x=36+440*index
        render=Contours(color);queues.append(render)
        c.setFillColor(HexColor(color));c.circle(x+6,H-150,6,stroke=0,fill=1)
        text(title,x+23,140,20,'Semibold')
        text(note,x,170,11.5,'Regular',MUTED)
        thumbnail=OUT/f'guide-{color[1:]}.png'
        c.drawImage(str(thumbnail),x,H-208-277,width=405,height=277,mask='auto')
        text(f'FULL SHEET ON PAGE {index+2}',x,493,9,'Semibold',MUTED)
        line(x,516,416)
        text('WHITE TUBING',x,534,9,'Semibold',MUTED)
        picture(render,DIR/'art/release-with-press.png',x+20,556,376,150)
        text('CLEAR GLASS',x,731,9,'Semibold',MUTED)
        picture(render,DIR/'art/edge-study/pour-base.png',x+97,750,222,143)
    line(36,910,1296)
    text('All contours are 0.6 pt wide on the page. Color changes; illustration size and instructions stay the same.',36,920,9.5,'Regular',MUTED)
    c.showPage();c.save()
    pending=[queue for queue in queues if queue.pending]
    if pending:
        for queue in pending:queue.render()
        subprocess.run([sys.executable,*sys.argv],cwd=ROOT,check=True)
        return
    writer=PdfWriter()
    writer.append(PdfReader(buffer),import_outline=False)
    for title,color,pdf,note in variants:
        writer.append(str(pdf),outline_item=title,import_outline=False)
    writer.add_metadata({'/Title':'Quick start - fine contour alternates','/Author':'Derek Bredensteiner'})
    pdf=DIR/'contour-alternates.pdf'
    with pdf.open('wb') as stream:writer.write(stream)
    shutil.copyfile(pdf,ROOT/'output/pdf/quick-start-contour-alternates.pdf')
    subprocess.run(['pdftoppm','-f','1','-singlefile','-scale-to','1900','-png',str(pdf),str(OUT/'contour-alternates')],check=True)
    im=Image.open(OUT/'contour-alternates.png');im.thumbnail((1200,1200));im.save(DIR/'contour-alternates.cover.png')
    (DIR/'contour-alternates.pdf.json').write_text(json.dumps({
        'title':'Quick start - fine contour alternates',
        'subtitle':'Compare original B gray, darker slate, and near-black - three complete 19 x 13 in sheets',
        'pages':4,'cover':'contour-alternates.cover.png','cover_size':list(im.size),
    },indent=2)+'\n')
    print(pdf)


if __name__=='__main__':main()
