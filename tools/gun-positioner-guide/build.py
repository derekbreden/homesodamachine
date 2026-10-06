#!/usr/bin/env python3
"""Build the current PGFUN shop guide with the shared Letter guide theme."""
from pathlib import Path
import hashlib, html, importlib.util, json, math, re, subprocess, sys, textwrap
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.font_manager import FontProperties
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, PageTemplate, Paragraph,
    Spacer, PageBreak, Table, TableStyle, Preformatted, Flowable, KeepTogether)
from reportlab.platypus.tableofcontents import TableOfContents
from fontTools.ttLib import TTFont as FontToolsFont
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[2]
CAD=ROOT/'hardware/printed-parts/fixtures/pgfun-positioner'
DEST=ROOT/'hardware/gun-positioner-guide'
DOC=ROOT/'hardware/gun-positioner'
ART=DEST/'art'
sys.path.insert(0,str(ROOT/'tools/assembly-guides'))
import common as theme
WIDTH=548
LINKBASE=DOC
INK=colors.HexColor(theme.INK)
BLUE=colors.HexColor(theme.BLUE)
ICE=colors.HexColor(theme.ICE)
RULE=colors.HexColor(theme.RULE)
MUTED=colors.HexColor(theme.MUTED)
CORAL=colors.HexColor('#d64050')
PAPER=colors.HexColor(theme.PAPER)
DOCS=[('assembly.md','Build the positioner'),('purchases.md','Parts and fasteners'),
      ('control.md','Wire the controller'),('commissioning.md','Commission the fixture'),
      ('observation.md','Learn with one camera'),('engineering.md','Engineering reference'),
      ('../../firmware/src_pgfun_positioner/README.md','Firmware and host commands')]
MONO_SOURCE=ROOT/'hardware/guide-assets/fonts/IBMPlexMono-400-normal-latin.woff2'
MONO_CACHE=ROOT/'.cache/pgfun-engineering/plex-mono.ttf'
MONO_CACHE.parent.mkdir(parents=True,exist_ok=True)
font=FontToolsFont(MONO_SOURCE);font.flavor=None;font.save(MONO_CACHE)
pdfmetrics.registerFont(TTFont('PlexMono',str(MONO_CACHE)))
FONT=FontProperties(fname=str(theme.FONT_DIR/'Plex-Regular.ttf'))

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(z):return {k[:-3]:(z[k],z[k[:-3]+'__f'])for k in z.files if k.endswith('__v')}

