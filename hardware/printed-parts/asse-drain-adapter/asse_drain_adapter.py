"""TPU vent cup with an aft-facing 4 mm drain socket.

The scanned ASSE's exposed vent stem enters the vertical cup. A printed
quarter turn carries its open drain to a horizontal socket on native -X.
Both sockets retain a separate four-inch tie land. Native +Z points into
its vent mouth; the printable frame tips both bores upward at 45 degrees.
"""
from pathlib import Path
import math
import sys

import cadquery as cq

HERE = Path(__file__).resolve().parent
HARDWARE = HERE.parents[1]
sys.path.insert(0, str(HARDWARE / "scripts"))
sys.path.insert(0, str(HARDWARE / "reference/multiplex-asse1022"))
from _cadq_export import export_assembly
from _material_base import M_TPU_BLACK, one_body
import multiplex_asse1022 as bfp

BARB_BORE = 6.10
TUBE_BORE = 3.80
TUBE_DEPTH = 14.0
REDUCER_LENGTH = .50  # Open taper below the vent tip, before the turn.
MIN_WALL = 3.45  # Shared relaxed radial minimum, under both tie lands.
GROOVE_DEPTH = .50
BARB_OD = BARB_BORE + 2 * (MIN_WALL + GROOVE_DEPTH)
TUBE_OD = TUBE_BORE + 2 * (MIN_WALL + GROOVE_DEPTH)
GROOVE_FLAT = 2.80  # Existing 0.1-inch / 2.54 mm-wide four-inch ties.
GROOVE_RAMP = 1.0  # At most .5 mm radial growth / mm build rise.
BARB_TIE_Z = 5.5
INSTALLED_REACH = 8.6  # Below the scanned vent hex, on the exposed stem.


def _revolve(profile):
    return (cq.Workplane("XZ").polyline(profile).close()
            .revolve(360, (0, 0), (0, 1)).val())


ELBOW_REACH = 25.4
ELBOW_R = 4.05
TURN_START_Z = -REDUCER_LENGTH
SOCKET_DROP = -TURN_START_Z+ELBOW_R


def build(*, installed=False):
    """One vent cup with an aft-facing 4 mm socket and two tie lands.

    Native -X is the tube exit, +Z points into the vent cup. The cup's
    upper lip is half a millimetre below the ASSE wrench flat.
    """
    barb_d = bfp.VENT_D if installed else BARB_BORE
    tube_d = 4. if installed else TUBE_BORE
    rb = math.sqrt(BARB_OD**2+barb_d**2-BARB_BORE**2)/2.
    rt = math.sqrt(TUBE_OD**2+tube_d**2-TUBE_BORE**2)/2.
    cup = cq.Solid.makeCylinder(rb,INSTALLED_REACH+SOCKET_DROP+rt,
                               cq.Vector(0.,0.,-SOCKET_DROP-rt))
    socket = cq.Solid.makeCylinder(rt,ELBOW_REACH,
        cq.Vector(0.,0.,-SOCKET_DROP),cq.Vector(-1.,0.,0.))
    body = cup.fuse(socket)
    barb = cq.Solid.makeCylinder(barb_d/2.,INSTALLED_REACH+.1,
                                cq.Vector(0.,0.,0.))
    # The short printed drain turn is separate from the LLDPE's bend rule.
    a = cq.Vector(0.,0.,TURN_START_Z)
    mid = cq.Vector(-ELBOW_R+ELBOW_R/math.sqrt(2.),0.,TURN_START_Z-ELBOW_R/math.sqrt(2.))
    b = cq.Vector(-ELBOW_R,0.,-SOCKET_DROP)
    turn = cq.Wire.assembleEdges([cq.Edge.makeThreePointArc(a,mid,b)])
    channel = (cq.Workplane(cq.Plane(origin=a,normal=(0.,0.,-1.)))
               .circle(tube_d/2.).sweep(turn).val())
    bore = cq.Solid.makeCylinder(tube_d/2.,ELBOW_REACH-ELBOW_R+.1,b,cq.Vector(-1.,0.,0.))
    transition = cq.Solid.makeCone(tube_d/2.,barb_d/2.,REDUCER_LENGTH,a)
    body = body.cut(barb,transition,channel,bore)
    for centre,radius,horizontal in ((INSTALLED_REACH-BARB_TIE_Z,rb,False),
                                     (ELBOW_REACH-6.,rt,True)):
        lo,hi = centre-GROOVE_FLAT/2.,centre+GROOVE_FLAT/2.
        groove = _revolve([(radius,lo-GROOVE_RAMP),(radius-GROOVE_DEPTH,lo),
            (radius-GROOVE_DEPTH,hi),(radius,hi+GROOVE_RAMP),
            (radius+1.,hi+GROOVE_RAMP),(radius+1.,lo-GROOVE_RAMP)])
        if horizontal:
            groove = groove.rotate((0,0,0),(0,1,0),-90.).translate((0.,0.,-SOCKET_DROP))
        body = body.cut(groove)
    # A small exterior flat supports the two upward 45-degree bores in the
    # print frame. It does not enter either socket or the drain turn.
    print_pose = body.rotate((0,0,0),(0,1,0),45.)
    z = print_pose.BoundingBox().zmin
    flat = cq.Solid.makeBox(100.,100.,1.,cq.Vector(-50.,-50.,z-.4))
    return print_pose.cut(flat).rotate((0,0,0),(0,1,0),-45.).clean()


def placed(vent_tip):
    """Installed on the scanned barb, with its tube socket along native -X."""
    return build(installed=True).translate(vent_tip)


def tube_mouth(vent_tip):
    x, y, z = vent_tip
    return (x-ELBOW_REACH,y,z-SOCKET_DROP)


def main():
    shape = build().rotate((0,0,0),(0,1,0),45.)
    b = shape.BoundingBox()
    shape = shape.translate((-(b.xmin+b.xmax)/2.,-(b.ymin+b.ymax)/2.,-b.zmin))
    stl = HERE / "asse-drain-adapter.stl"
    step = HERE / "asse-drain-adapter.step"
    cq.exporters.export(shape, str(stl), tolerance=.025, angularTolerance=.08)
    export_assembly(one_body(shape, "asse-drain-adapter", M_TPU_BLACK), str(step))
    import flute_payload
    flute_payload.cut(step, stl, preserve_print_triangles=True)
    sys.path.insert(0, str(HARDWARE.parent / "tools"))
    from docgen import substitute_md
    substitute_md(HERE / "README.md", variables={
        "BARB_BORE": f"{BARB_BORE:.2f}", "BARB_DEPTH": f"{INSTALLED_REACH:g}",
        "TUBE_BORE": f"{TUBE_BORE:.2f}", "TUBE_DEPTH": f"{TUBE_DEPTH:g}",
        "BARB_OD": f"{BARB_OD:g}", "TUBE_OD": f"{TUBE_OD:g}",
        "MIN_WALL": f"{MIN_WALL:.2f}",
        "SOCKET_DROP": f"{SOCKET_DROP:.2f}", "REDUCER_LENGTH": f"{REDUCER_LENGTH:.2f}",
        "VOLUME": f"{shape.Volume()/1000:.3f}",
    })
    print(f"-> {step.name}, {stl.name}, {step.name}.mesh; {shape.Volume()/1000:.3f} cm3")


if __name__ == "__main__":
    main()
