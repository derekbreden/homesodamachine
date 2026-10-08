"""Check the current back top against the recorded prototype print geometry.

No active enclosure, faucet, placement or funnel generator is imported.
"""

import argparse
from itertools import combinations
import json
import tarfile
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

import cadquery as cq
import manifold3d as mf
import numpy as np
import trimesh

import sys
ROOT = Path(__file__).resolve().parents[3]
REFERENCE = ROOT / 'hardware/printed-parts/enclosure/lillium-prototype-2026-10-07'
sys.path.insert(0, str(REFERENCE))
from materialize import digest, manifest as frozen_manifest, materialize as restore
HERE = ROOT / '.cache/prototype-launch-20261008'
CANDIDATE = ROOT / 'hardware/printed-parts/enclosure/enclosure'
REVIEW = ROOT / 'hardware/printed-parts/drain-readiness/reviews/back-top-native.json'
PROJECT = ROOT / 'hardware/printed-parts/drain-readiness/projects/back-top-black-z004-mark2.3mf'
FACTS = ROOT / 'hardware/manifold-layout/enclosure-assembly.facts.json'
DEFAULT_OUTPUT = HERE / 'frozen-fixtures'

def manifest():
    saved = frozen_manifest()
    for name in ('enclosure-back-top.step', 'enclosure-back-top.stl'):
        raw = (CANDIDATE / name).read_bytes()
        saved['artifacts'][name]['sha256'] = digest(raw)
    return saved

def materialize(names, output):
    paths = restore(names, output)
    for name in ('enclosure-back-top.step', 'enclosure-back-top.stl'):
        paths[name] = CANDIDATE / name
    paths['print-regions.json'] = ROOT / 'hardware/printed-parts/enclosure/enclosure/heat-set-review/print-regions.json'
    return paths

MESH_VOLUME_TOLERANCE_MM3 = 0.1
NATIVE_VOLUME_TOLERANCE_MM3 = 1e-5


def bounds(shape):
    b = shape.BoundingBox()
    return [b.xmin, b.ymin, b.zmin, b.xmax, b.ymax, b.zmax]


