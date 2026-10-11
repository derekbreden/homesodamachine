"""Compact enclosure constructed with the production working interfaces."""
from __future__ import annotations
import importlib.util
import json
import math
import os
import sys
from pathlib import Path

import cadquery as cq

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'hardware/scripts').is_dir())
CACHE_DIR = ROOT / '.cache/the-pour-v3/core'
SOURCE = ROOT / 'hardware/printed-parts/enclosure/enclosure/enclosure.py'
os.environ['HSM_NO_BUILD_LOCK'] = '1'
sys.path[:0] = [str(SOURCE.parent), str(ROOT / 'hardware/scripts'),
                str(ROOT / 'hardware/printed-parts/cadlib')]


def _handhold_roof_rim(before, rounded, x_face, inward, y0, y1, roof, corner, radius):
    """Production `overhang_round.roof_rim` geometry with a bounded union tolerance.

    Section points, circular-depth sampling, ellipse returns and the clipped
    additive stock are the source helper's exact construction. The final union
    uses 0.00001 mm tolerance for its coincident analytic faces.
    """
    from overhang_round import transition, OUTWARD_PER_HEIGHT
    height, foot = transition(radius)
    tangent_depth = foot-OUTWARD_PER_HEIGHT*height
    depths = {radius*(1-math.sin(math.radians(a))) for a in range(0,91,2)}
    depths.update((0.0,radius,foot,tangent_depth))
    wires = []
    for depth in sorted(depths):
        side = radius-math.sqrt(max(0,radius*radius-(radius-depth)**2))
        top = side if depth <= tangent_depth else max(0,(foot-depth)/OUTWARD_PER_HEIGHT)
        x = x_face+inward*depth
        base = roof-corner-1
        zl = roof-corner
        left, right = y0+corner,y1-corner
        def v(y,z): return cq.Vector(x,y,z)
        edges = [cq.Edge.makeLine(v(y0-side,base),v(y1+side,base)),
                 cq.Edge.makeLine(v(y1+side,base),v(y1+side,zl)),
                 cq.Edge.makeEllipse(corner+side,corner+top,(x,right,zl),
                                     (1,0,0),(0,1,0),0,90),
                 cq.Edge.makeLine(v(right,roof+top),v(left,roof+top)),
                 cq.Edge.makeEllipse(corner+side,corner+top,(x,left,zl),
                                     (1,0,0),(0,1,0),90,180),
                 cq.Edge.makeLine(v(y0-side,zl),v(y0-side,base))]
        wires.append(cq.Wire.assembleEdges(edges))
    air = cq.Solid.makeLoft(wires,ruled=False)
    xa, xb = sorted((x_face,x_face+inward*radius))
    cap = cq.Solid.makeBox(xb-xa,y1-y0+2*radius,corner+radius+.001,
                          cq.Vector(xa,y0-radius,roof-corner))
    fill = before.intersect(cap).cut(air)
    return rounded.fuse(fill,tol=1e-5).clean()


