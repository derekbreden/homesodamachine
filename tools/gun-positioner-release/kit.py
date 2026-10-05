"""Create the portable fabrication kit and verify its actual delivered bytes.

Run after the guide, selected purchases, CAD exports and UF2 assets are bound.
The archive preserves repository-relative paths so its drawings and documents
have the same part identifiers as the shop guide. No hardware is contacted.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PLAN = ROOT / "hardware/gun-positioner"
OUT = ROOT / "output/gun-positioner"
ARCHIVE = OUT / "gun-positioner-build-kit.zip"
SCOPES = (
    "hardware/gun-positioner",
    "hardware/gun-positioner-guide",
    "hardware/printed-parts/fixtures/gun-positioner",
    "hardware/printed-parts/fixtures/gun-positioner-observation",
    "firmware/src_gun_positioner",
    "tools/gun-positioner-observation",
    "tools/gun-positioner",
    "tools/gun-positioner-optics",
    "tools/gun-positioner-guide",
    "tools/gun-positioner-release",
    "future/robot-arm-study",
    "hardware/guide-assets/fonts",
)
EXCLUDE_DIRS = {"out", "__pycache__", ".venv", "venv", "build", "captures", "datasets"}
EXCLUDE_NAMES = {"release-manifest.json", "release-verification.json"}
SUFFIXES = {".md", ".json", ".pdf", ".png", ".svg", ".html", ".css", ".step",
            ".stl", ".mesh", ".dxf", ".uf2", ".py", ".h", ".cpp", ".txt",
            ".woff2", ".ttf", ".swift", ".plist", ".sh", ".lint-answers"}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def files():
    result = []
    for scope in SCOPES:
        for path in (ROOT / scope).rglob("*"):
            if not path.is_file() or path.name in EXCLUDE_NAMES:
                continue
            rel = path.relative_to(ROOT)
            if any(part in EXCLUDE_DIRS for part in rel.parts):
                continue
            if path.suffix in SUFFIXES or path.name == "CMakeLists.txt":
                result.append(path)
    # The signed native camera helper is an actual ready asset, alongside its
    # portable source. Zip preserves its executable mode and app-bundle layout.
    helper = ROOT / "tools/gun-positioner-observation/helper/build/GPOCapture.app"
    if not (helper / "Contents/MacOS/GPOCapture").is_file():
        raise ValueError("The native camera helper has not been built")
    result.extend(p for p in helper.rglob("*") if p.is_file())
    return sorted(set(result))


def check_bound_inputs():
    receipts = (
        PLAN.parent / "gun-positioner-guide/source-receipt.json",
        ROOT / "firmware/src_gun_positioner/assets/build-manifest.json",
    )
    for receipt in receipts:
        if not receipt.exists():
            raise ValueError(f"Missing final receipt: {receipt.relative_to(ROOT)}")
    book = json.loads(receipts[0].read_text())
    for rel, digest in book["source_sha256"].items():
        if sha((ROOT / rel).read_bytes()) != digest:
            raise ValueError(f"Guide source changed after binding: {rel}")
    pdf = PLAN.parent / "gun-positioner-guide/gun-positioner-guide.pdf"
    if sha(pdf.read_bytes()) != book["pdf_sha256"]:
        raise ValueError("The assembly PDF does not match its receipt")
    visual = json.loads((pdf.parent / "visual-qa-receipt.json").read_text())
    for key, name in (("guide", pdf.name), ("templates", "gun-positioner-drill-templates.pdf")):
        if visual["document_checks"][key]["pdf_sha256"] != sha((pdf.parent / name).read_bytes()):
            raise ValueError(f"Visual review belongs to a different {key} PDF")
    template_receipt = json.loads((pdf.parent / "drill-template-receipt.json").read_text())
    for rel, digest in template_receipt["source_sha256"].items():
        if sha((ROOT / rel).read_bytes()) != digest:
            raise ValueError(f"Fabrication-template source changed: {rel}")
    if sha((pdf.parent / template_receipt["file"]).read_bytes()) != template_receipt["pdf_sha256"]:
        raise ValueError("The fabrication-template PDF does not match its receipt")
    mechanism = ROOT / "hardware/printed-parts/fixtures/gun-positioner"
    mechanism_receipt = json.loads((mechanism / "export-receipt.json").read_text())
    for rel, digest in mechanism_receipt["sources_sha256"].items():
        if sha((ROOT / rel).read_bytes()) != digest:
            raise ValueError(f"Mechanism source changed after export: {rel}")
    if sha((mechanism / "gun-positioner-assembly.step").read_bytes()) != mechanism_receipt["assembly_STEP_sha256"]:
        raise ValueError("The mechanism assembly STEP does not match its export receipt")
    parts = json.loads((mechanism / "parts.json").read_text())
    mesh_check = json.loads((mechanism / "mesh-export-check.json").read_text())
    exported_names = {record["part"] for record in mesh_check["fabrication_parts"]}
    if (len(parts) != mechanism_receipt["fabrication_payloads"] or
            exported_names != {part["name"] for part in parts}):
        raise ValueError("The mechanism viewer/export set is incomplete")
    if mesh_check["source_sha256"] != sha((mechanism / "gun_positioner.py").read_bytes()):
        raise ValueError("The fabrication mesh check belongs to another CAD source")
    for part in parts:
        for rel in (part["step"], part["stl"], part["step"] + ".mesh"):
            if not (mechanism / rel).is_file():
                raise ValueError(f"Missing fabrication asset: {rel}")
    if not all(record["watertight"] and record["winding_consistent"] and
               record["payload_preserves_STL_triangles"]
               for record in mesh_check["fabrication_parts"]):
        raise ValueError("The fabrication mesh export checks are incomplete")
    for rel, digest in json.loads((mechanism / "asset-hashes.json").read_text()).items():
        if sha((mechanism / rel).read_bytes()) != digest:
            raise ValueError(f"Changed mechanism fabrication asset: {rel}")
    lint = json.loads((mechanism / "post-live-lint.json").read_text())
    if (lint["source_sha256"] != sha((mechanism / "gun_positioner.py").read_bytes()) or
            lint["unanswered_findings"] != 0):
        raise ValueError("The post-publication print review is incomplete or stale")
    for record in lint["parts"]:
        if record.get("answer_file") and sha((mechanism / record["answer_file"]).read_bytes()) != record["answer_sha256"]:
            raise ValueError(f"Changed print-review answers: {record['part']}")
    optics = ROOT / "hardware/printed-parts/fixtures/gun-positioner-observation"
    for rel, digest in json.loads((optics / "manifest.json").read_text())["sha256"].items():
        if sha((optics / rel).read_bytes()) != digest:
            raise ValueError(f"Changed camera-stage fabrication asset: {rel}")
    mounting = PLAN / "mounting"
    mounting_receipt = json.loads((mounting / "source-receipt.json").read_text())
    for rel, digest in mounting_receipt["source_sha256"].items():
        if sha((ROOT / rel).read_bytes()) != digest:
            raise ValueError(f"Controller mounting source changed: {rel}")
    for rel, digest in mounting_receipt["output_sha256"].items():
        if sha((mounting / rel).read_bytes()) != digest:
            raise ValueError(f"Changed controller mounting fabrication asset: {rel}")
    # Integrity includes the actual RP2040 blocks and their source/geometry
    # binding, rather than only the presence of the build receipt.
    firmware = ROOT / "firmware/src_gun_positioner"
    sys.path.insert(0, str(firmware))
    spec = importlib.util.spec_from_file_location("release_verify_uf2", firmware / "verify_assets.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.verify()
    purchases = json.loads((PLAN / "purchases.json").read_text())
    if not purchases["rows"] or any(not row["prime"] for row in purchases["rows"]):
        raise ValueError("The selected purchase set is incomplete")
    if purchases.get("verification_source_sha256") != sha((PLAN / "sourcing/prime-verified.json").read_bytes()):
        raise ValueError("The purchase lists do not match the final verified quantities")
    demand = json.loads((PLAN / "sourcing/final-demand-audit.json").read_text())
    if sha((ROOT / demand["audit_script"]).read_bytes()) != demand["audit_script_sha256"]:
        raise ValueError("The purchase coverage audit does not match its verifier")
    for rel, digest in demand["source_sha256"].items():
        if sha((ROOT / rel).read_bytes()) != digest:
            raise ValueError(f"Purchase coverage audit source changed: {rel}")
    if (demand["unknown_consumption_classes"] or demand["shortages"] or
            demand["text_quantity_mismatches"] or any(demand["schedule_vs_hardware_counts"].values())):
        raise ValueError("The final shared purchase quantities do not cover the assembly schedules")
    if not list((ROOT / "hardware/printed-parts/fixtures/gun-positioner").rglob("*.stl")):
        raise ValueError("The mechanism STL exports are missing")
    if not list((ROOT / "hardware/printed-parts/fixtures/gun-positioner").rglob("*.dxf")):
        raise ValueError("The mechanism metal drawings are missing")
    publication = json.loads((PLAN / "publication-verification.json").read_text())
    fabrication = publication["fabrication"]
    documents = publication["documents"]
    if fabrication["status"] != "pass" or documents["status"] != "pass":
        raise ValueError("The served fabrication files or documents have not passed verification")
    for record in fabrication["files"]:
        local = ROOT / "hardware" / record["file"]
        if (sha(local.read_bytes()) != record["expected_sha256"] or
                record["served_sha256"] != record["expected_sha256"] or not record["served_matches"]):
            raise ValueError(f"Publication verification is stale: {record['file']}")
    for record in documents["documents"]:
        local = ROOT / "hardware" / record["file"]
        if (not record["pass"] or sha(local.read_bytes()) != record["expected_sha256"] or
                record["served_sha256"] != record["expected_sha256"] or not record["cover_matches"]):
            raise ValueError(f"Document publication verification is stale: {record['file']}")


def build():
    check_bound_inputs()
    members = files()
    manifest = {
        "schema": 1,
        "title": "Gun positioner fabrication and dry-development kit",
        "archive": "output/gun-positioner/gun-positioner-build-kit.zip",
        "scope": "Fabrication files and dry-development tools; physical commissioning remains required.",
        "files": {str(p.relative_to(ROOT)): {"sha256": sha(p.read_bytes()), "bytes": p.stat().st_size}
                  for p in members},
    }
    start = """# Gun positioner build kit

