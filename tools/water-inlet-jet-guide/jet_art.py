"""Vector setup pictures for the jet bench guide; no CAD or appliance build.

The drilling jaws follow their source arrangement. Clamps, spindle, gun and
elbow are explanatory proxies. Purchased fitting bore/land and clamp envelopes
remain actual-workpiece measurements, not dimensions inferred from these views.
"""
from __future__ import annotations

import math
from common import *

GREEN = "#20745D"
DARK_STEEL = "#B9C3D0"
LIGHT_STEEL = "#F1F4F7"


def tag(a, value, x, y, fill=BLUE):
    a.ellipse(x-10, y-10, 20, 20, fill, fill)
    a.label(value, x, y+3.7, 10, PAPER, "PlexBold", "center")


def leader(a, label, x, y, knee, target, align="left", fill=BLUE, size=10.5):
    a.label(label, x, y, size, fill, align=align)
    # Text and the shoulder are beside one another, not underlined.
    extent = pdfmetrics.stringWidth(label, "PlexSemi", size)
    start = x-7 if align == "right" else x+extent+7
    sy = y-3
    a.line(start, sy, knee[0], knee[1], fill, .9)
    a.arrow(knee[0], knee[1], *target, fill, .9, 5)


def hatch(a, x, y, w, h, step=10):
    for k in range(-int(h), int(w)+int(h), step):
        x1, y1 = max(0, k), max(0, -k)
        x2, y2 = min(w, k+h), min(h, w-k)
        if x2 >= x1 and y2 >= y1:
            a.line(x+x1, y+y1, x+x2, y+y2, "#ABB6C4", .65)


def drill(a, x, y, length=90, diameter=13, point=9):
    a.rect(x-diameter/2, y, diameter, length-point, ORANGE)
    for yy in range(int(y+6), int(y+length-point-5), 11):
        a.line(x-diameter/2+1, yy, x+diameter/2-1, yy+6, PAPER, 1)
    a.shape([(x-diameter/2, y+length-point), (x, y+length),
             (x+diameter/2, y+length-point)], ORANGE)


def cap(a, cx, cy, r=58, hole_ratio=1.5875/9.5, fill=STEEL):
    a.ellipse(cx-r, cy-r, 2*r, 2*r, fill)
    a.ellipse(cx-r*hole_ratio, cy-r*hole_ratio,
              2*r*hole_ratio, 2*r*hole_ratio, PAPER)


def gun(a, tip, tail, width=21, wire=True):
    """Gun/nozzle proxy aimed at a seam point, with a separate fine wire."""
    tx, ty = tip; bx, by = tail
    dx, dy = bx-tx, by-ty
    length = math.hypot(dx,dy); ux,uy=dx/length,dy/length; nx,ny=-uy,ux
    def p(t, side):return tx+ux*t+nx*side,ty+uy*t+ny*side
    a.shape([p(4,-3),p(30,-9),p(45,-9),p(45,9),p(30,9),p(4,3)], COPPER)
    a.shape([p(45,-width),p(length,-width),p(length,width),p(45,width)], BLUE)
    a.line(*p(49,-width+5),*p(length-5,-width+5),PAPER,1.1)
    if wire:
        a.line(*p(length-10,width+10),*p(22,width+10),ORANGE,2)
        a.line(*p(22,width+10),tx+nx*2,ty+ny*2,ORANGE,1.6)
    a.ellipse(tx-3,ty-3,6,6,ORANGE,ORANGE)


