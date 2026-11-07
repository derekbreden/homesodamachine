#!/usr/bin/env python3
"""Run each generator once and write down every file it read and every file it wrote.

    tools/cad-venv/bin/python tools/bazel/trace_inputs.py <gen.py>   # the ones a change reached
    tools/cad-venv/bin/python tools/bazel/trace_inputs.py --all      # every one, over an hour

An audit hook watches the run, which happens the way the generator's own `__main__` runs. Every
path under this repo it opens is kept, on the side its mode names — reads on one, writes on the
other, and an atomic write on the rename that lands it. The answer is `graph.json`, which
`inventory.py` and `gen_build.py` both read.

OCCT READS A STEP BELOW PYTHON, where no audit hook reaches. `_cadq_export.import_step` is the
one loader and keeps the list; this takes it at the end of the run, so a generator that cuts no
solid of its own still names the ones it stood the machine off.

A WRITE THAT LANDS ON THE BYTES ALREADY THERE PERFORMS NO WRITE. Atomic geometry and document
exports skip the rename, and `docgen` skips the `write_text`. Their `_WRITE_TARGETS` registries
keep the target even when its bytes stay in place.

A generator that raises is traced to where it stopped. What it read is what it read; what it
had not yet written is absent from its outputs, and the copy at the end of its action finds
nothing there.

A RUST STEP IS A PROGRAM, NOT A SCRIPT. `RUST_STEPS` names each by the source of its `main`. Its
trace compiles the program, runs it into an empty directory with the kernel naming every file
it reads (`HSM_READS`), and carries what landed there into the tree. Its entry's `program` holds
what cargo compiled into it and the manifests that chose those crates; `gen_build.py` compiles
the program in a rule of its own from them, ahead of the rule that runs it.
"""

import argparse
import hashlib
import json
import os
import runpy
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve()
_ROOT = _HERE.parents[2]
GRAPH = _HERE.parent / "graph.json"

sys.path.insert(0, str(_HERE.parent))
from inventory import (  # noqa: E402
    IMPLICIT_SOLIDS,
    build_inert,
    tracked as _inventory_tracked,
)