def figures():
    """Actual assembly surfaces; coral identifies the pieces used by an operation."""
    ART.mkdir(parents=True,exist_ok=True)
    meshes=load(np.load(CAD/'assembly-meshes.npz'))
    spec=importlib.util.spec_from_file_location('pgfun_check',CAD/'check.py')
    check=importlib.util.module_from_spec(spec);spec.loader.exec_module(check)
    mat=check.gun_transform()
    for n,(v,f)in load(np.load(CAD/'reference-meshes.npz')).items():
        if n.startswith('gun:'):v=v@mat[:3,:3].T+mat[:3,3]
        meshes[n]=(v,f)
    printed={p['name']for p in json.loads((CAD/'display-meshes.json').read_text())}
    scenes=[
      ('assembly',lambda n:not n.startswith(('camera','raynox','controller','fan','umbilical')),
       {'yaw-reducer':'Swivel drive','pitch-reducer':'Pivot drive','lower-cradle':'Gun supported below','rotator:recessed-cap':'Recessed tube joint'},
       {'yaw-reducer','pitch-reducer','lower-cradle'}),
      ('bridge',lambda n:n.startswith(('bridge','bench-toe','motor-pedestal','rotator:base')),
       {'bridge':'Printed bridge','bench-toe-1':'Bench toes','motor-pedestal':'Motor pedestal','rotator:base':'Existing base'},
       {'bridge','bench-toe-1','bench-toe-2','motor-pedestal'}),
      ('motors',lambda n:n in ('pitch-reducer','pitch-motor'),
       {'pitch-motor':'NEMA 17 motor','pitch-reducer':'PGFUN 50:1'}, {'pitch-reducer'}),
      ('yaw',lambda n:n.startswith(('motor-pedestal','yaw-'))and'holder'not in n and'stop'not in n,
       {'yaw-bearing-cartridge':'Bearing cartridge','yaw-journal':'Supported journal','yaw-reducer':'PGFUN 50:1','yaw-motor':'Motor below the base'},
       {'yaw-bearing-cartridge','yaw-journal','yaw-output-adapter','yaw-bearing-cap'}),
      ('pivot',lambda n:n.startswith(('fork','pitch-','left-cheek','right-cheek','bottom-frame','opposite-','axle-'))and'holder'not in n and'stop'not in n and'standoff'not in n,
       {'fork':'Fixed fork','left-cheek':'Driven cheek','right-cheek':'Opposite cheek','opposite-bearing-cap':'6001 bearing pair'},
       {'left-cheek','right-cheek','bottom-frame-tie'}),
      ('cradle',lambda n:n.startswith(('gun:','gun-retainer','liner-','lower-cradle','left-cheek','right-cheek','bottom-frame')),
       {'lower-cradle':'Lower cradle','gun-retainer-1':'Front housing band','gun-retainer-2':'Rear housing band'},
       {'lower-cradle','gun-retainer-1','gun-retainer-2'}),
      ('stops',lambda n:n in ('fork','left-cheek','yaw-bearing-cartridge','yaw-journal')or'stop-'in n or'limit-holder'in n or'standoff'in n,
       {'yaw-stop-sector':'Yaw positive stop','pitch-stop-sector':'Pitch positive stop','pitch-switch-standoff-1':'Pitch switch standoffs'},
       {'yaw-stop-sector','pitch-stop-sector','yaw-limit-holder-1','yaw-limit-holder--1','pitch-limit-holder-1','pitch-limit-holder--1'}),
      ('camera',lambda n:n.startswith(('camera','raynox','rotator:spool','rotator:recessed-cap','rotator:tube-nest')),
       {'camera-riser-base':'Level camera base','camera-riser-top':'Camera tray','camera-lens-upright':'Macro carrier','camera-lens-cassette':'Raynox cassette'},
       {'camera-lens-upright','camera-lens-cassette','camera-lens-retainer'}),
      ('controller',lambda n:n.startswith(('controller','fan','umbilical')),
       {'controller-case':'SKR Pico case','fan-guard':'24 V fan guard','umbilical-saddle':'Cable saddle','umbilical-post-base':'Open service bore'},
       {'controller-case','umbilical-saddle'})]
    for file,select,labels,active in scenes:
        names=[n for n in meshes if select(n)]
        view=np.array([1.15,-1.8,1.05]);view/=np.linalg.norm(view)
        right=np.cross([0,0,1],view);right/=np.linalg.norm(right)
        basis=np.stack([right,np.cross(view,right),view],axis=1)
        polys=[];depth=[];fills=[];centres={}
        for n in names:
            v,f=meshes[n];q=v@basis;centres[n]=q[:,:2].mean(axis=0)
            tris=q[f];normal=np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]])
            normal/=np.maximum(np.linalg.norm(normal,axis=1)[:,None],1e-9)
            base=np.array([.26,.28,.34])if n in printed else np.array([.69,.73,.80])
            if n.startswith('gun:'):base=np.array([.20,.22,.28])
            if n.startswith('rotator:'):base=np.array([.73,.77,.84])
            if n.startswith('liner-'):base=np.array([.13,.14,.18])
            if n in active:base=np.array([.84,.25,.31])
            light=.66+.34*np.maximum(0,normal@np.array([.3,-.4,.85]))
            polys.extend(tris[:,:,:2]);depth.extend(tris[:,:,2].mean(axis=1));fills.extend(np.clip(light[:,None]*base,0,1))
        order=np.argsort(depth);polys=np.asarray(polys)
        fig,ax=plt.subplots(figsize=(10,5.8));fig.patch.set_alpha(0);ax.patch.set_alpha(0)
        ax.add_collection(PolyCollection(polys[order],facecolors=np.asarray(fills)[order],edgecolors='none',rasterized=True))
        bounds=np.vstack([meshes[n][0]@basis for n in names]);lo=bounds[:,:2].min(axis=0);hi=bounds[:,:2].max(axis=0)
        pad=(hi-lo)*.07;ax.set_xlim(lo[0]-pad[0],hi[0]+pad[0]);ax.set_ylim(lo[1]-pad[1],hi[1]+pad[1]);ax.set_aspect('equal');ax.axis('off')
        for i,(n,label)in enumerate(labels.items()):
            if n not in centres:continue
            side=-1 if i%2==0 else 1
            target=(lo[0]-.10*(hi[0]-lo[0])if side<0 else hi[0]+.10*(hi[0]-lo[0]),hi[1]-(i+.45)/(len(labels)+.2)*(hi[1]-lo[1]))
            ax.annotate(label,centres[n],xytext=target,ha='right'if side<0 else'left',va='center',fontsize=13,fontproperties=FONT,color=theme.INK,
                        arrowprops=dict(arrowstyle='-',color=theme.MUTED,lw=.8),annotation_clip=False)
        fig.subplots_adjust(left=.26,right=.76,bottom=.06,top=.96)
        fig.savefig(ART/f'{file}.png',dpi=220,transparent=True);plt.close(fig)
    return scenes

