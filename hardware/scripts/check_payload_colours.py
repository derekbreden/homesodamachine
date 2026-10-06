#!/usr/bin/env python3
"""check_payload_colours.py — whether every body the site draws from a payload carries its colour.

    tools/cad-venv/bin/python hardware/scripts/check_payload_colours.py             (0 = carried, 1 = not)
    tools/cad-venv/bin/python hardware/scripts/check_payload_colours.py --selftest

A BODY IN A PAYLOAD IS THREE NUMBERS AND NOTHING ELSE. `web/public/js/viewer/step.js` builds its
material from the linear triple the `.step.mesh` header carries and finds its finish by matching
that triple, within 4e-4, against `web/public/finishes.json`. A body with no triple is drawn at the
viewer's pale default, and a body whose triple is no row is drawn at `DEFAULT_FINISH`. The page
reports neither; it draws them.

`check_finishes.py` holds the table to the constants and `check_step_colours.py` holds each STEP
to carrying some colour. This holds the payloads to the table, and fails on the two faults that
never mean anything but a broken pipeline:

  a body with no colour at all;
  a body whose colour is a finish row converted from sRGB to linear a second time. A constant is
  sRGB and a payload is linear; a reader that rebuilds a colour from XCAF or a payload already
  holds linear, and handing that to `cq.Color(r, g, b)` converts it again. What lands is darker,
  matches no row, and is exactly one conversion away from the constant it was — so this names it.

A colour the table names nowhere is counted and not failed: tooling and fixtures paint in colours
of their own, and those are drawn at `DEFAULT_FINISH` by design until a row names them.

THE BYTES READ ARE THE ONES THE POINTER FILE NAMES, which are the bytes the site serves. A payload
on this disk is read here when its sha256 is the one `hardware/cad-artifacts.json` states; any
other is read off the store by that hash, header only, because a publish can be cut from a tree
other than this one.
"""

import hashlib
import json
import struct
import sys
import urllib.request
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import _mesh_payload                                             # noqa: E402

ROOT = HERE.parents[1]
POINTERS = ROOT / "hardware" / "cad-artifacts.json"
TOL = 4e-4      # step.js squares this for FINISH_TOL2; `_finishes.find` takes the same radius
SHOWN = 6       # bodies named per payload and per fault; the count says how many more