Start with hardware/gun-positioner/README.md and its Prime purchase lists.
Print hardware/gun-positioner-guide/gun-positioner-guide.pdf on Letter paper.
Print the separate fabrication-template PDF at 100% / actual size and verify
its scale bars before transferring any holes. STEP files describe the parts;
STL files are the print exports; DXF files use millimeters.

Use the firmware assets/README.md to select and verify the UF2 image. The
controller, camera and observation tools require explicit device selection;
opening this archive performs no connection or motion.

Ready fabrication files need no rebuild. Regenerating CAD or the illustrated
book uses the Home Soda Machine repository's toolchain and shared libraries.

The fixture has not been physically commissioned. Follow the guide's gates
before loaded motion and preserve the resulting records. Live welding requires
the separate observation and welder-interface acceptance described in the plan.

release-manifest.json records the SHA-256 and size of every delivered file.
"""
    OUT.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ARCHIVE, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        z.writestr("START-HERE.md", start)
        z.writestr("release-manifest.json", json.dumps(manifest, indent=2) + "\n")
        for path in members:
            z.write(path, str(path.relative_to(ROOT)))
    with zipfile.ZipFile(ARCHIVE) as z:
        if z.testzip() is not None:
            raise ValueError("Archive CRC verification failed")
        for name, record in manifest["files"].items():
            data = z.read(name)
            if len(data) != record["bytes"] or sha(data) != record["sha256"]:
                raise ValueError(f"Delivered bytes changed: {name}")
    (PLAN / "release-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    result = {
        "schema": 1, "files": len(members), "archive": manifest["archive"],
        "archive_bytes": ARCHIVE.stat().st_size, "archive_sha256": sha(ARCHIVE.read_bytes()),
        "archive_crc": "passed", "member_hashes": "passed", "guide_source_binding": "passed",
        "final_pdf_visual_review_binding": "passed",
        "fabrication_export_hashes": "passed", "template_source_binding": "passed",
        "complete_fabrication_and_viewer_asset_set": "passed",
        "mechanism_source_and_assembly_binding": "passed",
        "controller_mounting_source_and_export_hashes": "passed",
        "firmware_integrity_and_source_binding": "passed",
        "purchase_verification_source_binding": "passed",
        "shared_purchase_quantity_coverage": "passed",
        "post_publication_print_review_binding": "passed",
        "exact_served_fabrication_and_document_bytes": "passed",
        "physical_acceptance": "Unbuilt; follow commissioning gates.",
    }
    (PLAN / "release-verification.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    build()