class Iso:
    def __init__(self,a,origin=(260,236),sx=2.1,sy=.9,dx=.6,dy=-.45,sz=2.8):
        self.a=a;self.ox,self.oy=origin
        self.sx,self.sy,self.dx,self.dy,self.sz=sx,sy,dx,dy,sz
    def p(self,x,y,z):return (self.ox+self.sx*x+self.sy*y,
                              self.oy+self.dx*x+self.dy*y-self.sz*z)
    def box(self,x0,x1,y0,y1,z0,z1,front=STEEL,top=LIGHT_STEEL,side=DARK_STEEL):
        a=self.a;p=self.p
        a.shape([p(x0,y0,z0),p(x1,y0,z0),p(x1,y0,z1),p(x0,y0,z1)],front)
        a.shape([p(x1,y0,z0),p(x1,y1,z0),p(x1,y1,z1),p(x1,y0,z1)],side)
        a.shape([p(x0,y0,z1),p(x1,y0,z1),p(x1,y1,z1),p(x0,y1,z1)],top)
    def circle(self,x,y,z,r,fill=STEEL,stroke=INK):
        self.a.shape([self.p(x+r*math.cos(i*math.tau/48),y+r*math.sin(i*math.tau/48),z)
                      for i in range(48)],fill,stroke,1)
    def cylinder(self,x,y,z0,z1,r,fill=STEEL):
        p=self.p;a=self.a
        # A vertical cylinder's silhouette is at the extrema of screen X.
        theta=math.atan2(self.sy,self.sx)
        q=(r*math.cos(theta),r*math.sin(theta))
        a.shape([p(x+q[0],y+q[1],z0),p(x-q[0],y-q[1],z0),
                 p(x-q[0],y-q[1],z1),p(x+q[0],y+q[1],z1)],fill)
        self.circle(x,y,z1,r,fill)


def fixture(a):
    """Exact nominal jaw/base topology; four C-clamps have visible screw axes."""
    i=Iso(a)
    i.box(-75,75,-50,50,-14,-8,DARK_STEEL,STEEL,DARK_STEEL)
    i.box(-65,65,-50,50,-8,0,GLOVE,"#F4E4CC","#C5A77D")
    i.box(-60,60,-45,45,0,8)
    i.box(-32,32,.5,25.5,8,38)
    i.box(-32,32,-25.5,-.5,8,38,front="#E5EAF5",top=ICE,side="#BCCBE5")
    i.circle(0,.15,38,4.9,PAPER)
    i.cylinder(0,.15,38,58,4.75)
    # Horizontal jaw clamps: screw axes run Y, frames wrap outside +/-X.
    for sign in (-1,1):
        x=sign*20;spine=sign*42;z=24
        pts=[i.p(x,27,z),i.p(spine,27,z),i.p(spine,-36,z),i.p(x,-36,z)]
        a.shape(pts,None,BLUE,5,False)
        a.line(*i.p(x,-36,z),*i.p(x,-25.5,z),INK,2.3)
        a.line(*i.p(x-4,-25.5,z),*i.p(x+4,-25.5,z),BLUE,4)
        a.line(*i.p(x-5,-41,z),*i.p(x+5,-41,z),INK,2)
        tag(a,"A",*i.p(spine,-20,z+2))
    # Vertical table clamps: a screw pushes on each flange; return hooks under table.
    for sign in (-1,1):
        x=sign*46;spine=sign*79;y=-29
        pts=[i.p(x,y,-14),i.p(spine,y,-14),i.p(spine,y,22),i.p(x,y,22)]
        a.shape(pts,None,BLUE,5,False)
        a.line(*i.p(x,y,22),*i.p(x,y,8),INK,2.3)
        i.circle(x,y,8,3.5,BLUE)
        a.line(*i.p(x-5,y,25),*i.p(x+5,y,25),INK,2)
        tag(a,"B",*i.p(spine,y,7))
    tip=i.p(0,.15,60)
    drill(a,tip[0],tip[1]-42,42,5,4)
    a.rect(tip[0]-15,tip[1]-66,30,24,DARK_STEEL)
    a.line(tip[0],tip[1]+6,tip[0],tip[1]+20,BLUE,.8,[3,3])
    a.label("1/16-inch drill",337,35,11,BLUE)
    a.arrow(333,40,tip[0]+6,tip[1]-17,BLUE,1)
    a.label("50-60 mm blank",16,73,11,BLUE)
    a.arrow(132,77,*i.p(-4.75,.15,52),BLUE,1)
    a.label("30 mm jaw support",352,164,10.5,BLUE)
    a.arrow(369,171,*i.p(32,-25.5,25),BLUE,1)
    a.label("A: close both jaws",16,19,11,BLUE)
    a.label("B: clamp base + backer to table",16,343,11,BLUE)


