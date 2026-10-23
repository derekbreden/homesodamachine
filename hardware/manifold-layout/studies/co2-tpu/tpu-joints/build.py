"""Build threadless TPU CO2 layout joints derived from the pump elbow.

Manual CAD-queue operation. These are installed occupancy and relaxed fit
models, not pressure-qualified articles or sliced print jobs.
"""
from pathlib import Path
import hashlib
import json
import math
import shutil

import cadquery as cq
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "hardware/cad-artifacts.json").is_file())
WALL = 2.8
TUBE_BORE = 6.10
TUBE_INSTALLED = 6.35
TUBE_DEPTH = 15.
TUBE_STOP = 3.5
TUBE_MOUTH = TUBE_STOP + TUBE_DEPTH
PASSAGE = 4.4
NECK = TUBE_STOP + 3.
BAND_WIDTH = 9.
BAND_T = .6
BAND_AIR = 1.
ENTRY = .4
ENTRY_HEIGHT = ENTRY * math.tan(math.radians(60.))
CUFF_INTERFERENCE = .25
REG_BOSS_AF, REG_BOSS_MAX = 19., 20.6
REG_CUFF_DEPTH = 9.
CHECK_STUB_D = 13.7
CHECK_CUFF_DEPTH = 11.
CHECK_TIP = (0., 20., 0.)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def installed_od(bore, opened):
    return math.sqrt((bore + 2*WALL)**2 + opened**2 - bore**2)


TUBE_OD = installed_od(TUBE_BORE, TUBE_INSTALLED)
REG_CUFF_OD = installed_od(REG_BOSS_MAX-CUFF_INTERFERENCE, REG_BOSS_MAX)
CHECK_CUFF_OD = installed_od(CHECK_STUB_D-CUFF_INTERFERENCE, CHECK_STUB_D)
TURN_REACH = -(CHECK_CUFF_DEPTH-BAND_WIDTH) + BAND_AIR + TUBE_OD/2


def cylinder(radius, start, axis, length):
    return cq.Solid.makeCylinder(radius, length, cq.Vector(*start), cq.Vector(*axis))


def x(radius, x0, x1):
    return cylinder(radius, (x0, 0, 0), (1, 0, 0), x1-x0)


def y(radius, y0, y1):
    return cylinder(radius, (0, y0, 0), (0, 1, 0), y1-y0)


def tube_leg(radius, y0, y1, turn_reach):
    return cylinder(radius, (turn_reach, y0, 0), (0, 1, 0), y1-y0)


def smooth_reducer(rb, rt, length):
    # The same fifth-degree Bezier transition as diaphragm_pump_sleeve.py.
    profile = (cq.Workplane("XY").moveTo(0, 0).lineTo(rb, 0)
        .bezier([(rb, length/5), (rb, 2*length/5), (rt, 3*length/5),
                 (rt, 4*length/5), (rt, length)], includeCurrent=True)
        .lineTo(0, length).close())
    return profile.revolve(360, (0, 0, 0), (0, 1, 0)).val()


def reg_boss_cavity(installed):
    # Exact source inlet-front profile through its first9mm, clipped to flats.
    delta = 0. if installed else CUFF_INTERFERENCE/2
    af = REG_BOSS_AF if installed else REG_BOSS_AF-CUFF_INTERFERENCE
    outline = [(0, 0), (9.38-delta, 0), (9.93-delta, .35),
               (10.3-delta, .8), (10.3-delta, REG_CUFF_DEPTH+.01),
               (0, REG_CUFF_DEPTH+.01)]
    turned = cq.Workplane("XY").polyline(outline).close().revolve(360, (0, 0, 0), (0, 1, 0)).val()
    plane = cq.Plane(origin=(0, 0, 0), xDir=(1, 0, 0), normal=(0, 1, 0))
    # The regulator source's finalRx−90 maps its native flat normals here.
    prism = (cq.Workplane(plane).polygon(6, af/math.cos(math.pi/6))
             .extrude(REG_CUFF_DEPTH+.01).rotate((0, 0, 0), (0, 1, 0), 30).val())
    cavity = turned.intersect(prism)
    entry = cq.Solid.makeCone(REG_BOSS_MAX/2+ENTRY, REG_BOSS_MAX/2,
        ENTRY_HEIGHT, cq.Vector(0, REG_CUFF_DEPTH, 0), cq.Vector(0, -1, 0))
    return cavity.fuse(entry)


