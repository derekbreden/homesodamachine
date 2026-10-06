#!/usr/bin/env python3
"""Render current PGFUN CAD and governing instructions into the shop PDF."""
from pathlib import Path
import hashlib, html, importlib.util, json, re, subprocess, textwrap
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image, Table, TableStyle, Preformatted
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[2]
CAD=ROOT/'hardware/printed-parts/fixtures/pgfun-positioner'
DEST=ROOT/'hardware/gun-positioner-guide'
DOC=ROOT/'hardware/gun-positioner'
ART=DEST/'art'
WIDTH=468
LINKBASE=DOC
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(z):return {k[:-3]:(z[k],z[k[:-3]+'__f'])for k in z.files if k.endswith('__v')}
def figures():
    ART.mkdir(parents=True,exist_ok=True)
    meshes=load(np.load(CAD/'assembly-meshes.npz'))
    spec=importlib.util.spec_from_file_location('pgfun_check',CAD/'check.py')
    check=importlib.util.module_from_spec(spec);spec.loader.exec_module(check)
    mat=check.gun_transform()
    for n,(v,f) in load(np.load(CAD/'reference-meshes.npz')).items():
        if n.startswith('gun:'):v=v@mat[:3,:3].T+mat[:3,3]
        meshes[n]=(v,f)
    printed={p['name']for p in json.loads((CAD/'display-meshes.json').read_text())}
    scenes=[
      ('assembly','Fixture and recessed joint',lambda n:not n.startswith(('camera','raynox','controller','fan','umbilical')),['bridge','fork','lower-cradle','pitch-motor','rotator:recessed-cap']),
      ('bridge','Base bridge and vertical swivel',lambda n:n.startswith(('bridge','bench-toe','motor-pedestal','yaw-','rotator:base')),['bridge','motor-pedestal','yaw-bearing-cartridge']),
      ('pivot','Supported horizontal pivot',lambda n:n.startswith(('fork','pitch-','left-cheek','right-cheek','bottom-frame','opposite-','axle-')),['fork','pitch-journal','left-cheek','right-cheek','opposite-bearing-cap']),
      ('cradle','Housing grip from below',lambda n:n.startswith(('gun:','gun-retainer','liner-','lower-cradle','left-cheek','right-cheek','bottom-frame')),['lower-cradle','gun-retainer-1','gun-retainer-2']),
      ('stops','Positive stops and switch mounts',lambda n:n in ('fork','left-cheek','yaw-bearing-cartridge','yaw-journal')or 'stop-'in n or 'limit-holder'in n or 'standoff'in n,['yaw-stop-sector','pitch-stop-sector','pitch-switch-standoff-1']),
      ('camera','Level camera base and tilted macro cassette',lambda n:n.startswith(('camera','raynox','rotator:spool','rotator:recessed-cap','rotator:tube-nest')),['camera-riser-base','camera-riser-top','camera-lens-upright','camera-lens-cassette']),
      ('controller','Controller case and cable support',lambda n:n.startswith(('controller','fan','umbilical')),['controller-case','fan-guard','umbilical-saddle'])]
    for file,title,select,labels in scenes:
        names=[n for n in meshes if select(n)]
        view=np.array([1.15,-1.8,1.05]);view/=np.linalg.norm(view)
        right=np.cross([0,0,1],view);right/=np.linalg.norm(right)
        basis=np.stack([right,np.cross(view,right),view],axis=1)
        polys=[];depth=[];fills=[];centres={}
        for n in names:
            v,f=meshes[n];q=v@basis;centres[n]=q[:,:2].mean(axis=0)
            tris=q[f];normal=np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]])
            normal/=np.maximum(np.linalg.norm(normal,axis=1)[:,None],1e-9)
            base=np.array([.22,.40,.44])if n in printed else np.array([.66,.69,.71])
            if n.startswith('gun:'):base=np.array([.38,.39,.42])
            if n.startswith('rotator:'):base=np.array([.76,.77,.77])
            if n.startswith('liner-'):base=np.array([.18,.18,.19])
            light=.65+.35*np.maximum(0,normal@np.array([.3,-.4,.85]))
            polys.extend(tris[:,:,:2]);depth.extend(tris[:,:,2].mean(axis=1));fills.extend(np.clip(light[:,None]*base,0,1))
        order=np.argsort(depth);polys=np.asarray(polys)
        fig,ax=plt.subplots(figsize=(9,6));fig.patch.set_facecolor('white')
        ax.add_collection(PolyCollection(polys[order],facecolors=np.asarray(fills)[order],edgecolors='none',rasterized=True))
        bounds=np.vstack([meshes[n][0]@basis for n in names]);lo=bounds[:,:2].min(axis=0);hi=bounds[:,:2].max(axis=0)
        pad=(hi-lo)*.18;ax.set_xlim(lo[0]-pad[0],hi[0]+pad[0]);ax.set_ylim(lo[1]-pad[1],hi[1]+pad[1]);ax.set_aspect('equal');ax.axis('off')
        for i,n in enumerate(labels):
            if n not in centres:continue
            side=-1 if i%2==0 else 1
            target=(lo[0]-.06*(hi[0]-lo[0])if side<0 else hi[0]+.06*(hi[0]-lo[0]),hi[1]-(i+.4)/(len(labels)+.4)*(hi[1]-lo[1]))
            ax.annotate(n.replace('rotator:','').replace('-',' '),centres[n],xytext=target,ha='right'if side<0 else'left',va='center',fontsize=10,color='#183b40',arrowprops=dict(arrowstyle='-',color='#718b8f',lw=.7))
        fig.subplots_adjust(left=.18,right=.82,bottom=.04,top=.97);fig.savefig(ART/f'{file}.png',dpi=200);plt.close(fig)
    return scenes