ST={
 'body':ParagraphStyle('body',fontName='Plex',fontSize=11,leading=14.8,textColor=INK,spaceAfter=7),
 'engineering':ParagraphStyle('engineering',fontName='Plex',fontSize=11,leading=14.4,textColor=INK,spaceAfter=5),
 'small':ParagraphStyle('small',fontName='Plex',fontSize=9.4,leading=12.1,textColor=INK,spaceAfter=4),
 'caption':ParagraphStyle('caption',fontName='Plex',fontSize=9.6,leading=12.5,textColor=MUTED,spaceAfter=12),
 'chapter':ParagraphStyle('chapter',fontName='PlexBold',fontSize=30,leading=33,textColor=INK,spaceAfter=14,keepWithNext=True),
 'section':ParagraphStyle('section',fontName='PlexBold',fontSize=17,leading=21,textColor=BLUE,spaceBefore=13,spaceAfter=8,keepWithNext=True),
 'operation':ParagraphStyle('operation',fontName='PlexBold',fontSize=27,leading=30,textColor=INK,spaceAfter=12,keepWithNext=True),
 'minor':ParagraphStyle('minor',fontName='PlexSemi',fontSize=12.2,leading=16,textColor=BLUE,spaceBefore=10,spaceAfter=6,keepWithNext=True),
 'parts':ParagraphStyle('parts',fontName='Plex',fontSize=9.9,leading=13,textColor=INK),
 'code':ParagraphStyle('code',fontName='PlexMono',fontSize=8.5,leading=11.2,textColor=INK,spaceAfter=10),
 'cover':ParagraphStyle('cover',fontName='PlexBold',fontSize=40,leading=42,textColor=INK,spaceAfter=16),
 'lede':ParagraphStyle('lede',fontName='Plex',fontSize=14,leading=19,textColor=MUTED,spaceAfter=14),
}

class Rule(Flowable):
    def __init__(self):super().__init__();self.width=WIDTH;self.height=12
    def draw(self):self.canv.setFillColor(BLUE);self.canv.roundRect(0,7,30,3,1.5,stroke=0,fill=1)

class Panel(Flowable):
    def __init__(self,title,body,kind='note'):
        super().__init__();self.title=title;self.body=Paragraph(body,ST['parts']);self.kind=kind;self.width=WIDTH
    def wrap(self,w,h):
        self.width=w;_,bh=self.body.wrap(w-30,h);self.height=bh+43;return w,self.height
    def draw(self):
        c=self.canv;c.setFillColor(ICE);c.setStrokeColor(BLUE if self.kind=='check'else RULE);c.setLineWidth(1)
        c.roundRect(0,0,self.width,self.height,7,fill=1,stroke=self.kind=='check')
        if self.kind=='mind':c.setFillColor(colors.HexColor(theme.ORANGE));c.rect(0,0,3,self.height,stroke=0,fill=1)
        c.setFillColor(BLUE);c.setFont('PlexBold',9.5);c.drawString(14,self.height-18,self.title.upper())
        self.body.drawOn(c,14,12)

