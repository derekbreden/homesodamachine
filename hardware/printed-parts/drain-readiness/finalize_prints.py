"""Save the checked identification plate archives and their evidence beside the parts.

Run after `prepare.py labels` and `review_native.py`. No printer job is submitted.
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
    plates = []
    labels = read(WORK / "label-archive-review.json")
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
    for path in [Path(__file__), HERE / "prepare.py", HERE / "review_native.py", HERE / "review_roads.py"]:
        source_hashes[str(path.relative_to(ROOT))] = sha(path)
    reviews = {str(p.relative_to(ROOT)): sha(p) for p in sorted((HERE / "reviews").glob("*.json"))}
    save(HERE / "manifest.json", {"schema_version": 1,
        "status": "ready to print; four identification plates and five linked faucet plates finalized",
        "scope": "Current source geometry, editable projects, native archive integrity, emitted bead footprints and face-closing layers. No printer job is submitted. Lettering appearance, chip fit and collar grip remain physical observations.",
        "plates": plates, "source_sha256": source_hashes, "review_sha256": reviews,
        "faucet_print_manifest": str(faucet_path.relative_to(ROOT)), "faucet_print_manifest_sha256": sha(faucet_path),
        "submitted": False})
    print("Finalized four identification plates; linked five finalized faucet plates.")


if __name__ == "__main__":
    main()
