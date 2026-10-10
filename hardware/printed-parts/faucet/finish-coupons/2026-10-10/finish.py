"""Apply only the three declared model-cooling treatments to the native archive.

No XYZ, extrusion, feedrate, heater, support geometry or startup/end command is
changed. The editable project alone does not reproduce this fan comparison.
"""
from bisect import bisect_right
import hashlib
import json
from pathlib import Path
import re
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "tools/bambu_print.py").exists())
WORK = ROOT / ".cache/printer-control/faucet-finish-coupons-20261010"
FAN = re.compile(r"^M106(?:\s|$)")
START = re.compile(r"^; start printing object, unique label id: (\d+)")
WORD = re.compile(r"([A-Z])(-?(?:\d+(?:\.\d*)?|\.\d+))")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def part_fan(line):
    words = dict((k, float(v)) for k, v in WORD.findall(line.split(";", 1)[0]))
    return words.get("S") if FAN.match(line) and words.get("P", 1) == 1 else None


def base_fan_schedule(text):
    z = fan = 0.
    current = None
    feature = ""
    values = {}
    for line in text.splitlines():
        if line.startswith("; Z_HEIGHT:"):
            z = float(line.split(":", 1)[1])
        start = START.match(line)
        if start:
            current = int(start[1])
        elif line.startswith("; stop printing object"):
            current = None
        if line.startswith("; FEATURE:"):
            feature = line.split(":", 1)[1].strip()
        state = part_fan(line)
        if state is not None:
            fan = state
        # Read the fan actually commanded while the accepted base's show wall
        # is extruded, including native bridge/overhang cooling changes.
        if current == 1901 and feature in ("Outer wall", "Overhang wall") and line.startswith(("G1 ", "G2 ", "G3 ")):
            words = dict(WORD.findall(line.split(";", 1)[0]))
            if float(words.get("E", 0)) > 0 and ("X" in words or "Y" in words):
                values[z] = fan
    assert values and min(values) < 13.4 and max(values) > 29
    return sorted(values.items())


def strip_fan(text):
    return "\n".join(line for line in text.splitlines()
                     if part_fan(line) is None and not line.startswith("; coupon model cooling"))


def extrusion_fans(text):
    """Fan state at each depositing move; feature state follows native comments."""
    fan = z = 0.
    current = None
    feature = ""
    for line in text.splitlines():
        if line.startswith("; Z_HEIGHT:"):
            z = float(line.split(":", 1)[1])
            current = None
        start = START.match(line)
        if start:
            current = int(start[1])
        elif line.startswith("; stop printing object"):
            current = None
        if line.startswith("; FEATURE:"):
            feature = line.split(":", 1)[1].strip()
        state = part_fan(line)
        if state is not None:
            fan = state
        if line.startswith(("G1 ", "G2 ", "G3 ")):
            words = dict(WORD.findall(line.split(";", 1)[0]))
            if float(words.get("E", 0)) > 0 and ("X" in words or "Y" in words):
                yield line, current, z, feature, fan