def regulator_joint(installed):
    cuff_d = REG_CUFF_OD if installed else REG_BOSS_MAX-CUFF_INTERFERENCE+2*WALL
    tube_d = TUBE_OD if installed else TUBE_BORE+2*WALL
    bore_t = TUBE_INSTALLED if installed else TUBE_BORE
    length = NECK + (1. if installed else 0.)
    neck = smooth_reducer(cuff_d/2, tube_d/2, length).rotate((0, 0, 0), (1, 0, 0), 180)
    outer = y(cuff_d/2, 0, REG_CUFF_DEPTH).fuse(neck,
        y(tube_d/2, -TUBE_MOUTH, -length))
    bores = reg_boss_cavity(installed).fuse(y(PASSAGE/2, -TUBE_STOP, .01),
        y(bore_t/2, -TUBE_MOUTH-.01, -TUBE_STOP),
        cq.Solid.makeCone(bore_t/2+ENTRY, bore_t/2, ENTRY_HEIGHT,
            cq.Vector(0, -TUBE_MOUTH, 0), cq.Vector(0, 1, 0)))
    return outer.cut(bores)


def check_joint_local(installed):
    cuff_d = CHECK_CUFF_OD if installed else CHECK_STUB_D-CUFF_INTERFERENCE+2*WALL
    tube_d = TUBE_OD if installed else TUBE_BORE+2*WALL
    bore_c = CHECK_STUB_D if installed else CHECK_STUB_D-CUFF_INTERFERENCE
    bore_t = TUBE_INSTALLED if installed else TUBE_BORE
    rb, rt = cuff_d/2, tube_d/2
    length = NECK + (1. if installed else 0.)
    # Installed placement is the common socket datum; relaxed body's axes match it.
    reach = TURN_REACH
    neck = smooth_reducer(rb, rt, length).translate((reach, 0, 0))
    heel = cq.Solid.makeSphere(rb, cq.Vector(reach, 0, 0), angleDegrees1=-90)
    outer = x(rb, -CHECK_CUFF_DEPTH, reach).fuse(heel).fuse(neck)
    outer = outer.fuse(tube_leg(rt, length, TUBE_MOUTH, reach))
    foot_d = reach/math.sqrt(2) + PASSAGE/2 + WALL
    span = 4*(CHECK_CUFF_DEPTH+TUBE_MOUTH)
    foot = (cq.Solid.makeBox(span, span, span, cq.Vector(0, -span/2, -span/2))
        .rotate((0, 0, 0), (0, 0, 1), -45)
        .translate((foot_d/math.sqrt(2), -foot_d/math.sqrt(2), 0)))
    outer = outer.cut(foot)
    cavity = x(bore_c/2, -CHECK_CUFF_DEPTH-.01, 0).fuse(
        cq.Solid.makeCone(bore_c/2+ENTRY, bore_c/2, ENTRY_HEIGHT,
            cq.Vector(-CHECK_CUFF_DEPTH, 0, 0), cq.Vector(1, 0, 0)),
        x(PASSAGE/2, 0, reach), tube_leg(PASSAGE/2, 0, TUBE_STOP, reach),
        tube_leg(bore_t/2, TUBE_STOP, TUBE_MOUTH+.01, reach),
        cq.Solid.makeCone(bore_t/2, bore_t/2+ENTRY, ENTRY_HEIGHT,
            cq.Vector(reach, TUBE_MOUTH-ENTRY_HEIGHT, 0), cq.Vector(0, 1, 0)))
    return outer.cut(cavity)


def check_pose(solid):
    # Local barb+X -> parent+Y; local tube+Y -> parent−Z.
    return solid.moved(cq.Location(cq.Plane(origin=CHECK_TIP,
        xDir=(0, 1, 0), normal=(-1, 0, 0))))


def band(start, axis, diameter):
    return cylinder(diameter/2+BAND_T, start, axis, BAND_WIDTH).cut(
        cylinder(diameter/2, start, axis, BAND_WIDTH))


