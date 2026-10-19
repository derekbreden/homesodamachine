"""Permanent wall-supported asymmetric TPU pump junction.

Local +Y enters the enclosure; Y=0 is the PET-GF wall's pump-facing surface.
The closed wall locates X/Z. A flat interior keeper in the rear groove
retains Y. The three tube sockets use radial interference; the cartridge hard
stop sets insertion and leaves its tube tip clear of the annular stop.

The Ø6.10 bore and 2.8 mm minimum radial cuff wall follow the manually fitted
TPU elbow article. Six-millimetre lands, wall confinement, permanent service,
pressure holding and endurance are unqualified on this geometry. The lower-mouth print pose keeps the terminal bores at0/45/45 degrees.
External supports remain accessible before factory mounting. Round flow roofs
are separate from the round sealing lands.
"""
from functools import lru_cache
import json
from pathlib import Path
import argparse
import json
import math
import sys

import cadquery as cq
import fixed_returns as plumbing
import pump_return as returned
from flow_roof import cached_flow_cap

HERE = Path(__file__).resolve().parent
HARDWARE = next(p for p in HERE.parents if p.name == "hardware")
sys.path.insert(0, str(HARDWARE / "scripts"))

# Shared mechanical contract, all axial stations measured from the wall fore face.
WALL_THICKNESS = 7.0
TUBE_OD = 6.35
TUBE_ID = 4.30
SEAL_BORE_D = 6.10
BODY_OD = 11.70
WALL_BORE_D = 12.00
WALL_RADIAL_CLEARANCE = (WALL_BORE_D - BODY_OD) / 2
FRONT_LIP_OD = 14.0
FRONT_COUNTERBORE_D = 14.3
FRONT_LIP_Y = (0.0, 0.6)
FUNNEL_BORE_D = 9.0
FRONT_SEAL_Y = (1.0, 7.0)
FRONT_RELIEF_D = 6.8
CUSTOMER_TIP_Y = 7.5
CUSTOMER_STOP_Y = 8.0
CUSTOMER_TIP_END_D = 6.05
THROAT_D = 5.00
RELIEF_TAPER_START_Y = CUSTOMER_STOP_Y - (FRONT_RELIEF_D - CUSTOMER_TIP_END_D) / 2
RELIEF_TAPER_END_Y = RELIEF_TAPER_START_Y + (FRONT_RELIEF_D - THROAT_D) / 2
COLLAR_OD = 17.5
COLLAR_RAMP_Y = (3.6, 5.9)
FRONT_COLLAR_Y = (5.9, 7.0)
GROOVE_Y = (7.0, 10.35)
REAR_COLLAR_Y = (10.35, 13.35)
KEEPER_SLOT_D = 12.4
KEEPER_RADIAL_CLEARANCE = (KEEPER_SLOT_D - BODY_OD) / 2
KEEPER_Y = (7.15, 10.15)
KEEPER_THICKNESS = KEEPER_Y[1] - KEEPER_Y[0]
UPPER_MOUTH_LOCAL_Y = 22.775
BRANCH_OD = 11.72
FORK_BLEND_R = .60
LOWER_STOP_BORE_D = 5.50
LOWER_STOP_TAPER = (LOWER_STOP_BORE_D-TUBE_ID)/2
ENTRY_AXIAL = .50
ENTRY_RADIAL = .25
KEY_ROOT_X = 6.5
KEY_OUTER_X = 12.5
KEY_BASE_Z = -3.0
KEY_SHOULDER_Z = 0.0
KEY_TOP_Z = 3.0
MATERIAL = "Siraya Tech Flex TPU 85A Clear"
# Clear stock, rather than the black Bambu 90A gasket stock.
COLOR = cq.Color(.92, .92, .90, .60)
_EPS = 0.02


def _cylinder(diameter, y0, y1):
    return cq.Solid.makeCylinder(diameter / 2, y1 - y0,
                                 cq.Vector(0, y0, 0), cq.Vector(0, 1, 0))


def _cone(d0, d1, y0, y1):
    return cq.Solid.makeCone(d0 / 2, d1 / 2, y1 - y0,
                             cq.Vector(0, y0, 0), cq.Vector(0, 1, 0))


