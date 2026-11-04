"""Beduan 1/4-inch quick-connect valve: measured exterior and assembly interfaces.

Millimetres. X crosses the flow axis, +Y points toward the terminals/outlet,
and Z=0 is the plane of the four mounting-post ends. Analytic features follow
the coated MINI 2 sample in scan-evidence.json. Hidden fluid passages and
fastener threads are outside this exterior reference.


The reference STEP and payloads are declared in `frozen-asset.json`.
Native builder functions remain available to current composition callers.
"""

from __future__ import annotations
from functools import lru_cache
from pathlib import Path

_REFERENCE_DIR = Path(__file__).resolve().parent
STEP_PATH = _REFERENCE_DIR / 'beduan-solenoid.step'
PAYLOAD_PATH = _REFERENCE_DIR / 'beduan-solenoid.step.mesh'
FINE_PAYLOAD_PATH = _REFERENCE_DIR / 'beduan-solenoid.step.mesh'
ASSET_MANIFEST_PATH = _REFERENCE_DIR / "frozen-asset.json"
import json
import math
import sys

_here = Path(__file__).resolve()
_hardware = next(p for p in _here.parents if p.name == 'hardware')
sys.path.insert(0, str(_hardware / 'scripts'))
sys.path.insert(0,str(_hardware.parent/'tools'))

# Mounting and moulded body. The post pattern is rectangular.

_reference_hardware = next(p for p in Path(__file__).resolve().parents if p.name == 'hardware')
import sys as _reference_sys
_reference_sys.path.insert(0, str(_reference_hardware / 'reference'))
from _reference_data import data as _reference_data
_reference_values = _reference_data('beduan_solenoid')
globals().update({name: _reference_values[name] for name in ('corner_spacing_x', 'corner_spacing_y', 'corner_inset_x', 'corner_inset_y', 'corner_spacing', 'corner_inset', 'corner_boss_radius', 'post_shoulder_z', 'upper_corner_radius', 'post_mouth_radius', 'post_mouth_depth', 'body_radius', 'body_width', 'bearing_radius', 'bearing_z_range', 'lower_edge_fillet', 'body_main_z_range', 'cap_width_x', 'cap_depth_y', 'cap_corner_radius', 'top_box_z_range', 'body_top_z', 'top_box_height', 'boss_z_range', 'corner_boss_z_range', 'body_width_x', 'body_x_pad', 'coil_depth', 'coil_z_range', 'bracket_top_z', 'coil_center_x', 'coil_center_y', 'coil_radius', 'coil_body_z_range', 'bracket_width', 'bracket_depth', 'bracket_thickness', 'bracket_outer_bend', 'bracket_base_z_range', 'screw_head_radius', 'screw_head_height', 'port_radius', 'port_length', 'port_center_z', 'port_neck_radius', 'collet_radius', 'collet_neck_radius', 'collet_ear_radius', 'collet_ear_sectors', 'collet_clip_radius', 'collet_clip_sectors', 'port_mouth_radius', 'port_mouth_depth', 'spade_width', 'spade_thickness', 'spade_x_spacing', 'spade_z_center', 'coil_face_y', 'spade_length', 'spade_hole_radius', 'terminal_block_z_range', 'underside_relief_xy', 'underside_relief_size', 'underside_relief_top_z')})


# Station pitch includes assembly air; it is independent of the physical cap.

# Coil and bent steel yoke. The open front/back and side air gaps are real.

# Port barrel, release collet, and the observed tube-entry mouth.

# Terminals: exposed metal, plus the moulded root that sets connector access.

# Shallow moulded underside relief; the broad annulus remains the bearing face.


def mounting_centers():
    return _reference_data('beduan_solenoid', 'mounting_centers', (), {})


def _cylinder(radius, z0, z1, xy=(0, 0)):
    import cadquery as cq
    return (cq.Workplane('XY').workplane(offset=z0)
            .center(*xy).circle(radius).extrude(z1-z0))


def _rounded_plate(width, depth, z0, z1, radius):
    import cadquery as cq
    return (cq.Workplane('XY').workplane(offset=z0)
            .box(width, depth, z1-z0, centered=(True,True,False))
            .edges('|Z').fillet(radius))


def _cap_plate(z0, z1):
    plate = _rounded_plate(cap_width_x, cap_depth_y, z0, z1, cap_corner_radius)
    for side in (-1,1):
        notch = _rounded_plate(10.5,4,z0-1,z1+1,.7).translate((0,side*17,0))
        plate = plate.cut(notch)
    return plate