RUNNER = r'''
import json, os, sys, runpy
ROOT = %r
GEN = %r
OUT = %r
ARGV = %r
read, wrote, scanned, pieced = set(), set(), set(), set()

def _under(path):
    try:
        p = os.path.abspath(os.fspath(path))
    except (TypeError, ValueError):
        return None
    return os.path.relpath(p, ROOT) if p.startswith(ROOT + os.sep) else None

def _keep(into, path):
    rel = _under(path)
    if rel is not None:
        into.add(rel)

# THE WRITE MACHINERY LOOKS AT ITS OWN DESTINATION, and neither look is a build input.
# `_cadq_export._sweep_orphan_temps` globs the target's directory to unlink the temps a
# SIGKILLed build left behind, and `_matches_existing_target` compares the target's bytes to
# decide whether the rename is a no-op. A glob scans and a compare opens, so untold apart they
# both arrive as reading — and the scan is the expensive half, because every file a scanned
# directory holds is taken below as read. A generator would read the solid it writes, its own
# thumbnail, the README beside it, and the sibling assembly shelved in the same folder.
WRITE_MACHINERY = ("_sweep_orphan_temps", "_matches_existing_target")

# A PIECE FINDER LISTS A FOLDER TO PICK THE PIECES IT THEN OPENS. `flute_payload.pieces` globs
# each printed-part folder for a `*.step` with an `.stl` beside it, and `flute_payload.payloads`
# for the `*.step.mesh` a graft lands in; the solid and payload of every piece kept are opened,
# and read, in their own right. The rest of the folder — its README, its print log, the records
# filed beside the part — is nothing a piece is cut from.
#
# BUT THE MESH BESIDE THE SOLID IS NEVER OPENED, and it is what makes the solid a piece: the
# finder only asks whether it stands there. An action without it finds no piece, and grafts
# nothing, or dies on the name it expected. So a finder's folder is kept apart, and read below
# for the `.stl` beside each `.step` it holds.
PIECE_FINDERS = ("pieces", "payloads")

def _on_stack(names, module):
    """Whether a function `names` holds, defined in `module`, is what reached the disk here.

    The call lands under `glob` or `filecmp`, so the frame that raised the event never names
    the one that meant it — the stack is walked to find it. Bounded, because each sits within
    a few frames of the call it makes, and entered only for a path inside this tree.
    """
    try:
        f = sys._getframe(1)
    except ValueError:
        return False
    for _ in range(10):
        if f is None:
            return False
        code = f.f_code
        if code.co_name in names and code.co_filename.endswith(module):
            return True
        f = f.f_back
    return False

def _by_write_machinery():
    """Whether atomic export bookkeeping is what reached the disk here."""
    return any(_on_stack(WRITE_MACHINERY, module)
               for module in ("_cadq_export.py", "_document_export.py"))

def _hook(event, args):
    # `open` is most of it, and its mode says which side of the edge it is. `import` is the
    # rest of the reading: a module loaded by path through importlib is read by the loader,
    # not by open().
    if event == "open" and args and isinstance(args[0], (str, bytes, os.PathLike)):
        mode = args[1] if len(args) > 1 and isinstance(args[1], str) else "r"
        if set(mode) & set("wxa+"):
            _keep(wrote, args[0])
        elif _under(args[0]) is not None and not _by_write_machinery():
            _keep(read, args[0])
    # AN ATOMIC WRITE LANDS AS A RENAME. `_cadq_export._atomic_write` writes a sibling temp
    # and moves it over the target, so the name the tree carries is never opened for writing.
    elif event in ("os.rename", "os.replace") and len(args) > 1:
        _keep(wrote, args[1])
    # A tool opens its script outside Python's sight: a file named on a subprocess's command
    # line, such as a script handed to Blender, is read.
    elif event == "subprocess.Popen" and len(args) > 1:
        for a in (args[1] or ()):
            try:
                if os.path.isfile(os.fspath(a)):
                    _keep(read, a)
            except (TypeError, ValueError):
                pass
    # A DIRECTORY THIS RUN GLOBS names its files without opening one, and which files stand
    # there is part of what the run read: `flute_payload.pieces` takes each `*.step` in a piece
    # folder that has an `.stl` beside it.
    #
    # A DIRECTORY THE IMPORT MACHINERY SCANS IS NOT ONE THIS RUN GLOBBED. Python lists every
    # `sys.path` entry to find the module it is about to load, and a scan's files are read
    # below — so every entry a generator inserts would arrive as files it never opened:
    # `tools/` for `docgen`, `hardware/scripts/` for the shared machinery, and the run's own
    # directory, which for a doc sync is `hardware/assembly/`. What an import reads is the
    # module, which the `import` event below names outright, and `exec` names the ones loaded
    # by path.
    #
    # TWO PARTS OF THAT MACHINERY WALK `sys.path` AND THEY DO NOT LOOK ALIKE FROM HERE. The
    # finder runs frozen, so its frame is `<frozen importlib._bootstrap_external>`; the
    # `importlib.metadata` a package's version lookup reaches runs from a real file. Both are
    # the import system looking along the path, and a `Path.glob` of a content directory is
    # neither — its frame is `glob.py`.
    elif event in ("os.scandir", "os.listdir") and args and args[0]:
        try:
            by = sys._getframe(1).f_code.co_filename
        except ValueError:
            by = ""
        if not (by.startswith("<frozen importlib") or "/importlib/" in by) \
                and not _by_write_machinery():
            if _on_stack(PIECE_FINDERS, "flute_payload.py"):
                _keep(pieced, args[0])
            else:
                _keep(scanned, args[0])
    elif event == "import" and len(args) > 1 and args[1]:
        _keep(read, args[1])
    elif event == "exec" and args:
        code = getattr(args[0], "co_filename", None)
        if code:
            _keep(read, code)

sys.addaudithook(_hook)
sys.argv = [GEN, *ARGV]
sys.path.insert(0, os.path.dirname(os.path.join(ROOT, GEN)))
raised = None
try:
    runpy.run_path(os.path.join(ROOT, GEN), run_name="__main__")
except SystemExit as exc:
    if exc.code not in (None, 0):
        raised = f"SystemExit({exc.code!r})"
        print(f"  (raised {raised}; keeping what it read)", file=sys.stderr)
except BaseException as exc:
    raised = type(exc).__name__
    print(f"  (raised {raised}; keeping what it read)", file=sys.stderr)
finally:
    # THE SOLIDS OCCT OPENED BELOW PYTHON. `import_step` is the one loader and keeps the list;
    # a generator that cuts nothing of its own has no stamp to carry it, so it is taken here.
    mod = sys.modules.get("_cadq_export")
    read |= set(getattr(mod, "_STEP_READS", ())) | set(getattr(mod, "_READ_TARGETS", ()))
    # AND A PART THE RUST KERNEL CUTS IS COMPILED AND RUN BELOW PYTHON. `_rust_part` keeps the
    # sources cargo compiled into its program and the files the program wrote.
    rust = sys.modules.get("_rust_part")
    read |= set(getattr(rust, "_READ_TARGETS", ()))
    wrote |= set(getattr(rust, "_WRITE_TARGETS", ()))
    # A FILE IS CUT WHOLE OR REWRITTEN IN PLACE, and the module that wrote it is the one that
    # knows which. `_cadq_export` draws a solid from nothing; `docgen` reads a
    # doc, replaces the values it manages, and writes the rest of it back. A file of
    # the second kind belongs on both sides of its own action, and no suffix says so —
    # `.figures.json` carries no marker and is rewritten; a `.step` is read to be compared
    # against and is not.
    back = set()
    for mod in ("docgen",):
        back |= set(getattr(sys.modules.get(mod), "_WRITE_TARGETS", ()))
    wrote |= back
    for mod in ("_cadq_export", "_document_export"):
        wrote |= set(getattr(sys.modules.get(mod), "_WRITE_TARGETS", ()))
    with open(OUT, "w") as fh:
        json.dump({"reads": sorted(read), "writes": sorted(wrote),
                   "rewritten": sorted(back), "scanned": sorted(scanned),
                   "pieced": sorted(pieced),
                   "raised": raised}, fh)
'''


def _graph_writes(path=GRAPH) -> set:
    """Every output the existing graph declares, including ignored action intermediates."""
    try:
        graph = json.loads(Path(path).read_text())
    except (OSError, ValueError):
        return set()
    return {
        f for seen in graph.values() for f in seen.get("writes", ())
        if not build_inert(f)
    }


def _tracked(path=GRAPH, base=None) -> set:
    """Every file this tree stands behind: tracked inputs, pointed-at solids and declared outputs.

    A GENERATED SOLID IS IN NO INDEX AND A GENERATOR STILL OPENS IT. `_pump_replacement_sync`
    loads `kamoer-kphm400.step` through `manifold_layout.build_pump`. A trace filtered by
    `git ls-files` drops that read, the graph stops naming it, and the action built from the
    graph holds no such file and dies on `STEP File could not be loaded` — a generator that
    runs by hand and cannot run in the sandbox.

    AN ACTION INTERMEDIATE CAN BE IGNORED TOO. Its producer's prior `writes` declaration is the
    durable name: retaining graph writes here lets the next producer trace keep the write and
    the next consumer trace keep the read, rather than erasing both sides merely because the
    handoff is intentionally absent from git. `inventory.inventory` admits these same graph
    writes when it composes actions, so tracing and action construction share the boundary."""
    implicit = {f for paths in IMPLICIT_SOLIDS.values() for f in paths}
    files = set(_inventory_tracked() if base is None else base) | _graph_writes(path) | implicit
    return {path for path in files if not build_inert(path)}


def _filtered(seen: dict, files: set) -> dict:
    """The recorded sides after paths outside the declared tree are removed."""
    return {side: {p for p in seen.get(side, ()) if p in files and not build_inert(p)}
            for side in ("reads", "writes", "rewritten")}


