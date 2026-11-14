"""Compare the companion parts' ordered deposition on two complete plate tapes."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re

WORDS = re.compile(r"([XYZFEPSIJK])(-?(?:\d+(?:\.\d*)?|\.\d+))")
MOTION = ("G0 ", "G1 ", "G2 ", "G3 ")
PARTS = {1902: "tip", 1903: "cover", 1904: "mounting_plate", 1905: "lever"}
SIGNATURE_FIELDS = (
    "command", "start_xyz", "end_xyz", "arc_center_offset_ijk", "extrusion_length", "feed", "fan_pwm", "acceleration"
)


def deposition(path):
    """Digest native XYZ, arc geometry, E, feed and modal cooling and acceleration."""
    signatures = {obj: sha256() for obj in PARTS}
    totals = dict.fromkeys(PARTS, 0)
    xyz = (0.0, 0.0, 0.0)
    first_z = {}
    feed = fan = 0.0
    acceleration = 10000.0
    obj = None
    with path.open() as tape:
        if not any(line.startswith("; MACHINE_START_GCODE_END") for line in tape):
            raise ValueError(f"No model body start in {path}")
        for line in tape:
            if line.startswith("; MACHINE_END_GCODE_START"):
                break
            if line.startswith("; start printing object"):
                obj = int(line.rsplit(":", 1)[1])
            if line.startswith("; stop printing object"):
                obj = None
            if line.startswith("M204 S"):
                acceleration = float(line.split()[1][1:])
            if line.startswith("M106"):
                words = {key: float(value) for key, value in WORDS.findall(line.split(";", 1)[0])}
                if words.get("P", 1) == 1:
                    fan = words["S"]
            if not line.startswith(MOTION):
                continue
            words = {key: float(value) for key, value in WORDS.findall(line.split(";", 1)[0])}
            before = xyz
            xyz = tuple(words.get(axis, xyz[index]) for index, axis in enumerate("XYZ"))
            feed = words.get("F", feed)
            extrusion = words.get("E", 0.0)
            is_arc = line.startswith(("G2 ", "G3 "))
            if obj in signatures and extrusion > 0.0 and (xyz[:2] != before[:2] or is_arc):
                center = tuple(words.get(axis, 0.0) for axis in "IJK") if is_arc else ()
                numbers = (*before, *xyz, *center, extrusion, feed, fan, acceleration)
                row = line.split()[0] + "," + ",".join(f"{value:.5f}" for value in numbers) + "\n"
                signatures[obj].update(row.encode())
                totals[obj] += 1
                first_z.setdefault(obj, before[2])
        else:
            raise ValueError(f"No model body end in {path}")
    return {
        PARTS[obj]: {"road_count": totals[obj], "first_road_z_mm": first_z[obj], "ordered_road_sha256": digest.hexdigest()}
        for obj, digest in signatures.items()
    }


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("source", type=Path, help="The annotated precursor with native companion deposition")
    cli.add_argument("resequenced", type=Path, help="The resequenced plate tape before container metadata stamping")
    args = cli.parse_args()
    reference = deposition(args.source)
    result = deposition(args.resequenced)
    identical = reference == result
    print(json.dumps({
        "precursor_tape_sha256": sha256(args.source.read_bytes()).hexdigest(),
        "resequenced_tape_sha256_before_container_stamping": sha256(args.resequenced.read_bytes()).hexdigest(),
        "signature_fields": SIGNATURE_FIELDS,
        "companion_deposition_identical": identical,
        "companions": result,
    }, indent=2))
    if not identical:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