def elbow(a,x=160,y=100,scale=1,cap_on=True,purge=False):
    """Barstock street elbow proxy: male leg up, female lateral leg to right."""
    def p(px,py):return x+px*scale,y+py*scale
    def rect(px,py,w,h,fill=STEEL):a.rect(*p(px,py),w*scale,h*scale,fill)
    rect(-43,42,86,141)
    rect(-15,105,149,78)
    a.shape([p(-43,42),p(-25,31),p(62,31),p(43,42)],LIGHT_STEEL)
    a.shape([p(43,42),p(62,31),p(62,105),p(43,120)],DARK_STEEL)
    rect(-32,-6,64,48,LIGHT_STEEL)
    for k in range(6):
        a.line(*p(-33,3+k*7),*p(33,-3+k*7),INK,.8)
    a.ellipse(*p(-32,-14),64*scale,17*scale,STEEL)
    a.ellipse(*p(-19,-9),38*scale,9*scale,PAPER)
    a.ellipse(*p(120,105),28*scale,78*scale,DARK_STEEL)
    a.ellipse(*p(126,118),15*scale,51*scale,PAPER)
    if cap_on:
        rect(-28,-28,56,22,ORANGE)
        a.ellipse(*p(-28,-36),56*scale,16*scale,LIGHT_STEEL)
        a.ellipse(*p(-4,-31),8*scale,5*scale,PAPER)
    if purge:
        a.arrow(*p(171,144),*p(62,144),BLUE,2)
        a.arrow(*p(0,120),*p(0,-49),BLUE,2)


def overview(a):
    a.label("DRILL ON THE LONG BLANK",19,20,12,BLUE)
    a.rect(64,108,47,192,STEEL)
    a.ellipse(64,99,47,18,LIGHT_STEEL)
    drill(a,87.5,28,83,8,6)
    a.line(47,145,131,145,ORANGE,2,[5,3])
    a.label("cut off the drilled end",15,328,11,ORANGE)
    a.arrow(119,159,165,159,ORANGE,2)
    cap(a,218,159,34)
    a.label("FINISHED CAP",218,226,11,BLUE,align="center")
    a.arrow(265,159,312,159,ORANGE,2)
    elbow(a,384,120,.8,True)
    a.label("WELD TO WATER ELBOW",328,20,12,BLUE)
    a.label("water exits into headspace",309,328,11,BLUE)


def fit(a):
    cap(a,115,96,54)
    a.dim(61,166,169,166)
    a.label("9.50 ±0.05 mm",115,189,12,BLUE,align="center")
    a.label("2.00 ±0.20 mm thick",115,211,11,BLUE,align="center")
    a.label("1/16-inch axial hole",115,234,11,BLUE,align="center")
    # Enlarged axial section of the purchased tip, not a dimensioned fitting model.
    a.rect(289,109,78,115,STEEL);a.rect(426,109,78,115,STEEL)
    a.rect(306,74,73,35,LIGHT_STEEL);a.rect(414,74,73,35,LIGHT_STEEL)
    a.line(306,108,487,108,ORANGE,2)
    a.label("cap overlaps actual bore",396,35,11,BLUE,align="center")
    a.arrow(373,44,355,109,BLUE,1)
    a.label("measure bore + flat land",396,267,11,BLUE,align="center")
    a.arrow(396,249,396,142,BLUE,1)
    a.label("check cap + finished weld through tapped plate",260,321,11,BLUE,align="center")


