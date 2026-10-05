"""Read both exact centered archives for matrix coverage and actual road heights."""
from collections import Counter, defaultdict
from datetime import datetime, timezone
import argparse
import hashlib
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
import zipfile

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "tools/publish_now.py").is_file())
sys.path.insert(0, str(ROOT / "hardware/printed-parts/enclosure/enclosure/support-bottom-gap"))
from read_roads import layers, MODEL, WALL


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scope", type=Path)
    args = parser.parse_args()
    scope = args.scope.resolve()
    output_path = scope / "independent-plate-pair-review.json"
    assert not output_path.exists()
    reports = {p: json.loads((scope / p / "independent-coupon-review.json").read_text()) for p in ("mark2", "h2c")}
    labels = {s["label"] for r in reports.values() for s in r["samples"]}
    assert labels == {f"{a}{b}" for a in "ABCD" for b in range(1, 5)} | {"C0", "V72", "V71", "V70", "V69", "V68"}
    repeated = []
    for label in ("C0", "V70"):
        a, b = [next(s for s in reports[p]["samples"] if s["label"] == label) for p in ("mark2", "h2c")]
        assert a["stl_sha256"] == b["stl_sha256"] and a["step_sha256"] == b["step_sha256"]
        assert a["measured_sections"] == b["measured_sections"], label
        repeated.append(dict(label=label, stl_sha256=a["stl_sha256"], native_measured_fit_sections_identical=True))
    actual = []
    for printer, report in reports.items():
        assert sha(ROOT / report["archive"]) == report["archive_sha256"]
        parts = {s["identify_id"]: s for s in report["samples"]}
        observations, stations = defaultdict(Counter), {}
        max_height_error, circular_bridge_roads = 0., 0
        with zipfile.ZipFile(ROOT / report["archive"]) as archive:
            for obj in ET.fromstring(archive.read("Metadata/model_settings.config")).findall("object"):
                values = {m.get("key"): m.get("value") for m in obj.findall("metadata") if m.get("key") is not None}
                assert set(values) == {"name", "enable_support", "extruder"}, values
            with archive.open("Metadata/plate_1.gcode") as data:
                for z, _, roads, _ in layers(data):
                    for r in roads:
                        assert r[6] in parts and r[7] in MODEL | {"Floating vertical shell"}
                        assert r[5] == 0 and r[8] in ("G0", "G1")
                        expected = .2 if abs(z-.2) < 1e-8 else .24
                        if r[7] == "Bridge" and abs(r[10]-.4) < 1e-8:
                            assert z > .44
                            circular_bridge_roads += 1
                        else:
                            error = abs(r[10]-expected)
                            assert error < 3e-6, (printer, z, r[10])
                            max_height_error = max(max_height_error, error)
                        observations[r[6]][round(r[10], 6)] += 1
                    for owner, sample in parts.items():
                        chosen = [r for r in roads if r[6] == owner and r[7] in WALL]
                        if not chosen or owner in stations:
                            continue
                        if sample["kind"] == "rc62":
                            if abs(z-14.12) > 1e-8:
                                continue
                            witness = sample["measured_sections"][2]["expected_gap_y_mm"] / 2
                            cutoff = sample["measured_sections"][2]["expected_gap_x_mm"] / 2 + 1.5
                        else:
                            if not 39 < z < 40:
                                continue
                            witness, cutoff = 0., 18.
                        shift = sample["native_mesh_binding"]["source_to_plate_translation_mm"]
                        crossings = []
                        for r in chosen:
                            ay, by = r[1]-shift[1], r[3]-shift[1]
                            if (ay < witness) != (by < witness):
                                x = r[0]+(witness+shift[1]-r[1])*(r[2]-r[0])/(r[3]-r[1])-shift[0]
                                if x > cutoff:
                                    crossings.append(dict(source_x_mm=round(x, 6), width_mm=r[4], feature=r[7]))
                        assert len(crossings) == 2, (printer, sample["name"], z, crossings)
                        stations[owner] = dict(label=sample["label"], source_y_mm=witness, print_z_mm=z, wall_crossings=crossings)
        assert set(stations) == set(parts) and set(observations) == set(parts)
        actual.append(dict(printer=report["printer"], archive_sha256=report["archive_sha256"],
            all_model_roads_fixed_left=True, actual_first_layer_road_height_mm=.2,
            nominal_other_wall_and_model_road_height_mm=.24, maximum_serialized_height_rounding_error_mm=max_height_error,
            circular_bridge_road_cross_section_height_mm=.4, circular_bridge_road_count=circular_bridge_roads,
            bridge_height_scope="Native circular bridge flow; layer Z increments remain 0.24 mm.",
            no_per_object_wall_overrides=True,
            representative_emitted_wall_count=2, stations=list(stations.values())))
    output = dict(schema_version=1, checked_utc=datetime.now(timezone.utc).isoformat(), status="pair_pass",
        checks_pass=True, plate_count=2, physical_coupon_count=24, unique_fit_sample_count=22,
        rc62_matrix_complete=True, valve_diameter_matrix_complete=True, repeated_reference_checks=repeated,
        actual_model_road_checks=actual, reviewer_source_sha256=sha(Path(__file__)),
        road_reader_source_sha256=sha(ROOT / "hardware/printed-parts/enclosure/enclosure/support-bottom-gap/read_roads.py"),
        reviews={p: dict(record=str((scope/p/"independent-coupon-review.json").relative_to(ROOT)),
            sha256=sha(scope/p/"independent-coupon-review.json")) for p in reports},
        scope="All frozen fit variants are covered by the two centered plates; repeated controls have identical measured native sections. Actual model-road heights and representative two-wall sections were read from both exact archives. Physical cooled fit and adhesion remain unqualified.")
    output_path.write_text(json.dumps(output, indent=2)+"\n")
    print(json.dumps({k: output[k] for k in ("checks_pass", "physical_coupon_count", "unique_fit_sample_count",
        "rc62_matrix_complete", "valve_diameter_matrix_complete")}, indent=2))


if __name__ == "__main__":
    main()