#: HOW LONG ONE READING MAY TAKE. The runner stands the appliance in 36-45 minutes where this
#: Mac takes a few, and a step that stands it in-process — the installed machine — needs the
#: hour there. A run that outlives this comes back the way a
#: killed one does, with no reading, and the sweep keeps the entry it had; it never stops
#: the sweep. `derive.yml`'s `trace=all` dispatch budgets for these on top of the build.
DEADLINE = 3600


def trace(gen: str, files: set, argv=()) -> dict:
    """Every tracked file `gen` read and every one it wrote, plus the solids OCCT loaded."""
    out = Path(os.environ.get("TMPDIR", "/tmp")) / f"hsm-trace-{Path(gen).stem}.json"
    # A READING LEFT BY AN EARLIER RUN IS NOT THIS ONE'S. The runner writes `out` in its own
    # `finally`, so a run killed at the deadline leaves nothing — unless the file a previous
    # trace of the same generator wrote is still there to be read as if it were.
    out.unlink(missing_ok=True)
    # ONE GENERATOR AT A TIME IS WHAT THIS ALREADY DOES, so each run takes the global lock
    # the way a hand run does. Two traces on one machine are two pileups otherwise, and the
    # lock is what everything outside `bazel` shares.
    #
    # AND NEVER FOLLOWS SOMEBODY ELSE'S. `_run_lock` attaches a second run of the same script
    # to the one already going and hands back ITS exit status, so the generator's own `main`
    # never runs and the trace watches a process that opened nothing. A reading needs the run
    # to happen, so this one asks for the lock and refuses the shortcut.
    #
    # A TRACE WATCHES THE RUN A BUILD MAKES. What it hands the generator is what the generator
    # would have had anyway, bar the two the lock reads above — a flag that turned work off
    # here would be a reading of a shorter run than the one an action performs, and the graph
    # would name less than the sandbox has to hold.
    #
    # SO IT TAKES NO ANSWER THAT SKIPS THE READING. A run the `hsm` engine kept, or a result
    # the realized cache holds, comes back without opening what decided it, and an action on a
    # cold engine opens all of it. With both turned off the traced run does all of that work
    # itself, so what it reads is what any action can need.
    env = dict(os.environ, HSM_BUILD_SOURCE="trace", HSM_NO_BUILD_ATTACH="1",
               HSM_NO_ENGINE="1", HSM_NO_REALIZED_CACHE="1")
    sys.path.insert(0, str(_ROOT / 'hardware/scripts'))
    import _run_slots
    try:
        subprocess.run([sys.executable, "-c",
                        RUNNER % (str(_ROOT), gen, str(out), tuple(argv))],
                       cwd=str(_ROOT), capture_output=True, text=True,
                       **_run_slots.subprocess_kwargs(env),
                       timeout=DEADLINE)
    except subprocess.TimeoutExpired:
        # Killed at the deadline, and `finally` never ran: the reading is that it did not
        # finish, which the loop below files beside a generator that raised.
        return {"reads": [], "writes": [], "raised": f"TimeoutExpired after {DEADLINE} s"}
    try:
        seen = json.loads(out.read_text())
    except (OSError, ValueError):
        # The runner left no reading: killed, or stopped before its own `finally`.
        return {"reads": [], "writes": [], "raised": "no reading"}
    out = _filtered(seen, files)
    # A WORKER'S VENDORED CRATES. `_rust_part.program` names what cargo's dep-info lists, and
    # the dep-info names none of a vendored crate's files, so a run that found its programs
    # fresh would name none of what compiling them reads.
    manifests = [_ROOT / r for r in out["reads"]
                 if r.startswith("tools/hsm/") and r.endswith("/Cargo.toml") and r.count("/") == 3]
    if manifests:
        out["reads"] |= _vendored(_crates_of(manifests), files)
    # A SCANNED DIRECTORY IS READ FOR ITS OWN ENTRIES. A listing names the files standing in
    # that folder and nothing in the folders beneath it: `flute_payload` globs
    # `enclosure/enclosure/*.step`, and the print records filed under it are not what the
    # appliance is cut from. A walk scans each directory it enters, so a reader that descends
    # still has every level counted.
    here = set(seen.get("scanned", ()))
    if here:
        out["reads"] |= {f for f in files if os.path.dirname(f) in here}
    # A PIECE FINDER'S FOLDER IS READ FOR THE MESH BESIDE EACH SOLID, the one file it asks
    # after without opening (`PIECE_FINDERS` in the runner).
    pieced = set(seen.get("pieced", ()))
    if pieced:
        # The published inventory also names pieces absent from this checkout.
        # A directory finder can select only the STEP/STL pairs actually present.
        out["reads"] |= {f for f in files if f.endswith(".stl")
                         and os.path.dirname(f) in pieced and f[:-4] + ".step" in files
                         and (_ROOT / f).is_file()
                         and (_ROOT / (f[:-4] + ".step")).is_file()}
    answer = {k: sorted(v) for k, v in out.items()}
    if seen.get("raised"):
        answer["raised"] = seen["raised"]
    return answer