class CadFigure(Flowable):
    def __init__(self,file,caption,height=254):
        super().__init__();self.file=file;self.caption=Paragraph(caption,ST['caption']);self.picture_height=height;self.width=WIDTH;self.spaceAfter=8
    def wrap(self,w,h):
        self.width=w;_,ch=self.caption.wrap(w-24,h);self.height=self.picture_height+ch+30;return w,self.height
    def draw(self):
        c=self.canv;_,ch=self.caption.wrap(self.width-24,100)
        c.setFillColor(colors.HexColor('#f5f8ff'));c.setStrokeColor(RULE);c.setLineWidth(.6)
        c.roundRect(0,ch+14,self.width,self.picture_height+12,7,fill=1,stroke=1)
        c.drawImage(str(ART/(self.file+'.png')),9,ch+20,width=self.width-18,height=self.picture_height,preserveAspectRatio=True,anchor='c',mask='auto')
        self.caption.drawOn(c,12,0)

class WiringFigure(Flowable):
    """Connector-level diagram. Exact pin order remains in the harness schedule."""
    def __init__(self):super().__init__();self.width=WIDTH;self.height=244
    def draw(self):
        c=self.canv;c.setFillColor(colors.HexColor('#f5f8ff'));c.roundRect(0,0,WIDTH,244,7,stroke=0,fill=1)
        def node(x,y,w,h,title,body):
            c.setFillColor(PAPER);c.setStrokeColor(RULE);c.roundRect(x,y,w,h,5,fill=1,stroke=1)
            c.setFont('PlexBold',10);c.setFillColor(BLUE);c.drawString(x+9,y+h-17,title)
            p=Paragraph(body,ST['small']);_,ph=p.wrap(w-18,h-20);p.drawOn(c,x+9,y+h-23-ph)
        def line(points):
            c.setStrokeColor(MUTED);c.setLineWidth(1.2)
            for a,b in zip(points,points[1:]):c.line(*a,*b)
        node(190,57,164,132,'SKR PICO V1.0','X / yaw<br/>Y / pitch<br/>FAN3 / 24 V cooling<br/>TH0 / supply divider<br/>USB / motion host')
        node(12,183,142,48,'24 V / 4 A','VIN+ and VIN-')
        node(12,111,142,54,'MAC + ANKER 332','Camera USB3 + board USB')
        node(12,26,142,67,'NC INPUT LOOPS','X-STOP / GPIO4<br/>Y-STOP / GPIO3<br/>Z-STOP / GPIO25')
        node(390,177,145,53,'YAW MOTOR','X / four coil leads')
        node(390,111,145,53,'PITCH MOTOR','Y / four coil leads')
        node(390,26,145,67,'ROTATOR PEDAL','E0-STOP / GPIO16<br/>NO signal + shared GND')
        line([(154,207),(172,207),(172,177),(190,177)])
        line([(154,138),(190,138)])
        line([(154,58),(174,58),(174,94),(190,94)])
        line([(354,175),(372,175),(372,203),(390,203)])
        line([(354,141),(390,141)])
        line([(354,94),(372,94),(372,58),(390,58)])
        c.setFont('Plex',9);c.setFillColor(MUTED);c.drawString(191,22,'SIG/GND only at stop inputs; remove all DIAG jumpers.')

