"""TPU hand-pressure pad for the Touch-Flo in the existing insertion base.

The installed frame is the parent fixture's frame. Export is manual; importing
the builders writes no files. The broad hand face is the manufacturing bed face.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import cadquery as cq

HERE = Path(__file__).resolve().parent
FIXTURE = HERE.parent
ROOT = next(p for p in HERE.parents if (p / "tools/docgen").is_dir())
sys.path.insert(0, str(FIXTURE))
import tube_insertion as jig

BODY_RADIUS = jig.DONOR_BODY_OD / 2
CYLINDER_END_CLEARANCE = 0.5
LEVER_ATTACHMENT_AXIAL_CLEARANCE = 3.0
BODY_X0 = jig._donor["cylinder_height"] + CYLINDER_END_CLEARANCE
BODY_X1 = jig._donor["plateau_z"] - LEVER_ATTACHMENT_AXIAL_CLEARANCE
BODY_HALF_WIDTH = 13.0
BODY_BOTTOM_Z = jig.DONOR_AXIS_Z + jig._donor["rect_short"] / 2
FACE_Z = jig.THRUST_WALL_Z1 + 2.0
TONGUE_X0 = jig.THRUST_WALL_X0 + 0.5
TONGUE_X1 = jig.THRUST_WALL_X1
TONGUE_WIDTH = jig.SHANK_SLOT_D + 1.0
# The tongue ends at the cylinder crown, leaving clearance above the threads.
TONGUE_BOTTOM_Z = jig.DONOR_AXIS_Z + BODY_RADIUS
BRIDGE_X0 = TONGUE_X1
BRIDGE_X1 = BODY_X0
CYLINDER_BRIDGE_CLEARANCE = 1.0
BRIDGE_BOTTOM_Z = jig.DONOR_AXIS_Z + BODY_RADIUS + CYLINDER_BRIDGE_CLEARANCE
LEAD_HEIGHT = 0.75
LEAD_IN_PER_SIDE = 0.75
PAD_COLOR = cq.Color(0.11, 0.12, 0.13)
FIT_PAD_COLOR = cq.Color(0.20, 0.43, 0.78)


def donor_exterior():
    """Fill the port internally so the pad follows only the external metal."""
    port_start = jig._donor["plateau_z"] - jig.DONOR_PORT_DEPTH_MIN
    port = jig.cylinder_x(port_start, jig._donor["plateau_z"],
                          jig.TUBE_Y, jig.TUBE_Z, jig._donor["port_diameter"] / 2)
    return jig.donor_shape().union(port)


def build_pad(print_frame=False):
    """A transition/flat-face pad and compression tongue joined by a clear bridge."""
    body = jig.block(BODY_X0, BODY_X1, -BODY_HALF_WIDTH, BODY_HALF_WIDTH,
                     BODY_BOTTOM_Z, FACE_Z)
    body = body.cut(donor_exterior())
    bridge = jig.block(BRIDGE_X0, BRIDGE_X1, -TONGUE_WIDTH / 2,
                       TONGUE_WIDTH / 2, BRIDGE_BOTTOM_Z, FACE_Z)
    half = TONGUE_WIDTH / 2
    plane = cq.Plane(origin=(TONGUE_X0, 0, 0), xDir=(0, 1, 0), normal=(1, 0, 0))
    tongue = (cq.Workplane(plane)
              .polyline([(-half + LEAD_IN_PER_SIDE, TONGUE_BOTTOM_Z),
                         (-half, TONGUE_BOTTOM_Z + LEAD_HEIGHT),
                         (-half, FACE_Z), (half, FACE_Z),
                         (half, TONGUE_BOTTOM_Z + LEAD_HEIGHT),
                         (half - LEAD_IN_PER_SIDE, TONGUE_BOTTOM_Z)])
              .close().extrude(TONGUE_X1 - TONGUE_X0))
    pad = body.union(bridge).union(tongue)
    if print_frame:
        pad = pad.rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, FACE_Z))
    return pad


def build_fit_context():
    """Contact-zone view in the parent fixture frame, up to the lever attachment."""
    crop = jig.block(jig.THRUST_WALL_X0 - 2, jig.DONOR_ARCH_X + 1,
                     -24, 24, 20, FACE_Z + 2)
    assembly = cq.Assembly(name="donor-hold-down-contact-zone")
    assembly.add(jig.build_base().intersect(crop), name="existing-base-contact-zone",
                 color=jig.COLOR_RIGID)
    assembly.add(jig.donor_shape().intersect(crop), name="donor-contact-zone",
                 color=jig.COLOR_DONOR)
    assembly.add(build_pad(), name="tpu-hand-pad", color=FIT_PAD_COLOR)
    return assembly


def dimensions():
    printed = build_pad(print_frame=True)
    bb = printed.val().BoundingBox()
    return {
        "material": "TPU 85A",
        "quantity": 1,
        "print_bounds_mm": [bb.xlen, bb.ylen, bb.zlen],
        "print_face": "Broad flat hand face at print Z=0; transition/flat contact upward",
        "flat_face_above_petgf_mm": FACE_Z - jig.THRUST_WALL_Z1,
        "donor_contact_region": "Rounded cylinder-to-column transition and upper flat side of the rectangular column",
        "donor_contact_axial_range_mm": [BODY_X0, BODY_X1],
        "donor_transition_radius_mm": jig._donor["transition_fillet_r"],
        "donor_flat_starts_axial_mm": jig._donor["cylinder_height"] + jig._donor["transition_fillet_r"],
        "donor_flat_contact_z_mm": BODY_BOTTOM_Z,
        "donor_flat_contact_width_mm": 2 * BODY_HALF_WIDTH,
        "body_flat_backing_mm": FACE_Z - BODY_BOTTOM_Z,
        "cylindrical_base_end_clearance_mm": CYLINDER_END_CLEARANCE,
        "bridge_above_cylindrical_base_mm": CYLINDER_BRIDGE_CLEARANCE,
        "lever_attachment_axial_clearance_mm": LEVER_ATTACHMENT_AXIAL_CLEARANCE,
        "existing_canyon_width_mm": jig.SHANK_SLOT_D,
        "retention_tongue_width_mm": TONGUE_WIDTH,
        "nominal_interference_per_side_mm": (TONGUE_WIDTH - jig.SHANK_SLOT_D) / 2,
        "thread_clearance_mm": TONGUE_BOTTOM_Z - jig.DONOR_AXIS_Z - jig.DONOR_SHANK_OD / 2,
        "tongue_canyon_engagement_mm": jig.THRUST_WALL_Z1 - TONGUE_BOTTOM_Z,
        "full_width_canyon_engagement_mm": jig.THRUST_WALL_Z1 - TONGUE_BOTTOM_Z - LEAD_HEIGHT,
        "bearing_pad_axial_clearance_from_lower_cradle_mm": BODY_X0 - jig.NEST_LENGTH,
        "rear_face_clearance_mm": TONGUE_X0 - jig.THRUST_WALL_X0,
        "tongue_entry_width_mm": TONGUE_WIDTH - 2 * LEAD_IN_PER_SIDE,
        "tongue_entry_lead_height_mm": LEAD_HEIGHT,
        "flat_bed_contact_area_mm2": ((BODY_X1 - BODY_X0) * 2 * BODY_HALF_WIDTH
                                      + (BRIDGE_X1 - TONGUE_X0) * TONGUE_WIDTH),
        "volume_mm3": printed.val().Volume(),
        "status": "Unprinted fit candidate; retention and hand-pressure performance unmeasured",
        "load_path": "Hand pressure through the conforming transition/flat face to the donor metal; tongue interference retains the pad in the existing canyon",
        "lever_scope": "The bearing pad ends 3 mm before the donor plateau/lever attachment. Its sides end on the upper flat metal face, without wrapping down beside the lever. The lever stays attached and down at unpressed rest; its installed transform is not measured.",
        "print_support_basis": "With the hand face down, successive sections shrink as the conforming contact opens; the bridge and tongue also end above their bed-supported stock.",
    }


def main():
    sys.path.insert(0, str(ROOT / "hardware/scripts"))
    from _cadq_export import export_assembly

    part = build_pad(print_frame=True)
    assembly = cq.Assembly(name="donor-hold-down").add(part, name="tpu-hand-pad", color=PAD_COLOR)
    export_assembly(assembly, str(HERE / "donor-hold-down.step"))
    cq.exporters.export(part, str(HERE / "donor-hold-down-print.stl"),
                        tolerance=0.025, angularTolerance=0.08)
    export_assembly(build_fit_context(), str(HERE / "donor-hold-down-fit.step"))
    record = dimensions()
    record["source_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    record["fixture_source_sha256"] = hashlib.sha256((FIXTURE / "tube_insertion.py").read_bytes()).hexdigest()
    (HERE / "dimensions.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