def depth(a):
    # Physical relationships enlarged 60:1. The drill point is schematic.
    x,y,w=86,70,156
    a.rect(x,y,w,231,STEEL);hatch(a,x,y,w,231)
    hole=26;cx=x+w/2;full=129;tip=147
    a.shape([(cx-hole/2,y),(cx-hole/2,y+full),(cx,y+tip),
             (cx+hole/2,y+full),(cx+hole/2,y)],PAPER)
    drill(a,cx,7,y+tip-7,hole,18)
    cut_y=y+93
    a.line(57,y,275,y,BLUE,1,[5,3])
    a.line(57,cut_y,275,cut_y,ORANGE,2,[6,4])
    a.dim(285,y,285,y+tip)
    a.label("3-4 mm",300,115,17,BLUE)
    a.label("to drill tip",300,138,12,BLUE)
    a.label("2 mm cap",315,184,14,ORANGE)
    a.label("final back face",315,204,11,ORANGE)
    a.arrow(307,189,251,cut_y,ORANGE,1.3)
    a.label("full-size hole",306,260,12,BLUE)
    a.label("extends below cut",306,281,12,BLUE)
    a.arrow(300,248,cx+hole/2+3,y+full-2,BLUE,1.2)
    a.label("end face = depth zero",300,41,11,BLUE)
    a.arrow(290,46,235,y,BLUE,1)
    a.label("remaining handling stock",165,327,11,BLUE,align="center")


def drilling(a):
    labels=["1  CUT CHIPS","2  RETRACT","3  RENEW FLUID"]
    for n,left in enumerate([12,189,366]):
        cx=left+75;top=130
        a.label(labels[n],cx,22,11,BLUE,align="center")
        a.rect(left+40,top,70,175,STEEL)
        a.rect(left+17,212,116,93,ICE,BLUE)
        a.rect(left+40,top,70,82,STEEL)
        a.ellipse(left+40,top-7,70,14,LIGHT_STEEL)
        bit_y=78 if n==0 else 41
        drill(a,cx,bit_y,70,12,8)
        if n==0:
            a.arrow(cx+34,65,cx+34,110,ORANGE,2)
            for k in range(3):
                a.line(cx+11+k*7,top+5-k*4,cx+16+k*7,top-k*5,ORANGE,2)
        elif n==1:
            a.arrow(cx+34,105,cx+34,65,BLUE,2)
        if n==1:
            for k in range(4):a.line(cx+19+k*7,top-6,cx+23+k*7,top-13,ORANGE,1.4)
        if n==2:
            a.shape([(cx+29,top-31),(cx+34,top-15),(cx+24,top-15)],BLUE,BLUE)
            a.arrow(cx+56,top-35,cx+32,top-14,BLUE,1)
        a.label(["steady positive feed","clear chips from flutes","resume at proved stop"][n],cx,333,10.5,BLUE,align="center")


def saw_finish(a):
    a.label("CUT WITH RETAINED ROD IN VISE",20,20,11,BLUE)
    a.rect(38,91,243,35,STEEL)
    a.rect(58,63,141,28,ICE,BLUE);a.rect(58,126,141,57,ICE,BLUE)
    a.rect(261,105,20,7,PAPER)
    a.rect(258,40,6,144,ORANGE,ORANGE)
    a.dim(264,64,281,64)
    a.label("2.0 ±0.2 mm",328,77,12,BLUE)
    a.arrow(321,80,282,79,BLUE,1)
    a.arrow(286,133,309,190,ORANGE,1.5)
    a.rect(278,202,75,12,ICE,BLUE)
    a.label("free cutoff / catch tray",226,241,10.5,BLUE)
    cap(a,414,146,53)
    a.label("inspect both faces",414,235,11,BLUE,align="center")
    a.label("burr removal by hand",414,262,11,BLUE,align="center")
    # A larger twist drill is hand-turned at the hole, with its point visible.
    tx,ty=421,142;bx,by=476,64
    length=math.hypot(bx-tx,by-ty);ux,uy=(bx-tx)/length,(by-ty)/length
    nx,ny=-uy,ux
    def p(t,s):return tx+ux*t+nx*s,ty+uy*t+ny*s
    a.shape([p(8,-6),p(length,-6),p(length,6),p(8,6)],ORANGE)
    a.shape([(tx,ty),p(8,-6),p(8,6)],ORANGE)
    for t in range(15,int(length)-8,12):a.line(*p(t,-5),*p(t+7,5),PAPER,1)
    a.label("clear bore; square OD rim",277,321,12,BLUE,align="center")