def _outside(installed=False):
    # Conserved annular area supplies a conservative occupied envelope only.
    # It is not an elastic-deformation or contact-pressure prediction.
    growth = TUBE_OD ** 2 - SEAL_BORE_D ** 2 if installed else 0.0
    od = lambda diameter: math.sqrt(diameter ** 2 + growth)
    return (_cylinder(od(BODY_OD), FRONT_LIP_Y[0], REAR_COLLAR_Y[1])
            .fuse(_cylinder(od(FRONT_LIP_OD), *FRONT_LIP_Y))
            .fuse(_cone(od(BODY_OD), od(COLLAR_OD), *COLLAR_RAMP_Y))
            .fuse(_cylinder(od(COLLAR_OD), *FRONT_COLLAR_Y))
            .fuse(_cylinder(od(COLLAR_OD), *REAR_COLLAR_Y)).clean())


def _place(shape, wall_fore_y=0.0, x=0.0, z=0.0):
    return shape.translate((x, wall_fore_y, z))


def _wire(segments):
    edges=[]
    for segment in segments:
        a=cq.Vector(*segment["start_mm"]); b=cq.Vector(*segment["end_mm"])
        edges.append(cq.Edge.makeThreePointArc(a,cq.Vector(*segment["midpoint_mm"]),b)
                     if segment["kind"]=="arc" else cq.Edge.makeLine(a,b))
    return cq.Wire.assembleEdges(edges)


def _sweep(diameter,segments):
    first=segments[0]
    profile=cq.Wire.makeCircle(diameter/2,cq.Vector(*first["start_mm"]),
                              cq.Vector(*first["start_tangent"]))
    return cq.Solid.sweep(profile,[],_wire(segments),makeSolid=True,isFrenet=True)


def _default_junction():
    return plumbing.junction_ports(0.,0.,0.,
        {"point":(0.,UPPER_MOUTH_LOCAL_Y,36.501),"axis":(0.,0.,-1.)},
        {"point":(0.,83.725,-16.),"axis":(0.,0.,-1.)})


def _local_junction(junction,origin):
    if junction is None:return _default_junction()
    out=dict(junction)
    for key in ("upper_flow_segments","lower_flow_segments"):
        out[key]=tuple({k:tuple(v[i]-origin[i] for i in range(3))
                        if k in ("start_mm","end_mm","midpoint_mm") else v
                        for k,v in segment.items()} for segment in junction[key])
    for key in ("upper","lower","upper_target","return_target"):
        out[key]=dict(junction[key])
        for field in ("point","tube_stop"):
            if field in junction[key]:out[key][field]=tuple(junction[key][field][i]-origin[i] for i in range(3))
    return out


def anti_rotation_keys():
    """Broad rear-flange ears enter open-aft house-shaped PET-GF seats.

    The rear flange is three millimetres thick. These keys carry clocking
    loads; the wall and flat keeper retain the permanent junction axially.
    """
    parts=[]
    for sign in (-1,1):
        cx=sign*(KEY_ROOT_X+KEY_OUTER_X)/2
        points=[(cx-3,KEY_BASE_Z),(cx+3,KEY_BASE_Z),
                (cx+3,KEY_SHOULDER_Z),(cx,KEY_TOP_Z),
                (cx-3,KEY_SHOULDER_Z)]
        wire=cq.Wire.makePolygon([cq.Vector(x,REAR_COLLAR_Y[0],z) for x,z in points]
                                +[cq.Vector(points[0][0],REAR_COLLAR_Y[0],points[0][1])])
        parts.append(cq.Solid.extrudeLinear(wire,[],cq.Vector(0,REAR_COLLAR_Y[1]-REAR_COLLAR_Y[0],0)))
    return parts[0].fuse(parts[1])