def inline(s):
    for a,b in [('°',' degrees'),('µ','u'),('×','x'),('–','-'),('—','-'),('≤','<='),('≥','>='),('σ','sigma')]:s=s.replace(a,b)
    s=html.escape(s)
    def link(m):
        href=m[2]
        if not href.startswith(('http:','https:')):
            path,_,anchor=href.partition('#');rel=(LINKBASE/path).resolve().relative_to(ROOT).as_posix()
            if rel.endswith('.step'):
                href='https://homesodamachine.com/steps/'+rel.removeprefix('hardware/')
            elif rel.endswith(('.zip','.uf2')):
                href='https://raw.githubusercontent.com/derekbreden/homesodamachine/main/'+rel
            else:href='https://github.com/derekbreden/homesodamachine/blob/main/'+rel
            if anchor:href+='#'+anchor
        return f'<link href="{href}">{m[1]}</link>'
    s=re.sub(r'\[([^]]+)\]\(([^)]+)\)',link,s)
    s=re.sub(r'\*\*([^*]+)\*\*',r'<b>\1</b>',s)
    return re.sub(r'`([^`]+)`',r'<font name="Courier">\1</font>',s)
ST=getSampleStyleSheet()
ST.add(ParagraphStyle(name='BodyShop',fontName='Helvetica',fontSize=9.5,leading=13.5,spaceAfter=7))
ST.add(ParagraphStyle(name='SmallShop',fontName='Helvetica',fontSize=8,leading=10.5,spaceAfter=4))
ST.add(ParagraphStyle(name='CodeShop',fontName='Courier',fontSize=7.5,leading=10,spaceAfter=10))
ST['Heading1'].fontSize=22;ST['Heading1'].leading=26;ST['Heading1'].textColor=colors.HexColor('#173c43')
ST['Heading2'].fontSize=13;ST['Heading2'].leading=17;ST['Heading2'].spaceBefore=12
ST['Heading3'].fontSize=10.5;ST['Heading3'].leading=14
ST['Heading3'].keepWithNext=True
def markdown(path):
    global LINKBASE
    LINKBASE=path.parent
    lines=path.read_text().splitlines();out=[];i=0
    while i<len(lines):
        line=lines[i]
        if not line.strip():i+=1;continue
        if line.startswith('```'):
            i+=1;code=[]
            while i<len(lines)and not lines[i].startswith('```'):
                code.extend(textwrap.wrap(lines[i],width=102,replace_whitespace=False,drop_whitespace=False)or['']);i+=1
            out.append(Preformatted('\n'.join(code),ST['CodeShop']));i+=1;continue
        if line.startswith('|'):
            rows=[]
            while i<len(lines)and lines[i].startswith('|'):
                cells=[s.strip()for s in lines[i].strip('|').split('|')]
                if not all(re.fullmatch(r':?-+:?',c.replace(' ',''))for c in cells):rows.append(cells)
                i+=1
            n=max(map(len,rows));widths=[WIDTH/n]*n
            if n==3:widths=[WIDTH*.28,WIDTH*.40,WIDTH*.32]
            if n==4:widths=[WIDTH*.43,WIDTH*.13,WIDTH*.20,WIDTH*.24]
            data=[[Paragraph(inline(c),ST['SmallShop'])for c in r]for r in rows]
            t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT',rowSplitRange=(2,len(data)-3)if len(data)>6 else None)
            t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#eaf0f0')),('LINEBELOW',(0,0),(-1,-1),.25,colors.HexColor('#c8d7d8')),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]));out.extend([t,Spacer(1,10)]);continue
        h=re.match(r'^(#{1,3}) (.*)',line)
        if h:out.append(Paragraph(inline(h[2]),ST[f'Heading{len(h[1])}']));i+=1;continue
        para=[line];i+=1
        while i<len(lines)and lines[i].strip()and not re.match(r'^(#|\||```|[-*] |\d+\. )',lines[i]):para.append(lines[i].strip());i+=1
        out.append(Paragraph(inline(' '.join(para)),ST['BodyShop']))
    return out
def footer(c,d):
    c.setStrokeColor(colors.HexColor('#c8d7d8'));c.line(72,44,540,44);c.setFont('Helvetica',8);c.setFillColor(colors.HexColor('#536b70'))
    c.drawString(72,30,'PGFUN two-axis weld positioner | R1');c.drawRightString(540,30,str(d.page))
