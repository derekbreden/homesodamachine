"""Read-only correspondence of frozen clearance natives and their recipes.

The signature uses complete native surface supports and trimmed boundary curves
in world coordinates. Parametric seam placement and local surface axes do not
change the physical boundary. Solid ownership and all wire loops are retained.
"""
import hashlib,json,math
import cadquery as cq
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.BRep import BRep_Tool

def geometric_signature(shape):
    def raw(value):return value.toTuple() if isinstance(value,cq.Vector) else (value.X(),value.Y(),value.Z())
    def vec(value):
        values=raw(value)
        return [round(float(n),8) if abs(float(n))>=5e-9 else 0. for n in values]
    def normal(direction,rounded=True):
        values=list(raw(direction))
        for value in vec(direction):
            if value:
                canonical=[-n for n in values] if value<0 else values
                return [round(n,8) if abs(n)>=5e-9 else 0. for n in canonical] if rounded else canonical
        raise ValueError('Zero native support axis')
    def support(face):
        adaptor=BRepAdaptor_Surface(face.wrapped);kind=face.geomType()
        if kind=='PLANE':
            plane=adaptor.Plane();n=normal(plane.Axis().Direction(),False);p=raw(plane.Location())
            value=[normal(plane.Axis().Direction()),round(sum(a*b for a,b in zip(n,p)),8)]
        elif kind=='CYLINDER':
            cylinder=adaptor.Cylinder();n=normal(cylinder.Axis().Direction(),False);p=raw(cylinder.Location())
            dot=sum(a*b for a,b in zip(n,p));foot=[round(a-dot*b,8) for a,b in zip(p,n)]
            value=[normal(cylinder.Axis().Direction()),foot,round(cylinder.Radius(),8)]
        elif kind=='TORUS':
            torus=adaptor.Torus();value=[vec(torus.Location()),normal(torus.Axis().Direction()),
                round(torus.MajorRadius(),8),round(torus.MinorRadius(),8)]
        elif kind=='SPHERE':
            sphere=adaptor.Sphere();value=[vec(sphere.Location()),round(sphere.Radius(),8)]
        else:raise ValueError('Unsupported clearance surface '+kind)
        return [kind,value]
    def trim(edge):
        adaptor=edge._geomAdaptor();kind=edge.geomType();length=edge.Length()
        first,last=adaptor.FirstParameter(),adaptor.LastParameter()
        if kind=='LINE':
            return [kind,sorted([vec(adaptor.Value(first)),vec(adaptor.Value(last))]),round(length,8)]
        if kind=='CIRCLE':
            circle=adaptor.Circle();geometry=[vec(circle.Location()),normal(circle.Axis().Direction()),round(circle.Radius(),8)]
            if abs(length-2*math.pi*circle.Radius())<1e-7:return [kind,geometry,'complete circle']
            return [kind,geometry,sorted([vec(adaptor.Value(first)),vec(adaptor.Value(last))]),
                vec(adaptor.Value((first+last)/2)),round(length,8)]
        raise ValueError('Unsupported clearance trim '+kind)
    def face_signature(face):
        outer=face.outerWire();loops=[]
        for wire in face.Wires():
            edges=[trim(edge) for edge in wire.Edges() if not BRep_Tool.IsClosed_s(edge.wrapped,face.wrapped)]
            loops.append([wire.wrapped.IsSame(outer.wrapped),sorted(edges,key=lambda r:json.dumps(r,sort_keys=True))])
        return [support(face),sorted(loops,key=lambda r:json.dumps(r,sort_keys=True))]
    solids=[sorted([face_signature(f) for f in solid.Faces()],key=lambda r:json.dumps(r,sort_keys=True))
        for solid in shape.Solids()]
    data=sorted(solids,key=lambda r:json.dumps(r,sort_keys=True))
    return hashlib.sha256(json.dumps(data,separators=(',',':')).encode()).hexdigest()

def expected_clearance(body,record):
    from native_harness import sweep
    from circular_clearance import paired_members
    from controls_looms import clearance_envelope
    circular=('points_mm' in record and abs(body.Volume(tol=1e-9)-
        math.pi*(record['diameter_mm']/2)**2*record['length_mm'])<.001)
    if not circular:return clearance_envelope(body,fused_union=record.get('clearance_fused_union',False))
    if record.get('clearance_member_proof',{}).get('members'):
        authored=body if len(body.Solids())==1 else sweep(record['points_mm'],record['diameter_mm'],record['radius_mm'])[0]
        return paired_members(authored,record['diameter_mm'],gap=1.,fuse_clearance=True)[1]
    return sweep(record['points_mm'],record['diameter_mm']+2.,record['radius_mm'])[0]

def correspondence(body,cutter,record):
    expected=expected_clearance(body,record)
    recipe='Accepted enlarged analytic sweep or bounded cube Minkowski recipe'
    actual_signature=geometric_signature(cutter);expected_signature=geometric_signature(expected)
    if actual_signature!=expected_signature and 'points_mm' in record:
        # Fusing the separately enlarged exact lateral members can retain a
        # different boundary partition from the whole sweep. Both recipes
        # use the same authored centreline and the same1mm radial enlargement.
        # Admission still requires a complete support/trim/solid match.
        from native_harness import sweep
        from circular_clearance import paired_members
        authored=sweep(record['points_mm'],record['diameter_mm'],record['radius_mm'])[0]
        _,paired,_=paired_members(authored,record['diameter_mm'],gap=1.,fuse_clearance=True)
        paired_signature=geometric_signature(paired)
        if actual_signature==paired_signature:
            expected=paired;expected_signature=paired_signature
            recipe='Fused concentric1mm enlargement of each exact authored cylinder/torus member'
    delta_volume=abs(cutter.Volume(tol=1e-9)-expected.Volume(tol=1e-9))
    delta_area=abs(cutter.Area()-expected.Area())
    from native_harness import bounds
    delta_bounds=max(abs(a-b)for a,b in zip(bounds(cutter),bounds(expected)))
    return {'received_geometric_signature_sha256':actual_signature,
        'recipe_geometric_signature_sha256':expected_signature,'recipe':recipe,'volume_delta_mm3':delta_volume,
        'area_delta_mm2':delta_area,'maximum_bounds_delta_mm':delta_bounds,
        'received_solid_count':len(cutter.Solids()),'recipe_solid_count':len(expected.Solids()),
        'pass':cutter.isValid() and expected.isValid() and bool(cutter.Solids()) and
            actual_signature==expected_signature and delta_volume<.001 and delta_area<.001 and delta_bounds<1e-6,
        'scope':'Complete native plane/cylinder/torus/sphere supports, all real line/circle trim intervals and wire-loop/solid ownership agree at1e-8mm. Parametric seams and local support axes are excluded because they do not alter the physical boundary. The expected cutter uses the accepted1mm enlargement or bounded cube Minkowski recipe. No native file is written.'}