def _geometry(*,installed=False,junction=None,mount_side=1):
    """Local wet solid, occupied envelope and cavity from shared port datums."""
    junction=junction or _default_junction()
    growth=TUBE_OD**2-SEAL_BORE_D**2 if installed else 0.
    od=math.sqrt(BRANCH_OD**2+growth)
    seal=TUBE_OD if installed else SEAL_BORE_D
    root=junction["upper_flow_segments"][0]["start_mm"][1]
    outer=_outside(installed).fuse(anti_rotation_keys())
    void=(_cone(FUNNEL_BORE_D,seal,0.,FRONT_SEAL_Y[0])
          .fuse(_cylinder(FUNNEL_BORE_D,-_EPS,0.))
          .fuse(_cylinder(seal,*FRONT_SEAL_Y))
          .fuse(_cylinder(FRONT_RELIEF_D,FRONT_SEAL_Y[1],RELIEF_TAPER_START_Y))
          .fuse(_cone(FRONT_RELIEF_D,THROAT_D,RELIEF_TAPER_START_Y,RELIEF_TAPER_END_Y))
          .fuse(_cylinder(THROAT_D,RELIEF_TAPER_END_Y,root+.08)))
    for branch in ("upper","lower"):
        segments=junction[branch+"_flow_segments"]
        outer=outer.fuse(_sweep(od,segments))
        void=void.fuse(_sweep(TUBE_ID,segments))
        port=junction[branch]; d=cq.Vector(*port["axis"])
        stop=cq.Vector(*port["tube_stop"])
        if branch=='lower':
            # The downward-printed socket retains a supported0.30mm annular
            # stop. The downstream45degree taper leaves the6mm land and the
            # factory tip datum untouched.
            void=void.fuse(cq.Solid.makeCone(LOWER_STOP_BORE_D/2,TUBE_ID/2,
                          LOWER_STOP_TAPER,stop,d*-1))
        end=stop+d*plumbing.SEAL_LAND
        void=void.fuse(cq.Solid.makeCylinder(seal/2,plumbing.SEAL_LAND,stop,d),
                       cq.Solid.makeCone(seal/2,seal/2+ENTRY_RADIAL,ENTRY_AXIAL,end,d),
                       cq.Solid.makeCylinder(seal/2+ENTRY_RADIAL,_EPS,cq.Vector(*port["point"]),d))
    lower=junction["lower_flow_segments"][0]
    blend_edges=[e for e in void.Edges() if e.geomType()=="BSPLINE"
                 and e.BoundingBox().ymax>lower["end_mm"][1]+1.2
                 and e.BoundingBox().zmin>lower["end_mm"][2]/2-.04
                 and e.BoundingBox().zmax<0]
    void=void.fillet(FORK_BLEND_R,blend_edges).clean()
    # Build the roof in the actual lower-mouth-flat print frame. A clocked
    # outer junction first yaws its terminal's horizontal tangent onto+Y.
    zrot,xrot=print_rotations(junction)
    arc=junction["upper_flow_segments"][0]
    def rz(v):
        a=math.radians(zrot);return (v[0]*math.cos(a)-v[1]*math.sin(a),v[0]*math.sin(a)+v[1]*math.cos(a),v[2])
    rotated={k:rz(v) if k in ("start_mm","midpoint_mm","end_mm","start_tangent","end_tangent") else v for k,v in arc.items()}
    roof=cached_flow_cap(rotated,TUBE_ID/2,print_angle=xrot).rotate((0,0,0),(0,0,1),-zrot)
    void=void.fuse(roof).clean()
    # Broad keys retain the two supported sockets; the lower key's aft shift
    # is parallel to its actual print bed, leaving the lower rim seated.
    bare=outer.clean()
    lower=junction['lower'];target=junction['return_target']
    local_return=plumbing.return_layout(lower['point'],lower['axis'],target)
    origin,n,h=returned.frame(local_return)
    build=print_build_direction(junction)
    local_build=(build.dot(n),build.dot(h),build.z)
    keys=[]
    for point in mount_stations(junction):
        center=returned._point(point,origin,n,h)
        key=returned.to_world(returned.button(center,mount_side,installed=installed,build_direction=local_build),local_return)
        keys.append(key);outer=outer.fuse(key)
    neck_od=math.sqrt(BODY_OD**2+growth)
    ring=_cylinder(50.,*GROOVE_Y).cut(_cylinder(neck_od,GROOVE_Y[0]-.01,GROOVE_Y[1]+.01))
    outer=outer.cut(ring).clean()
    return {"body":outer.cut(void).clean(),"envelope":outer,"bare_envelope":bare,"void":void,
            "junction":junction,"occupied_od":od,"keys":tuple(keys)}