def main():
    DEST.mkdir(exist_ok=True);scenes=figures()
    story=[Paragraph('PGFUN two-axis<br/>weld positioner',ST['Title']),Spacer(1,8),Paragraph('Swivel base. Horizontal pivot. Gun supported from below.',ST['BodyShop']),Image(str(ART/'assembly.png'),width=WIDTH,height=312),Spacer(1,10),Paragraph('Assembly, wiring, controller and one-camera dry-run learning',ST['Heading2']),Paragraph('Build release R1 | October 2026',ST['BodyShop']),Paragraph('New purchases: $479.36 mechanism/controller + $524.50 camera/lens = $1,003.86 before tax. Prime prices observed October 5, 2026.',ST['BodyShop']),PageBreak()]
    docs=[('assembly.md','Assembly'),('purchases.md','Purchases and fasteners'),('control.md','Electrical control'),('commissioning.md','Loaded commissioning'),('observation.md','One-camera learning'),('engineering.md','Engineering'),('../../firmware/src_pgfun_positioner/README.md','Firmware and host commands')]
    story.extend([Paragraph('Using this guide',ST['Heading1']),Paragraph('Follow assembly, control commissioning and optical commissioning in order. Use the STL files without automatic reorientation. The source documents and release receipts in hardware/gun-positioner govern the build.',ST['BodyShop'])])
    for _,label in docs:story.append(Paragraph(label,ST['BodyShop']))
    story.extend([Paragraph('The supplied 60-degree attitude and 16 mm nozzle gap are editable mounting parameters. Establish welding focus and attitude on a sacrificial joint. Physical commissioning records received fits and loaded performance. No unperformed weld or measurement is asserted.',ST['BodyShop']),PageBreak()])
    for file,title,_,_ in scenes[1:]:story.extend([Paragraph(title,ST['Heading1']),Image(str(ART/f'{file}.png'),width=WIDTH,height=312),Paragraph('Actual generated assembly geometry. Dimensions are governed by the STEP, print manifest and editable parameters.',ST['SmallShop']),PageBreak()])
    for path,_ in docs:story.extend(markdown((DOC/path).resolve()));story.append(PageBreak())
    story.extend([Paragraph('Print manifest',ST['Heading1']),Paragraph('All STLs are oriented on the bed. Solid mass excludes supports, brim and purge.',ST['BodyShop'])])
    parts=json.loads((CAD/'print-manifest.json').read_text())['parts']
    data=[[Paragraph(s,ST['SmallShop'])for s in ['Part / material','Size X x Y x Z (mm)','Solid grams','Supports']]]
    for p in parts:data.append([Paragraph(p['name']+'<br/>'+p['material'],ST['SmallShop']),Paragraph(' x '.join(f'{v:g}'for v in p['print_bounds_mm']),ST['SmallShop']),Paragraph(f"{p['solid_mass_g']:.1f}",ST['SmallShop']),Paragraph('Yes'if p['support_required']else'No',ST['SmallShop'])])
    t=Table(data,colWidths=[195,143,65,65],repeatRows=1);t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#eaf0f0')),('LINEBELOW',(0,0),(-1,-1),.25,colors.HexColor('#c8d7d8')),('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4)]));story.append(t)
    pdf=DEST/'gun-positioner-guide.pdf'
    SimpleDocTemplate(str(pdf),pagesize=(612,792),leftMargin=72,rightMargin=72,topMargin=56,bottomMargin=58,title='PGFUN two-axis weld positioner',author='Home Soda Machine').build(story,onFirstPage=footer,onLaterPages=footer)
    pages=len(PdfReader(pdf).pages)
    subprocess.run(['pdftoppm','-f','1','-singlefile','-scale-to-x','800','-scale-to-y','-1','-png',str(pdf),str(DEST/'gun-positioner-guide.cover')],check=True)
    from PIL import Image as PILImage
    size=PILImage.open(DEST/'gun-positioner-guide.cover.png').size
    (DEST/'gun-positioner-guide.pdf.json').write_text(json.dumps(dict(title='PGFUN two-axis weld positioner',subtitle=f'Shop guide - {pages} pages, Letter 8.5 x 11 in',pages=pages,cover='gun-positioner-guide.cover.png',cover_size=size),indent=2)+'\n')
    sources=[(DOC/p).resolve()for p,_ in docs]+[CAD/'motion-geometry.json',CAD/'print-manifest.json',CAD/'assembly-meshes.npz',CAD/'reference-meshes.npz',Path(__file__)]
    (DEST/'source-receipt.json').write_text(json.dumps(dict(geometry_sha256=json.loads((CAD/'motion-geometry.json').read_text())['sha256'],sources={str(p.relative_to(ROOT)):sha(p)for p in sources},pdf_sha256=sha(pdf),pages=pages,scope='Generated instructions and CAD figures; physical results recorded separately.'),indent=2)+'\n')
    print(json.dumps(dict(pages=pages,pdf=str(pdf),sha256=sha(pdf))))
if __name__=='__main__':main()
