"""Analytic circle-pipe members with independent native clearance containment.

Separate cylindrical and circular-arc members retain the received pipe's
complete lateral surfaces. This avoids an ambiguous whole-pipe containment
Boolean while keeping each paired native member independently verifiable.
"""
import math
import cadquery as cq
from OCP.BRepAdaptor import BRepAdaptor_Surface

class CircularSelfIntersection(ValueError):
    def __init__(self,a,b,indices,volume):
        super().__init__(f'Circular physical members {indices} overlap by {volume:g} mm³')
        self.overlap=a.intersect(b,tol=.0001);self.indices=indices;self.volume=volume

def paired_members(shape,diameter,gap=1.,fuse_clearance=True):
    radius=diameter/2;source=[];clearance=[];checks=[];length=0.;planes=0.;nodes={}
    for face in shape.Faces():
        kind=face.geomType()
        if kind=='PLANE':planes+=face.Area();continue
        if kind not in ['CYLINDER','TORUS']:raise ValueError('Nonanalytic circular pipe lateral face '+kind)
        sections=[edge for edge in face.Edges() if edge.geomType()=='CIRCLE' and abs(edge.radius()-radius)<1e-6]
        points=[]
        for edge in sections:
            p=edge._geomAdaptor().Circle().Location();v=cq.Vector(p.X(),p.Y(),p.Z())
            if not any((v-q).Length<1e-6 for q in points):points.append(v)
        if len(points)!=2:raise ValueError('Pipe member has no complete two-section boundary')
        a,b=points
        if kind=='CYLINDER':edge=cq.Edge.makeLine(a,b)
        else:
            torus=BRepAdaptor_Surface(face.wrapped).Torus();p=torus.Location();c=cq.Vector(p.X(),p.Y(),p.Z())
            u=a-c;v=b-c;major=torus.MajorRadius()
            if abs(u.Length-major)>1e-6 or abs(v.Length-major)>1e-6:raise ValueError('Torus section is off its native centreline')
            mid=c+(u+v).normalized()*major
            edge=cq.Edge.makeThreePointArc(a,mid,b)
        member_length=edge.Length();expected_area=2*math.pi*radius*member_length
        if abs(face.Area()-expected_area)>max(.0001,expected_area*1e-6):raise ValueError('Native lateral surface differs from circular-member recipe')
        wire=cq.Wire.assembleEdges([edge]);normal=edge.tangentAt(0)
        for point,tangent in [(a,normal),(b,-edge.tangentAt(1))]:
            key=tuple(round(v,7) for v in point.toTuple())
            nodes.setdefault(key,[]).append(tangent.normalized())
        pieces=[]
        for member_radius in [radius,radius+gap]:
            profile=cq.Wire.makeCircle(member_radius,a,normal)
            solid=cq.Solid.sweep(profile,[],wire,makeSolid=True,isFrenet=False)
            expected=math.pi*member_radius**2*member_length
            if not solid.isValid() or abs(solid.Volume(tol=1e-9)-expected)>max(.001,expected*1e-6):raise ValueError('Invalid circular pipe member')
            pieces.append(solid)
        missing=abs(pieces[0].cut(pieces[1],tol=.0001).Volume(tol=1e-9))
        if missing>.001:raise ValueError('Paired native circular-member clearance failed')
        source.append(pieces[0]);clearance.append(pieces[1]);length+=member_length
        checks.append({'kind':kind,'length_mm':member_length,'paired_missing_mm3':missing,'pass':True})
    if abs(planes-2*math.pi*radius**2)>.0001:raise ValueError('Received pipe has extra planar members')
    expected=math.pi*radius**2*length
    physical=cq.Compound.makeCompound(source);tool=cq.Compound.makeCompound(clearance)
    if abs(shape.Volume(tol=1e-9)-expected)>.001 or abs(physical.Volume(tol=1e-9)-expected)>.001:raise ValueError('Circular members differ from received pipe section volume')
    if not physical.isValid() or not tool.isValid():raise ValueError('Invalid native circular-member compound')
    seams=[];ends=[]
    for point,tangents in nodes.items():
        if len(tangents)==1:ends.append(point);continue
        if len(tangents)!=2:raise ValueError('Circular-member centreline branches or crosses itself')
        dot=tangents[0].dot(tangents[1]);aligned=abs(dot+1.)<1e-8
        if not aligned:raise ValueError('Circular-member endpoint tangent is discontinuous')
        seams.append({'centre_mm':list(point),'diameter_mm':diameter,'outward_tangent_dot':dot,
            'full_section_face_coincidence':True,'pass':aligned})
    if len(ends)!=2 or len(seams)!=len(source)-1:raise ValueError('Circular members do not form one continuous open wire')
    from audit import common
    from native_harness import bounds,broad
    self_checks=[]
    for i,a in enumerate(source):
        for j in range(i+1,len(source)):
            b=source[j]
            if not broad(bounds(a),bounds(b),.0001):continue
            overlap=common(a,b)
            if overlap>.001:raise CircularSelfIntersection(a,b,[i,j],overlap)
            self_checks.append({'members':[i,j],'common_mm3':overlap,'pass':True})
    # A single native union avoids treating touching clearance members as
    # competing volumes in a later shell Boolean. The physical conductor
    # keeps the exact, independently verified full-section member seams.
    if fuse_clearance:
        tool=clearance[0].fuse(*clearance[1:],tol=.0001) if len(clearance)>1 else clearance[0]
        if not tool.isValid() or len(tool.Solids())!=1:raise ValueError('Circular clearance members do not form one valid native union')
    union_checks=[]
    for index,member in enumerate(source if fuse_clearance else []):
        missing=abs(member.cut(tool,tol=.0001).Volume(tol=1e-9))
        if missing>.001:raise ValueError('Circular clearance union loses a physical member')
        union_checks.append({'member':index,'missing_mm3':missing,'pass':True})
    return physical,tool,{'members':checks,'complete_length_mm':length,'received_section_volume_mm3':shape.Volume(tol=1e-9),
        'member_section_volume_mm3':physical.Volume(tol=1e-9),'radial_air_mm':gap,
        'tangent_full_section_seams':seams,'open_end_centres_mm':[list(p) for p in ends],
        'physical_member_self_checks':self_checks,
        'clearance_union_containment_checks':union_checks,'clearance_union_valid_one_solid':fuse_clearance,
        'scope':'Each received cylinder/torus lateral face supplies the exact centreline and cross-section boundaries. Surface areas and complete circular-section volume match. Every native physical member is contained by its own concentric enlarged clearance member.'}
