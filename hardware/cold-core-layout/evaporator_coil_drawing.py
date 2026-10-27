"""EVAP-01: production coil, complete tube outlines and tangent tail forms.

The installed coil and both tails share _coil's geometry. Views are OCCT
hidden-line projections of the tube exterior. The local bridge relief is
defined separately by a radial section and its dimensions.
Sheet two defines all circular bends and their tangent stations. Dimensions
and tolerances define the manufactured article rather than a prototype state.
"""
import math
import sys
from functools import lru_cache
from pathlib import Path
import cadquery as cq
from reportlab.pdfgen import canvas
from OCP.HLRBRep import HLRBRep_Algo, HLRBRep_HLRToShape, HLRBRep_TypeOfResultingEdge
from OCP.HLRAlgo import HLRAlgo_Projector
from OCP.gp import gp_Ax2, gp_Pnt, gp_Dir
from OCP.BRepLib import BRepLib
from OCP.GCPnts import GCPnts_QuasiUniformDeflection

HERE = Path(__file__).resolve().parent
HW = HERE.parent
sys.path.insert(0, str(HW / 'scripts'))
sys.path.insert(0, str(HERE))
import _coil as source
import coil_mandrel as mandrel
from _fabrication_drawing import *

PDF_PATH = HERE / 'evaporator-coil-drawing.pdf'
SHEET = (1224, 792)
SCALE = MM / 2
WALL = 0.031 * 25.4
CUT_LENGTH = math.ceil(source.cut_length())
CUT_PLUS = 10
MATERIAL_ID = 'HSM-000015'
REVISION = 'B'
REVIEW_REGIONS = [
 (1,'elevation',35,442,687,756),
 (1,'plan-upper',35,265,687,439),
 (1,'plan-lower',35,120,687,280),
 (1,'dimensions',700,476,1190,756),
 (1,'requirements',700,154,1190,479),
 (1,'title-footer',35,27,1197,147),
 (2,'inlet-form-table',35,459,613,756),
 (2,'outlet-form-table',622,451,1202,756),
 (2,'side-view',35,147,687,454),
 (2,'form-instructions',700,252,1190,449),
 (2,'tube-section',700,149,1190,275),
 (2,'title-footer',35,27,1197,147),
]


def tube_exterior(wire, *, frenet=False):
 plane=cq.Plane(origin=wire.startPoint(),normal=wire.tangentAt(0))
 return cq.Workplane(plane).circle(source.TUBE_R).sweep(
  cq.Workplane('XY').newObject([wire]),isFrenet=frenet).val()


@lru_cache(None)
def drawing_parts():
 # The winding views use the nominal cylindrical envelope. The radial
 # bridge relief has its own dimensioned local section and acceptance note.
 # Separate smooth half-turn spans let the hidden-line kernel resolve
 # occlusion between turns; a single periodic sweep face self-hides poorly.
 spans=[]
 for i in range(round(2*source.TOTAL_WRAPS)):
  wire=cq.Wire.makeHelix(source.PITCH,source.PITCH/2,source.WIND_R)
  wire=wire.rotate((0,0,0),(0,0,1),source.AZ_IN+180*i).translate(
   (0,0,source.evap_tail_low_z+source.PITCH*i/2))
  spans.append(tube_exterior(wire,frenet=True))
 shapes={'wrap':spans[0].fuse(*spans[1:],tol=1e-5)}
 for end in ['inlet','outlet']:
  shapes[end]=tube_exterior(source.tail_form(end,working_tail=True).wire())
 return shapes