class CutFigure(Flowable):
    """The specified M3 cutting fixture, drawn as a labelled schematic."""
    def __init__(self):super().__init__();self.width=WIDTH;self.height=174;self.spaceAfter=12
    def draw(self):
        c=self.canv;c.setFillColor(colors.HexColor('#f5f8ff'));c.roundRect(0,0,WIDTH,174,7,stroke=0,fill=1)
        c.setFillColor(BLUE);c.setFont('PlexBold',9.5);c.drawString(12,157,'SHORTEN M3 STOCK / SCHEMATIC')
        c.setStrokeColor(MUTED);c.setFillColor(colors.HexColor(theme.STEEL));c.setLineWidth(1)
        c.roundRect(68,83,18,40,2,fill=1,stroke=1);c.rect(86,96,380,14,fill=1,stroke=1)
        for x in range(92,465,7):c.line(x,96,x+5,110)
        def nut(x,r):
            p=c.beginPath()
            for i in range(6):
                a=math.pi*i/3;point=(x+r*math.cos(a),103+r*math.sin(a))
                if i==0:p.moveTo(*point)
                else:p.lineTo(*point)
            p.close();c.setFillColor(colors.HexColor(theme.STEEL));c.drawPath(p,fill=1,stroke=1)
        nut(153,16);nut(342,21)
        c.setFillColor(colors.HexColor('#9aa4b5'));c.rect(317,124,50,10,fill=1,stroke=1);c.rect(317,72,50,10,fill=1,stroke=1)
        c.setStrokeColor(CORAL);c.setLineWidth(2);c.setDash(4,2);c.line(342,87,342,143);c.setDash([])
        c.setStrokeColor(MUTED);c.setLineWidth(.8);c.line(153,122,126,139);c.line(363,115,412,139);c.line(368,78,414,66)
        c.setFillColor(INK);c.setFont('Plex',9.4);c.drawString(82,141,'Backing nut');c.drawString(395,141,'Steel cutting nut');c.drawString(397,53,'Saw vise jaws')
        c.setStrokeColor(BLUE);c.line(86,52,342,52);c.line(86,47,86,63);c.line(342,47,342,63)
        c.setFillColor(BLUE);c.setFont('PlexSemi',9.4);c.drawCentredString(214,36,'Measure finished under-head length')
        c.setFillColor(MUTED);c.setFont('Plex',9);c.drawString(12,14,'Cut through the sacrificial nut and screw; deburr, then back the other nut over the end.')

class LearningFigure(Flowable):
    def __init__(self):super().__init__();self.width=WIDTH;self.height=140
    def draw(self):
        c=self.canv
        nodes=[('OBSERVE','Actual dot, wire and seam'),('LEARN','Loaded motion + reversals'),('VALIDATE','Two independent dry runs'),('REPLAY','Indexed rotator + factory trigger')]
        for i,(title,body)in enumerate(nodes):
            x=i*138;c.setFillColor(ICE);c.roundRect(x,48,126,81,6,stroke=0,fill=1)
            c.setFont('PlexBold',9.5);c.setFillColor(BLUE);c.drawString(x+10,110,title)
            p=Paragraph(body,ST['small']);_,ph=p.wrap(106,50);p.drawOn(c,x+10,100-ph)
            if i<3:
                c.setStrokeColor(CORAL);c.setLineWidth(1.5);c.line(x+127,86,x+136,86);c.line(x+132,89,x+136,86);c.line(x+132,83,x+136,86)
        p=Paragraph('One camera measures projected error during dry learning. Withdraw the stand before emission.',ST['caption']);p.wrap(WIDTH,32);p.drawOn(c,0,12)

class GuideDoc(BaseDocTemplate):
    def __init__(self,pdf):
        super().__init__(str(pdf),pagesize=(612,792),title='PGFUN two-axis weld positioner',author='Home Soda Machine',allowSplitting=True)
        frame=Frame(32,64,WIDTH,660,id='body',leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)
        self.addPageTemplates(PageTemplate(id='shop',frames=[frame],onPage=self.start_page,onPageEnd=self.finish_page))
        self.outline=[]
    def beforeDocument(self):
        self.outline=[];self.current_chapter=None;self.current_operation=None
    def start_page(self,c,d):
        self.heading_on_current_page=False
        theme.page_backdrop(c);c.saveState();c.translate(612*.01,792*.01);c.scale(.98,.98)
        theme.text(c,'HOME SODA MACHINE / GUN POSITIONER',32,35,9.5,'PlexSemi',theme.BLUE)
        theme.text(c,f'R1 / {d.page:02d}',580,35,10,'PlexSemi',theme.MUTED,'right')
    def finish_page(self,c,d):
        if not self.heading_on_current_page and self.current_chapter:
            theme.text(c,self.current_operation or self.current_chapter,32,56,9.4,'PlexSemi',theme.BLUE)
        theme.footer(c,d.page,'PGFUN swivel + pivot | shop guide | 8.5 x 11 inches','https://homesodamachine.com/drawings');c.restoreState()
    def afterFlowable(self,f):
        if not isinstance(f,Paragraph)or not hasattr(f,'outline_key'):return
        key=f.outline_key;title=f.getPlainText();level=f.outline_level
        self.heading_on_current_page=True
        if level==0:self.current_chapter=title;self.current_operation=None
        else:self.current_operation=title
        self.canv.bookmarkPage(key);self.canv.addOutlineEntry(title,key,level=level,closed=False)
        self.outline.append(dict(title=title,page=self.page,level=level,key=key))
        if level==0:self.notify('TOCEntry',(0,title,self.page,key))

