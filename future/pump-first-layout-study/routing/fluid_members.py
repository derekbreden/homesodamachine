"""Read-only correspondence between received fluid exteriors and native members.

The selected BReps remain untouched. Each cylinder or circular-arc solid is
reconstructed from its received lateral face. Carbonated sleeves are annuli;
their occupied outer envelope is independently matched to the saved native
centreline, outer and inner lateral faces, end sections and material volume.
"""
import math
import cadquery as cq
from OCP.BRepAdaptor import BRepAdaptor_Surface
from circular_clearance import paired_members


def _point(point):
    return [point.X(),point.Y(),point.Z()]


def _centres(face,radius):
    points=[]
    for edge in face.Edges():
        if edge.geomType()!='CIRCLE' or abs(edge.radius()-radius)>1e-6:continue
        p=_point(edge._geomAdaptor().Circle().Location())
        if not any(sum((a-b)**2 for a,b in zip(p,q))<1e-12 for q in points):points.append(p)
    if len(points)!=2:raise ValueError('Received lateral face does not have two complete circular sections')
    return sorted(points)


def lateral_records(shape,radius):
    records=[]
    for face in shape.Faces():
        kind=face.geomType()
        if kind=='PLANE':continue
        if kind not in ['CYLINDER','TORUS']:raise ValueError('Nonanalytic fluid lateral face '+kind)
        surface=BRepAdaptor_Surface(face.wrapped)
        native_radius=surface.Cylinder().Radius() if kind=='CYLINDER' else surface.Torus().MinorRadius()
        if abs(native_radius-radius)>1e-6:continue
        row={'kind':kind,'radius_mm':native_radius,'section_centres_mm':_centres(face,radius),'area_mm2':face.Area()}
        if kind=='TORUS':
            torus=surface.Torus();row['major_radius_mm']=torus.MajorRadius();row['arc_centre_mm']=_point(torus.Location())
        records.append(row)
    return records


def _same_lateral(a,b):
    if a['kind']!=b['kind']:return False
    if abs(a['radius_mm']-b['radius_mm'])>1e-6:return False
    if abs(a['area_mm2']-b['area_mm2'])>max(.0001,a['area_mm2']*1e-6):return False
    pa=a['section_centres_mm'];pb=b['section_centres_mm']
    if min(max(math.dist(pa[i],pb[i]) for i in [0,1]),
           max(math.dist(pa[i],pb[1-i]) for i in [0,1]))>1e-5:return False
    if a['kind']=='TORUS':
        if abs(a['major_radius_mm']-b['major_radius_mm'])>1e-6 or math.dist(a['arc_centre_mm'],b['arc_centre_mm'])>1e-5:return False
    return True


def compare_lateral(received,expected):
    unused=list(range(len(expected)));checks=[]
    for index,row in enumerate(received):
        match=next((i for i in unused if _same_lateral(row,expected[i])),None)
        checks.append({'received_face':index,'expected_face':match,'pass':match is not None})
        if match is not None:unused.remove(match)
    return {'received_lateral_faces':received,'expected_lateral_faces':expected,'face_matches':checks,
            'unmatched_expected_faces':unused,'pass':all(r['pass'] for r in checks) and not unused}


def outer_sweep(edges,diameter):
    profile=cq.Wire.makeCircle(diameter/2,edges[0].startPoint(),edges[0].tangentAt(0))
    return cq.Solid.sweep(profile,[],cq.Wire.assembleEdges(edges),makeSolid=True,isFrenet=True)


def circular_parity(received,diameter,edges=None):
    """Return independently received-face-derived native physical members."""
    physical,_,section=paired_members(received,diameter,gap=0.,fuse_clearance=False)
    correspondence=None
    if edges is not None:
        expected=outer_sweep(edges,diameter)
        correspondence=compare_lateral(lateral_records(received,diameter/2),lateral_records(expected,diameter/2))
        section['supplied_centreline_length_mm']=sum(e.Length() for e in edges)
        section['centreline_length_error_mm']=abs(section['complete_length_mm']-section['supplied_centreline_length_mm'])
        section['saved_centreline_lateral_correspondence']=correspondence
        section['centreline_correspondence_pass']=correspondence['pass'] and section['centreline_length_error_mm']<1e-5
    section['received_valid']=received.isValid();section['physical_members_valid']=physical.isValid()
    section['diameter_mm']=diameter
    section['pass']=section['received_valid'] and section['physical_members_valid'] and (section.get('centreline_correspondence_pass',True))
    return physical,section