def build_body():
    import cadquery as cq
    lower = _cylinder(bearing_radius, *bearing_z_range).edges('<Z').fillet(lower_edge_fillet)
    body = _cylinder(body_radius, *body_main_z_range)
    for xy in mounting_centers():
        body = body.union(_cylinder(upper_corner_radius, post_shoulder_z, body_main_z_range[1], xy))
    body = body.edges('|Z').fillet(.8)
    body = body.union(lower)
    relief=(cq.Workplane('XZ').polyline([(12.05,10.5),(14.6,10.5),
                                       (14.6,11.1),(12.05,14.4)])
            .close().revolve(360,(0,0),(0,1)))
    body=body.cut(relief)
    for xy in mounting_centers():
        foot = _cylinder(corner_boss_radius, 0, bearing_z_range[1], xy).edges('<Z').fillet(.45)
        mouth = _cylinder(post_mouth_radius, -.1, post_mouth_depth, xy)
        body = body.union(foot.cut(mouth))
    cap = _cap_plate(*top_box_z_range)
    cap = cap.edges('#Z').fillet(.35)
    return body.union(cap).cut(build_underside_relief())


def _port_half(side):
    import cadquery as cq
    profile = [(9.5,0),(9.5,port_neck_radius),(16.0,port_neck_radius),
               (17.6,7.35),(18.4,port_radius),(25.8,port_radius),
               (26.5,7.25),(26.5,0)]
    barrel = (cq.Workplane('XY').polyline(profile).close()
              .revolve(360,(0,0),(1,0)).rotate((0,0,0),(0,0,1),90)
              .translate((0,0,port_center_z)))
    collet = cq.Workplane(obj=cq.Solid.makeCylinder(
        collet_neck_radius, 2.0, cq.Vector(0,26.3,port_center_z), cq.Vector(0,1,0)))
    lip = cq.Workplane(obj=cq.Solid.makeCylinder(
        collet_radius, port_length/2-28.1, cq.Vector(0,28.1,port_center_z), cq.Vector(0,1,0)))
    lip = lip.edges().fillet(.25)
    collet = collet.union(lip)
    mouth = cq.Solid.makeCylinder(port_mouth_radius, port_mouth_depth+.1,
        cq.Vector(0,port_length/2-port_mouth_depth,port_center_z),cq.Vector(0,1,0))
    barrel, collet = barrel.cut(mouth), collet.cut(mouth)
    if side < 0:
        barrel = barrel.rotate((0,0,0),(0,0,1),180)
        collet = collet.rotate((0,0,0),(0,0,1),180)
    def sector(inner_radius,outer_radius,start,end,y0,y1):
        def polar(radius,angle):
            angle=math.radians(angle)
            return radius*math.cos(angle),radius*math.sin(angle)
        return (cq.Workplane('XZ',origin=(0,side*y0,port_center_z))
                .moveTo(*polar(inner_radius,start)).lineTo(*polar(outer_radius,start))
                .threePointArc(polar(outer_radius,(start+end)/2),polar(outer_radius,end))
                .lineTo(*polar(inner_radius,end))
                .threePointArc(polar(inner_radius,(start+end)/2),polar(inner_radius,start))
                .close().extrude(-side*(y1-y0)))
    collet=collet.union(sector(4.8,collet_clip_radius,*collet_clip_sectors[side],26.8,28.2))
    for start,end in collet_ear_sectors[side]:
        def polar(radius, angle):
            angle=math.radians(angle)
            return radius*math.cos(angle),radius*math.sin(angle)
        ear=(cq.Workplane('XZ',origin=(0,side*27.3,port_center_z))
             .moveTo(*polar(4.8,start)).lineTo(*polar(collet_ear_radius,start))
             .threePointArc(polar(collet_ear_radius,(start+end)/2),polar(collet_ear_radius,end))
             .lineTo(*polar(4.8,end)).threePointArc(polar(4.8,(start+end)/2),polar(4.8,start))
             .close().extrude(-side*(port_length/2-27.3)))
        collet=collet.union(ear)
    return barrel.cut(build_underside_relief()), collet


def build_port():
    import cadquery as cq
    parts = [_port_half(side) for side in (-1,1)]
    return cq.Workplane(obj=cq.Compound.makeCompound([p.val() for pair in parts for p in pair]))


def build_winding():
    import cadquery as cq
    winding = _cylinder(coil_radius, *coil_body_z_range, (coil_center_x,coil_center_y))
    winding = winding.edges().fillet(.6)
    rim = _cylinder(12.65,50.2,54.8,(coil_center_x,coil_center_y)).edges().fillet(.5)
    block = (cq.Workplane('XY').box(24.6,6.2,terminal_block_z_range[1]-terminal_block_z_range[0])
             .translate((coil_center_x,13.1,sum(terminal_block_z_range)/2))
             .edges('|Y').fillet(3.0))
    relief=(cq.Workplane('XY').box(10.4,7.0,4.0)
            .translate((coil_center_x,11.3,57.8)).edges('|Y').fillet(.6))
    block=block.cut(relief)
    nose=(cq.Workplane('YZ',origin=(-1.0,0,0)).moveTo(15.5,49.7)
          .lineTo(17.2,49.7).threePointArc((18.15,50.1),(18.5,51.2))
          .lineTo(18.5,54.8).threePointArc((17.8,56.6),(16.2,57.1))
          .lineTo(15.5,57.1).close().extrude(2.2))
    block=block.union(nose)
    winding = winding.union(rim).union(block)
    for side in (-1,1):
        root = (cq.Workplane('XY').box(7.7,3.1,1.8)
                .translate((side*spade_x_spacing/2,17.3,spade_z_center))
                .edges('|Z').fillet(.5))
        winding = winding.union(root)
    roof=_cylinder(12.2,54.8,56.4,(coil_center_x,coil_center_y)).edges('>Z').fillet(.65)
    tongue=_rounded_plate(10,6.5,54.8,56.0,.6).translate((coil_center_x,11.25,0))
    return winding.union(roof).union(tongue).cut(build_bracket())


