"""Bare 22 AWG 4P relay-ribbon clip on a 3 mm wall, in back-top's print pose.

Run manually with tools/cad-venv/bin/python. The installed design has its
entry upward; the coupon prints entry-down, like back-top printed ceiling-down.
The coupon does not change the enclosure or the installed wiring routes.
"""
from pathlib import Path
import hashlib
import json

import cadquery as cq

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GAP = 2.20
SEAT_HEIGHT = 7.75
SPAN = 8.0
STOCK = 3.0
WALL_RUN = 14.0
BEAK = .75
MOUTH = GAP - BEAK
PROJECTION = GAP + STOCK
SEAT_FLOOR = PROJECTION + STOCK
SEAT_ROOF = SEAT_FLOOR + SEAT_HEIGHT
TOP = SEAT_ROOF + BEAK + STOCK
WIRE_OD = 1.70
RIBBON_PITCH = 1.85
SECTION = ((0.,0.),(PROJECTION,PROJECTION),(PROJECTION,TOP),
           (GAP,TOP),(MOUTH,TOP-BEAK),(MOUTH,SEAT_ROOF),
           (GAP,SEAT_ROOF),(GAP,SEAT_FLOOR),(0.,SEAT_FLOOR))
PROVENANCE = (
    "hardware/wiring/installed/model.py",
    "hardware/wiring/installed/routes.py",
    "hardware/assembly/cable-assemblies.md",
    "hardware/printed-parts/enclosure/enclosure/enclosure.py",
)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prism(section, length):
    wire = cq.Wire.makePolygon([cq.Vector(x,-length/2,z) for x,z in section],close=True)
    return cq.Solid.extrudeLinear(wire,[],cq.Vector(0,length,0))


def print_pose(shape):
    return shape.rotate((0,0,0),(1,0,0),180).translate((0,0,TOP))


def signature(shape):
    b = shape.BoundingBox()
    return dict(valid=shape.isValid(),solids=len(shape.Solids()),volume_mm3=abs(shape.Volume()),
                bounds_mm=[getattr(b,n) for n in ('xmin','ymin','zmin','xmax','ymax','zmax')])


def build():
    # Ending the wall at TOP puts both the wall and the outer arm on the bed.
    # Extending the wall above the entry would leave the arm floating at startup.
    wall = cq.Solid.makeBox(STOCK,WALL_RUN,TOP,cq.Vector(-STOCK,-WALL_RUN/2,0))
    clip = prism(SECTION,SPAN)
    installed = wall.fuse(clip).clean()
    cable = None
    centers = []
    for i in range(4):
        x,z = GAP/2,SEAT_FLOOR+.25+WIRE_OD/2+i*RIBBON_PITCH
        centers.append([x,z])
        strand = cq.Solid.makeCylinder(WIRE_OD/2,WALL_RUN,
                                       cq.Vector(x,-WALL_RUN/2,z),cq.Vector(0,1,0))
        cable = strand if cable is None else cable.fuse(strand)
    overlap = abs(installed.intersect(cable).Volume())
    clearance = installed.distance(cable)
    if not installed.isValid() or len(installed.Solids())!=1 or overlap>1e-8:
        raise ValueError("The clip must join its wall and clear the seated conductors")
    printed = print_pose(installed).clean()
    bed_faces = [f for f in printed.Faces() if f.geomType()=="PLANE"
                 and f.normalAt().z<-.9999 and abs(f.Center().z)<1e-5]
    return installed,printed,dict(
        native_seated_overlap_mm3=overlap,native_seated_clearance_mm=clearance,
        conductor_centers_xz_mm=centers,
        bed_contact_face_areas_mm2=sorted(f.Area() for f in bed_faces),
        total_native_bed_contact_mm2=sum(f.Area() for f in bed_faces))


def main():
    parts = HERE/"parts"
    parts.mkdir(parents=True,exist_ok=True)
    installed,printed,readings = build()
    stl = parts/"relay-ribbon-4p-print.stl"
    step = parts/"relay-ribbon-4p-print.step"
    installed_step = parts/"relay-ribbon-4p-installed.step"
    cq.exporters.export(printed,str(stl),tolerance=.025,angularTolerance=.10)
    cq.exporters.export(printed,str(step))
    cq.exporters.export(installed,str(installed_step))
    report = dict(
        scope="One bare 22 AWG 4P relay-ribbon fit coupon. No production geometry or wiring changes.",
        source=str(Path(__file__).relative_to(ROOT)),source_sha256=sha(Path(__file__)),
        intended_stock="BNTECHGO 22 AWG black silicone 4P ribbon, the J5 RELAYS loom stock",
        stock_basis="1.70 mm modeled insulated conductor OD on 1.85 mm modeled pitch; full physical ribbon section unmeasured.",
        dimensions=dict(ribbon_width_mm=3*RIBBON_PITCH+WIRE_OD,ribbon_depth_mm=WIRE_OD,
                        seat_depth_mm=GAP,seat_height_mm=SEAT_HEIGHT,mouth_depth_mm=MOUTH,
                        post_wall_cap_minimum_mm=STOCK,span_along_cable_mm=SPAN,
                        beak_projection_mm=BEAK,projection_from_wall_mm=PROJECTION,
                        host_wall_mm=STOCK,host_run_mm=WALL_RUN,overall_print_height_mm=TOP),
        installed_frame="X outward from wall; Z up; cable axis Y. Mouth opens upward.",
        print_pose="Half-turn about X followed by +19.70 mm Z. Entry faces the bed, matching installed-up on ceiling-down back-top. In a +Z quadrant the same print pose corresponds to installed-down entry.",
        print_pocket_bounds_mm=[0.,-SPAN/2,TOP-SEAT_ROOF,GAP,SPAN/2,TOP-SEAT_FLOOR],
        print_entry_core_bounds_mm=[0.,-SPAN/2,0.,MOUTH,SPAN/2,TOP-SEAT_ROOF],
        pocket_closure=dict(width_mm=GAP,build_z_mm=TOP-SEAT_FLOOR,
                            mechanism="Short bridge between the standing wall and outer arm"),
        support_requirement="No support or brim roads inside the cable seat or entry corridor; verify the emitted native slice with Tree(auto)/Default retained.",
        print_native=signature(printed),installed_native=signature(installed),readings=readings,
        files={str(p.relative_to(ROOT)):sha(p) for p in (stl,step,installed_step)},
        provenance={p:sha(ROOT/p) for p in PROVENANCE},
        evaluation="Use the actual bare 4P ribbon to compare entry force, seated retention, axial slide, release and layer/root survival. Does not test a braided sleeve, finished crimp or other conductor count.",
        production_placement="Proposed west-wall J5 bare fan-out guide; placement/redressing and equipment clearance have separate review. Coupon is not an integrated enclosure feature.")
    (HERE/"geometry-report.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2),flush=True)


if __name__=="__main__":
    main()
