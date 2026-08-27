#!/usr/bin/env python3
"""Which solids the payload beside them does not stand for.

`loadStepFile` fetches `<file>.step.mesh` and parses the solid only where there is none
(`web/public/js/viewer/step.js`), and every picture this repository draws goes through that one
mount: `/3d` in a browser,
`tools/render/render-step-posed.js` for the assembly cards. On the enclosure the payload is
where the show surface is — `printed-parts/cadlib/flute_skin.py` cuts the flutes
into the printed mesh and `hardware/scripts/flute_payload.py` puts them into the payload at the
viewer's own deflection, and the solid beside them is a smooth prism of planes and cylinders. A
payload that is absent draws that prism; one older than the solid draws the surface the solid no
longer holds. The page reports neither: it draws, and what it draws is a part.

WHICH SOLIDS OWE ONE is `pack.py`'s `BUNDLED_PAYLOAD_DIRS` — the directories whose `.step.mesh`
goes into the bundle, so a solid under one is a solid a deploy is served a payload for. It is
imported, so the list a pack walks and the list read here are one list, and the walk is
`pack.solids`: this disk, which is what a pack reads, and not the lock the last one wrote. Every
other solid in the catalog is drawn from its STEP and owes nothing.

WHETHER A PAYLOAD STANDS FOR ITS SOLID IS READ OFF ITS BYTES AND NEVER OFF ITS MTIME. The
payload states `src`, the sha256 of the STEP it was cut from (`_mesh_payload.write`), and the
reading here is that digest against the solid's own bytes.

`src` RECORDS DESCENT AND NOT AGREEMENT. Under the directories above the payload carries surface
the solid does not — that is the whole reason it is bundled — so the two are unequal by design
and equality is not a thing there is to test. What the digest settles is which STEP's bytes the
payload answers to; `flute_payload` grafting flutes into one carries the host's own `src`
forward, because grafting a surface does not change which bytes it descends from.

An mtime test cannot answer this across a cache boundary: a restore stamps what it restores with the time it restored it, so a
stale payload arrives NEWER than the STEP just cut beside it, and the one ordering an mtime test
calls current is exactly the one where it is not.

A payload that states no `src`, or a version this repository no longer writes, is named too —
`decodeMeshPayload` reads the STEP for any version it does not know, so such a payload is one to
write again whether or not the solid's bytes have moved.

WHAT A GREEN READING SAYS. Per solid, one header read and one hash: the payload beside it names
these exact bytes. The triangles in it are still not read and not held against anything. And a
build hands the tree the payloads that are in a step's `outs`.
`enclosure.step.mesh`, `enclosure-assembly.step.mesh` and `manifold-layout.step.mesh` are in
none: they are written inside the sandbox and go with it, so `tools/bazel/sync_tree.py` carries
the solid into the tree and leaves the payload the tree had. A run of the generator on this disk
is what writes those three.

AND A SCENE IS READ FOR ITS FINISH. `pack.BUNDLED_GLB_DIRS` is the bundle's other half: the
assembly scenes, which `/3d` opens as `.glb` themselves, with no STEP under them to read instead.
A glTF material carries `baseColorFactor` and, beside it, `roughnessFactor` and `metallicFactor`
— and a material naming those two not at all is FULLY ROUGH METAL, because 1.0 and 1.0 are the
spec's defaults rather than an absence. So a scene composed without them opens with every body
the right colour and every one of them drawn as scratched metal.

`render_scenes._write_payload_glb` puts the pair on each material from `_finishes.py`. The
reading here is that pair, out of the file's own JSON chunk, against `web/public/finishes.json` —
the same table where the browser looks a finish up, matched on distance the way both of them
match it. `check_finishes.py` is what keeps the file and the module one table.

Naming them costs a stat each and one header read per scene. Writing one costs the generator's
run.
"""
import json
import struct
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]

# ONE WALK ANSWERS WHICH SOLIDS A BUNDLE CARRIES A PAYLOAD FOR and `pack.py` is where it lives.
# Its directory's hyphen keeps it out of a dotted import, so the path goes on `sys.path` and the
# module is imported by name — the way `tools/bazel/inventory.py` reaches the same walk.
sys.path.append(str(_ROOT / "tools" / "cad-artifacts"))
import pack  # noqa: E402