def source_module(width=258., depth=216., height=140., joint_y=100., joint_z=80.):
    """Private source instance; change envelope/stations, retain working sections."""
    spec = importlib.util.spec_from_file_location('_pour_native_enclosure', SOURCE)
    native = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = native
    spec.loader.exec_module(native)
    native.appliance_width = width
    # Production uses a floor whose bed face is -floor_t. The compact object
    # uses Z0 on that bed instead, with the interior floor at +floor_t.
    native.appliance_height = height + native.floor_t
    native.rear_plane_y = depth - native.wall
    native.y_seam = joint_y
    native.z_seam = joint_z
    native.handhold_y = joint_y
    native.fridge_reliefs = ()
    native.flute_count = 181
    def one_handhold(solid, inner, y_joint, y_side):
        """The native west handhold, with its complete rounded rim and receiver.

        The east wall carries the tee window. No handhold is constructed there.
        The operations and selections below are the production `_handholds`
        west iteration and `_grip_interface` west receiver, at the same datums.
        """
        bed, roof, _crown = native._handhold_levels(inner)
        y0, y1 = native._handhold_y()
        x_ext, sx = inner[0] - native.wall, 1.0
        solid = solid.fuse(native._handhold_frame(inner, y_joint, x_ext, sx, y_side))
        solid = solid.cut(native._handhold_cutter(inner, x_ext, sx))
        if y_side == 'front':
            solid = solid.cut(native._handhold_backing_joint(inner, y_joint, x_ext, sx, y_side))
            solid = solid.cut(native._handhold_floor_side_relief(inner, y_joint, x_ext, sx))
        solid = solid.clean()
        rim = []
        for edge in solid.Edges():
            b = edge.BoundingBox()
            if (abs(b.xmin-x_ext) < 1e-6 and abs(b.xmax-x_ext) < 1e-6
                and b.ymin >= y0-1e-6 and b.ymax <= y1+1e-6
                and b.zmin >= bed-1e-6 and b.zmax <= roof+1e-6
                and b.zmax > bed+1e-6):
                rim.append(edge)
        if not rim:
            raise ValueError(f'{y_side} west handhold at X{x_ext:g} has no exterior lifting edge')
        before = solid
        solid = solid.fillet(native.handhold_edge_r, rim)
        solid = _handhold_roof_rim(before, solid, x_ext, sx, y0, y1, roof,
                                   native.handhold_corner_r, native.handhold_edge_r)
        grip = native.grip_interface(inner)
        index = 0 if y_side == 'front' else 1
        return (solid.cut(grip.placed(grip.receiver_reliefs()[index], -1))
                     .cut(grip.placed(grip.receiver_slots()[index], -1)).clean())
    native._handholds = one_handhold
    return native


def compact_box(native, *, width=258., depth=216., height=140.,
                joint_y=100., joint_z=80.):
    outer = (-width/2, width/2, 0., depth, 0., height)
    inner = (-width/2+native.wall, width/2-native.wall,
             native.front_wall, depth-native.wall,
             native.floor_t, height-native.ceiling_skin)
    pack = native.Pack(placed={}, c14=(), port_field=native.PortField(0.,0.,()))
    bosses = native._bosses(inner, joint_y)
    box = native.Box(pack, inner, outer, joint_y, (joint_z, joint_z),
                     bosses, (), (), None)
    return box


def build_core(**dimensions):
    native = source_module(**dimensions)
    box = compact_box(native, **dimensions)
    # Individual production builders construct the authentic joints without
    # exporting production assets or deriving the complete refrigerated pack.
    cache = {}
    pieces = {}
    for yside in ('front', 'back'):
        for zside in ('bottom', 'top'):
            print(f'building {yside}-{zside}', flush=True)
            piece = native.build_piece(box, yside, zside, halves_cache=cache)
            shape = piece.val()
            pieces[f'{yside}-{zside}'] = shape
            print(f'  {len(shape.Solids())} solids, valid={shape.isValid()}, '
                  f'volume={shape.Volume():.1f}', flush=True)
    return native, box, pieces


if __name__ == '__main__':
    from _cadq_export import export_assembly
    out = CACHE_DIR
    out.mkdir(parents=True,exist_ok=True)
    native, box, pieces = build_core()
    assembly = cq.Assembly(name='the-pour-core')
    readings = {}
    for name, shape in pieces.items():
        assembly.add(shape, name=name,
                     color=cq.Color(.13,.15,.16))
        cq.exporters.export(shape, str(out / f'{name}.step'))
        b = shape.BoundingBox()
        readings[name] = dict(solids=len(shape.Solids()), valid=shape.isValid(),
                              bounds=[b.xmin,b.xmax,b.ymin,b.ymax,b.zmin,b.zmax],
                              volume=shape.Volume())
    export_assembly(assembly, str(out / 'core.step'))
    (out / 'geometry.json').write_text(json.dumps(readings, indent=2)+'\n')