def build_bracket():
    import cadquery as cq
    z0,z1 = coil_z_range[0],bracket_top_z
    outer = (cq.Workplane('XY').box(bracket_width,bracket_depth,z1-z0)
             .translate((coil_center_x,0,(z0+z1)/2)).edges('|Y and >Z').fillet(bracket_outer_bend))
    inner = (cq.Workplane('XY').box(bracket_width-2*bracket_thickness,bracket_depth+2,z1-bracket_thickness-z0+2)
             .translate((coil_center_x,0,(z0-2+z1-bracket_thickness)/2))
             .edges('|Y and >Z').fillet(bracket_outer_bend-bracket_thickness))
    base = _cap_plate(*bracket_base_z_range)
    return outer.cut(inner).union(base)


def build_coil():
    coil=build_winding().union(build_bracket())
    for screw in build_screw_heads():
        coil=coil.union(screw)
    return coil


def build_screw_heads():
    return [_cylinder(screw_head_radius,bracket_base_z_range[1],bracket_base_z_range[1]+screw_head_height,xy)
            .edges('>Z').fillet(.65) for xy in mounting_centers()]


def build_spades():
    import cadquery as cq
    tabs=[]
    for side in (-1,1):
        x=side*spade_x_spacing/2
        tab=(cq.Workplane('XY').box(spade_width,spade_length,spade_thickness)
             .translate((x,coil_face_y+spade_length/2,spade_z_center)).edges('|Z').fillet(.75))
        hole=_cylinder(spade_hole_radius,spade_z_center-1,spade_z_center+1,(x,23.6))
        tabs.append(tab.cut(hole))
    return tabs


def build_underside_relief():
    return (_rounded_plate(*underside_relief_size,4.5,underside_relief_top_z,.9)
            .translate((*underside_relief_xy,0)).edges('>Z').fillet(.45))


def inlet():
    return _reference_data('beduan_solenoid', 'inlet', (), {})


def outlet():
    return _reference_data('beduan_solenoid', 'outlet', (), {})


@lru_cache(maxsize=1)
def _parts():
    import cadquery as cq
    from _materials import C_VALVE, M_MOULDED_BLACK, M_ZINC_PLATED_STEEL, M_TINNED_STEEL
    body=build_body()
    collets=[]
    for side in (-1,1):
        barrel,collet=_port_half(side)
        body=body.union(barrel)
        collets.append(collet)
    screws=build_screw_heads()
    return {'body':(body,C_VALVE),'collets':(cq.Workplane(obj=cq.Compound.makeCompound([s.val() for s in collets])),C_VALVE),
            'winding':(build_winding(),M_MOULDED_BLACK),'yoke':(build_bracket(),M_ZINC_PLATED_STEEL),
            'terminals':(cq.Workplane(obj=cq.Compound.makeCompound([s.val() for s in build_spades()])),M_TINNED_STEEL),
            'screw-heads':(cq.Workplane(obj=cq.Compound.makeCompound([s.val() for s in screws])),M_ZINC_PLATED_STEEL)}


def build_beduan_solenoid():
    """Exterior compound in the mounting frame, including all material components."""
    import cadquery as cq
    return cq.Workplane(obj=cq.Compound.makeCompound([s for p,_ in _parts().values() for s in p.val().Solids()]))


def build_assembly():
    import cadquery as cq
    assy=cq.Assembly(name='beduan-solenoid')
    for name,(part,color) in _parts().items():
        assy.add(part,name=name,color=color)
    return assy


def main():
    print(f"Frozen STEP: {STEP_PATH}")
    print(f"Display payload: {PAYLOAD_PATH}")
    print(f"Fine payload: {FINE_PAYLOAD_PATH}")


if __name__=='__main__':
    main()


def __getattr__(name):
    if name == "substitute_md":
        from docgen import substitute_md
        return substitute_md
    if name == "cq":
        import cadquery
        return cadquery
    if name == "export_assembly":
        from _cadq_export import export_assembly
        return export_assembly
    if name in {"C_VALVE", "M_MOULDED_BLACK", "M_ZINC_PLATED_STEEL", "M_TINNED_STEEL"}:
        import _materials
        return getattr(_materials, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