GRAPH = _ROOT / "tools" / "bazel" / "graph.json"
FINISHES = _ROOT / "web" / "public" / "finishes.json"
FINISHES_REL = "web/public/finishes.json"

sys.path.insert(0, str(_ROOT / "tools" / "bazel"))
from inventory import IMPLICIT_SOLIDS as _IMPLICIT_BY_GEN            # noqa: E402

#: The payloads named by hand because no trace can see them — flattened, since what matters
#: here is whether a path is produced and not which generator produces it.
_IMPLICIT = {p for paths in _IMPLICIT_BY_GEN.values() for p in paths}


def owed(root: Path) -> list:
    """Every solid the bundle carries a `.step.mesh` for, repo-relative and sorted."""
    dirs = tuple(f"{d}/" for d in pack.BUNDLED_PAYLOAD_DIRS)
    return [rel for rel in pack.solids(root)
            if rel.endswith(".step") and rel.startswith(dirs)]


# `_mesh_payload` owns this format, and its four header readers need nothing but `struct` and
# `json` — but the module imports OCP at its top, which this checker does not have and must not
# pay for. The read is repeated here against the version that module writes.
PAYLOAD_VERSION = 3

#: `_finishes.find`'s own tolerance and `render_scenes._VIEWER_DEFAULT_FINISH`, restated for the
#: same reason `PAYLOAD_VERSION` is: both live in modules that import OCP at their top. Near black
#: the linear palette is crowded enough that a byte holds two of its colours, so a finish is found
#: by distance; `tol` is a quarter of the closest gap between two materials in the table.
FINISH_TOL = 4e-4
VIEWER_FINISH = (0.6, 0.1)


def payload_header(path) -> dict:
    """An existing payload's header dict — u32 length, then that many bytes of JSON."""
    with open(path, "rb") as f:
        return json.loads(f.read(struct.unpack("<I", f.read(4))[0]))


def behind(root: Path) -> list:
    """Every owed solid whose payload is absent, unreadable, of a version the page does not
    decode, or cut from bytes the solid no longer holds, as (solid, which)."""
    out = []
    for rel in owed(root):
        mesh = root / (rel + ".mesh")
        if not mesh.exists():
            out.append((rel, "absent"))
            continue
        try:
            header = payload_header(mesh)
        except (OSError, ValueError, struct.error):
            out.append((rel, "not a payload"))
            continue
        if header.get("v") != PAYLOAD_VERSION:
            out.append((rel, "a payload version the page does not decode"))
            continue
        src = header.get("src")
        if src is None:
            out.append((rel, "states no source digest"))
            continue
        try:
            if src != pack._sha256(root / rel):
                out.append((rel, "cut from other bytes than the solid holds"))
        except OSError:
            continue
    return sorted(out)


def scenes(root: Path) -> list:
    """Every scene mesh the bundle carries, repo-relative and sorted."""
    dirs = tuple(f"{d}/" for d in pack.BUNDLED_GLB_DIRS)
    return [rel for rel in pack.solids(root)
            if rel.endswith(".glb") and rel.startswith(dirs)]


def gltf_tree(path) -> dict:
    """A binary glTF's JSON chunk — a 12-byte file header, then a u32 chunk length and the tag
    `JSON`, then that many bytes. Raises on a file that is not one."""
    with open(path, "rb") as f:
        head = f.read(20)
        if len(head) != 20 or head[:4] != b"glTF" or head[16:20] != b"JSON":
            raise ValueError("not a binary glTF")
        tree = json.loads(f.read(struct.unpack("<I", head[12:16])[0]))
    if not isinstance(tree, dict):
        raise ValueError("glTF JSON chunk is not an object")
    return tree


def finishes() -> list:
    """`(rgb, roughness, metalness)` for every material this tree states."""
    rows = json.loads(FINISHES.read_text(encoding="utf-8"))["finishes"]
    return [(tuple(r["rgb"]), r["roughness"], r["metalness"]) for r in rows]


def finish_for(table, rgb) -> tuple:
    """The finish stated at a linear triple, or the viewer's own default where this tree names no
    material there — which is the one case `web/public/js/viewer/step.js` cannot look up either."""
    best, held = VIEWER_FINISH, FINISH_TOL * FINISH_TOL
    for row, rough, metal in table:
        d = sum((row[i] - rgb[i]) ** 2 for i in range(3))
        if d <= held:
            best, held = (rough, metal), d
    return best


