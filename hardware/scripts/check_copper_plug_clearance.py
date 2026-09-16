#!/usr/bin/env python3
"""Measure both finished copper plugs against front-top and the foam assembly.

This reads standalone STEP outputs through the production placement transforms. It does
not rebuild the appliance, route tubing, slice a part, or run the all-body clearance audit.
Run after the relevant CAD outputs are regenerated, using tools/cad-venv/bin/python.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
PLUG_DIR = ROOT / "hardware/printed-parts/cold-core/copper-plugs"
FRONT_TOP = ROOT / "hardware/printed-parts/enclosure/enclosure/enclosure-front-top.step"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def label(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--front-top", type=Path, default=FRONT_TOP)
    parser.add_argument("--output", type=Path, default=PLUG_DIR / "clearance-check.json")
    args = parser.parse_args()
    sources = (
        Path(__file__).resolve(),
        ROOT / "hardware/manifold-layout/enclosure_assembly.py",
        ROOT / "hardware/cold-core-layout/cold_core_assembly.py",
        ROOT / "hardware/printed-parts/cold-core/copper-plugs/copper_plugs.py",
        ROOT / "hardware/printed-parts/cold-core/_cold_core_interface.py",
        ROOT / "hardware/printed-parts/enclosure/enclosure/enclosure.py",
        ROOT / "hardware/printed-parts/cadlib/fits.py",
    )
    source_hashes = {label(p): digest(p) for p in sources}

    # A short, read-only measurement has no generated CAD outputs to serialize with builders.
    os.environ.setdefault("HSM_NO_BUILD_LOCK", "1")
    sys.path.insert(0, str(ROOT / "hardware/manifold-layout"))
    import enclosure_assembly as ea

    paths = {
        "front_top": args.front_top.resolve(),
        "foam_assembly": ea.FOAM_STEP,
        **{f"plug_{name}": PLUG_DIR / f"copper-plug-{name}.step"
           for name in ea._plugs.plug_specs},
    }
    before = {label(p): digest(p) for p in paths.values()}
    front = ea.import_step(str(paths["front_top"])).val()
    # The appliance seats the envelope from its rear datum, rather than seating the larger
    # internal assembly by its own bounding box. Use that same transform for the plugs.
    zero = ea.build_foam(0.0)[0].BoundingBox()
    foam, carry = ea.build_foam(
        ea._enc.rear_plane_y - ea._enc.rear_seam_clear - zero.ylen)
    minimum_gap = ea._enc.fits.slip
    tolerance = 1e-6
    rows = {}
    for name, spec in ea._plugs.plug_specs.items():
        plug = ea.import_step(str(paths[f"plug_{name}"])).val()
        placed = ea._cca._plug_into_shell(plug, spec.column).moved(carry.where)
        gap = placed.distance(front)
        front_overlap = placed.intersect(front).Volume()
        foam_overlap = placed.intersect(foam).Volume()
        good = (plug.isValid() and len(plug.Solids()) == 1
                and gap >= minimum_gap - tolerance
                and front_overlap <= tolerance and foam_overlap <= tolerance)
        rows[name] = {
            "valid": plug.isValid(), "solids": len(plug.Solids()),
            "valve_support_gap_mm": gap,
            "valve_support_overlap_mm3": front_overlap,
            "foam_assembly_overlap_mm3": foam_overlap,
            "step_sha256": before[label(paths[f"plug_{name}"])],
            "passed": good,
        }
        print(f"{name}: front-top gap {gap:.6f} mm, front-top overlap "
              f"{front_overlap:.9f} mm³, foam overlap {foam_overlap:.9f} mm³", flush=True)

    after = {label(p): digest(p) for p in paths.values()}
    if before != after:
        raise RuntimeError("a STEP input changed during the reading; rerun after its build finishes")
    if source_hashes != {label(p): digest(p) for p in sources}:
        raise RuntimeError("a placement source changed during the reading; rerun after it settles")
    passed = front.isValid() and foam.isValid() and all(r["passed"] for r in rows.values())
    result = {
        "schema_version": 2,
        "reading_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "Both finished copper-plug STEPs against the finished front-top and foam "
                 "assembly, using production placement transforms. Other cold-core bodies, "
                 "routed tubing, print meshes and physical prints are outside this reading.",
        "nominal_cad_only": True,
        "minimum_front_top_clearance_mm": minimum_gap,
        "distance_tolerance_mm": tolerance,
        "overlap_tolerance_mm3": tolerance,
        "front_top_valid": front.isValid(), "foam_assembly_valid": foam.isValid(),
        "front_top_sha256": before[label(paths["front_top"])],
        "geometry_input_sha256": before,
        "placement_source_sha256": source_hashes,
        **rows,
        "passed": passed,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    temporary.write_text(json.dumps(result, indent=2) + "\n")
    temporary.replace(args.output)
    print(f"{'PASS' if passed else 'FAIL'}: {args.output}", flush=True)
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