@lru_cache(None)
def outline(view):
 # Normal points toward the viewer; x-direction is the page's positive u.
 normal,xdir={'front':((1,0,0),(0,1,0)),
              'plan':((0,0,1),(1,0,0)),
              'side':((0,1,0),(-1,0,0))}[view]
 parts=drawing_parts()
 algo=HLRBRep_Algo()
 for part in parts.values():algo.Add(part.wrapped)
 algo.Projector(HLRAlgo_Projector(gp_Ax2(gp_Pnt(0,0,0),gp_Dir(*normal),gp_Dir(*xdir))))
 print('Projecting tube outlines:',view,flush=True)
 algo.Update();algo.Hide();converted=HLRBRep_HLRToShape(algo)
 paths=[]
 # This part has smooth, continuous tube surfaces. Sharp-edge output also
 # contains periodic sweep seams. Discard circular cross-section boundaries
 # at tangent stations, except where they coincide with the skin's
 # silhouette in an axial view. Retain the actual cut-end boundaries.
 projected=[(converted.OutLineVCompound(),False,None)]
 for end in ['inlet','outlet']:
  shape=converted.CompoundOfEdges(parts[end].wrapped,
   HLRBRep_TypeOfResultingEdge.HLRBRep_Sharp,True,True)
  projected.append((shape,True,source.tail_form(end,working_tail=True).point))
 for shape,world,cut in projected:
  if shape.IsNull():continue
  BRepLib.BuildCurves3d_s(shape,1e-6)
  for edge in cq.Shape(shape).Edges():
   curve=edge._geomAdaptor()
   if world and edge.geomType()=='CIRCLE' and abs(curve.Circle().Radius()-source.TUBE_R)<1e-5:
    circle=curve.Circle();location=circle.Location();axis=circle.Axis().Direction()
    axial=abs(axis.Dot(gp_Dir(*normal)))>1-1e-7
    if not axial and (cq.Vector(location.X(),location.Y(),location.Z())-cut).Length>1e-4:continue
   sample=GCPnts_QuasiUniformDeflection(curve,0.025,curve.FirstParameter(),curve.LastParameter())
   if sample.IsDone():
    points=[]
    for i in range(1,sample.NbPoints()+1):
     p=sample.Value(i)
     points.append((p.Y(),p.Z()) if world and view=='front' else
                   (p.X(),p.Y()) if not world or view=='plan' else (-p.X(),p.Z()))
    paths.append(points)
 return paths


def render_view(c,view,origin,scale=SCALE):
 for points in outline(view):
  if len(points)>1:polyline(c,[(origin[0]+u*scale,origin[1]+v*scale) for u,v in points],0.7)
 if view in ['plan','side']:
  for end in ['inlet','outlet']:
   point=source.tail_form(end,working_tail=True).point
   u,v=(point.x,point.y) if view=='plan' else (-point.x,point.z)
   line(c,origin[0]+u*scale,origin[1]+(v-source.TUBE_R)*scale,
        origin[0]+u*scale,origin[1]+(v+source.TUBE_R)*scale,VISIBLE)


def endpoint(end):
 return source.tail_form(end).point.toTuple()


def station_mark(c,point,label,x,y,view):
 u,v={'front':(point[1],point[2]),'plan':(point[0],point[1]),'side':(-point[0],point[2])}[view]
 px,py=x+u*SCALE,y+v*SCALE
 center(c,px,py,5)
 return px,py


def elevation(c):
 x,z0=300,450
 text(c,x,741,'INSTALLED ELEVATION - LOOKING ALONG -X',11,bold=True,align='center')
 text(c,x,724,'TUBE OUTLINES - NOMINAL WINDING - SCALE 1:2',9,align='center')
 render_view(c,'front',(x,z0))
 lo,hi=source.evap_tail_low_z,source.evap_tail_high_z
 h1=source.tail_form('inlet').segments[0]['start']
 h2=source.tail_form('outlet').segments[0]['start']
 for pt in [h1,h2]:
  px,py=x+pt[1]*SCALE,z0+pt[2]*SCALE
  line(c,120,py,px-7,py)
 line(c,125,z0+lo*SCALE,125,z0+hi*SCALE)
 arrow(c,(125,z0+lo*SCALE),(125,z0+hi*SCALE))
 arrow(c,(125,z0+hi*SCALE),(125,z0+lo*SCALE))
 c.saveState();c.translate(115,z0+(lo+hi)*SCALE/2);c.rotate(90)
 text(c,0,0,f'{source.WIND_HEIGHT:.2f} ±1.0 HELIX CL SPAN',9.5,align='center');c.restoreState()
 for end,label in [('inlet','E1 / INLET'),('outlet','E2 / OUTLET')]:
  pt=endpoint(end)
  text(c,x+pt[1]*SCALE,z0+pt[2]*SCALE-16,label,9,bold=True,align='center')
 p1=station_mark(c,h1,'H1',x,z0,'front');p2=station_mark(c,h2,'H2',x,z0,'front')
 leader(c,p2,(451,704),(476,704),['H2 / UPPER HELIX CL END',f'Z {hi:.2f} REF'],9)
 leader(c,p1,(455,450),(479,450),['H1 / LOWER HELIX CL END',f'Z {lo:.2f} ±0.5'],9)
 text(c,455,625,'9.500 RIGHT-HAND TURNS',10,bold=True)
 text(c,455,608,f'{source.PITCH:.3f} PITCH REF',9)
 text(c,455,573,'BOTH TAILS FULLY DEFINED',9,bold=True)
 text(c,455,557,'R15 FORMS / STATIONS ON SHEET 2',8.5)
 axes(c,56,456,'+Y','+Z')