#: WHAT THE MAIN BOARD READS IS NOT IN THIS REPO. `hardware/pcb/pcba/package.json` pins seven
#: `@tscircuit/*` packages to commits of `github:derekbreden/*`, resolved at install from
#: outside the tree, and `board-3d.py` runs `tsci` through them. An action cannot hold what
#: it reads, so the main board is built by `bun render-board.ts` and its GLB carried by the hook.
#: Vendoring the forks is what would let it join the graph.
#:
#: A CHECK IS NOT A STEP. It runs when someone asks the question it answers (CLAUDE.md, "What
#: Runs Every Time"), so these are run by hand and their records commit like any other file.
ELSEWHERE = ("tools/", "hardware/pcb/pcba/",
             'hardware/printed-parts/enclosure/asse-drip-pan/',  # retained historical study geometry
             'hardware/printed-parts/enclosure/display-cover/reach-trial/',  # retained historical study geometry
             'hardware/printed-parts/enclosure/display-cover/receiver-trial/',  # retained historical study geometry
             'hardware/printed-parts/enclosure/display-cover/retention-reach-trial/',  # retained historical study geometry
             'hardware/printed-parts/enclosure/display-cover/retention-trial/',  # retained historical study geometry
             'hardware/printed-parts/fixtures/faucet-cover-retention/',  # retained historical study geometry
             'hardware/printed-parts/fixtures/faucet-display-snap/',  # retained historical study geometry
             'hardware/printed-parts/fixtures/valve-socket-fit/',  # retained historical study geometry
             'hardware/printed-parts/zone-c/funnel/cradle-trial/',  # retained historical study geometry
             "hardware/assembly/scenes/render_scenes.py",
             "hardware/manifold-layout/enclosure_assembly.py",  # the old machine pipeline; hand-run tools import it
             "hardware/scripts/flute_payload.py",  # payload cutting for hand-run tools; each piece's program cuts its own
             "hardware/scripts/check_faucet_geometry.py",
             "hardware/printed-parts/enclosure/pump-dock/print-preparation/",
             "hardware/printed-parts/enclosure/enclosure/heat-set-review/print_regions.py",
             "hardware/printed-parts/faucet/lever-replica/check_replica.py")


