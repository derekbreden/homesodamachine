"""Save the checked DRAIN native archives and their evidence beside the parts.

Run after prepare.py and the four native reviews. No printer job is submitted.
The strict radial pore/bore reading is retained as an independent diagnostic.
"""
from pathlib import Path
import hashlib
import json
import shutil
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "tools/docgen").is_dir())
WORK = ROOT / ".cache/prints/2026-10-07-drain"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + "\n")


def copy(source, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)
    assert sha(source) == sha(destination)
    return str(destination.relative_to(ROOT))


def archive_binding(path, expected_gcode):
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        raw = z.read("Metadata/plate_1.gcode")
        assert hashlib.sha256(raw).hexdigest() == expected_gcode
        assert hashlib.md5(raw).hexdigest() == z.read("Metadata/plate_1.gcode.md5").decode().strip().lower()


def main():
    job = WORK / "back-top-mark2"
    stem = "back-top-black-z004-mark2"
    prep = read(job / (stem + ".preparation.json"))
    archive = read(job / "archive-review.json")
    dense = read(job / "dense-region-review.json")
    support = read(job / "show-support-clearance-summary.json")
    radial = read(job / "insert-radial-backing.json")
    stock = read(HERE / "reviews/insert-stock.json")
    assert archive["passed"] and dense["passed"] and support["pass"] and stock["passed"]
    assert dense["preparation_sha256"] == radial["preparation_sha256"] == sha(job / (stem + ".preparation.json"))
    source = ROOT / prep["parts"][0]["source"]
    assert dense["source_stl_sha256"] == radial["source_stl_sha256"] == stock["source_stl_sha256"] == archive["source_stl_sha256"] == sha(source)
    assert stock["source_step_sha256"] == support["source_step_sha256"] == archive["source_step_sha256"] == sha(source.with_suffix(".step"))
    region_spec = ROOT / "hardware/printed-parts/enclosure/enclosure/heat-set-review/print-regions.json"
    assert prep["solid_host_region_source_sha256"] == sha(region_spec)
    assert len(dense["regions"]) == 23 and len(stock["stations"]) == 19
    sliced = job / "ready" / (stem + ".gcode.3mf")
    assert archive["native_archive_sha256"] == dense["native_archive_sha256"] == radial["native_archive_sha256"] == sha(sliced)
    archive_binding(sliced, archive["gcode_sha256"])
    project = job / (stem + ".3mf")
    assert prep["project_sha256"] == sha(project)
    project_path = copy(project, HERE / "projects" / project.name)
    archive_path = copy(sliced, HERE / "ready" / sliced.name)
    archive["native_archive"] = archive_path
    save(HERE / "reviews/back-top-native.json", archive)
    for name in ("dense-region-review.json", "insert-radial-backing.json", "show-support-clearance-summary.json",
                 "show-support-clearance.json", "rear-port-support-contacts.json"):
        copy(job / name, HERE / "reviews" / name)
    copy(job / (stem + ".preparation.json"), HERE / "projects" / (stem + ".preparation.json"))
    copy(job / "preview.png", HERE / "reviews/back-top.png")
    result = read(job / "ready/result.json")["sliced_plates"][0]
    plates = [{"name": "back-top", "printer": "Mark2", "filament": ["Black PET-GF"],
               "project": project_path, "project_sha256": sha(project),
               "native_archive": archive_path, "native_archive_sha256": sha(sliced),
               "gcode_sha256": archive["gcode_sha256"],
               "native_estimated_seconds": result["total_predication"],
               "complete_emitted_bead_minimum_bed_margin_mm": archive["full_native_bead_footprint"]["minimum_shared_bed_margin_mm"],
               "minimum_sampled_host_root_coverage_fraction": min(r["minimum_sample_coverage_fraction"] for r in dense["regions"])}]
    labels = read(HERE / "reviews/labels.json")
    assert labels["passed"] and len(labels["plates"]) == 4
    source_hashes = {}
    for plate in labels["plates"]:
        colour = plate["colour"]
        label_job = WORK / f"labels-{colour}-mark2"
        label_prep = read(label_job / "preparation.json")
        for path, digest in label_prep["source_sha256"].items():
            assert sha(ROOT / path) == digest, path
            source_hashes[path] = digest
        label_stem = f"labels-{colour}-z004-mark2"
        editable = label_job / (label_stem + ".3mf")
        sliced = label_job / "ready" / (label_stem + ".gcode.3mf")
        assert label_prep["project_sha256"] == sha(editable)
        assert plate["native_archive_sha256"] == sha(sliced)
        archive_binding(sliced, plate["gcode_sha256"])
        project_path = copy(editable, HERE / "projects" / editable.name)
        archive_path = copy(sliced, HERE / "ready" / sliced.name)
        plate["native_archive"] = archive_path
        plate["editable_project"] = {"path": project_path, "sha256": sha(editable)}
        copy(label_job / "preparation.json", HERE / "projects" / (label_stem + ".preparation.json"))
        plates.append({"name": colour + " identification", "printer": "Mark2",
                       "project": project_path, "project_sha256": sha(editable),
                       "native_archive": archive_path, "native_archive_sha256": sha(sliced),
                       "gcode_sha256": plate["gcode_sha256"],
                       "complete_emitted_bead_minimum_bed_margin_mm": plate["full_native_bead_margin_mm"]})
    save(HERE / "reviews/labels.json", labels)
    faucet_path = ROOT / "hardware/printed-parts/faucet/vent-print-readiness/manifest.json"
    faucet = read(faucet_path)
    assert len(faucet["plates"]) == 5
    for plate in faucet["plates"]:
        assert sha(ROOT / plate["project"]) == plate["project_sha256"]
        assert sha(ROOT / plate["native_archive"]) == plate["native_archive_sha256"]
    for path in [Path(__file__), HERE / "prepare.py", HERE / "review_native.py", HERE / "review_dense_regions.py",
                 HERE / "review_insert_backing.py", HERE / "review_show_support.py", HERE / "review_roads.py", source,
                 source.with_suffix(".step"), region_spec]:
        source_hashes[str(path.relative_to(ROOT))] = sha(path)
    reviews = {str(p.relative_to(ROOT)): sha(p) for p in sorted((HERE / "reviews").glob("*.json"))}
    save(HERE / "manifest.json", {"schema_version": 1,
        "status": "ready to print; five cabinet plates and five linked faucet plates finalized",
        "scope": "Current source geometry, editable projects, native archive integrity, emitted bead footprints, sampled whole-host/root deposition and geometric support access. No printer job is submitted. Physical fit, fusion, insert retention, support release, vent capacity and product lifetime remain qualification properties.",
        "plates": plates, "source_sha256": source_hashes, "review_sha256": reviews,
        "faucet_print_manifest": str(faucet_path.relative_to(ROOT)), "faucet_print_manifest_sha256": sha(faucet_path),
        "strict_radial_pore_bore_diagnostic_passed": radial["passed"],
        "strict_radial_pore_bore_diagnostic_scope": radial["scope"], "submitted": False})
    print("Finalized five cabinet plates; linked five finalized faucet plates.")


if __name__ == "__main__":
    main()