def purge(a):
    a.rect(23,57,72,133,STEEL);a.ellipse(23,42,72,30,STEEL)
    a.rect(46,25,26,20,BLUE)
    a.label("ARGON",59,127,13,BLUE,align="center")
    a.line(72,35,126,35,BLUE,5)
    a.ellipse(128,24,23,23,PAPER,BLUE)
    a.label("regulated 6 mm hose",150,25,10.5,BLUE)
    a.line(143,43,207,43,BLUE,5)
    a.ellipse(199,35,16,16,BLUE,BLUE)
    a.line(207,43,434,43,BLUE,5)
    a.arrow(266,43,307,43,BLUE,2)
    a.rect(437,19,75,50,STEEL)
    a.label("WELDER",474,50,11,BLUE,align="center")
    a.line(207,43,207,76,BLUE,5)
    a.label("tee branch",222,65,11,BLUE)
    # Keep both threaded connections and the two straight tube links in series.
    a.rect(192,76,30,28,STEEL)
    a.label("FNPT coupling",244,95,11,BLUE)
    a.line(207,104,207,114,BLUE,3)
    a.rect(192,114,30,28,STEEL)
    a.label("compression adapter",244,134,11,BLUE)
    a.line(207,142,207,180,STEEL,8)
    a.arrow(207,149,207,173,BLUE,1.8)
    a.label("1/4-inch OD stainless link",244,163,10.5,BLUE)
    a.rect(182,180,50,30,STEEL)
    a.line(232,195,257,195,INK,2)
    a.line(257,184,257,206,BLUE,5)
    a.label("metal needle valve",282,200,11,BLUE)
    a.line(207,210,207,248,STEEL,8)
    a.arrow(207,217,207,241,BLUE,1.8)
    a.label("1/4-inch OD stainless link",244,232,10.5,BLUE)
    a.rect(192,248,30,28,STEEL)
    a.label("adapter into female port",244,267,10.5,BLUE)
    # Rotate the proxy so the final adapter meets the actual female opening.
    a.c.saveState();a.c.translate(149.4,335.2);a.c.rotate(-90)
    elbow(a,0,0,.4,True)
    a.c.restoreState()
    a.line(207,281,207,335,BLUE,2)
    a.arrow(207,335,112,335,BLUE,2)
    a.label("gentle purge out jet",15,248,10.5,BLUE)
    a.arrow(121,256,132,322,BLUE,1)