def mount_stations(junction):
    """Aft lower key keeps its socket-stop build height and a broad cuff root."""
    target=junction['return_target'];port=junction['lower']
    layout=plumbing.return_layout(port['point'],port['axis'],target)
    _,n,h=returned.frame(layout)
    build=print_build_direction(junction)
    move=(cq.Vector(*port['point'])-cq.Vector(*port['tube_stop'])).dot(h)
    shift=h*move+cq.Vector(0,0,-build.dot(h)/build.z*move)
    return ((cq.Vector(*port['tube_stop'])+shift).toTuple(),tuple(junction['upper']['tube_stop']))


@lru_cache(maxsize=24)
def _cached_geometry(declaration,installed,mount_side):
    return _geometry(installed=installed,junction=json.loads(declaration),mount_side=mount_side)


def geometry(*,installed=False,junction=None,mount_side=1):
    declaration=json.dumps(junction or _default_junction(),sort_keys=True)
    return _cached_geometry(declaration,installed,mount_side)


def build_receiver(wall_fore_y=0.,x=0.,z=0.,*,installed=False,junction=None,mount_side=None):
    local=_local_junction(junction,(x,wall_fore_y,z))
    return _place(geometry(installed=installed,junction=local,mount_side=(1 if x>=0 else -1) if mount_side is None else mount_side)["body"],wall_fore_y,x,z)


def receiver_envelope(wall_fore_y=0.,x=0.,z=0.,*,installed=False,junction=None,mount_side=None,include_mounts=True):
    local=_local_junction(junction,(x,wall_fore_y,z))
    return _place(geometry(installed=installed,junction=local,mount_side=(1 if x>=0 else -1) if mount_side is None else mount_side)["envelope" if include_mounts else "bare_envelope"],wall_fore_y,x,z)


def receiver_wall_cut(wall_fore_y=0.0, x=0.0, z=0.0):
    """Closed-bore wall tool including front lip and recessed collar seats.

    This only cuts Y=0..7; keeper guides and rear cuff support belong to the
    enclosure. The collar recess carries the same 0.15 mm normal radial room
    as the supported cylindrical cuff. Its ramp allows the TPU to be pressed
    from the interior while flexing the small front lip through the bore.
    """
    tool = (_cylinder(WALL_BORE_D, -_EPS, WALL_THICKNESS + _EPS)
            .fuse(_cylinder(FRONT_COUNTERBORE_D, -_EPS, FRONT_LIP_Y[1]))
            .fuse(_cone(WALL_BORE_D, COLLAR_OD + 2 * WALL_RADIAL_CLEARANCE,
                        *COLLAR_RAMP_Y))
            .fuse(_cylinder(COLLAR_OD + 2 * WALL_RADIAL_CLEARANCE,
                            FRONT_COLLAR_Y[0], WALL_THICKNESS + _EPS)))
    return _place(tool.clean(), wall_fore_y, x, z)


def wet_stations(wall_fore_y=0.,x=0.,z=0.,*,junction=None):
    local=_local_junction(junction,(x,wall_fore_y,z))
    return {"axis":(0.,1.,0.),
            "customer_tip":(x,wall_fore_y+CUSTOMER_TIP_Y,z),
            "customer_stop":(x,wall_fore_y+CUSTOMER_STOP_Y,z),
            "front_seal":((x,wall_fore_y+FRONT_SEAL_Y[0],z),(x,wall_fore_y+FRONT_SEAL_Y[1],z)),
            "upper":local["upper"],"lower":local["lower"]}


def print_rotations(junction=None):
    d=(junction or _default_junction())['lower']['axis']
    return math.degrees(math.atan2(d[0],d[1])),-math.degrees(math.atan2(math.hypot(d[0],d[1]),-d[2]))