#: THE RUST STEPS, by the source of each program's `main`: the crate under `tools/hsm` whose
#: `[[bin]]` it is, the program's name, and the directory it writes into when given none. A
#: program that writes into several directories writes each file at its path from the root, "".
RUST_STEPS = {
    "hardware/printed-parts/enclosure/enclosure/enclosure.rs":
        ("enclosure", "enclosure", "hardware/printed-parts/enclosure/enclosure"),
    "hardware/printed-parts/enclosure/enclosure/enclosure_back_bottom.rs":
        ("enclosure-back-bottom", "enclosure-back-bottom", "hardware/printed-parts/enclosure/enclosure"),
    "hardware/printed-parts/enclosure/enclosure/enclosure_back_top.rs":
        ("enclosure-back-top", "enclosure-back-top", "hardware/printed-parts/enclosure/enclosure"),
    "hardware/printed-parts/enclosure/enclosure/enclosure_front_bottom.rs":
        ("enclosure-front-bottom", "enclosure-front-bottom", "hardware/printed-parts/enclosure/enclosure"),
    "hardware/printed-parts/enclosure/enclosure/enclosure_front_top.rs":
        ("enclosure-front-top", "enclosure-front-top", "hardware/printed-parts/enclosure/enclosure"),
    "hardware/printed-parts/enclosure/enclosure/enclosure_pump_retainer.rs":
        ("enclosure-pump-retainer", "enclosure-pump-retainer", "hardware/printed-parts/enclosure/enclosure"),
    "hardware/printed-parts/enclosure/enclosure/enclosure_pump_tube_setting_jig.rs":
        ("enclosure-pump-tube-setting-jig", "enclosure-pump-tube-setting-jig", "hardware/printed-parts/enclosure/enclosure"),
    "hardware/cut-parts/carbonation/endcaps-circular/endcap_circular_step.rs":
        ("endcap-circular", "endcap-circular-step", "hardware/cut-parts/carbonation/endcaps-circular"),
    "hardware/manifold-layout/installed_machine.rs":
        ("installed-machine", "installed-machine", ""),
    "hardware/install-guide/kit_art.rs": ("kit-art", "kit-art", ""),
    "hardware/install-guide/opening_scene.rs": ("opening-scene", "opening-scene", ""),
    "hardware/install-guide/install_guide.rs": ("install-guide", "install-guide", ""),
    "hardware/printed-parts/refrigeration/fuse-clamp/fuse_clamp.rs": ("fuse-clamp", "fuse-clamp", "hardware/printed-parts/refrigeration/fuse-clamp"),
    "hardware/printed-parts/fixtures/weld-rotator/weld_rotator.rs": ("weld-rotator", "weld-rotator", "hardware/printed-parts/fixtures/weld-rotator"),
    "hardware/printed-parts/electronics/pcba-tray/pcba_assembly.rs": ("pcba-assembly", "pcba-assembly", "hardware/printed-parts/electronics/pcba-tray"),
    "hardware/printed-parts/soda-bend-holder/soda_bend_holder.rs": ("soda-bend-holder", "soda-bend-holder", "hardware/printed-parts/soda-bend-holder"),
    "hardware/printed-parts/diaphragm-pump-sleeve/diaphragm_pump_sleeve.rs": ("diaphragm-pump-sleeve", "diaphragm-pump-sleeve", "hardware/printed-parts/diaphragm-pump-sleeve"),
    "hardware/printed-parts/fixtures/tube-miter-box/tube_miter_box.rs": ("tube-miter-box", "tube-miter-box", "hardware/printed-parts/fixtures/tube-miter-box"),
    "hardware/printed-parts/fixtures/fake-countertop/fake_countertop.rs": ("fake-countertop", "fake-countertop", "hardware/printed-parts/fixtures/fake-countertop"),
    "hardware/printed-parts/collet-press/collet_press.rs": ("collet-press", "collet-press", "hardware/printed-parts/collet-press"),
    "hardware/printed-parts/asse-straight-cuffs/asse_straight_cuffs.rs": ("asse-straight-cuffs", "asse-straight-cuffs", "hardware/printed-parts/asse-straight-cuffs"),
    "hardware/printed-parts/asse-drain-adapter/asse_drain_adapter.rs": ("asse-drain-adapter", "asse-drain-adapter", "hardware/printed-parts/asse-drain-adapter"),
    "hardware/printed-parts/cold-core/prv-shroud/prv_shroud.rs":
        ("prv-shroud", "prv-shroud", "hardware/printed-parts/cold-core/prv-shroud"),
    "hardware/ledger/purchases.rs": ("ledger", "purchases", ""),
    "hardware/printed-parts/enclosure/display-cover/display_cover.rs":
        ("enclosure-components", "display-cover", "hardware/printed-parts/enclosure/display-cover"),
    "hardware/printed-parts/enclosure/display-gasket/display_gasket.rs":
        ("enclosure-components", "display-gasket", "hardware/printed-parts/enclosure/display-gasket"),
    "hardware/printed-parts/enclosure/rear-identification/rear_identification.rs":
        ("enclosure-components", "rear-identification", "hardware/printed-parts/enclosure/rear-identification"),
    "hardware/printed-parts/enclosure/nameplate/nameplate.rs":
        ("enclosure-components", "nameplate", "hardware/printed-parts/enclosure/nameplate"),
    "hardware/ledger/bom.rs": ("bom", "bom", ""),
    "hardware/ledger/machine_time.rs": ("ledger", "machine-time", ""),
    "hardware/manifold-layout/manifold_layout.rs":
        ("manifold-layout", "manifold-layout", "hardware/manifold-layout"),
    "hardware/printed-parts/enclosure/rear-equipment-caps/rear_equipment_caps.rs":
        ("rear-equipment-caps", "rear-equipment-caps", "hardware/printed-parts/enclosure/rear-equipment-caps"),
    "hardware/topology/fluid_topology.rs": ("fluid-topology", "fluid-topology", ""),
    "hardware/printed-parts/faucet/tpu-o-ring/tpu_o_ring.rs":
        ("tpu-o-ring", "tpu-o-ring", "hardware/printed-parts/faucet/tpu-o-ring"),
    "hardware/printed-parts/faucet/umbilical-organizer/umbilical_organizer.rs":
        ("umbilical-organizer", "umbilical-organizer", "hardware/printed-parts/faucet/umbilical-organizer"),
    "hardware/printed-parts/cold-core/reservoir/reservoir.rs":
        ("reservoir", "reservoir", "hardware/printed-parts/cold-core/reservoir"),
    "hardware/printed-parts/cold-core/foam-shell/foam_shell.rs":
        ("foam-shell", "foam-shell", "hardware/printed-parts/cold-core/foam-shell"),
    "hardware/printed-parts/faucet/faucet-shell/faucet_shell.rs":
        ("faucet-shell", "faucet-shell", "hardware/printed-parts/faucet/faucet-shell"),
    "hardware/printed-parts/faucet/above-counter-plate/above_counter_plate.rs":
        ("above-counter-plate", "above-counter-plate", "hardware/printed-parts/faucet/above-counter-plate"),
    "hardware/printed-parts/faucet/above-counter-gasket/above_counter_gasket.rs":
        ("above-counter-gasket", "above-counter-gasket", "hardware/printed-parts/faucet/above-counter-gasket"),
    "hardware/printed-parts/faucet/faucet-display-cover/faucet_display_cover.rs":
        ("faucet-display-cover", "faucet-display-cover", "hardware/printed-parts/faucet/faucet-display-cover"),
    "hardware/printed-parts/faucet/industrial/industrial_faucet.rs":
        ("industrial-faucet", "industrial-faucet", "hardware/printed-parts/faucet/industrial"),
    "hardware/printed-parts/cold-core/magnetic-float/magnetic_float.rs":
        ("magnetic-float", "magnetic-float", "hardware/printed-parts/cold-core/magnetic-float"),
    "hardware/printed-parts/cold-core/magnetic-float/all-aero/all_aero_float.rs":
        ("all-aero-float", "all-aero-float", "hardware/printed-parts/cold-core/magnetic-float/all-aero"),
    "hardware/printed-parts/cold-core/coil-mandrel/coil_mandrel.rs":
        ("coil-mandrel", "coil-mandrel", "hardware/printed-parts/cold-core/coil-mandrel"),
    "hardware/printed-parts/cold-core/reed-bridge/reed_bridge.rs":
        ("reed-bridge", "reed-bridge", "hardware/printed-parts/cold-core/reed-bridge"),
    "hardware/printed-parts/cold-core/foam-cap/foam_cap.rs":
        ("foam-cap", "foam-cap", "hardware/printed-parts/cold-core/foam-cap"),
    "hardware/printed-parts/faucet/lever-replica/lever_replica.rs":
        ("lever-replica", "lever-replica", "hardware/printed-parts/faucet/lever-replica"),
    "hardware/printed-parts/faucet/tube-collar/tube_collar.rs":
        ("tube-collar", "tube-collar", "hardware/printed-parts/faucet/tube-collar"),
    "hardware/faucet-layout/faucet_assembly.rs":
        ("faucet-assembly", "faucet-assembly", "hardware/faucet-layout"),
    "hardware/faucet-layout/faucet_industrial_assembly.rs":
        ("faucet-assembly", "faucet-industrial-assembly", "hardware/faucet-layout"),
    "hardware/printed-parts/cold-core/foam-assembly/foam_assembly.rs":
        ("foam-assembly", "foam-assembly", "hardware/printed-parts/cold-core/foam-assembly"),
    "hardware/cold-core-layout/cold_core_assembly.rs":
        ("cold-core-assembly", "cold-core-assembly", "hardware/cold-core-layout"),
    "hardware/cut-parts/carbonation/carbonator-tube/carbonator_tube_step.rs":
        ("carbonator-tube", "carbonator-tube-step", "hardware/cut-parts/carbonation/carbonator-tube"),
    "hardware/printed-parts/fixtures/water-inlet-jet/water_inlet_jet_fixture.rs":
        ("water-inlet-jet-fixture", "water-inlet-jet-fixture", "hardware/printed-parts/fixtures/water-inlet-jet"),
    "hardware/printed-parts/zone-c/funnel/funnel.rs":
        ("funnel", "funnel", "hardware/printed-parts/zone-c/funnel"),
    "hardware/printed-parts/zone-c/funnel/funnel_frame.rs":
        ("funnel", "funnel-frame", "hardware/printed-parts/zone-c/funnel"),
    "hardware/printed-parts/zone-c/funnel/elbow_cradle.rs":
        ("funnel", "elbow-cradle", "hardware/printed-parts/zone-c/funnel"),
    "hardware/printed-parts/zone-c/funnel-cover/funnel_cover.rs":
        ("funnel", "funnel-cover", "hardware/printed-parts/zone-c/funnel-cover"),
    "hardware/printed-parts/zone-c/funnel-mold/funnel_mold.rs":
        ("funnel", "funnel-mold", "hardware/printed-parts/zone-c/funnel-mold"),
}