def aim(a):
    # Whole setup at left: clamp the body to a metal block; separate cap restraint.
    elbow(a,131,125,.79,True)
    a.rect(12,270,225,22,DARK_STEEL)
    # Screw and opposing fixed anvil share the same vertical clamp axis.
    a.shape([(102,135),(42,135),(42,301),(102,301)],None,BLUE,6,False)
    a.line(102,125,102,154,INK,2)
    a.ellipse(98,120,8,6,INK,INK)
    a.ellipse(99,153,6,4,BLUE,BLUE)
    a.line(102,301,102,292,INK,2)
    a.line(98,292,106,292,BLUE,3)
    a.line(123,101,123,79,BLUE,3)
    a.line(123,79,18,79,BLUE,3)
    a.line(18,79,18,270,BLUE,3)
    a.rect(12,262,12,8,DARK_STEEL)
    a.label("metal hold-down",17,48,10.5,BLUE)
    a.arrow(118,51,123,78,BLUE,1)
    a.label("grip elbow body / hex",19,326,11,BLUE)
    a.arrow(164,316,137,225,BLUE,1)
    # Magnified local joint. The horizontal dark line is the cap/tip interface.
    a.rect(310,165,75,113,STEEL);a.rect(440,165,75,113,STEEL)
    a.rect(324,128,72,37,LIGHT_STEEL);a.rect(429,128,72,37,LIGHT_STEEL)
    a.line(324,165,385,165,INK,1.6);a.line(440,165,501,165,INK,1.6)
    gun(a,(499,163),(510,65),13,True)
    a.label("AIM AT THIS SEAM",402,29,12,ORANGE,align="center")
    a.line(405,36,444,77,ORANGE,1)
    a.arrow(444,77,499,163,ORANGE,1)
    a.label("cap",351,105,11,BLUE,align="center")
    a.arrow(351,111,355,128,BLUE,1)
    a.label("jet passage stays open",414,308,10.5,BLUE,align="center")
    a.arrow(414,294,414,180,BLUE,1)
    a.label("tip / wire point meet the joint",399,345,10.5,BLUE,align="center")


def tacks(a):
    for idx,(cx,cy,active) in enumerate([(137,91,0),(403,91,180),(137,248,90),(403,248,270)]):
        cap(a,cx,cy,54)
        for angle in [0,180,90,270][:idx]:
            t=math.radians(angle-90);px,py=cx+54*math.cos(t),cy+54*math.sin(t)
            a.ellipse(px-4,py-4,8,8,INK,INK)
        t=math.radians(active-90);px,py=cx+54*math.cos(t),cy+54*math.sin(t)
        a.ellipse(px-5,py-5,10,10,ORANGE,ORANGE)
        gx,gy=px+28*math.cos(t),py+28*math.sin(t)
        # Only a tip is needed: the same clamped work stays put between poses.
        a.arrow(gx,gy,px,py,ORANGE,2,7)
        tag(a,str(idx+1),cx-83,cy-45)
        a.label(["12 o'clock","opposite: 6","then 3","opposite: 9"][idx],cx,cy+96,12,BLUE,align="center")
    a.label("cap center and vent remain clear",270,358,11,BLUE,align="center")


def arc(a,cx,cy,r,start,end,fill=ORANGE,width=5):
    steps=max(5,int(abs(end-start)/5));points=[]
    for j in range(steps+1):
        t=math.radians(start+(end-start)*j/steps-90)
        points.append((cx+r*math.cos(t),cy+r*math.sin(t)))
    a.shape(points,None,fill,width,False)
    x,y=points[-1];prev=points[-3]
    a.arrow(*prev,x,y,fill,1.5,7)


def weld(a):
    for idx,(cx,cy,start,end) in enumerate([(137,100,0,90),(403,100,180,270),
                                          (137,267,90,180),(403,267,270,360)]):
        cap(a,cx,cy,54)
        for oldstart,oldend in [(0,90),(180,270),(90,180),(270,360)][:idx]:
            arc(a,cx,cy,54,oldstart,oldend,INK,3)
        arc(a,cx,cy,54,start,end)
        tag(a,str(idx+1),cx-83,cy-45)
        a.label(["first accessible arc","opposite arc","connect this side","close final tie-in"][idx],cx,cy+79,11,BLUE,align="center")
    a.label("quarter circumference ~7.5 mm at nominal cap OD",270,358,11,BLUE,align="center")


