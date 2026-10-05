"""True-size Letter drill templates, tiled from the fabrication registries.

Only the CAD plate holes are fabrication instructions. Transfer-drilled
catalog interfaces remain explicitly marked in the part notes. An SVG or
screen picture is never silently fitted to a Letter sheet.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
GUIDE=ROOT/'hardware/gun-positioner-guide'
MM=72/25.4
W,H=612,792
MARGIN=30
AREA_X,AREA_Y=MARGIN,87
AREA_W,AREA_H=(W-2*MARGIN)/MM,215.0
OVERLAP=12.0
SX,SY=AREA_W-OVERLAP,AREA_H-OVERLAP
INK,BLUE,CORAL,MUTED='#202337','#1749d1','#d64050','#606a78'


def registry(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    sys.modules[name]=mod
    spec.loader.exec_module(mod)
    mod.init_parts()
    return mod


def tile_count(length,usable):
    return max(1,math.ceil(max(0,length-OVERLAP)/(usable-OVERLAP)))


def make_rows():
    source=ROOT/'hardware/printed-parts/fixtures/gun-positioner/gun_positioner.py'
    gp=registry(source,'positioner_template_geometry')
    parts=gp.PARTS
    rows=[]
    for name,data in parts.items():
        shape_type=data.get('template_type','plate')
        if data['kind']=='metal' and data.get('blank_mm') and shape_type in ('plate','bar') and 'spacer' not in name and 'angle' not in name:
            holes=data.get('holes',[])
            for i,a in enumerate(holes):
                for b in holes[i+1:]:
                    if math.hypot(a[0]-b[0],a[1]-b[1]) < (a[2]+b[2])/2-.01:
                        raise ValueError(f'{name}: intersecting drilled holes {a} and {b}; reconcile the fabrication interface before making a template')
            if data.get('outline'):
                measured=[max(p[i] for p in data['outline'])-min(p[i] for p in data['outline']) for i in (0,1)]
                if any(actual>stock+.01 for actual,stock in zip(measured,data['blank_mm'][:2])):
                    raise ValueError(f'{name}: CAD outline {measured} does not fit registered blank {data["blank_mm"]}')
            rows.append(dict(id=name,**{k:v for k,v in data.items() if k!='model'}))
    hub=parts['shaft-hub'];faces=hub['drilling_faces'];hx,hy,hz=hub['blank_mm']
    slit=faces['slit_mm']
    rows.append(dict(id='shaft-hub-XY-mounting-projection',kind='metal',quantity=hub['quantity'],
                     blank_mm=[hx,hy,hz],holes=faces['XY_mounting']['holes_mm'],
                     saw_slit_mm=slit,
                     notes='Registered broad face of the 3D hub: REAM central bore 12 mm. Saw slit 1.5 mm from +Y edge 2 mm into bore; keep shaft plain.'))
    rows.append(dict(id='shaft-hub-YZ-clamp-projection',kind='metal',quantity=hub['quantity'],
                     blank_mm=[hy,hz,hx],blank_center_xy=[0,hz/2],
                     holes=faces['YZ_clamp_bores']['holes_mm'],
                     notes=f'Registered side face at X = {faces["YZ_clamp_bores"]["face_X_mm"]:g} mm. Y horizontal / Z upward from hub bottom; drill both 4.2 mm passages along X through split side only.'))
    rows.append(dict(id='shaft-end-pilot-projection',kind='catalog',quantity=8,
                     blank_mm=[12,12,16],holes=[[0,0,4.2]],circle_outline_mm=12,
                     notes='Axial end of a plain 12 mm shaft. Centered 4.2 mm pilot 16 mm deep; tap M5 × 0.8, usable full thread ≥10 mm. Verify keeper engagement/bottom margin.'))
    cap=parts['proof-gauge-quill-cap']
    rows.append(dict(id='proof-gauge-quill-cap-upright-projection',kind='metal',quantity=cap['quantity'],
                     blank_mm=[cap['blank_mm'][1],cap['blank_mm'][0],cap['blank_mm'][2]],
                     blank_center_xy=[0,-cap['blank_mm'][0]/2],
                     holes=cap['drilling_faces']['upright_XZ'],
                     notes='Registered upright face of the intact 50.8 × 50.8 × 6.35 mm angle, cut 70 mm wide. X horizontal / Z below angle corner; STEP governs the 3D part.'))
    # Each leg is a drilling projection of an intact bought angle.
    stop=parts['linear-stop-angle']
    for face,holes in stop['drilling_faces'].items():
        foot=face=='foot_XY'
        rows.append(dict(id='linear-stop-angle-'+('foot' if foot else 'upright')+'-projection',
                         kind='metal',quantity=stop['quantity'],
                         blank_mm=stop['blank_mm'] if foot else [stop['blank_mm'][1],stop['blank_mm'][0],stop['blank_mm'][2]],
                         blank_center_xy=[-stop['blank_mm'][0]/2,0] if foot else [0,stop['blank_mm'][0]/2],
                         holes=holes,notes='Drilling projection of the intact 50.8 mm angle. Its registered foot and upright faces govern; STEP retains the 3D corner.'))
    for name in ('guard-thrust-angle-minus','guard-thrust-angle-plus'):
        angle=parts[name]
        for face,holes in angle['drilling_faces'].items():
            foot=face=='foot_XY'
            rows.append(dict(id=name+'-'+('foot' if foot else 'upright')+'-projection',
                             kind='metal',quantity=angle['quantity'],
                             blank_mm=angle['blank_mm'],
                             blank_center_xy=[0,0] if foot else [0,angle['blank_mm'][0]/2],
                             holes=holes,notes='Registered face of the intact 25.4 mm angle. Transfer the guard passage from the actual bulkhead; preserve M6 head and washer clearance.'))
    jack=parts['installed-Z-jack-angle']
    circles=[e for e in jack['model'].val().Edges() if e.geomType()=='CIRCLE' and abs(e.radius()-3.25)<1e-5]
    for foot in (True,False):
        holes=[]
        for e in circles:
            center=e.Center()
            if abs(center.z if foot else center.x)>1e-5:continue
            h=[center.x,center.y,6.5] if foot else [center.y,center.z,6.5]
            if not any(sum(abs(a-b) for a,b in zip(h,old))<1e-4 for old in holes):holes.append(h)
        if len(holes)!=(1 if foot else 2):raise ValueError('Unexpected installed-Z jack face holes')
        rows.append(dict(id='installed-Z-jack-angle-'+('foot' if foot else 'upright')+'-projection',
                         kind='metal',quantity=jack['quantity'],
                         blank_mm=jack['blank_mm'] if foot else [jack['blank_mm'][1],jack['blank_mm'][0],jack['blank_mm'][2]],
                         blank_center_xy=[-jack['blank_mm'][0]/2,0] if foot else [0,jack['blank_mm'][0]/2],
                         holes=holes,notes='Drilling projection of the intact jack angle. Hole circles come directly from its CAD faces; STEP governs the 3D part.'))
    # Bought steel annuli need added keeper/guide holes. Their circles remain
    # intact; these pages are drilling projections, not plate-cutting recipes.
    for name,qty,holes in [
        ('friction-washer',3,[[-15,0,3.4],[15,0,3.4]]),
        ('crash-striker',3,[[-9,0,3.4],[9,0,3.4]]),
    ]:
        data=parts[name];bb=data['model'].val().BoundingBox()
        od=min(bb.xlen,bb.ylen)
        circle_diameters=[2*e.radius() for e in data['model'].val().Edges() if e.geomType()=='CIRCLE']
        bore=max(d for d in circle_diameters if d<od-.5)
        rows.append(dict(id=name+'-drilling-projection',kind='catalog',quantity=qty,
                         blank_mm=[bb.xlen,bb.ylen,bb.zlen],holes=holes,
                         existing_bore_mm=bore,circle_outline_mm=od,
                         notes='Drill the added holes in the purchased steel washer; preserve its flat contact annulus.'))
    optics_source=ROOT/'tools/gun-positioner-optics/mounts.py'
    opt=registry(optics_source,'positioner_template_optics')
    for name,data in opt.PARTS.items():
        if data['kind']=='metal' and name not in ('camera-rail-stop','lens-angle'):
            row=dict(id=name,**{k:v for k,v in data.items() if k!='model'})
            if name=='lens-upright':row['windows']=[[0,22,64,150]]
            rows.append(row)
    # Flat projections of each leg of the bought angle. These are drilling
    # layouts, never instructions to cut a flat replacement for the angle.
    rows.append(dict(id='lens-angle-foot-projection',kind='metal',quantity=2,
                     blank_mm=[50.8,80,6.35],holes=[[x-25.4,y,5.5] for x in (125-opt.LENS_X,145-opt.LENS_X) for y in (-32,32)],
                     slots=[],notes='Drilling projection of the foot of the preformed 50.8 × 50.8 mm aluminum angle, cut 80 mm wide. STEP governs the angle.'))
    rows.append(dict(id='lens-angle-upright-projection',kind='metal',quantity=2,
                     blank_mm=[80,50.8,6.35],holes=[[y,z-25.4,5.5] for y in (-32,32) for z in (15,35)],
                     slots=[],notes='Drilling projection of the upright of the preformed 50.8 × 50.8 mm aluminum angle, cut 80 mm wide. STEP governs the angle.'))
    return rows,[str(source.relative_to(ROOT)),str(optics_source.relative_to(ROOT))]


def draw_leaf(c,row,col_index,row_index,columns,rows,rotated,page,total):
    bx,by,t=row['blank_mm']
    width,height=(by,bx) if rotated else (bx,by)
    x0,y0=col_index*SX,row_index*SY
    c.setFillColor(HexColor('#ffffff'))
    c.rect(0,0,W,H,fill=1,stroke=0)
    c.setFillColor(HexColor(BLUE));c.rect(0,H-7,W,7,fill=1,stroke=0)
    c.setFont('PlexSemi',9);c.drawString(MARGIN,H-29,'HOME SODA MACHINE / FABRICATION TEMPLATE')
    c.setFont('PlexBold',19);c.setFillColor(HexColor(INK));c.drawString(MARGIN,H-57,row['id'])
    c.setFont('Plex',10);c.drawString(MARGIN,H-75,f'{bx:g} × {by:g} × {t:g} mm   •   make {row["quantity"]}   •   tile R{row_index+1} C{col_index+1} / {rows} × {columns}')
    c.saveState()
    clip=c.beginPath();clip.rect(AREA_X,AREA_Y,AREA_W*MM,AREA_H*MM)
    c.clipPath(clip,stroke=0,fill=0)
    # Template coordinates are viewed from the same top face as the CAD blank.
    # A registered polygon can use a convenient assembly datum away from the
    # stock center. Keep every CAD hole/cut at that datum, then map the whole
    # part into its actual blank rather than silently clipping an outer edge.
    blank_cx,blank_cy=row.get('blank_center_xy',[0,0])
    if row.get('outline') and 'blank_center_xy' not in row:
        blank_cx=(min(p[0] for p in row['outline'])+max(p[0] for p in row['outline']))/2
        blank_cy=(min(p[1] for p in row['outline'])+max(p[1] for p in row['outline']))/2
    def coord(hx,hy):
        hx-=blank_cx;hy-=blank_cy
        if rotated:gx,gy=hy+by/2,bx/2+hx
        else:gx,gy=hx+bx/2,by/2-hy
        return AREA_X+(gx-x0)*MM,AREA_Y+(AREA_H-(gy-y0))*MM
    def line_world(ax,ay,bx2,by2,stroke=INK,lw=.35):
        c.setStrokeColor(HexColor(stroke));c.setLineWidth(lw)
        c.line(AREA_X+(ax-x0)*MM,AREA_Y+(AREA_H-(ay-y0))*MM,
               AREA_X+(bx2-x0)*MM,AREA_Y+(AREA_H-(by2-y0))*MM)
    for gx in range(0,math.ceil(width/50)*50+1,50):
        line_world(gx,0,gx,height,'#dce2eb',.25)
    for gy in range(0,math.ceil(height/50)*50+1,50):
        line_world(0,gy,width,gy,'#dce2eb',.25)
    for a,b in [((0,0),(width,0)),((width,0),(width,height)),((width,height),(0,height)),((0,height),(0,0))]:
        line_world(*a,*b,'#b8c1cf' if row.get('outline') or row.get('circle_outline_mm') else INK,.6)
    if row.get('outline'):
        c.setStrokeColor(HexColor(INK));c.setLineWidth(.7)
        points=row['outline']+[row['outline'][0]]
        for a,b in zip(points,points[1:]):c.line(*coord(*a),*coord(*b))
    if row.get('circle_outline_mm'):
        px,py=coord(0,0)
        c.setStrokeColor(HexColor(MUTED));c.setLineWidth(.7)
        c.circle(px,py,row['circle_outline_mm']/2*MM,fill=0,stroke=1)
        if row.get('existing_bore_mm'):
            c.circle(px,py,row['existing_bore_mm']/2*MM,fill=0,stroke=1)
            c.setFillColor(HexColor(MUTED));c.setFont('Plex',7)
            c.drawString(px+3*MM,py-4*MM,f'EXISTING Ø{row["existing_bore_mm"]:g}')
    if row.get('saw_slit_mm'):
        slit=row['saw_slit_mm'];end=min(slit['to_Y'],by/2)
        c.setStrokeColor(HexColor(CORAL));c.setLineWidth(.5);c.setDash(2,2)
        for sx in(-slit['width']/2,slit['width']/2):
            c.line(*coord(slit['X']+sx,slit['from_Y']),*coord(slit['X']+sx,end))
        c.setDash()
    for hx,hy,d in row.get('holes',[]):
        px,py=coord(hx,hy)
        c.setStrokeColor(HexColor(INK));c.setLineWidth(.45)
        c.circle(px,py,d/2*MM,fill=0,stroke=1)
        c.setStrokeColor(HexColor(BLUE));c.setLineWidth(.3)
        c.line(px-2*MM,py,px+2*MM,py);c.line(px,py-2*MM,px,py+2*MM)
        c.setFillColor(HexColor(INK));c.setFont('Plex',7)
        c.drawString(px+(d/2+1)*MM,py+.8*MM,f'Ø{d:g}')
    for hx,hy,length,slot_width,angle in row.get('slots',[]):
        px,py=coord(hx,hy)
        c.saveState();c.translate(px,py);c.rotate(angle-(90 if rotated else 0))
        c.setStrokeColor(HexColor(INK));c.setLineWidth(.45)
        c.roundRect(-length/2*MM,-slot_width/2*MM,length*MM,slot_width*MM,slot_width/2*MM,fill=0,stroke=1)
        c.restoreState()
    for hx,hy,ww,hh in row.get('windows',[]):
        px,py=coord(hx,hy)
        window_w,window_h=(hh,ww) if rotated else (ww,hh)
        c.setStrokeColor(HexColor(INK));c.setLineWidth(.6)
        c.rect(px-window_w*MM/2,py-window_h*MM/2,window_w*MM,window_h*MM,stroke=1,fill=0)
        c.setFillColor(HexColor(MUTED));c.setFont('PlexSemi',9)
        c.drawCentredString(px,py,f'CUT {ww:g} × {hh:g} mm')
    # Union outline for overlapping rectangular CAD cutouts. Internal edges
    # inside a removed union are not machining boundaries.
    cutouts=row.get('cutouts',[])
    if cutouts:
        xs=sorted({v for x,y,w,h in cutouts for v in (x,x+w)})
        ys=sorted({v for x,y,w,h in cutouts for v in (y,y+h)})
        cells={(i,j) for i in range(len(xs)-1) for j in range(len(ys)-1)
               if any(x<= (xs[i]+xs[i+1])/2 <= x+w and y<= (ys[j]+ys[j+1])/2 <= y+h
                      for x,y,w,h in cutouts)}
        c.setStrokeColor(HexColor(INK));c.setLineWidth(.6)
        for i,j in cells:
            for neighbor,a,b in [((i-1,j),(xs[i],ys[j]),(xs[i],ys[j+1])),
                                  ((i+1,j),(xs[i+1],ys[j]),(xs[i+1],ys[j+1])),
                                  ((i,j-1),(xs[i],ys[j]),(xs[i+1],ys[j])),
                                  ((i,j+1),(xs[i],ys[j+1]),(xs[i+1],ys[j+1]))]:
                if neighbor not in cells:
                    c.line(*coord(*a),*coord(*b))
        center_x=(xs[0]+xs[-1])/2;center_y=(ys[0]+ys[-1])/2
        px,py=coord(center_x,center_y)
        label='CUT THROUGH'
        label_width=(ys[-1]-ys[0] if rotated else xs[-1]-xs[0])*MM
        font_size=min(9,max(6,(label_width-2*MM)/pdfmetrics.stringWidth(label,'PlexSemi',1)))
        c.setFont('PlexSemi',font_size);c.setFillColor(HexColor(MUTED))
        c.drawCentredString(px,py,label)
    if row['id']=='force-shuttle-boss':
        px,py=coord(0,0)
        c.setStrokeColor(HexColor(CORAL));c.setLineWidth(.5);c.setDash(2,2)
        c.circle(px,py,12.1/2*MM,fill=0,stroke=1);c.setDash()
    # Crosses are inside every shared overlap, even if no 50 mm gridline falls there.
    crosses=[]
    for n in range(1,columns):
        cx=n*SX+OVERLAP/2
        crosses.extend((cx,cy) for cy in (min(35,height/4),max(height-35,height*.75)))
    for n in range(1,rows):
        cy=n*SY+OVERLAP/2
        crosses.extend((cx,cy) for cx in (min(35,width/4),max(width-35,width*.75)))
    for cx,cy in crosses:
        for a,b in [((cx-3,cy),(cx+3,cy)),((cx,cy-3),(cx,cy+3))]:
            line_world(*a,*b,CORAL,.8)
    c.restoreState()
    c.setStrokeColor(HexColor('#dce2eb'));c.setLineWidth(.6)
    c.rect(AREA_X,AREA_Y,AREA_W*MM,AREA_H*MM,fill=0,stroke=1)
    c.setFillColor(HexColor(MUTED));c.setFont('Plex',8)
    notes=row.get('notes','')
    # The recipe notes remain in the parts manifest; the template carries only its status.
    transfer=('AXIAL END: Ø4.2 pilot 16 mm deep; tap M5 × 0.8, usable full thread ≥10 mm.' if row['id']=='shaft-end-pilot-projection' else
              'HUB BROAD FACE: ream Ø12; saw 1.5 mm split slit 2 mm into bore. Shaft stays plain.' if row['id']=='shaft-hub-XY-mounting-projection' else
              'HUB SIDE FACE: Y horizontal / Z from bottom; drill both Ø4.2 bores along X.' if row['id']=='shaft-hub-YZ-clamp-projection' else
              'DRILLING PROJECTION: bought steel washer; drill only added guide/keeper holes.' if row.get('circle_outline_mm') else
              'INWARD FACE: counterbore Ø12.1 × 2 mm deep; Ø8.5 passes through.' if row['id']=='force-shuttle-boss' else
              'DRILLING PROJECTION: keep the angle intact; STEP governs the 3D part.'
              if 'projection' in row['id'] else
              'Transfer catalog mounting holes from the received part.' if 'transfer' in notes.lower() else
              'Hole diameters and blank dimensions are in the fabrication manifest.')
    c.drawString(MARGIN,72,transfer)
    c.setStrokeColor(HexColor(BLUE));c.setLineWidth(.6)
    c.line(MARGIN,51,MARGIN+50*MM,51)
    for x in (MARGIN,MARGIN+50*MM):c.line(x,47,x,55)
    c.setFont('PlexSemi',8);c.setFillColor(HexColor(BLUE));c.drawString(MARGIN+50*MM+10,48,'50 mm - measure before drilling')
    c.setFont('Plex',8);c.setFillColor(HexColor(MUTED))
    c.drawString(MARGIN,28,'LETTER / ACTUAL SIZE / 100% • 12 mm tile overlap • align red crosses')
    c.drawRightString(W-MARGIN,28,f'{page} / {total}')
    c.showPage()


def build():
    source_paths=[ROOT/'hardware/printed-parts/fixtures/gun-positioner/gun_positioner.py',ROOT/'tools/gun-positioner-optics/mounts.py',Path(__file__).resolve()]
    input_hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths}
    fontdir=ROOT/'hardware/quickstart-codex/fonts'
    for name,file in [('Plex','Plex-Regular.ttf'),('PlexSemi','Plex-Semibold.ttf'),('PlexBold','Plex-Bold.ttf')]:
        pdfmetrics.registerFont(TTFont(name,str(fontdir/file)))
    parts,sources=make_rows()
    jobs=[]
    for row in parts:
        x,y,_=row['blank_mm']
        options=[(tile_count(x,AREA_W)*tile_count(y,AREA_H),False),
                 (tile_count(y,AREA_W)*tile_count(x,AREA_H),True)]
        rotated=min(options)[1]
        width,height=(y,x) if rotated else (x,y)
        cols,rows=tile_count(width,AREA_W),tile_count(height,AREA_H)
        for ry in range(rows):
            for cx in range(cols):jobs.append((row,cx,ry,cols,rows,rotated))
    path=GUIDE/'gun-positioner-drill-templates.pdf'
    c=canvas.Canvas(str(path),pagesize=(W,H),invariant=1)
    c.setTitle('Gun positioner - actual-size fabrication templates')
    c.setAuthor('Home Soda Machine')
    previous=None
    index=[]
    for page,args in enumerate(jobs,1):
        name=args[0]['id']
        if name!=previous:
            c.bookmarkPage(name)
            c.addOutlineEntry(name,name,0,False)
            index.append(dict(part=name,first_page=page))
            previous=name
        draw_leaf(c,*args,page,len(jobs))
    c.save()
    changed=[p for p,h in input_hashes.items() if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h]
    if changed:raise RuntimeError(f'Fabrication inputs changed during template build: {changed}')
    (GUIDE/'drill-template-receipt.json').write_text(json.dumps({
        'file':path.name,'pages':len(jobs),'page_inches':[8.5,11],
        'scale':'1 mm = 72/25.4 PDF points; print actual size',
        'tile_overlap_mm':OVERLAP,
        'source_sha256':input_hashes,
        'pdf_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'parts':[dict(id=r['id'],quantity=r['quantity'],blank_mm=r['blank_mm']) for r in parts],
        'index':index,
        'coverage':'Flat plate/bar faces, registered hub faces, centered shaft-end pilots, purchased steel washer drilling projections and formed-angle face projections. STEP geometry, cut schedules and received-part transfer checks govern three-dimensional joints and tube spacers.',
    },indent=2)+'\n')
    print(f'Wrote {len(jobs)} true-size Letter template pages')


if __name__=='__main__':build()