#: The media a Rust step can rewrite in place: documents with authored text round the figures it
#: maintains. A solid it reads back is never one.
DOCUMENT_MEDIA = (".md", ".mmd", ".csv", ".json")


_METADATA = []


def _cargo_metadata() -> dict:
    """The workspace's `cargo metadata` for this host, read once per tracer run."""
    if not _METADATA:
        sys.path.insert(0, str(_ROOT / "hardware/scripts"))
        from _rust_part import _cargo
        # Only the host's dependencies: offline, cargo cannot read another platform's manifests.
        # cargo asks the `rustc` beside it, so its own directory comes first on the PATH.
        cargo = _cargo()
        env = dict(os.environ, PATH=os.pathsep.join([str(Path(cargo).parent), os.environ.get("PATH", "")]))
        host = next(line.removeprefix("host: ") for line in subprocess.run(
            [str(Path(cargo).with_name("rustc")), "-vV"], capture_output=True, text=True,
            check=True, env=env).stdout.splitlines() if line.startswith("host: "))
        _METADATA.append(json.loads(subprocess.run(
            [cargo, "metadata", "--format-version", "1", "--offline", "--locked",
             "--filter-platform", host, "--manifest-path", str(_ROOT / "tools/hsm/Cargo.toml")],
            cwd=str(_ROOT / "tools/hsm"), capture_output=True, text=True, check=True, env=env).stdout))
    return _METADATA[0]


def _crates_of(manifests) -> set:
    """The packages the crates at `manifests` are compiled from, theirs included."""
    meta = _cargo_metadata()
    nodes = {node["id"]: node for node in meta["resolve"]["nodes"]}
    wanted = {str(m) for m in manifests}
    todo = [package["id"] for package in meta["packages"] if package["manifest_path"] in wanted]
    seen = set()
    while todo:
        pid = todo.pop()
        if pid in seen:
            continue
        seen.add(pid)
        # A dev-dependency builds the crate's tests, never the program.
        todo += [dep["pkg"] for dep in nodes[pid]["deps"]
                 if any(kind["kind"] != "dev" for kind in dep["dep_kinds"])]
    return seen


def _vendored(seen: set, files: set) -> set:
    """Every file of the vendored crates among the packages `seen`. A vendored crate is no
    member, and cargo names none of its files: it is all of them."""
    meta = _cargo_metadata()
    packages = {package["id"]: package for package in meta["packages"]}
    out = set()
    for pid in seen - set(meta["workspace_members"]):
        path = Path(packages[pid]["manifest_path"])
        if path.is_relative_to(_ROOT):
            crate = path.parent.relative_to(_ROOT).as_posix() + "/"
            out |= {f for f in files if f.startswith(crate) and not build_inert(f)}
    return out


def _compiled_from(krate: str, name: str, files: set) -> list:
    """What cargo compiled into `krate`'s program `name`, and the manifests that chose it: what
    of the workspace's manifest and lockfile can change a program (`cargo_config.py`), and the
    manifest of every crate of this tree in the program."""
    sys.path.insert(0, str(_ROOT / "hardware/scripts"))
    from _build_data import request
    target = _ROOT / "tools/hsm/target/release"
    sources = set(request("compiled", path=str(target / f"{name}.d"), workspace=str(_ROOT)))
    packages = {package["id"]: package for package in _cargo_metadata()["packages"]}
    seen = _crates_of([_ROOT / "tools/hsm" / krate / "Cargo.toml"])
    sources |= {"tools/hsm/cargo-config.json"}
    for pid in seen:
        path = Path(packages[pid]["manifest_path"])
        if path.is_relative_to(_ROOT):
            sources.add(path.relative_to(_ROOT).as_posix())
    sources |= _vendored(seen, files)
    return sorted(p for p in sources if p in files and not build_inert(p))


def trace_rust(gen: str, files: set) -> dict:
    """What the Rust step `gen` read and wrote, and the program it ran."""
    krate, name, output = RUST_STEPS[gen]
    sys.path.insert(0, str(_ROOT / "hardware/scripts"))
    import _rust_part
    program = _rust_part.program(krate, name)
    sources = _compiled_from(krate, name, files)
    with tempfile.TemporaryDirectory(prefix=f"hsm-trace-{name}-") as scratch:
        made, log = Path(scratch) / "out", Path(scratch) / "reads"
        made.mkdir()
        slots = _rust_part._slots()
        try:
            ran = subprocess.run(slots.command([program, made]), cwd=str(_ROOT), capture_output=True,
                                 text=True, timeout=DEADLINE,
                                 **slots.subprocess_kwargs(dict(os.environ, HSM_READS=str(log))))
        except subprocess.TimeoutExpired:
            return {"reads": [], "writes": [], "raised": f"TimeoutExpired after {DEADLINE} s"}
        if ran.returncode:
            return {"reads": [], "writes": [],
                    "raised": ran.stderr.strip().splitlines()[-1] if ran.stderr.strip() else f"exit {ran.returncode}"}
        wrote = sorted(p.relative_to(made).as_posix() for p in made.rglob("*") if p.is_file())
        # The trace is a cut, as a generator's is: what the program made lands in the tree.
        for rel in wrote:
            into = _ROOT / output / rel
            into.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(made / rel, into.with_name(into.name + ".trace"))
            os.replace(into.with_name(into.name + ".trace"), into)
        read = set()
        for line in log.read_text().splitlines()[1:]:
            path = Path(line.split("\t")[0])
            if path.is_relative_to(_ROOT):
                read.add(path.relative_to(_ROOT).as_posix())
    at = lambda rel: f"{output}/{rel}" if output else rel
    writes = sorted(at(rel) for rel in wrote if not build_inert(at(rel)))
    # A document the program reads and writes back is rewritten in place, as a Python step's
    # docgen rewrites are: one of the step's inputs as well as one of its outputs.
    rewritten = sorted(w for w in writes if w in read and w.endswith(DOCUMENT_MEDIA))
    reads = (({p for p in read if p in files and not build_inert(p)} | set(sources))
             - (set(writes) - set(rewritten)))
    return {"reads": sorted(reads), "writes": writes, "rewritten": rewritten,
            "program": {"crate": krate, "name": name, "sources": sources}}