def print_build_direction(junction=None):
    yaw,tilt=map(math.radians,print_rotations(junction))
    return cq.Vector(math.sin(tilt)*math.sin(yaw),math.sin(tilt)*math.cos(yaw),math.cos(tilt))


def print_solid(*,junction=None,mount_side=1):
    """Actual lower mouth normal points down, giving a flat sealing rim bed."""
    zrot,xrot=print_rotations(junction)
    solid=geometry(junction=junction,mount_side=mount_side)['body'].rotate((0,0,0),(0,0,1),zrot).rotate((0,0,0),(1,0,0),xrot)
    return solid.translate((0,0,-solid.BoundingBox().zmin))


def engineering_record():
    return {"material":MATERIAL,"wall_thickness_mm":WALL_THICKNESS,
            "front_seal_bore_mm":SEAL_BORE_D,"front_seal_land_mm":6.,
            "branch_seal_land_mm":plumbing.SEAL_LAND,"branch_entry_axial_mm":ENTRY_AXIAL,
            "branch_entry_radial_mm":ENTRY_RADIAL,"branch_mouth_radial_stock_mm":BRANCH_OD/2-SEAL_BORE_D/2-ENTRY_RADIAL,
            "relaxed_cuff_od_mm":BODY_OD,"occupied_cuff_od_mm":math.sqrt(BODY_OD**2+TUBE_OD**2-SEAL_BORE_D**2),
            "rear_flange_y_mm":REAR_COLLAR_Y,"anti_rotation_key_x_mm":[KEY_ROOT_X,KEY_OUTER_X],
            "groove_y_mm":GROOVE_Y,"keeper_y_mm":KEEPER_Y,
            "keeper_wall_face_gap_mm":KEEPER_Y[0]-WALL_THICKNESS,"keeper_rear_groove_room_mm":GROOVE_Y[1]-KEEPER_Y[1],
            "lower_socket_stop_bore_mm":LOWER_STOP_BORE_D,"lower_socket_stop_radial_mm":(SEAL_BORE_D-LOWER_STOP_BORE_D)/2,
            "lower_socket_stop_taper_mm":LOWER_STOP_TAPER,"installed_tip_stop_contact_area_mm2":math.pi*(TUBE_OD**2-LOWER_STOP_BORE_D**2)/4,
            "fork_blend_radius_mm":FORK_BLEND_R,"customer_tip_clearance_mm":CUSTOMER_STOP_Y-CUSTOMER_TIP_Y,
            "flow_throat_d_mm":THROAT_D,"relief_taper_y_mm":[RELIEF_TAPER_START_Y,RELIEF_TAPER_END_Y],
            "print_orientation":"Yaw the actual lower outward axis onto+Y, then rotate it onto−Z; lower mouth rim flat on the bed. Exterior Tree(auto)/Default support only.",
            "physical_reference":"future/pump-elbow-exploration/prints/2026-10-14-compact-single-siraya85a-overhang10-engineering-z000-mark1/physical-result.json",
            "scope":"Native manufacturing geometry. Siraya elbow exterior acceptance does not establish this fork, wet-service suitability, seal retention, pressure holding, support release or lifetime."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=HERE.parent / "enclosure")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    from _cadq_export import export_assembly
    from _material_base import one_body
    import flute_payload
    shape = build_receiver()
    stem = args.out / "enclosure-pump-receiver"
    cq.exporters.export(shape, str(stem.with_suffix(".stl")),
                        tolerance=.015, angularTolerance=.06)
    export_assembly(one_body(shape, "enclosure-pump-receiver", COLOR),
                    str(stem.with_suffix(".step")))
    flute_payload.cut(stem.with_suffix(".step"), stem.with_suffix(".stl"),
                       preserve_print_triangles=True)
    (HERE / "pump-receiver.json").write_text(
        json.dumps(engineering_record(), indent=2) + "\n")
    print(f"{stem}: {shape.Volume():.1f} mm³, {len(shape.Solids())} solid")


if __name__ == "__main__":
    main()