def plan(c):
 x,y=563,275
 text(c,325,433,'PLAN - LOOKING ALONG -Z',11,bold=True,align='center')
 text(c,325,417,'TUBE OUTLINES - NOMINAL WINDING - SCALE 1:2',9,align='center')
 render_view(c,'plan',(x,y))
 center(c,x,y,13);text(c,x+12,y-14,'O',9)
 plane_x=endpoint('inlet')[0];px=x+plane_x*SCALE
 line(c,px,142,px,401,dash=CENTER_DASH)
 text(c,px,132,f'E PLANE: X {plane_x:.2f}',8,align='center')
 for end,label,dy in [('inlet','E1 / INLET',142),('outlet','E2 / OUTLET',400)]:
  ex,ey,ez=endpoint(end);cut=source.tail_form(end,working_tail=True).point
  a=(x+ex*SCALE,y+ey*SCALE);b=(x+cut.x*SCALE,a[1])
  center(c,*a,6)
  horizontal_dimension(c,b[0],a[0],b[1],dy,
   f'{mandrel.stub_protrusion[end]:.0f} +5 / -0 WORKING TAIL',9)
  text(c,(a[0]+b[0])/2,a[1]+(15 if end=='inlet' else -21),label,9,bold=True,align='center')
 for end,ident in [('inlet','H1'),('outlet','H2')]:
  point=source.tail_form(end).segments[0]['start']
  px,py=station_mark(c,point,ident,x,y,'plan')
  text(c,px+13,py+(-15 if end=='inlet' else 12),ident,8.5)
 text(c,x,y+40,'180° ±0.5° END CLOCKING',8.5,align='center')
 text(c,x,y+25,'INLET TO OUTLET CCW',8,align='center')
 text(c,x,y-34,'HELIX CL Ø133.35 REF',8.5,align='center')
 text(c,x,y-51,'LOCAL BRIDGE RELIEF: NOTE 4',7.5,align='center')
 axes(c,55,322,'+X','+Y')


def dimension_table(c):
 x,r,top=714,1178,698
 text(c,x,741,'PRODUCTION FORM DEFINITION',11,bold=True)
 text(c,x,724,'ONE CONTINUOUS COPPER TUBE - FINISHED FORM',9)
 entries=[('TUBE STOCK','1/4 IN OD x 0.031 IN WALL ACR COPPER'),
 ('FINISHED WINDING',f'{source.TOTAL_WRAPS:.3f} RH TURNS / 180° END CLOCKING'),
 ('HELIX CL SPAN',f'{source.WIND_HEIGHT:.2f} ±1.0'),
 ('NOMINAL PITCH',f'{source.PITCH:.3f} REF'),
 ('ALL TAIL BENDS',f'CL R{source.TAIL_BEND_R:.1f} ±0.5'),
 ('FORMING DATA','ANGLES / STRAIGHT LENGTHS REF; SHEET 2'),
 ('EXIT E1 / E2','Y -77.50 / +77.50; Z 28.425; ±0.25'),
 ('EXIT DIRECTIONS','PARALLEL TO -X WITHIN 1°'),
 ('STOCK CUT',f'{CUT_LENGTH} +{CUT_PLUS} / -0; FINISH ENDS AFTER FORMING')]
 bottom=top-22*len(entries)
 c.setLineWidth(THIN);c.rect(x,bottom,r-x,top-bottom,stroke=1,fill=0)
 line(c,870,bottom,870,top)
 for i,(label,value) in enumerate(entries):
  yy=top-22*i
  if i:line(c,x,yy,r,yy)
  text(c,x+7,yy-14,label,8,bold=True);text(c,877,yy-14,value,8.2)