def heading(text,style='section',key=None,level=0):
    p=Paragraph(inline(text),ST[style])
    if key:p.outline_key=key;p.outline_level=level
    return p

def inline(s):
    for a,b in [('°',' degrees'),('µ','u'),('×','x'),('–','-'),('—','-'),('≤','<='),('≥','>='),('σ','sigma')]:s=s.replace(a,b)
    s=html.escape(s)
    def link(m):
        href=m[2]
        if not href.startswith(('http:','https:')):
            path,_,anchor=href.partition('#');rel=(LINKBASE/path).resolve().relative_to(ROOT).as_posix()
            if rel.endswith('.step'):href='https://homesodamachine.com/steps/'+rel.removeprefix('hardware/')
            elif rel.endswith(('.zip','.uf2')):href='https://raw.githubusercontent.com/derekbreden/homesodamachine/main/'+rel
            else:href='https://github.com/derekbreden/homesodamachine/blob/main/'+rel
            if anchor:href+='#'+anchor
        return f'<link color="{theme.BLUE}" href="{href}">{m[1]}</link>'
    s=re.sub(r'\[([^]]+)\]\(([^)]+)\)',link,s)
    s=re.sub(r'\*\*([^*]+)\*\*',r'<b>\1</b>',s)
    return re.sub(r'`([^`]+)`',r'<font name="PlexMono">\1</font>',s)

OPERATION_ART={
 1:('bridge','Coral shows the bridge, bench toes and pedestal added to the stationary rotator base.'),
 2:('motors','Each drive uses one NEMA 17 motor and one PGFUN 50:1 reducer. Remove the input flange to reach the motor screws.'),
 3:('yaw','The supported journal and cartridge carry the fixture load. Align the reducer case after the bearing stack is seated.'),
 4:('pivot','Coral shows the driven and opposite cheeks and the bottom tie. Both sides support the cradle.'),
 5:('cradle','Two lined housing bands retain the gun. The lower cradle carries its weight; the forward shoulder stops axial sliding.'),
 6:('stops','Coral marks the positive-stop sectors and switch holders. Set switch opening before either mechanical stop.'),
 7:('controller','The cable post unloads the gun-side cable. Its central bore remains open for inspection and support removal.'),
 8:('camera','The camera base stays level. The head and macro cassette look down at 29 degrees during dry observation.'),
}
OPERATION_TITLES={
 1:'1. Mount the bridge',
 2:'2. Assemble the motor drives',
 3:'3. Install the swivel',
 4:'4. Install the horizontal pivot',
 5:'5. Secure the gun from below',
 6:'6. Set stops and switches',
 7:'7. Support cables and controller',
 8:'8. Set up the camera',
}

def table(rows,widths=None):
    n=max(map(len,rows));widths=widths or [WIDTH/n]*n
    data=[[Paragraph(inline(cell),ST['small'])for cell in row]for row in rows]
    t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT',rowSplitRange=(2,len(data)-2)if len(data)>6 else None)
    t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('BACKGROUND',(0,0),(-1,0),ICE),
        ('LINEBELOW',(0,0),(-1,0),1,BLUE),('LINEBELOW',(0,1),(-1,-1),.45,RULE),
        ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
        ('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7)]))
    return t

def action(number,text):
    number=Paragraph(f'<font color="{theme.BLUE}"><b>{number:02d}</b></font>',ST['body'])
    p=Paragraph(inline(text),ST['body'])
    t=Table([[number,p]],colWidths=[32,WIDTH-32],hAlign='LEFT')
    t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0),('TOPPADDING',(0,0),(-1,-1),1),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
    return t