def _number(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def unfinished(material, table):
    """What one scene material is short of, or None where it carries the finish this tree states.

    A see-through body is held at metalness 0 whatever its stock says, which is where
    `_write_payload_glb` puts it: metalness and alpha do not compose."""
    pbr = material.get("pbrMetallicRoughness")
    if not isinstance(pbr, dict):
        return "a material with no pbrMetallicRoughness"
    rgba = pbr.get("baseColorFactor")
    if not isinstance(rgba, list) or len(rgba) != 4 or not all(_number(v) for v in rgba):
        return "a material with no base colour"
    rough, metal = pbr.get("roughnessFactor"), pbr.get("metallicFactor")
    if not _number(rough) or not _number(metal):
        return "a material naming no finish, which glTF draws as fully rough metal"
    want = finish_for(table, rgba[:3])
    if rgba[3] < 1.0:
        want = (want[0], 0.0)
    if (rough, metal) != want:
        return f"a material at {rough}/{metal} where this tree states {want[0]}/{want[1]}"
    return None


def flat(root: Path, table) -> list:
    """Every scene mesh the bundle carries whose materials are not the ones this tree states, as
    (scene, which)."""
    out = []
    for rel in scenes(root):
        try:
            tree = gltf_tree(root / rel)
        except (OSError, ValueError, struct.error):
            out.append((rel, "not a binary glTF"))
            continue
        materials = tree.get("materials")
        if not isinstance(materials, list) or not materials:
            out.append((rel, "carries no material at all"))
            continue
        which = None
        for material in materials:
            which = ("a material that is not an object" if not isinstance(material, dict)
                     else unfinished(material, table))
            if which:
                break
        if which:
            out.append((rel, which))
    return sorted(out)


def graph() -> dict:
    try:
        return json.loads(GRAPH.read_text())
    except (OSError, ValueError):
        return {}


def writers(seen: dict, path: str) -> list:
    """The generators a trace was watched writing `path`."""
    return sorted(gen for gen, step in seen.items() if path in step.get("writes", ()))


def undeclared(seen: dict, root: Path) -> list:
    """Every solid the bundle serves a payload for whose producer declares no payload.

    A PAYLOAD THE PAGE ASKS FOR AND NO RULE PRODUCES IS INVISIBLE UNTIL SOMEONE WATCHES THE
    NETWORK TAB. The sandbox writes what a rule's `outs` name and carries nothing else, so a
    producer that does not declare `<solid>.mesh` ships none, `/meshes/<solid>.mesh` answers
    404, and the page silently falls back to parsing the STEP — the right picture, seconds
    later, and under these directories not even the right picture.

    THE DECLARATION CANNOT BE LEARNED BY WATCHING. `trace_inputs._filtered` keeps a recorded
    write only where the path is already tracked, already in the graph, or named in
    `inventory.IMPLICIT_SOLIDS`; a `.step.mesh` is gitignored, so a payload absent from that
    table is discarded by the very trace that watched it being written. The table is the road
    in, and this is what says a solid has not taken it.

    A RULE PRODUCES WHAT EITHER SOURCE NAMES. `inventory` composes an action's outputs from the
    graph's writes AND that table, so both are asked here — a payload named in the table alone
    is produced, and the trace catching up later changes nothing about that."""
    out = []
    for rel in owed(root):
        mesh = rel + ".mesh"
        if not writers(seen, mesh) and mesh not in _IMPLICIT:
            out.append((rel, sorted(writers(seen, rel))))
    return out


def flute_dirs(seen: dict) -> tuple:
    """The directories `flute_payload.py` declares a payload in."""
    written = seen.get("hardware/scripts/flute_payload.py", {}).get("writes", ())
    return tuple(sorted({f"{Path(p).parent.as_posix()}/"
                         for p in written if p.endswith(".step.mesh")}))


def selftest() -> int:
    import tempfile
    import os

    holds = 0

    def hold(label, got, want):
        nonlocal holds
        ok = got == want
        holds += ok
        print(f"  {'✓' if ok else '✗'} {label}" + ("" if ok else f" — {got!r} != {want!r}"))

    # A REAL PAYLOAD DIRECTORY AND A REAL SOLID DIRECTORY, because the rule under test is which
    # of the two owes a payload, and `pack.BUNDLED_PAYLOAD_DIRS` is what answers.
    payload_dir = pack.BUNDLED_PAYLOAD_DIRS[0]
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        here = root / payload_dir
        here.mkdir(parents=True)
        elsewhere = root / "hardware" / "printed-parts" / "cap"
        elsewhere.mkdir(parents=True)
        def payload(path, src, v=PAYLOAD_VERSION):
            """A payload carrying just the header this checker reads."""
            head = json.dumps({"v": v, "src": src}).encode()
            path.write_bytes(struct.pack("<I", len(head)) + head)

        (here / "a.step").write_text("x")
        solid_x = pack._sha256(here / "a.step")
        payload(here / "a.step.mesh", solid_x)
        (elsewhere / "cap.step").write_text("x")

        hold("only a solid in a payload directory owes one",
             owed(root), [f"{payload_dir}/a.step"])

        hold("a payload cut from these bytes is not named", behind(root), [])

        # THE READING THAT AN MTIME TEST GETS BACKWARDS. A cache restore stamps a stale payload
        # with the time it restored it, so it lands newer than the STEP cut beside it.
        os.utime(here / "a.step", ns=(1_000_000_000_000_000_000,) * 2)
        os.utime(here / "a.step.mesh", ns=(9_000_000_000_000_000_000,) * 2)
        hold("mtime alone does not make a payload current", behind(root), [])

        (here / "a.step").write_text("moved")
        hold("a payload cut from other bytes is named", behind(root),
             [(f"{payload_dir}/a.step", "cut from other bytes than the solid holds")])

        payload(here / "a.step.mesh", pack._sha256(here / "a.step"), v=PAYLOAD_VERSION - 1)
        hold("a payload of a version the page does not decode is named", behind(root),
             [(f"{payload_dir}/a.step", "a payload version the page does not decode")])

        (here / "a.step.mesh").write_bytes(b"m")
        hold("a file that is not a payload is named", behind(root),
             [(f"{payload_dir}/a.step", "not a payload")])

        (here / "a.step.mesh").unlink()
        hold("a solid with no payload at all is named", behind(root),
             [(f"{payload_dir}/a.step", "absent")])

        payload(elsewhere / "cap.step.mesh", "0" * 64)
        hold("a solid outside a payload directory is never named",
             [rel for rel, _ in behind(root)], [f"{payload_dir}/a.step"])

    # AND THE SCENE HALF, AGAINST A TABLE THIS BLOCK STATES rather than the tree's. What is under
    # test is the reading, not which materials this machine happens to be made of.
    scene_dir = pack.BUNDLED_GLB_DIRS[0]
    table = [((0.1, 0.2, 0.3), 0.35, 0.0), ((0.5, 0.5, 0.5), 0.05, 1.0)]
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        here = root / scene_dir
        here.mkdir(parents=True)
        elsewhere = root / "hardware" / "pcb" / "board"
        elsewhere.mkdir(parents=True)

        def glb(path, materials):
            """A binary glTF carrying just the JSON chunk this checker reads."""
            body = json.dumps({"asset": {"version": "2.0"}, "materials": materials}).encode()
            body += b" " * (-len(body) % 4)
            path.write_bytes(struct.pack("<4sII", b"glTF", 2, 20 + len(body))
                             + struct.pack("<I4s", len(body), b"JSON") + body)

        def material(rgba, **pbr):
            return {"pbrMetallicRoughness": {"baseColorFactor": list(rgba), **pbr}}

        matte = material((0.1, 0.2, 0.3, 1.0), roughnessFactor=0.35, metallicFactor=0.0)
        glb(here / "one.glb", [matte])
        glb(elsewhere / "board.glb", [material((0.1, 0.2, 0.3, 1.0))])

        hold("only a mesh in a scene directory is read", scenes(root), [f"{scene_dir}/one.glb"])

        hold("a scene whose materials are this tree's finishes is not named",
             flat(root, table), [])

        glb(here / "one.glb", [material((0.1, 0.2, 0.3, 1.0))])
        hold("a material naming no finish is named", flat(root, table),
             [(f"{scene_dir}/one.glb",
               "a material naming no finish, which glTF draws as fully rough metal")])

        glb(here / "one.glb", [matte, material((0.5, 0.5, 0.5, 1.0),
                                               roughnessFactor=0.6, metallicFactor=1.0)])
        hold("a material at another finish than the table states is named",
             flat(root, table), [(f"{scene_dir}/one.glb",
                                  "a material at 0.6/1.0 where this tree states 0.05/1.0")])

        # A COLOUR THE TABLE DOES NOT NAME IS NOT A FAILURE. It takes the viewer's own default,
        # which is what `step.js` draws it at, so both renderers agree on the one case neither
        # of them can look up.
        glb(here / "one.glb", [material((0.9, 0.1, 0.4, 1.0),
                                        roughnessFactor=VIEWER_FINISH[0],
                                        metallicFactor=VIEWER_FINISH[1])])
        hold("a colour the table does not name takes the viewer's own default",
             flat(root, table), [])

        # Metalness and alpha do not compose, so a see-through body is held at 0 whatever the
        # table states for its colour — here, a mirror-bright metal seen through.
        glb(here / "one.glb", [material((0.5, 0.5, 0.5, 0.35),
                                        roughnessFactor=0.05, metallicFactor=0.0)])
        hold("a see-through body is held nonmetallic at its own roughness",
             flat(root, table), [])
        glb(here / "one.glb", [material((0.5, 0.5, 0.5, 0.35),
                                        roughnessFactor=0.05, metallicFactor=1.0)])
        hold("a see-through body carrying its stock's metal is named",
             flat(root, table), [(f"{scene_dir}/one.glb",
                                  "a material at 0.05/1.0 where this tree states 0.05/0.0")])

        glb(here / "one.glb", [])
        hold("a scene with no material at all is named", flat(root, table),
             [(f"{scene_dir}/one.glb", "carries no material at all")])

        (here / "one.glb").write_bytes(b"not a gltf at all")
        hold("a file that is not a binary glTF is named", flat(root, table),
             [(f"{scene_dir}/one.glb", "not a binary glTF")])

    print(f"check_payloads selftest {holds}/17")
    return 0 if holds == 17 else 1


def main(argv) -> int:
    if argv and argv[0] == "selftest":
        return selftest()
    seen = graph()
    missing = undeclared(seen, _ROOT)
    if missing:
        print(f"{len(missing)} solid(s) the bundle serves a payload for that no rule produces:")
        for rel, cut_by in missing:
            print(f"    {rel}.mesh — declared by nobody")
            for gen in cut_by:
                print(f"      name it in tools/bazel/inventory.py IMPLICIT_SOLIDS under {gen},")
                print(f"      re-run tools/bazel/trace_inputs.py {gen}, then gen_build.py")
        return 1

    named = behind(_ROOT)
    if named:
        print(f"{len(named)} solid(s) whose surface is not in the payload beside them:")
        for rel, which in named:
            print(f"    {rel}.mesh — {which}")
        cut_by = sorted({gen for rel, _ in named for gen in writers(seen, rel)})
        if cut_by:
            print("  the run that cuts a solid writes the payload beside it:")
            for gen in cut_by:
                print(f"    tools/cad-venv/bin/python {gen}")
        flutes = flute_dirs(seen)
        if flutes and any(rel.startswith(flutes) for rel, _ in named):
            print("  and the enclosure's flutes go back into those payloads after:")
            print("    tools/cad-venv/bin/python hardware/scripts/flute_payload.py")
        return 1

    try:
        table = finishes()
    except (OSError, ValueError, KeyError, TypeError):
        print(f"{FINISHES_REL} is not a finish table this reading can take.")
        print("  fix: tools/cad-venv/bin/python hardware/scripts/check_finishes.py --write")
        return 1
    plain = flat(_ROOT, table)
    if plain:
        print(f"{len(plain)} scene(s) whose materials are not the finishes this tree states:")
        for rel, which in plain:
            print(f"    {rel} — {which}")
        print("  the run that composes a scene writes its materials:")
        print("    tools/cad-venv/bin/python hardware/assembly/scenes/render_scenes.py")
        return 1
    print(f"payloads: {len(owed(_ROOT))} solid(s) cut from the bytes beside them, "
          f"{len(scenes(_ROOT))} scene(s) at the finishes this tree states")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
