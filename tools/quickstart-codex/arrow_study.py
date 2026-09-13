#!/usr/bin/env python3
"""Review tube-withdrawal arrows at the guide's printed size and enlarged."""
from pathlib import Path
import io
import math
import subprocess
import sys

from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from contours import Contours, PAD

ROOT=Path(__file__).resolve().parents[2]
DIR=ROOT/'hardware/quickstart-codex'
OUT=DIR/'out/action-audit'
W,H=900,660
VARIANTS=[
    ('A',(1305.98,317.07),(1723.5,437.79)),
    ('B',(1510,380),(1780,458)),
    ('C',(1510,554),(1780,632)),
    ('D',(1465,488),(1780,579)),
]


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    buffer=io.BytesIO();c=canvas.Canvas(buffer,pagesize=(W,H))
    pdfmetrics.registerFont(TTFont('Plex',str(DIR/'fonts/Plex-Semibold.ttf')))
    renderer=Contours('#46515b')
    def arrow(start,end,scale):
        width,head,outline=2.4*scale,5*scale,1.1*scale
        dx,dy=end[0]-start[0],end[1]-start[1]
        length=math.hypot(dx,dy);ux,uy=dx/length,dy/length
        back,half=head*math.cos(.5),head*math.sin(.5)
        neck=(end[0]-back*ux,end[1]-back*uy)
        tip=c.beginPath();tip.moveTo(end[0],H-end[1]);tip.lineTo(neck[0]-half*uy,H-neck[1]-half*ux);tip.lineTo(neck[0]+half*uy,H-neck[1]+half*ux);tip.close()
        c.setLineCap(1);c.setLineJoin(1)
        c.setStrokeColor(white);c.setFillColor(white);c.setLineWidth(width+2*outline);c.line(start[0],H-start[1],neck[0],H-neck[1]);c.setLineWidth(2*outline);c.drawPath(tip,fill=1,stroke=1)
        c.setStrokeColor(HexColor('#d64050'));c.setFillColor(HexColor('#d64050'));c.setLineWidth(width);c.line(start[0],H-start[1],neck[0],H-neck[1]);c.drawPath(tip,fill=1,stroke=0)
    def scene(x,y,scale,tail,tip):
        ih=53*scale;iw=1840/1040*ih
        asset,(pw,ph)=renderer.picture(DIR/'art/release-with-press.png',(0,0,1840,1040),iw,ih)
        if asset.exists():c.drawImage(str(asset),x-PAD,H-y-ih-PAD,width=pw,height=ph,mask='auto')
        p=lambda a,b:(x+a*iw/1840,y+b*ih/1040)
        arrow(p(1316.97,779.94),p(1042.29,700.52),scale)
        arrow(p(*tail),p(*tip),scale)
    c.setFillColor(white);c.rect(0,0,W,H,fill=1,stroke=0)
    for index,(label,tail,tip) in enumerate(VARIANTS):
        x,y=25+(index%2)*450,24+(index//2)*330
        c.setFillColor(HexColor('#1a1a2e'));c.setFont('Plex',18);c.drawString(x,H-y,label)
        scene(x+52,y+23,3.25,tail,tip)
        scene(x+90,y+223,1,tail,tip)
    c.showPage();c.save()
    if renderer.pending:
        renderer.render();subprocess.run([sys.executable,*sys.argv],cwd=ROOT,check=True);return
    pdf=OUT/'tube-options.pdf';pdf.write_bytes(buffer.getvalue())
    subprocess.run(['pdftoppm','-singlefile','-scale-to','1800','-png',str(pdf),str(OUT/'tube-options')],check=True)
    print(pdf)


if __name__=='__main__':main()