def markdown(path,label,key):
    global LINKBASE
    LINKBASE=path.parent
    lines=path.read_text().splitlines();out=[heading(label,'chapter',key),Rule()];i=0
    body_style=ST['engineering'] if path.name=='engineering.md' else ST['body']
    references=False;assembly_operation=False
    if path.name=='control.md':out.extend([WiringFigure(),Spacer(1,12)])
    if path.name=='observation.md':out.extend([LearningFigure(),Spacer(1,4)])
    while i<len(lines):
        line=lines[i]
        if not line.strip():i+=1;continue
        if line.startswith('# '):i+=1;continue
        if line.startswith('```'):
            i+=1;code=[]
            while i<len(lines)and not lines[i].startswith('```'):
                code.extend(textwrap.wrap(lines[i],width=96,replace_whitespace=False,drop_whitespace=False)or['']);i+=1
            out.append(KeepTogether([Preformatted('\n'.join(code),ST['code'])]));i+=1;continue
        if line.startswith('|'):
            rows=[]
            while i<len(lines)and lines[i].startswith('|'):
                cells=[s.strip()for s in lines[i].strip('|').split('|')]
                if not all(re.fullmatch(r':?-+:?',c.replace(' ',''))for c in cells):rows.append(cells)
                i+=1
            n=max(map(len,rows));widths=None
            if n==3:widths=[WIDTH*.25,WIDTH*.40,WIDTH*.35]
            elif n==4:widths=[WIDTH*.43,WIDTH*.13,WIDTH*.20,WIDTH*.24]
            elif n==5:
                widths=[73,55,87,100,233] if rows[0][0]=='Screw' else [220,30,65,65,168]
            out.extend([table(rows,widths),Spacer(1,12)]);continue
        h=re.match(r'^(#{2,3}) (.*)',line)
        if h:
            text=h[2];op=re.match(r'([1-8])\. (.*)',text)if path.name=='assembly.md'else None
            if op:
                assembly_operation=True
                num=int(op[1]);image,caption=OPERATION_ART[num]
                out.extend([PageBreak(),heading(OPERATION_TITLES[num],'operation',f'assembly-step-{num}',1),Rule(),CadFigure(image,caption,height=200 if num==1 else 254)])
            else:
                references=path.name=='engineering.md' and text=='Manufacturer references'
                out.append(heading(text,'minor' if references or len(h[1])==3 else 'section'))
            i+=1;continue
        para=[line];i+=1
        while i<len(lines)and lines[i].strip()and not re.match(r'^(#|\||```|[-*] |\d+\. )',lines[i]):para.append(lines[i].strip());i+=1
        text=' '.join(para)
        numbered=re.match(r'^(\d+)\. (.*)',text)
        if numbered:out.append(action(int(numbered[1]),numbered[2]))
        elif text.startswith('Parts:'):out.extend([Panel('At this operation',inline(text[6:].strip())),Spacer(1,12)])
        elif text.startswith('Ready check:'):out.extend([Spacer(1,6),Panel('Ready check',inline(text[12:].strip()),'check')])
        elif text.startswith('- '):out.append(Paragraph('&#8226; '+inline(text[2:]),ST['small'] if references else body_style))
        else:
            p=Paragraph(inline(text),body_style)
            if path.name=='assembly.md' and text.startswith('Cut two purchased M8x80'):
                out.append(KeepTogether([CutFigure(),p]))
            elif path.name=='assembly.md' and assembly_operation:
                out.append(KeepTogether([p]))
            else:out.append(p)
    return out

