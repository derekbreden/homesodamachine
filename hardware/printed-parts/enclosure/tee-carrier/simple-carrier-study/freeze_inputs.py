"""Freeze measured-tee blank and fore-lap stock for the isolated design study.

This exports only into this study. The concept generator reads these native
inputs and never imports the evolving production carrier.
"""
import dataclasses
import hashlib
import json
from pathlib import Path
import sys

import cadquery as cq

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "NAMES.md").exists())
sys.path[:0] = [str(HERE.parent), str(ROOT / "hardware/printed-parts/cadlib")]
import tee_carrier as carrier


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    spec = carrier.DEFAULT_SPEC
    out = HERE / "inputs"
    blank = carrier._carrier_blank(spec).val()
    # Continue the lap into the left web but preserve actual tee/tie clearance.
    lap = carrier._box(-16, 10.35, spec.web_fore_y-6, spec.web_fore_y,
                       *spec.web_z)
    for cut in carrier._station_cutters(spec):
        lap = lap.cut(cut)
    for x in spec.tee_xs:
        lap=lap.cut(carrier._box(x-spec.trough_r,x+spec.trough_r,
                                spec.web_fore_y-6.1,spec.stub_relief_y,
                                spec.stub_relief_z0,spec.web_z[1]+.1))
    for site in carrier.tie_sites(spec):
        for x in site.slot_xs:
            lap = lap.cut(carrier._box(x-spec.tie_slot_x/2,
                                      x+spec.tie_slot_x/2,
                                      spec.web_fore_y-6.1, spec.web_aft_y+.1,
                                      site.band_z-spec.tie_slot_z/2,
                                      site.band_z+spec.tie_slot_z/2+.25))
    rows = {}
    for name, body in (("continuous-blank", blank), ("fore-lap", lap.val())):
        path = out / (name+".brep")
        cq.exporters.export(body, str(path))
        rows[name] = {"path": path.name, "sha256": sha(path),
                      "valid": body.isValid(), "solids": len(body.Solids()),
                      "volume_mm3": body.Volume()}
    data = {"status": "isolated_concept_inputs_not_print_release",
            "spec": dataclasses.asdict(spec), "interface": carrier.interface(spec),
            "files": rows, "source_sha256": {}}
    for path in (HERE.parent/"tee_carrier.py",
                 ROOT/"hardware/printed-parts/enclosure/enclosure/_enclosure_interface.py",
                 ROOT/"hardware/reference/tee-connector/tee_connector.py",
                 ROOT/"hardware/printed-parts/cadlib/fits.py", Path(__file__)):
        data["source_sha256"][str(path.relative_to(ROOT))] = sha(path)
    (out / "manifest.json").write_text(json.dumps(data, indent=2)+"\n")
    print(json.dumps(rows), flush=True)


if __name__ == "__main__":
    main()