def _generators(files: set) -> list:
    """Every `.py` with a `__main__` this tree builds through — see `ELSEWHERE` — and every Rust
    step's program."""
    out = []
    for f in sorted(files):
        if f in RUST_STEPS:
            out.append(f)
        if not f.endswith(".py") or f.startswith(ELSEWHERE):
            continue
        try:
            if '__name__ == "__main__"' in (_ROOT / f).read_text():
                out.append(f)
        except OSError:
            continue
    return out


def gave_up(prior: dict, seen: dict) -> bool:
    """Whether a reading hands back fewer files than the one it replaces, on EITHER side.

    Each side on its own, because a run can open MORE and write LESS — the inputs load, then it
    dies before the exports land — and that reading has its reads intact, which is the one that
    looks healthy. Asking it as an ordered pair against `(0, 0)` answers on the reads and never
    reaches the writes: `(-1, 1)` is a run that gained four reads and lost two writes, and it
    compares less-than on the first element and passes."""
    return any(len(prior[side]) > len(seen[side]) for side in ("reads", "writes"))


def selftest() -> int:
    """Every shape the reading can take, against the answer. Two agents got this comparison
    wrong before it was named — the trace is no part of it, so neither is a run."""
    holds = 0

    def hold(label, prior, seen, want):
        nonlocal holds
        got = gave_up({"reads": [0] * prior[0], "writes": [0] * prior[1]},
                      {"reads": [0] * seen[0], "writes": [0] * seen[1]})
        holds += got == want
        print(f"  {'✓' if got == want else '✗'} {label}"
              + ("" if got == want else f" — {got} != {want}"))

    hold("both sides shrank", (9, 3), (5, 1), True)
    hold("the reads shrank and the writes stood", (9, 3), (5, 3), True)
    hold("the writes shrank and the reads stood", (9, 3), (9, 1), True)
    hold("the reads shrank and the writes grew", (9, 1), (5, 3), True)
    # THE ONE AN ORDERED PAIR WAVES THROUGH, and the one a part-way run most looks like.
    hold("the reads GREW and the writes shrank", (5, 3), (9, 1), True)
    hold("both sides grew", (5, 1), (9, 3), False)
    hold("neither side moved", (9, 3), (9, 3), False)

    import tempfile
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "graph.json"
        intermediate = "out/spec/enclosure-box.json"
        result = "out/consumer/panel.step"
        path.write_text(json.dumps({
            "producer.py": {"reads": ["producer.py"], "writes": [intermediate]},
            "consumer.py": {"reads": ["consumer.py", intermediate], "writes": [result]},
        }))
        files = _tracked(path, {"producer.py", "consumer.py"})
        producer = _filtered(
            {"reads": ["producer.py"], "writes": [intermediate], "rewritten": []}, files)
        consumer = _filtered(
            {"reads": ["consumer.py", intermediate], "writes": [result], "rewritten": []},
            files)
        survived = (producer["writes"] == {intermediate}
                    and intermediate in consumer["reads"] and consumer["writes"] == {result})
        holds += survived
        print(f"  {'✓' if survived else '✗'} an ignored JSON handoff keeps its producer and "
              "consumer edges")

        core_mesh = "hardware/cold-core-layout/cold-core-assembly.step.mesh"
        admitted = core_mesh in _tracked(path, {"producer.py", "consumer.py"})
        holds += admitted
        print(f"  {'✓' if admitted else '✗'} an implicit mesh is admitted before its first "
              "trace writes graph.json")

        slicer = "hardware/printed-parts/petgf.3mf"
        inert = (slicer not in _tracked(path, {"producer.py", "consumer.py", slicer})
                 and slicer not in _filtered(
                     {"reads": ["consumer.py", slicer], "writes": [result], "rewritten": []},
                     {"consumer.py", slicer, result},
                 )["reads"])
        holds += inert
        print(f"  {'✓' if inert else '✗'} a slicer workspace never enters a trace or action")

    print(f"trace_inputs selftest {holds}/10")
    return 0 if holds == 10 else 1