def make_story():
    story=[Paragraph('Gun positioner<br/>assembly guide',ST['cover']),Rule(),
           Paragraph('Two coaxial PGFUN 50:1 drives.<br/>Swivel base, horizontal pivot, gun supported from below.',ST['lede']),
           CadFigure('assembly','The fixture mounts to the existing rotator base. Coral identifies the two drives and lower housing cradle.',height=306),
           Panel('One complete build','$479.36 mechanism/controller + $524.50 camera/lens = <b>$1,003.86</b> before tax. Prime prices observed October 5, 2026.'),
           Spacer(1,13),Paragraph('Printing, assembly, wiring and one-camera dry-run learning',ST['lede']),PageBreak()]
    story.extend([heading('Find the operation','chapter'),Rule(),Paragraph('Build in order, use the picture at each operation, and complete its visible check before continuing.',ST['lede'])])
    toc=TableOfContents();toc.levelStyles=[ParagraphStyle('toc',fontName='PlexSemi',fontSize=13.5,leading=19,textColor=BLUE,spaceBefore=10,leftIndent=0,rightIndent=0)]
    story.extend([toc,Spacer(1,14),Panel('Read the pictures','Coral identifies the parts used by the operation. Dark grey is the printed fixture and gun; light grey is the existing rotator or purchased hardware. CAD dimensions and the print manifest govern the build.'),Spacer(1,12),
      Panel('Set the working pose','The 60-degree attitude and 16 mm nozzle gap are editable print parameters. Establish welding focus and attitude on a sacrificial joint, then record the accepted setup. Use the supplied STL orientation.','mind'),Spacer(1,12),
      Paragraph('Print at 100% on Letter, single-sided. The content is centered at 98%; cobalt and coral bands have their own bleed layer. Select the matching paper profile and rear feeder for Epson Letter borderless printing.',ST['caption'])])
    for index,(path,label)in enumerate(DOCS):
        story.append(PageBreak());story.extend(markdown((DOC/path).resolve(),label,f'chapter-{index}'))
    story.extend([PageBreak(),heading('Print manifest','chapter','print-manifest'),Rule(),
      Paragraph('All 60 STLs have their bed orientation. The six bearing coupons and optional lens shim are included. Solid-equivalent mass excludes supports, brim and purge.',ST['body'])])
    parts=json.loads((CAD/'print-manifest.json').read_text())['parts']
    rows=[['Part / material','Size X x Y x Z (mm)','Solid g','Supports']]
    for p in parts:rows.append([p['name']+' / '+p['material'],' x '.join(f'{v:g}'for v in p['print_bounds_mm']),f"{p['solid_mass_g']:.1f}",'Yes'if p['support_required']else'No'])
    story.append(table(rows,[220,180,74,74]))
    return story

def main():
    DEST.mkdir(exist_ok=True);figures();pdf=DEST/'gun-positioner-guide.pdf'
    doc=GuideDoc(pdf);doc.multiBuild(make_story())
    pages=len(PdfReader(pdf).pages)
    subprocess.run(['pdftoppm','-f','1','-singlefile','-scale-to-x','800','-scale-to-y','-1','-png',str(pdf),str(DEST/'gun-positioner-guide.cover')],check=True)
    from PIL import Image as PILImage
    size=PILImage.open(DEST/'gun-positioner-guide.cover.png').size
    (DEST/'gun-positioner-guide.pdf.json').write_text(json.dumps(dict(title='PGFUN two-axis weld positioner',subtitle=f'Illustrated shop guide - {pages} pages, Letter 8.5 x 11 in',pages=pages,cover='gun-positioner-guide.cover.png',cover_size=size),indent=2)+'\n')
    sources=[(DOC/p).resolve()for p,_ in DOCS]+[CAD/'motion-geometry.json',CAD/'print-manifest.json',CAD/'assembly-meshes.npz',CAD/'reference-meshes.npz',Path(__file__),Path(theme.__file__),MONO_SOURCE]+list(theme.FONT_DIR.glob('*.ttf'))
    receipt=dict(geometry_sha256=json.loads((CAD/'motion-geometry.json').read_text())['sha256'],sources={str(p.relative_to(ROOT)):sha(p)for p in sources},pdf_sha256=sha(pdf),pages=pages,
        theme='Shared Letter shop-guide theme: IBM Plex, cobalt/coral bleed bands, ice panels',
        print_layout=dict(content_scale=.98,bleed_overhang_inches=.25,colored_band_inset_inches=1/3,print_scaling='100% / none'),
        outline=doc.outline,scope='Source-complete illustrated instructions and current CAD; physical results recorded separately.')
    (DEST/'source-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(pages=pages,pdf=str(pdf),sha256=sha(pdf))))
if __name__=='__main__':main()