def main():
    prep_path = HERE / "preparation.json"
    prep = json.loads(prep_path.read_text())
    for receipt in (HERE / "launch-plan.json", HERE / "launch.json"):
        if receipt.exists():
            state = json.loads(receipt.read_text())
            assert not any(state.get(k) for k in ("import_attempted", "send_attempted", "accepted"))
    source = WORK / (Path(prep["project"]).stem + ".gcode.3mf")
    with zipfile.ZipFile(ROOT / prep["shipping_reference"]) as archive:
        reference = archive.read("Metadata/plate_1.gcode").decode()
    schedule = base_fan_schedule(reference)
    heights = [p[0] for p in schedule]
    with zipfile.ZipFile(source) as archive:
        assert archive.testzip() is None
        members = {n: archive.read(n) for n in archive.namelist()}
    native = members["Metadata/plate_1.gcode"].decode()
    treatments = {r["identify_id"]: r for r in prep["specimens"] if r["kind"] == "foot"}
    native_fan = emitted_fan = z = 0.
    current = None
    feature = ""
    result = []
    additions, replacements, witnesses = [], [], []
    for index, raw in enumerate(native.splitlines(keepends=True), 1):
        line = raw.strip()
        if line.startswith("; Z_HEIGHT:"):
            z = float(line.split(":", 1)[1])
            current = None
        start = START.match(line)
        if start:
            current = int(start[1])
        elif line.startswith("; stop printing object"):
            current = None
        if line.startswith("; FEATURE:"):
            feature = line.split(":", 1)[1].strip()
        fan = part_fan(line)
        if fan is not None:
            native_fan = fan
        treatment = treatments.get(current)
        active = (treatment is not None and 13.4 <= z <= 29.0
                  and bool(feature) and not feature.startswith(("Support", "Skirt", "Brim", "Custom")))
        desired = native_fan
        if active:
            ref = schedule[max(0, bisect_right(heights, z)-1)][1]
            mode = treatment["cooling"]
            desired = ref if mode == "reference" else ref*.5 if mode == "half" else max(ref, 178.5)
        assert 0 <= desired <= 255
        if fan is not None:
            if abs(desired - fan) > 1e-7:
                result.append(f"M106 S{desired:.5f}\n")
                replacements.append({"native_line": index, "from": line, "to": result[-1].strip()})
            else:
                result.append(raw)
            emitted_fan = desired
        else:
            result.append(raw)
            # A comment transition carries no machine motion. Set the next
            # segment's fan before the following native machine command.
            if (start or line.startswith(("; FEATURE:", "; Z_HEIGHT:", "; stop printing object"))) and abs(emitted_fan-desired) > 1e-7:
                result.append(f"; coupon model cooling object={current} z={z:.5f}\nM106 S{desired:.5f}\n")
                additions.append({"after_native_line": index, "object": current, "z": z, "fan_pwm": desired})
                emitted_fan = desired
        if active and line.startswith(("G1 ", "G2 ", "G3 ")):
            words = dict(WORD.findall(line.split(";", 1)[0]))
            if float(words.get("E", 0)) > 0 and ("X" in words or "Y" in words):
                witnesses.append((current, round(z, 5), round(emitted_fan, 5)))
    final = "".join(result)
    assert strip_fan(native) == strip_fan(final), "Non-part-fan commands changed"
    unchanged_cooling_moves = treatment_moves = support_moves = 0
    for before, after in zip(extrusion_fans(native), extrusion_fans(final), strict=True):
        assert before[:4] == after[:4]
        _, oid, height, kind, actual = after
        active = (oid in treatments and 13.4 <= height <= 29
                  and bool(kind) and not kind.startswith(("Support", "Skirt", "Brim", "Custom")))
        if active:
            ref = schedule[max(0, bisect_right(heights, height)-1)][1]
            mode = treatments[oid]["cooling"]
            expected = ref if mode == "reference" else ref*.5 if mode == "half" else max(ref, 178.5)
            assert abs(actual-expected) < 1e-4, (oid, height, kind, actual, expected)
            treatment_moves += 1
        else:
            assert abs(actual-before[-1]) < 1e-4, (oid, height, kind, actual, before[-1])
            unchanged_cooling_moves += 1
            support_moves += int(kind.startswith("Support"))
    # Independently scan final wall extrusion, rather than trusting the writer's
    # annotations or its treatment selection.
    fan = z = 0.
    current = None
    feature = ""
    checked = {key: 0 for key in treatments}
    actual_values = {key: set() for key in treatments}
    for line in final.splitlines():
        if line.startswith("; Z_HEIGHT:"):
            z = float(line.split(":", 1)[1])
            current = None
        start = START.match(line)
        if start:
            current = int(start[1])
        elif line.startswith("; stop printing object"):
            current = None
        if line.startswith("; FEATURE:"):
            feature = line.split(":", 1)[1].strip()
        state = part_fan(line)
        if state is not None:
            fan = state
        if current in treatments and 13.4 <= z <= 29 and feature in ("Outer wall", "Overhang wall") and line.startswith(("G1 ", "G2 ", "G3 ")):
            words = dict(WORD.findall(line.split(";", 1)[0]))
            if float(words.get("E", 0)) > 0 and ("X" in words or "Y" in words):
                ref = schedule[max(0, bisect_right(heights, z)-1)][1]
                mode = treatments[current]["cooling"]
                expected = ref if mode == "reference" else ref*.5 if mode == "half" else max(ref, 178.5)
                assert abs(fan-expected) < 1e-4, (current, z, fan, expected)
                checked[current] += 1
                actual_values[current].add(round(fan/255*100, 2))
    assert all(checked.values())
    payload = final.encode()
    members["Metadata/plate_1.gcode"] = payload
    members["Metadata/plate_1.gcode.md5"] = hashlib.md5(payload).hexdigest().upper().encode()
    destination = HERE / source.name
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for name, data in sorted(members.items()):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data)
    report = {"schema": 1, "native_archive_sha256": sha(source.read_bytes()),
              "final_archive": str(destination.relative_to(ROOT)), "final_archive_sha256": sha(destination.read_bytes()),
              "native_gcode_sha256": sha(native.encode()), "final_gcode_sha256": sha(payload),
              "only_part_fan_commands_changed": True,
              "all_motion_extrusion_feedrate_heater_and_other_fan_commands_identical": True,
              "all_other_deposition_fan_states_identical": True,
              "unchanged_cooling_deposition_moves_checked": unchanged_cooling_moves,
              "unchanged_support_deposition_fan_moves_checked": support_moves,
              "treatment_deposition_moves_checked": treatment_moves,
              "treatment_band_print_z_mm": [13.4, 29.0],
              "reference_schedule": [{"z": z, "fan_pwm": fan} for z, fan in schedule if 12 <= z <= 30],
              "wall_extrusions_independently_checked": checked,
              "actual_wall_fan_percent": {k: sorted(v) for k,v in actual_values.items()},
              "inserted_commands": additions, "replaced_commands": replacements,
              "fan_response_and_neighbor_cooling_unmeasured": True}
    (HERE / "cooling-command-review.json").write_text(json.dumps(report, indent=2)+"\n")
    prep.update(native_archive=str(destination.relative_to(ROOT)), native_archive_sha256=report["final_archive_sha256"],
                gcode_sha256=report["final_gcode_sha256"], native_source_archive_sha256=report["native_archive_sha256"])
    prep_path.write_text(json.dumps(prep, indent=2)+"\n")
    (ROOT / prep["project"]).with_suffix(".print.json").write_text(json.dumps(prep, indent=2)+"\n")
    print(json.dumps({"archive": report["final_archive"], "checked":checked,
                      "fan_percent":report["actual_wall_fan_percent"]}, indent=2))


if __name__ == "__main__":
    main()