def root_panel(a,x,y,kind,title):
    a.label(title,x+81,y-10,12,GREEN if kind=="fused" else ORANGE,align="center")
    a.rect(x,y+57,39,128,STEEL);a.rect(x+123,y+57,39,128,STEEL)
    a.rect(x+15,y+18,53,39,LIGHT_STEEL);a.rect(x+94,y+18,53,39,LIGHT_STEEL)
    if kind=="fused":
        a.shape([(x+15,y+32),(x+30,y+39),(x+43,y+55),(x+39,y+72),
                 (x+19,y+67),(x+9,y+53)],ORANGE,ORANGE)
        a.shape([(x+147,y+32),(x+132,y+39),(x+119,y+55),(x+123,y+72),
                 (x+143,y+67),(x+153,y+53)],ORANGE,ORANGE)
        a.label("fusion reaches",x+81,y+214,10.5,GREEN,align="center")
        a.label("bore-side root",x+81,y+230,10.5,GREEN,align="center")
    elif kind=="lap":
        a.ellipse(x+6,y+36,22,28,ORANGE,ORANGE)
        a.ellipse(x+134,y+36,22,28,ORANGE,ORANGE)
        a.line(x+27,y+57,x+39,y+57,ORANGE,3)
        a.line(x+123,y+57,x+135,y+57,ORANGE,3)
        a.arrow(x+76,y+120,x+39,y+58,BLUE,1.2)
        a.label("crevice opens",x+81,y+214,10.5,ORANGE,align="center")
        a.label("to water bore",x+81,y+230,10.5,ORANGE,align="center")
    else:
        a.shape([(x+35,y+57),(x+53,y+65),(x+64,y+86),(x+43,y+93)],ORANGE,ORANGE)
        a.shape([(x+123,y+57),(x+103,y+65),(x+92,y+86),(x+121,y+93)],ORANGE,ORANGE)
        a.ellipse(x+69,y+21,25,33,ORANGE,ORANGE)
        a.label("obstruction /",x+81,y+214,10.5,ORANGE,align="center")
        a.label("root contamination",x+81,y+230,10.5,ORANGE,align="center")


def roots(a):
    root_panel(a,4,36,"fused","TARGET SECTION")
    root_panel(a,186,36,"lap","OUTER BEAD ONLY")
    root_panel(a,368,36,"blocked","REJECT")
    a.label("section 1: through jet axis",17,329,11,BLUE)
    a.label("section 2: another tack / restart azimuth",17,350,11,BLUE)


def flow(a):
    a.label("CLEAN",24,27,12,BLUE)
    elbow(a,94,90,.65,True,False)
    a.arrow(94,43,94,65,BLUE,2)
    a.arrow(174,180,207,180,BLUE,2)
    a.label("COLLECT + TIME",260,27,12,BLUE,align="center")
    a.c.saveState();a.c.translate(257,172);a.c.rotate(180)
    elbow(a,0,0,.49,True,False)
    a.c.restoreState()
    a.arrow(166,102,185,102,BLUE,2)
    a.arrow(257,192,257,233,BLUE,2)
    a.shape([(214,219),(224,292),(295,292),(306,219)],None,BLUE,2)
    for j in [0,1,2]:a.line(284,236+j*16,295,236+j*16,BLUE,1)
    a.label("mass / time",260,327,11,BLUE,align="center")
    a.arrow(312,180,350,180,BLUE,2)
    a.label("INSTALL AT PORT 2",444,27,12,BLUE,align="center")
    a.rect(386,125,128,29,STEEL)
    a.rect(431,125,28,29,PAPER)
    a.rect(427,91,36,70,STEEL)
    a.rect(433,160,24,10,ORANGE)
    a.arrow(445,179,445,268,BLUE,2)
    a.label("CO2 headspace",444,298,11,BLUE,align="center")
    a.label("clear jet below inner plate face",444,346,10.5,BLUE,align="center")


def parameter_strip(a):
    for j,(title,value) in enumerate([("MODE","record"),("POWER","%"),("SWING","Hz / mm"),("WIRE","mm/s")]):
        x=6+j*135
        a.rect(x,12,123,70,ICE,BLUE)
        a.label(title,x+61,34,10,BLUE,align="center")
        a.label(value,x+61,65,14,BLUE,align="center")
    a.label("Pulse mode: also record emission time + interval",13,108,11,BLUE)