def requirements(c):
 text(c,714,473,'MANUFACTURING AND ACCEPTANCE',10,bold=True)
 items=[
 '1. Units: mm. O is the winding axis in X,Y. Z=0 is the cold-core shell base plane. Form and inspect on a fixture locating that axis and the shell exits. This drawing defines the coil before final refrigeration tie-in.',
 '2. Material: soft ACR copper, continuous and clean. No joint within the core. Form nine full turns plus the 180° upper-end clocking. The helix rises CCW from H1 to H2 when viewed from +Z.',
 '3. Tail geometry is the tangent sequence on sheet 2. Coordinate stations are tube-centerline points. All bends are R15; preserve the stated straight lengths and exit directions. The working-tail dimensions are measured from E, before refrigeration trimming.',
 f'4. Fit to the nominal Ø{2*source.carbonator_outer_radius:.0f} vessel with the foil thermal interface. Over the reed bridge, raise the tube centerline {source.BRIDGE_LIFT:.2f} ±0.5 radially and blend smoothly at R12.7 MIN. Bridge zone Z {source.BRIDGE_Z[0]:.2f}-{source.BRIDGE_Z[1]:.2f} REF, centered on +X. Preserve reed clearance and thermal contact elsewhere.',
 '5. Use the undersized mandrel for rough forming; feed stock and adjust winding to the finished dimensions on the vessel fixture. Acceptance is the specified finished form, not the mandrel groove or an assumed springback.',
 '6. Reject kinks, creases, cracks and visible flattening. Square-cut and deburr both ends; remove chips and cutting fluid, preserve the open bore and cap the ends until tie-in. Verify the formed coil and both feed-throughs before foam.',
 '7. Refrigeration joint preparation, heat protection, brazing and leak acceptance follow assembly/refrigerant-loop.md. Trim working tails only at that assembly operation.'
 ]
 return paragraphs(c,714,453,items,464,size=9,leading=12,gap=6)


def table(c,end,x,right):
 title='INLET TAIL / E1' if end=='inlet' else 'OUTLET TAIL / E2'
 text(c,x,741,title+' - TANGENT STATIONS',11,bold=True)
 text(c,x,724,'FOLLOW FROM HELIX TO CUT END; ALL BENDS CL R15 ±0.5',8.5)
 form=source.tail_form(end,working_tail=True)
 data=[('H1' if end=='inlet' else 'H2','START','-',form.segments[0]['start'])]
 for segment in form.segments:
  if segment['kind']=='bend':
   data.append((segment['id'],f"{segment['angle']:.2f}°",'XZ' if segment['id'] in ['B0','B3','B4'] else 'XY',segment['end']))
  else:
   label='CUT' if segment['id']=='WORKING TAIL' else 'E1' if segment['id']=='S2' and end=='inlet' else 'E2' if segment['id']=='S2' else segment['id']
   data.append((label,f"{segment['length']:.2f}",'STRAIGHT',segment['end']))
 cols=[x,x+51,x+140,x+209,x+314,x+419,right]
 top,row=698,24;bottom=top-23-row*len(data)
 c.setLineWidth(THIN);c.rect(x,bottom,right-x,top-bottom,stroke=1,fill=0)
 for xx in cols[1:-1]:line(c,xx,bottom,xx,top)
 for j,title in enumerate(['END','ANGLE / L REF','PLANE','X','Y','Z']):
  text(c,(cols[j]+cols[j+1])/2,top-15,title,8,bold=True,align='center')
 line(c,x,top-23,right,top-23)
 for i,(label,value,plane,point) in enumerate(data):
  yy=top-23-row*i
  if i:line(c,x,yy,right,yy)
  for j,value in enumerate([label,value,plane,*[f'{v:.3f}' for v in point]]):
   text(c,(cols[j]+cols[j+1])/2,yy-16,value,8.3,align='center',bold=(j==0))
 return bottom


def side_view(c):
 text(c,325,441,'SIDE - LOOKING ALONG -Y',11,bold=True,align='center')
 text(c,325,425,'TUBE OUTLINES - NOMINAL WINDING - SCALE 1:2',9,align='center')
 render_view(c,'side',(150,160))
 outlet=source.tail_form('outlet')
 straight=next(seg for seg in outlet.segments if seg['id']=='S1')
 px=150+(-straight['start'][0]+source.TUBE_R)*SCALE
 py=160+(straight['start'][2]+straight['end'][2])*SCALE/2
 leader(c,(px,py),(300,330),(324,330),['OUTLET VERTICAL STRAIGHT',f"{straight['length']:.2f} REF"],9)
 text(c,47,153,'BOTH TAILS CONTINUOUS WITH THE HELIX. HIDDEN LINES OMITTED.',8)
 axes(c,65,170,'-X','+Z')