def srgb_to_linear(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _nearest(rgb, table):
    """The `(triple, label)` of `table` within `TOL` of `rgb`, or None."""
    best, bestd = None, TOL * TOL
    for triple, label in table:
        d = sum((triple[i] - rgb[i]) ** 2 for i in range(3))
        if d <= bestd:
            best, bestd = (triple, label), d
    return best


def finish_table():
    """`[(linear triple, label)]` for every finish row, labelled by the constant that states it."""
    import _finishes
    import _materials as _mat
    import _routing
    names = {}
    for name, value in sorted(vars(_mat).items(), key=lambda kv: (not kv[0].startswith("M_"), kv[0])):
        if (name.startswith("M_") or name.startswith("C_")) and hasattr(value, "wrapped"):
            for rgb in (_mat.linear(value), _mat.linear(_mat.step_safe(value))):
                names.setdefault(rgb, name)
    for name in sorted(_routing.SPOOLS):
        raw = _routing.color(name)
        for rgb in (_mat.linear(raw), _mat.linear(_mat.step_safe(raw))):
            names.setdefault(rgb, f"spool {name}")
    rows = []
    for row in _finishes.rows():
        rgb = tuple(row["rgb"])
        rows.append((rgb, names.get(rgb, "(" + ", ".join(f"{c:.5f}" for c in rgb) + ")")))
    return rows


def classify(meshes, table, fallback="body"):
    """`{fault: [body]}` over a payload's meshes — `uncoloured`, `twice` (labelled with the row it
    was) and `unnamed` — with every body the table names left out."""
    doubled = [(tuple(srgb_to_linear(c) for c in rgb), label) for rgb, label in table]
    out = {"uncoloured": [], "twice": [], "unnamed": []}
    for m in meshes:
        name, color = m.get("name") or fallback, m.get("color")
        if not color:
            out["uncoloured"].append(name)
        elif _nearest(color, table):
            continue
        elif (hit := _nearest(color, doubled)):
            out["twice"].append(f"{name} ({hit[1]})")
        else:
            out["unnamed"].append(name)
    return out


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _stored_header(url: str) -> dict:
    """The JSON header of a gzipped payload on the store, inflating only as far as it reaches."""
    req = urllib.request.Request(url, headers={"User-Agent": "homesodamachine-checks"})
    inflate, buf, size = zlib.decompressobj(16 + zlib.MAX_WBITS), b"", None
    with urllib.request.urlopen(req, timeout=60) as resp:
        while True:
            chunk = resp.read(1 << 16)
            if not chunk:
                break
            buf += inflate.decompress(chunk)
            if size is None and len(buf) >= 4:
                size = struct.unpack("<I", buf[:4])[0]
            if size is not None and len(buf) >= 4 + size:
                return json.loads(buf[4:4 + size])
    raise ValueError("the object ends before its header does")


def published_header(rel: str, sha: str, store: dict):
    """`(header, where)` for the payload the pointer file names at `rel`."""
    local = ROOT / rel
    if local.is_file() and _sha256(local) == sha:
        return _mesh_payload.read_header(str(local)), "this disk"
    return _stored_header(f"{store['url']}{store['objects']}{sha}.gz"), "the store"


def main() -> int:
    pointers = json.loads(POINTERS.read_text())
    store = pointers.get("store") or pointers["release"]
    store = {"url": store["url"], "objects": store.get("objects", "s-")}
    payloads = sorted((rel, sha) for rel, sha in pointers["solids"].items()
                      if rel.endswith(".step.mesh"))
    table = finish_table()

    bodies, faults, unread, unnamed = 0, [], [], {}
    for rel, sha in payloads:
        try:
            header, where = published_header(rel, sha, store)
        except (OSError, ValueError) as exc:
            unread.append(f"{rel}: {exc}")
            continue
        if header.get("v") not in _mesh_payload.DECODABLE:
            continue        # the viewer reads the STEP for a version it does not decode
        meshes = header.get("meshes") or []
        bodies += len(meshes)
        found = classify(meshes, table, fallback=Path(rel).name.removesuffix(".step.mesh"))
        if found["unnamed"]:
            unnamed[rel] = len(found["unnamed"])
        if found["uncoloured"] or found["twice"]:
            faults.append((rel, sha, where, found))

    failing = sum(len(f["uncoloured"]) + len(f["twice"]) for _, _, _, f in faults)
    if failing:
        print(f"payload colours: {failing} of {bodies} bodies in {len(payloads)} published payload(s) "
              f"carry no colour or a colour converted twice")
    else:
        print(f"payload colours: all {bodies} bodies in {len(payloads)} published payload(s) carry a "
              f"colour, and none is converted twice")
    for rel, sha, where, found in faults:
        print(f"  {rel} (published {sha[:12]}, read from {where}):")
        for fault, says in (("uncoloured", "carry no colour, so the viewer draws them at its pale default"),
                            ("twice", "are a finish row converted from sRGB to linear a second time")):
            names = found[fault]
            if names:
                more = f", and {len(names) - SHOWN} more" if len(names) > SHOWN else ""
                print(f"    {len(names)} {says}: {', '.join(names[:SHOWN])}{more}")
    for line in unread:
        print(f"  could not read the published bytes of {line}")
    if unnamed:
        top = sorted(unnamed.items(), key=lambda kv: -kv[1])[:3]
        print(f"  {sum(unnamed.values())} body(ies) in {len(unnamed)} payload(s) carry a colour no "
              f"finish row names and draw at DEFAULT_FINISH, which is counted and not failed: "
              + ", ".join(f"{rel} ({n})" for rel, n in top)
              + (", ..." if len(unnamed) > len(top) else ""))
    if not faults and not unread:
        return 0
    print("  A payload colour is `_materials.linear` of the body's constant; a colour read back from "
          "XCAF or a payload is linear already, and is rebuilt with `cq.Color(r, g, b, a, False)`.")
    return 1


def selftest() -> int:
    table = [((0.0331, 0.0331, 0.0363), "M_PETGF_BLACK"), ((1.0, 1.0, 1.0), "spool water")]
    meshes = [
        {"name": "front-top", "color": [0.0331, 0.0331, 0.0363]},
        {"name": "white-tube", "color": [1.0, 1.0, 1.0]},
        {"name": "back-top", "color": [srgb_to_linear(0.0331), srgb_to_linear(0.0331),
                                       srgb_to_linear(0.0363)]},
        {"name": "funnel-frame", "color": None},
        {"name": "", "color": None},
        {"name": "countertop", "color": [0.26, 0.26, 0.30]},
    ]
    found = classify(meshes, table, fallback="spacer")
    ok = (found["uncoloured"] == ["funnel-frame", "spacer"]
          and found["twice"] == ["back-top (M_PETGF_BLACK)"]
          and found["unnamed"] == ["countertop"])
    print("payload colours selftest:", "passed" if ok else f"FAILED {found}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv else main())