def _pointer_debt(wrote: set) -> list:
    """The bundle members this run rewrote that `cad-artifacts.json` no longer names.

    A TRACE IS A CUT. Watching a generator means running it, and a generator writes its
    outputs — which are ignored, so `git status` reads clean over a tree whose bundle has
    moved. `pack.py --check` is the only thing that sees that, and a trace is not a publish,
    so nobody was going to ask it. The run that moved the bytes is the run that says so.

    Only what this run wrote is hashed, so the answer costs the members it touched and not
    the 460 MB `--check` reads to answer the same question about all of them.
    """
    pointers = _ROOT / "hardware" / "cad-artifacts.json"
    if not pointers.is_file():
        return []
    named = json.loads(pointers.read_text()).get("solids", {})
    behind = []
    for rel in sorted(set(wrote) & set(named)):
        path = _ROOT / rel
        if not path.is_file():
            continue
        digest = hashlib.sha256()
        with path.open("rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                digest.update(chunk)
        if digest.hexdigest() != named[rel]:
            behind.append(rel)
    return behind


def main() -> int:
    if sys.argv[1:] == ["selftest"]:
        return selftest()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("gen", nargs="*", help="generator paths; the ones the change reached")
    ap.add_argument("--all", action="store_true",
                    help="re-trace every generator; 80 minutes, and it loses writes")
    args = ap.parse_args()

    files = _tracked()

    # A BARE SWEEP RE-TRACES EVERY GENERATOR SERIALLY, AND THAT IS OVER AN HOUR. It is not the
    # remedy for a target that declared too few inputs — the remedy is the generators the change
    # reached, and `check_declared_imports.py` and `gen_build.py --check` each name those where
    # they fail. Held behind a word, because the cost lands on whoever is at the keyboard and
    # a stale derived doc does not.
    #
    # AND A SWEEP LOSES WRITES. A generator whose outputs are already current writes fewer than
    # it declares, and the loop below reads any write as a whole run — so the entry is replaced
    # by the part it reached, and every output it stopped naming loses the rule that cuts it. A
    # generator the change actually reached rewrites its outputs, which is why tracing THOSE is
    # the accurate answer as well as the fast one.
    if not args.gen and not args.all:
        every = _generators(files)
        print(
            f"  A bare sweep re-traces all {len(every)} generators, serially, and that is over\n"
            f"  an hour. Trace the ones the change reached:\n\n"
            f"    tools/cad-venv/bin/python tools/bazel/trace_inputs.py <gen.py> [<gen.py> ...]"
            f"\n\n  Where that list comes from:\n"
            f"    check_declared_imports.py   names them when a target declares too few inputs\n"
            f"    gen_build.py --check        names them when BUILD.bazel has drifted\n"
            f"    git diff --name-only        the generators actually edited\n\n"
            f"  `--all` is for a change that moves every reading at once. It also drops the\n"
            f"  writes of every generator whose outputs are already current, so run it where\n"
            f"  nobody is waiting on it:\n\n"
            f"    gh workflow run derive.yml --ref main -f trace=all\n",
            file=sys.stderr)
        return 2

    gens = args.gen or _generators(files)

    # A LINE PER GENERATOR, AS IT LANDS. On the runner stdout is a pipe and Python holds the
    # lines until a buffer fills, so a run killed at its step's deadline shows every reading it
    # made stamped with the minute the buffer emptied, and none with the minute it was read.
    sys.stdout.reconfigure(line_buffering=True)

    graph = json.loads(GRAPH.read_text()) if GRAPH.is_file() else {}
    shrank = []
    wrote = set()
    for i, gen in enumerate(gens, 1):
        seen = trace_rust(gen, files) if gen in RUST_STEPS else trace(gen, files)
        # `probe.py`, `fit.py` and `lanes.py` are instruments: they answer and write nothing,
        # and a generator this has never watched write is not a step of the build.
        #
        # A RUN THAT DID NOT HAPPEN IS NOT A GENERATOR THAT MAKES NOTHING. Attached, superseded,
        # killed, timed out — each comes back the way an instrument does, with no writes, and
        # dropping the entry on that reading takes the generator out of `graph.json`, out of
        # `inventory`, out of `BUILD.bazel`, and its solids stop being cut against a green
        # build. So an entry already standing is left standing, and the line below says the
        # reading failed rather than writing a verdict over it.
        # A GENERATOR THAT RAISED WROTE NOTHING TOO, and the RUNNER is where the two part: it
        # names the exception. One that raised keeps the entry it had, and one with no entry
        # is named on its own line, because a build cannot cut what a red generator makes.
        # AND A RUN THAT DID PART OF ITS WORK WROTE SOMETHING. The branch below reads any write
        # as a whole run, so a generator that stopped halfway replaces its entry with the part
        # it reached — `render_scenes` came back 38 read / 22 written where it stands at
        # 210 / 76, and the reading that catches it is the entry already in hand. A shrink is
        # not wrong on its own: a tracer that stops recording what a run never opened shrinks
        # every entry it touches, on purpose. So this takes the reading and NAMES it, at the
        # tail as well, where a sweep of a hundred generators cannot scroll it away.
        raised = seen.pop("raised", None)
        if seen["writes"]:
            wrote |= set(seen["writes"])
            prior = graph.get(gen)
            if prior and gave_up(prior, seen):
                shrank.append((gen, len(prior["reads"]), len(seen["reads"]),
                               len(prior["writes"]), len(seen["writes"])))
            graph[gen] = seen
        elif raised and gen in graph:
            print(f"  [{i:3d}/{len(gens)}] {gen:60s} raised {raised} — keeping what it had")
            continue
        elif raised:
            print(f"  [{i:3d}/{len(gens)}] {gen:60s} raised {raised} — NOT IN THE GRAPH, so "
                  f"nothing it makes is cut")
            continue
        elif gen in graph:
            print(f"  [{i:3d}/{len(gens)}] {gen:60s} wrote nothing — keeping what it had")
            continue
        else:
            graph.pop(gen, None)
        print(f"  [{i:3d}/{len(gens)}] {gen:60s} "
              f"{len(seen['reads']):3d} read {len(seen['writes']):3d} written")
        GRAPH.write_text(json.dumps(graph, indent=2, sort_keys=True) + "\n")
    print(f"{len(graph)} generator(s) in the graph")
    if shrank:
        # Either side alone is the reading, so the line cannot say the entry came back smaller:
        # a run can open more and still write less, which is the shape that gets past a guard
        # comparing the pair in order.
        print(f"\n{len(shrank)} entr(y/ies) gave up reads or writes they had:")
        for gen, r0, r1, w0, w1 in shrank:
            print(f"    {gen}\n      {r0:3d} -> {r1:3d} read   {w0:3d} -> {w1:3d} written")
        print("  A run that stopped part way writes down the part it reached. Re-trace the one")
        print("  generator and read it again; the second reading is the one to keep.")
    behind = _pointer_debt(wrote)
    if behind:
        print(f"\n{len(behind)} member(s) this run wrote are no longer the pointer file's:")
        for rel in behind[:8]:
            print(f"    {rel}")
        if len(behind) > 8:
            print(f"    ... and {len(behind) - 8} more")
        print("  A TRACE IS A CUT — the run rewrote them, and they are ignored, so")
        print("  `git status` reads clean over a bundle that has moved. `pack.py --check`")
        print("  is the only thing that sees this, and it reads rc=1 until someone publishes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