def native_overlap(first, second):
    a, b = bounds(first), bounds(second)
    if any(a[axis + 3] < b[axis] or b[axis + 3] < a[axis] for axis in range(3)):
        return 0.0
    return abs(first.intersect(second).Volume(tol=1e-9))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=HERE / "current-back-top-fit.json")
    parser.add_argument("--materialized-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    saved = manifest()
    paths = materialize(tuple(saved["artifacts"]), args.materialized_dir)
    rows = []

    def check(name, passed, **measurements):
        row = {"check": name, "pass": bool(passed), **measurements}
        rows.append(row)
        print(name, "PASS" if passed else "FAIL", flush=True)

    check("Frozen printed-part fixtures restore to their recorded bytes; current back-top candidate has separate source bindings", True, artifacts=len(paths))
    with tarfile.open(paths["source.tar"]) as archive:
        archived_sources = {member.name: digest(archive.extractfile(member).read())
                            for member in archive.getmembers() if member.isfile()}
    check("Archived source files match every generation-record binding",
          archived_sources == saved["sources"], source_files=len(archived_sources))
    review = json.loads(REVIEW.read_text())
    native_archive = ROOT / review["native_archive"]
    with zipfile.ZipFile(native_archive) as archive, zipfile.ZipFile(PROJECT) as project:
        config = ET.fromstring(archive.read("Metadata/model_settings.config"))
        project_config = ET.fromstring(project.read("Metadata/model_settings.config"))
        modifiers = config.findall(".//part[@subtype='modifier_part']")
        project_modifiers = project_config.findall(".//part[@subtype='modifier_part']")
        gcode = archive.read("Metadata/plate_1.gcode")
        archive_valid = archive.testzip() is None
    check("Current native source bindings and reviewed solid-host modifiers",
          review["passed"] and archive_valid and
          digest(native_archive.read_bytes()) == review["native_archive_sha256"] and
          digest(gcode) == review["gcode_sha256"] and
          all(review["source_" + ext + "_sha256"] ==
              saved["artifacts"]["enclosure-back-top." + ext]["sha256"] for ext in ("step", "stl")) and
          len(modifiers) == len(project_modifiers) == review["solid_host_modifier_count"] == 23,
          modifier_regions=len(modifiers), native_review_sha256=digest(REVIEW.read_bytes()),
          native_archive_sha256=digest(native_archive.read_bytes()), project_sha256=digest(PROJECT.read_bytes()))
    for name, binding in saved["print_bindings"].items():
        receipt = json.loads(paths[binding["receipt_artifact"]].read_text())
        fixture_name = "funnel-frame.stl" if name == "funnel-frame" else "enclosure-" + name + ".stl"
        record = saved["artifacts"][fixture_name]
        expected = record.get("extraction", {}).get("original_stl_sha256", record["sha256"])
        if name == "front-top":
            preparation = json.loads(paths[binding["preparation_artifact"]].read_text())
            actual = preparation["source_stl_sha256"]
        else:
            actual = receipt["source_stl_sha256"]
        check(name + " fixture binds its production print receipt", actual == expected,
              original_stl_sha256=expected,
              printer_task_id=receipt.get("printer_task_id", receipt.get("task_id")))
    native = {}
    for name in ("enclosure-back-top", "enclosure-front-top", "funnel-frame"):
        shape = cq.importers.importStep(str(paths[name + ".step"])).val()
        native[name] = shape
        check(name + " native solid", shape.isValid() and len(shape.Solids()) == 1,
              solids=len(shape.Solids()), bounds_mm=bounds(shape))

    mesh_shapes = {}
    for name in ("enclosure-back-top", "enclosure-front-top", "enclosure-back-bottom",
                 "enclosure-front-bottom", "funnel-frame"):
        mesh = trimesh.load_mesh(paths[name + ".stl"])
        shape = mf.Manifold(mf.Mesh(np.asarray(mesh.vertices, np.float32), np.asarray(mesh.faces, np.uint32)))
        check(name + " closed printable mesh",
              mesh.is_watertight and mesh.is_winding_consistent and shape.status() == mf.Error.NoError,
              triangles=len(mesh.faces), manifold_status=str(shape.status()),
              bounds_mm=mesh.bounds.tolist())
        if shape.status() != mf.Error.NoError:
            raise ValueError("Cannot check an invalid mesh: " + name)
        mesh_shapes[name] = shape

    back = mesh_shapes["enclosure-back-top"]
    front = mesh_shapes["enclosure-front-top"]
    bottoms = {name: mesh_shapes["enclosure-" + name] for name in ("front-bottom", "back-bottom")}
    for first, second in combinations(("enclosure-front-bottom", "enclosure-back-bottom",
                                       "enclosure-front-top", "enclosure-back-top"), 2):
        overlap = abs((mesh_shapes[first] ^ mesh_shapes[second]).volume())
        check(first + " / " + second + " seated", overlap < MESH_VOLUME_TOLERANCE_MM3,
              overlap_mm3=overlap)

    translation = saved["frame_to_machine_translation_mm"]
    frame = mesh_shapes["funnel-frame"].translate(translation)
    native_frame = native["funnel-frame"].translate(tuple(translation))
    back_native = native["enclosure-back-top"]
    front_native = native["enclosure-front-top"]
    for name, shell in (("back-top", back_native), ("front-top", front_native)):
        overlap = native_overlap(native_frame, shell)
        check("Native frame seated / " + name, overlap < NATIVE_VOLUME_TOLERANCE_MM3,
              overlap_mm3=overlap, minimum_gap_mm=native_frame.distance(shell))

    # The complete upper rear corners end 0.25 mm before the Y200 seam.
    # Their side faces also require the ordinary 0.25 mm sliding allowance.
    for sign in (-1, 1):
        x0 = -98.25 if sign == -1 else 92.25
        corner = cq.Solid.makeBox(6.0, 6.0, 6.0, cq.Vector(x0, 193.75, 349.0))
        gaps = {name: corner.distance(shell) for name, shell in
                (("back-top", back_native), ("front-top", front_native))}
        check(f"Frame rear roof corner {sign:+d} running air",
              all(gap >= 0.25 - 1e-6 for gap in gaps.values()), clearance_mm=gaps)

    # Y-only motion leaves the cut-off Z ranges separated at every pose.
    # The back-top/front-top cut omits only stock aft of the front's full bounds.
    check("Motion crops retain every potentially intersecting face",
          all(body.bounding_box()[5] < 180 for body in bottoms.values()) and
          back.bounding_box()[2] > 159 and front.bounding_box()[2] > 159 and
          front.bounding_box()[4] < 260,
          crop_bottom_min_z_mm=159, crop_top_max_z_mm=180, crop_back_max_y_mm=260)
    motions = [
        ("back-top / printed back-bottom", back.trim_by_plane((0, 0, -1), -180),
         bottoms["back-bottom"].trim_by_plane((0, 0, 1), 159), 1, 50),
        ("front-top / printed front-bottom", front.trim_by_plane((0, 0, -1), -180),
         bottoms["front-bottom"].trim_by_plane((0, 0, 1), 159), -1, 50),
        ("back-top / printed front-top", back.trim_by_plane((0, -1, 0), -260), front, 1, 50),
        ("frame / back-top", frame, back, -1, 50),
        ("frame / printed front-top", frame, front, 1, 70),
    ]
    for name, moving, fixed, sign, travel in motions:
        samples = []
        for distance in sorted(set([0, .25, .5, .75] + list(range(1, travel + 1)))):
            overlap = abs((moving.translate((0, sign * distance, 0)) ^ fixed).volume())
            samples.append({"travel_mm": distance, "overlap_mm3": overlap})
        worst = max(sample["overlap_mm3"] for sample in samples)
        check(name + " sampled sliding motion", worst < MESH_VOLUME_TOLERANCE_MM3,
              maximum_overlap_mm3=worst, translation_axis="Y", translation_sign=sign,
              samples=samples)

    overlap = abs((back.translate((0, 0, 2)) ^ bottoms["back-bottom"]).volume())
    check("Back-top hooks capture a 2 mm upward displacement", overlap > MESH_VOLUME_TOLERANCE_MM3,
          bearing_intersection_mm3=overlap)
    for axis in range(3):
        for sign in (-1, 1):
            shift = np.zeros(3)
            shift[axis] = sign * 2
            moved = frame.translate(shift)
            bearing = abs((moved ^ front).volume()) + abs((moved ^ back).volume())
            check(f"Frame captured at {'XYZ'[axis]} {sign * 2:+d} mm",
                  bearing > MESH_VOLUME_TOLERANCE_MM3, bearing_intersection_mm3=bearing)

    facts = json.loads(FACTS.read_text())
    installed_placement = {}
    for name, record in saved["installed_parts"].items():
        shape = cq.Shape.importBrep(str(paths[record["artifact"]]))
        translation = [0.0, 0.0, 0.0]
        if name == "digiten-flow":
            target = facts["bodies"][name]
            if isinstance(target, dict):
                target = target["bounds_mm"] if "bounds_mm" in target else target["bbox"]
            original = bounds(shape)
            translation = [target[axis] - original[axis] for axis in range(3)]
            check("Same physical DIGITEN meter dimensions at the current installation seat",
                  all(abs((target[axis+3] - target[axis]) - (original[axis+3] - original[axis])) < 1e-6
                      for axis in range(3)),
                  recorded_print_fixture_bounds_mm=original, current_bounds_mm=target,
                  translation_mm=translation, placement_facts_sha256=digest(FACTS.read_bytes()))
            shape = shape.translate(tuple(translation))
        installed_placement[name] = translation
        overlap = native_overlap(back_native, shape)
        check("Back-top / installed " + name, overlap < NATIVE_VOLUME_TOLERANCE_MM3,
              overlap_mm3=overlap, minimum_gap_mm=back_native.distance(shape),
              installed_bounds_mm=bounds(shape), placement_translation_mm=translation)

    report = {
        "schema_version": 1,
        "pass": all(row["pass"] for row in rows),
        "manifest_sha256": digest((REFERENCE / "manifest.json").read_bytes()),
        "checker_sha256": digest(Path(__file__).read_bytes()),
        "materializer_sha256": digest((REFERENCE / "materialize.py").read_bytes()),
        "source_sha256": {name: record["sha256"] for name, record in saved["artifacts"].items()},
        "libraries": {"cadquery": cq.__version__, "trimesh": trimesh.__version__, "numpy": np.__version__},
        "scope": "Current redesigned back-top CAD against frozen front-top v20, October 1 bottoms and October 5 funnel-frame print fixtures. Seated intersections, sampled Y sliding motions, nominal capture and installed-part clearance, including the same DIGITEN meter moved to the current mount seat.",
        "installed_part_translation_mm": installed_placement,
        "native_review": str(REVIEW.relative_to(ROOT)),
        "native_review_sha256": digest(REVIEW.read_bytes()),
        "mesh_intersection_tolerance_mm3": MESH_VOLUME_TOLERANCE_MM3,
        "native_intersection_tolerance_mm3": NATIVE_VOLUME_TOLERANCE_MM3,
        "limits": [
            "The founder's October 7 report accepts existing printed-part fit; it does not identify individual archive names.",
            "Sliding samples do not establish continuous motion, insertion force, print distortion or support cleanup.",
            "Zero-volume contact at seating, clamp and locating faces is permitted; it does not establish running air everywhere.",
            "The back top has no physical print, load-capacity, lifetime or wet prototype acceptance in this package.",
            "The bound current native slice has separate emitted support and solid-host deposition reviews; this report verifies mating geometry.",
        ],
        "checks": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(f"{'PASS' if report['pass'] else 'FAIL'}: {len(rows)} checks; {args.output}", flush=True)
    if not report["pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