def sealed_sleeve_parity(tube,foam,edges,outer_diameter=25.4,tube_diameter=6.35):
    """Verify the received annulus and return its complete occupied envelope."""
    outer=outer_sweep(edges,outer_diameter)
    physical,section=circular_parity(outer,outer_diameter,edges)
    outer_faces=compare_lateral(lateral_records(foam,outer_diameter/2),lateral_records(outer,outer_diameter/2))
    inner_faces=compare_lateral(lateral_records(foam,tube_diameter/2),lateral_records(tube,tube_diameter/2))
    planar=sum(f.Area() for f in foam.Faces() if f.geomType()=='PLANE')
    expected_planar=2*math.pi*((outer_diameter/2)**2-(tube_diameter/2)**2)
    length=sum(e.Length() for e in edges)
    expected_volume=math.pi*((outer_diameter/2)**2-(tube_diameter/2)**2)*length
    actual_volume=foam.Volume(tol=1e-9)
    material_outside_outer=abs(foam.cut(outer,tol=.0001).Volume(tol=1e-9))
    tube_outside_outer=abs(tube.cut(outer,tol=.0001).Volume(tol=1e-9))
    section['received_annular_sleeve']={'valid':foam.isValid(),'solids':len(foam.Solids()),
        'outer_lateral_correspondence':outer_faces,'inner_lateral_correspondence':inner_faces,
        'native_planar_end_area_mm2':planar,'expected_annular_end_area_mm2':expected_planar,
        'end_section_pass':abs(planar-expected_planar)<.001,
        'native_material_volume_mm3':actual_volume,'expected_annular_material_volume_mm3':expected_volume,
        'material_volume_pass':abs(actual_volume-expected_volume)<max(.001,expected_volume*1e-6),
        'material_outside_occupied_outer_mm3':material_outside_outer,'tube_outside_occupied_outer_mm3':tube_outside_outer,
        'native_containment_pass':material_outside_outer<.001 and tube_outside_outer<.001,
        'scope':'Full occupied outer circular section; the saved insulation material is separately matched on both lateral surfaces and both annular ends. This does not treat the lumen as available space.'}
    annular=section['received_annular_sleeve']
    section['pass']=section['pass'] and foam.isValid() and len(foam.Solids())==1 and outer_faces['pass'] and inner_faces['pass'] and annular['end_section_pass'] and annular['material_volume_pass'] and annular['native_containment_pass']
    return physical,section


def received_member_compound(received,diameter):
    """Retain an independently section-checked received circular compound.

    Already published physical members carry their internal section caps.
    Check each received solid separately, then compare the aggregate volume.
    Its network continuity and self-clearance belong to the conductor proof.
    """
    pieces=[];checks=[]
    for index,solid in enumerate(received.Solids()):
        physical,proof=circular_parity(solid,diameter)
        pieces.extend(physical.Solids());checks.append({'received_solid':index,**proof})
    result=cq.Compound.makeCompound(pieces)
    delta=abs(result.Volume(tol=1e-9)-received.Volume(tol=1e-9))
    proof={'received_solid_sections':checks,'diameter_mm':diameter,
        'received_material_volume_mm3':received.Volume(tol=1e-9),
        'member_material_volume_mm3':result.Volume(tol=1e-9),'section_volume_error_mm3':delta,
        'pass':bool(checks) and all(q['pass'] for q in checks) and delta<.001,
        'scope':'Every received power solid retains exact circular lateral faces and complete circular section volume. The separate19-conductor proof owns network continuity, self-clearance and terminal mapping.'}
    return result,proof


def closest_members(a,b):
    """Distance and common use individual closed physical members only."""
    import audit
    minimum=math.inf;closest=None;overlap=0.;checked=0
    aa=[(s,audit.bbox(s)) for s in a.Solids()];bb=[(s,audit.bbox(s)) for s in b.Solids()]
    for i,(s,sb) in enumerate(aa):
        for j,(t,tb) in enumerate(bb):
            # A one-millimetre broad phase is sufficient for the air gate;
            # reported minima are limited to these admitted member pairs.
            if not audit.broad(sb,tb,1.):continue
            checked+=1;gap=s.distance(t)
            if gap<minimum:
                minimum=gap;closest={'a_member':i,'b_member':j,'air_mm':gap}
            if gap<1e-5:overlap+=audit.common(s,t)
    if closest is not None and minimum<1.:
        from OCP.BRepExtrema import BRepExtrema_DistShapeShape
        operation=BRepExtrema_DistShapeShape(aa[closest['a_member']][0].wrapped,bb[closest['b_member']][0].wrapped)
        if not operation.IsDone():raise ValueError('Native closest-member distance did not complete')
        closest['a_point_mm']=_point(operation.PointOnShape1(1));closest['b_point_mm']=_point(operation.PointOnShape2(1))
    return minimum,overlap,checked,closest