def save(name, solid):
    points, triangles = solid.tessellate(.035, .12)
    v = np.array([p.toTuple() for p in points], dtype=np.float32)
    f = np.array(triangles, dtype=np.int32)
    path = HERE / "geometry" / (name+".npz")
    np.savez_compressed(path, v=v, f=f)
    cq.exporters.export(solid, str(path.with_suffix(".step")))
    return {"npz": str(path.relative_to(HERE)), "npz_sha256": sha(path),
        "step": str(path.with_suffix(".step").relative_to(HERE)),
        "step_sha256": sha(path.with_suffix(".step")),
        "bounds_mm": [v.min(0).tolist(), v.max(0).tolist()],
        "volume_mm3": float(solid.Volume()), "valid_native_solid": bool(solid.isValid()),
        "native_solid_count": len(solid.Solids()), "vertices": len(v), "triangles": len(f)}


def main():
    (HERE / "geometry").mkdir(parents=True, exist_ok=True)
    meshes = {}
    for installed in (False, True):
        suffix = "" if installed else "-relaxed"
        meshes["regulator-inlet-tpu"+suffix] = save("regulator-inlet-tpu"+suffix, regulator_joint(installed))
        meshes["check-outlet-tpu"+suffix] = save("check-outlet-tpu"+suffix, check_pose(check_joint_local(installed)))
    bands = {
        "regulator-inlet-band-cuff": band((0, 0, 0), (0, 1, 0), REG_CUFF_OD),
        "regulator-inlet-band-tube": band((0, -TUBE_MOUTH, 0), (0, 1, 0), TUBE_OD),
        "check-outlet-band-cuff": check_pose(band((-CHECK_CUFF_DEPTH, 0, 0), (1, 0, 0), CHECK_CUFF_OD)),
        "check-outlet-band-tube": check_pose(band((TURN_REACH, TUBE_MOUTH-BAND_WIDTH, 0), (0, 1, 0), TUBE_OD)),
    }
    for name, shape in bands.items():
        meshes[name] = save(name, shape)
    source_paths = [
        "hardware/printed-parts/diaphragm-pump-sleeve/diaphragm_pump_sleeve.py",
        "hardware/printed-parts/diaphragm-pump-sleeve/README.md",
        "hardware/reference/wr1110-regulator/wr1110_regulator.py",
        "hardware/reference/wr1110-regulator/scan-measurements.json",
        "hardware/reference/gasher-check-valve/gasher_check_valve.py",
        "future/pump-elbow-exploration/prints/2026-10-13-compact-single-tpu85a-outer10-engineering-z000-mark1/physical-result.json",
        "future/pump-elbow-exploration/prints/2026-10-22-deposited-links-siraya85a-mark2/physical-result.json",
    ]
    (HERE / "reference").mkdir(exist_ok=True)
    reference = {}
    for name in ("wr1110", "gasher-co2"):
        src = HERE.parents[1] / "co2-grid/co2-parts/geometry" / (name+".npz")
        dest = HERE / "reference" / (name+".npz")
        shutil.copyfile(src, dest)
        reference[name] = {"npz": str(dest.relative_to(HERE)), "sha256": sha(dest),
                           "source": str(src.relative_to(ROOT))}
    metadata = {
        "units": "mm", "scope": "Threadless installed TPU gas-joint layout candidates, plus relaxed geometry; no gas-service qualification claimed",
        "material_basis": "Siraya Tech Flex TPU85A Clear pump-sleeve baseline; these metal cuff interfaces have no physical acceptance record",
        "source_sha256": {p: sha(ROOT/p) for p in source_paths},
        "geometry": meshes, "reference": reference,
        "shared": {"relaxed_radial_wall_mm": WALL, "tube_socket_relaxed_diameter_mm": TUBE_BORE,
            "tube_socket_installed_diameter_mm": TUBE_INSTALLED, "tube_engagement_mm": TUBE_DEPTH,
            "tube_socket_relaxed_od_mm": TUBE_BORE+2*WALL, "tube_socket_installed_od_mm": TUBE_OD,
            "passage_diameter_mm": PASSAGE, "tube_stop_from_corner_axis_mm": TUBE_STOP,
            "tube_mouth_from_corner_axis_mm": TUBE_MOUTH, "clamp_band_width_mm": BAND_WIDTH,
            "band_skin_thickness_mm": BAND_T, "band_to_elbow_leg_air_mm": BAND_AIR,
            "entry_radial_chamfer_mm": ENTRY, "new_cuff_diametral_interference_estimate_mm": CUFF_INTERFERENCE},
        "regulator": {
            "frame": "WR1110/WR1105 native female inletfaceY0, flow+Y",
            "cuff_installed_max_bore_mm": REG_BOSS_MAX, "cuff_installed_af_mm": REG_BOSS_AF,
            "cuff_relaxed_max_bore_mm": REG_BOSS_MAX-CUFF_INTERFERENCE,
            "cuff_relaxed_af_mm": REG_BOSS_AF-CUFF_INTERFERENCE,
            "cuff_engagement_mm": REG_CUFF_DEPTH, "cuff_span_y_mm": [0., REG_CUFF_DEPTH],
            "cuff_installed_od_mm": REG_CUFF_OD,
            "source_straight_hex_band_y_mm": [.8, 13.35],
            "tube_mouth": {"point_mm": [0., -TUBE_MOUTH, 0.], "outward_axis": [0., -1., 0.]},
            "tube_end_at_stop_mm": [0., -TUBE_STOP, 0.],
            "flow_entry_face_mm": [0., 0., 0.],
            "outer_neck_length_installed_mm": NECK+1.,
            "notes": "Cuff follows the external clipped wrench-boss profile over its first9mm; no printed NPT or internal threaded insert. The9mm band lies over this cuff."
        },
        "check": {
            "frame": "GASHER native centerY0, femalein−Y, maletipY20, flow+Y; tubeleg−Z",
            "stub_installed_diameter_mm": CHECK_STUB_D,
            "cuff_relaxed_bore_mm": CHECK_STUB_D-CUFF_INTERFERENCE,
            "cuff_installed_od_mm": CHECK_CUFF_OD,
            "cuff_engagement_mm": CHECK_CUFF_DEPTH, "cuff_span_y_mm": [9., 20.],
            "metal_tip_mm": list(CHECK_TIP),
            "corner_axis_mm": [0., CHECK_TIP[1]+TURN_REACH, 0.],
            "turn_reach_past_metal_tip_mm": TURN_REACH,
            "turn_reach_rule": "−(11mm cuff−9mm band)+1mm air+installed tube radius",
            "tube_mouth": {"point_mm": [0., CHECK_TIP[1]+TURN_REACH, -TUBE_MOUTH],
                           "outward_axis": [0., 0., -1.]},
            "tube_end_at_stop_mm": [0., CHECK_TIP[1]+TURN_REACH, -TUBE_STOP],
            "notes": "Cuff covers the existing male stub to shoulderY9; the turn is inside TPU, without an additional elbow or threaded fitting."
        },
        "clamps": {
            "representation": "Four9mm-wide closed rings with0.6mm radial band skin; housing/screw/key are not modeled",
            "installed_cuff_band_inner_diameters_mm": [REG_CUFF_OD, CHECK_CUFF_OD],
            "installed_tube_band_inner_diameter_mm": TUBE_OD,
            "owned10_to16mm_band_fit": "Tube seats only; both new metal-cuff bands require a larger diameter range",
        },
        "physical_evidence_scope": {
            "existing_pump_articles": "Identified articles have qualitative manual fit, stringing and seal-comparison observations. Preserve that acceptance for those articles and recipes.",
            "new_joint_interfaces": "External regulator hex cuff and check threaded-stub cuff are layout estimates, without physical fit or gas acceptance.",
            "installed_envelope_method": "The pump source's annular-area conservation formula opens the relaxed bore and grows OD; it is an occupancy approximation, not a deformation or clamp-load model.",
        },
        "direct_metal_joint": {
            "connection": "WR1105 male outlet directly into GASHER female inlet; retained without intermediate TPU",
            "nominal_engagement_mm": 9.18, "check_center_in_regulator_frame_mm": [0., 74.47, 0.],
            "scope": "Scanned-stub-bounded make-up estimate"
        },
    }
    (HERE/"interfaces.json").write_text(json.dumps(metadata, indent=2)+"\n")
    print(json.dumps({"regulator_tube_mouth": metadata["regulator"]["tube_mouth"],
        "check_tube_mouth": metadata["check"]["tube_mouth"],
        "native_solids_valid": all(v["valid_native_solid"] for v in meshes.values()),
        "installed_cuff_od_mm": [REG_CUFF_OD, CHECK_CUFF_OD]}, indent=2))


if __name__ == "__main__":
    main()