def forming_notes(c):
 text(c,714,434,'HOW THE FORM TABLES DEFINE THE TAILS',10,bold=True)
 items=[
 '1. Each row gives the END of the identified bend or straight. Begin at H1/H2 with the helix tangent. B0 is the small pitch roll-off ending parallel to -X.',
 '2. B1/B2 are opposite circular bends in XY: first toward the exit lane (-Y inlet, +Y outlet), then back parallel to -X. Each pair has zero intervening straight.',
 '3. Inlet B3/B4 are opposite bends in XZ, first downward and then back parallel to -X. Outlet B3 turns downward 90°; S1 is vertical; B4 turns 90° back parallel to -X.',
 '4. E1/E2 end the in-core straights. Continue straight along -X to CUT. Straight lengths are tangent-to-tangent; bend angles are changes in direction. Use a form fixture to reproduce the specified geometry.',
 '5. Centerline stations: ±0.5 unless separately toleranced. Exit Y/Z: ±0.25. H2 Z and CUT coordinates are REF. Keep every junction tangent; inspect after forming and end finishing.'
 ]
 return paragraphs(c,714,414,items,464,size=9,leading=12,gap=6)


def tube_section(c):
 x,y,s=780,206,4*MM;outer=source.TUBE_R*s
 annulus=c.beginPath();annulus.circle(x,y,outer);annulus.circle(x,y,outer-WALL*s)
 hatch(c,annulus,(x-outer,y-outer,x+outer,y+outer),spacing=6)
 c.setLineWidth(VISIBLE)
 for r in [outer,outer-WALL*s]:c.circle(x,y,r,stroke=1,fill=0)
 center(c,x,y,outer+6)
 text(c,x,160,'TUBE SECTION - 4:1',8,align='center')
 text(c,840,224,'1/4 IN OD x 0.031 IN WALL',8)
 text(c,840,208,'Ø6.35 x 0.787 WALL REF',8)
 text(c,840,191,'OPEN BORE; ENDS DEBURRED',8)


def bridge_section(c):
 vessel_x=1035;scale=4*MM;lift=source.BRIDGE_LIFT*scale
 cy=206;outer=source.TUBE_R*scale;cx=vessel_x+lift+outer
 steel=path_from_points(c,[(vessel_x-15,170),(vessel_x,170),(vessel_x,245),(vessel_x-15,245)])
 hatch(c,steel,(vessel_x-15,170,vessel_x,245),spacing=6)
 c.setLineWidth(VISIBLE);c.drawPath(steel,stroke=1,fill=0)
 c.rect(vessel_x,cy-17,lift,34,stroke=1,fill=0)
 annulus=c.beginPath();annulus.circle(cx,cy,outer);annulus.circle(cx,cy,outer-WALL*scale)
 hatch(c,annulus,(cx-outer,cy-outer,cx+outer,cy+outer),spacing=6)
 c.setLineWidth(VISIBLE);c.drawPath(annulus,stroke=1,fill=0)
 horizontal_dimension(c,vessel_x,vessel_x+lift,cy+17,252,f'{source.BRIDGE_LIFT:.2f} ±0.5',8.5)
 text(c,1090,158,'BRIDGE RELIEF - RADIAL SECTION 4:1',7.4,align='center')


def build_pdf(path):
 c=canvas.Canvas(str(path),pagesize=SHEET,invariant=1,pageCompression=1)
 c.setTitle('Evaporator coil - production engineering drawing')
 c.setAuthor('Home Soda Machine / Codex')
 c.setSubject('EVAP-01 Rev B: complete formed tube, R15 tangent tails and production form tables')
 frame(c,SHEET);elevation(c);plan(c);dimension_table(c);requirements(c)
 title_block(c,SHEET,'EVAPORATOR COIL','EVAP-01','ACR COPPER TUBE','1 PER COLD CORE',MATERIAL_ID,
  ('PRODUCTION PART','FORMED COIL'),revision=REVISION,sheet_label='1 OF 2')
 c.showPage()
 frame(c,SHEET);table(c,'inlet',47,605);table(c,'outlet',635,1190);side_view(c);forming_notes(c);tube_section(c);bridge_section(c)
 title_block(c,SHEET,'EVAPORATOR COIL / TAIL FORMS','EVAP-01','ACR COPPER TUBE','1 PER COLD CORE',MATERIAL_ID,
  ('PRODUCTION PART','FORMED COIL'),revision=REVISION,sheet_label='2 OF 2')
 c.showPage();c.save()


if __name__=='__main__':
 export_pdf(build_pdf,str(PDF_PATH));print(f'Exported: {PDF_PATH}',flush=True)
