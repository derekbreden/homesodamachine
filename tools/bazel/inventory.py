#!/usr/bin/env python3
"""Every generator in the tree and what it makes, read off what a run of it was watched doing.

    tools/cad-venv/bin/python tools/bazel/inventory.py        # print it

`trace_inputs.py` watches each generator run and writes down every tracked file it opened, by
the side it opened it on. `graph.json` is that record. This sorts each generator's writes into
the solids it cuts and the docs it rewrites, and carries its reads through to `gen_build.py`.
"""

import json
import subprocess
import sys
from pathlib import Path

# The job runner every heavy action runs through. No step is made from it: a Python step copies
# the checkout's current files into its folder when it runs, so an edit to them reruns nothing.
RUNTIME_READS = frozenset({'hardware/scripts/_run_slots.py', 'hardware/scripts/_run_lock.py',
                           'hardware/scripts/_run_native.py',
                           'tools/run.py', 'tools/run-slots.mjs', 'tools/hsm/run-slots.defaults.json'})
RUST_RUNTIME_READS = frozenset({'tools/hsm/run-native/Cargo.toml',
                                'tools/hsm/run-native/src/lib.rs',
                                'tools/hsm/run-slots/Cargo.toml',
                                'tools/hsm/run-slots/src/lib.rs',
                                'tools/hsm/run-slots/src/ipc.rs',
                                'tools/hsm/run-slots/src/runtime.rs',
                                'tools/hsm/run-slots/src/main.rs',
                                'tools/hsm/run-slots/src/runtime/slots.rs',
                                'tools/hsm/run-slots/src/runtime/cad.rs',
                                'tools/hsm/run-slots/src/runtime/runner.rs',
                                'tools/hsm/run-slots/src/runtime/install.rs',
                                'tools/hsm/run-slots.defaults.json'})

_HERE = Path(__file__).resolve()
_ROOT = _HERE.parents[2]
GRAPH = _HERE.parent / "graph.json"

# A 3MF IS A SLICER WORKSPACE, NOT A BUILD INPUT. It may hold the profile used to print a
# generated STL, and a check may inspect that profile explicitly, but changing the workspace
# cannot change any CAD solid or generated document. Keeping this boundary here means neither a
# directory scan observed by the tracer nor a tracked 3MF can leak into a Bazel action.
# A `.bbscfg` is that workspace's presets saved loose: the filament and process a slicer is
# pointed at before it opens a project.
BUILD_INERT_SUFFIXES = (".3mf", ".bbscfg")

# PRINT PREPARATION AND INDEPENDENT GEOMETRY READINGS, WRITTEN OUT AS JSON. The recipe a print run is asked for, the
# settings the slicer resolved it to, the audit that holds those two against each other, and the
# reading taken off the machine at the start of the print. Nozzles, chamber temperatures, layer
# heights, plate trims and verification of a solid that is already cut.
#
# NAMED ONE BY ONE, because `.json` beside a part is the tree's load-bearing kind: `.scene.json`
# carries a render, `.facts.json` a measured solid, and `cad-artifacts.json` the shipped bundle.
# Each slicer record joins by being named here.
BUILD_INERT_BASENAMES = frozenset({
    "print-profile.json",
    "faucet-petgf.print.json",
    "lever-replica-petgf.print.json",
    "lever-replica-petgf.readiness.json",
    "lever-replica-petgf-white.print.json",
    "lever-replica-petgf-white.readiness.json",
    "tube-miter-box-petgf.print.json",
    "tube-miter-box-petgf.readiness.json",
    "tube-miter-box-petgf-mark2.print.json",
    "tube-miter-box-petgf-mark2.readiness.json",
    "fake-countertop-petgf.print.json",
    "fake-countertop-petgf.readiness.json",
    "fake-countertop-petgf-mark2.print.json",
    "fake-countertop-petgf-mark2.readiness.json",
    "fake-countertop-petgf-mark2-stock.print.json",
    "fake-countertop-petgf-mark2-stock.readiness.json",
    "lever-replica-petgf.support-audit.json",
    "lever-replica-petgf-white.support-audit.json",
    "corner-trial-profile.json",
    "layer-review.json",
    "toolpath-review.json",
    "slice-review.json",
    "repaired-wall-review.json",
    "containment-review.json",
    "wall-review.json",
})


def build_inert(path: str) -> bool:
    return _native("inventory-inert", path=str(path))

def pinned_copies(files) -> set:
    return set(_native("inventory-pinned", root=str(_ROOT), files=list(files)))


#: WHICH KIND OF WRITE IT WAS IS THE WRITER'S TO SAY, and `graph.json` carries the answer:
#: `rewritten` is what `docgen` read and wrote back, and the rest of `writes`
#: is what `_cadq_export` cut whole. A name cannot tell them apart — `.figures.json` carries
#: no marker and is rewritten, a `.step` is read to be compared against and is not — and a
#: suffix list forgot a medium four times before this: a driver's own docstring, a mermaid
#: chart's `%%` lines, a doc's figures sidecar, and a driver's own source comments.


#: The generated solids, which are on this disk and in no index. A sandbox is filled from `srcs`,
#: so a solid one generator cuts and the next loads has to be named there whichever side of the
#: index it sits.
#:
#: TWO READINGS SAY WHICH SOLIDS THOSE ARE AND `tracked` TAKES BOTH, because each holds one the
#: other does not. `pack.py`'s walk reads this disk, so a solid cut since the last release is in
#: it — and a solid a trace is filtered against the pointer file alone cannot enter the graph until a
#: bundle is pointed at, which is a part the sandbox is never filled with and an action that dies
#: on a file sitting in the tree. `hardware/cad-artifacts.json` names the solids the pointed at
#: bundle carries, which is the reading a checkout that has cut nothing of its own still has.
POINTERS = _ROOT / "hardware" / "cad-artifacts.json"


def frozen_assets(root: Path = _ROOT) -> dict:
    return _native("publication-frozen-assets", root=str(root))


#: Outputs whose writer deliberately avoids touching them when the bytes beside its STEP are
#: already current. A syscall trace therefore sees the read that proves they are current, not a
#: write, even though a clean action must produce them. Each normal producer owns its complete
#: payload set, including files its Rust writer leaves unchanged when their bytes are current.
IMPLICIT_SOLIDS = {
    "hardware/printed-parts/soda-bend-holder/soda_bend_holder.py": tuple(
        f"hardware/printed-parts/soda-bend-holder/soda-bend-holder.{suffix}"
        for suffix in ("step", "stl", "step.mesh")
    ),
    "hardware/printed-parts/enclosure/rear-identification/rear_identification.py": tuple(
        f"hardware/printed-parts/enclosure/rear-identification/rear-label-{station}.{suffix}"
        for station in ("water", "co2", "drain", "carb", "flavor-a", "flavor-b")
        for suffix in ("step", "stl", "step.mesh")
    ),
    "hardware/printed-parts/zone-c/funnel-cover/funnel_cover.py": (
        "hardware/printed-parts/zone-c/funnel-cover/funnel-cover.stl",
        "hardware/printed-parts/zone-c/funnel-cover/funnel-cover-print.stl",
        "hardware/printed-parts/zone-c/funnel-cover/funnel-cover.step.mesh",
        "hardware/printed-parts/zone-c/funnel-cover/funnel-cover-print.step.mesh",
    ),
    # These STL exports are written by OCCT below Python's filesystem audit.
    # Their generators still own them in a clean action.
    "hardware/printed-parts/zone-c/funnel/funnel_frame.py": (
        "hardware/printed-parts/zone-c/funnel/funnel-frame.stl",
        "hardware/printed-parts/zone-c/funnel/funnel-frame.step.mesh",
    ),
    "hardware/printed-parts/zone-c/funnel/elbow_cradle.py": (
        "hardware/printed-parts/zone-c/funnel/elbow-cradle.stl",
        "hardware/printed-parts/zone-c/funnel/elbow-cradle.step.mesh",
    ),
    "hardware/printed-parts/enclosure/display-cover/display_cover.py": (
        "hardware/printed-parts/enclosure/display-cover/display-cover.stl",
    ),
    # And its two viewer payloads and the fasteners it cuts beside the first unit, which stand
    # unwritten when their bytes already do. The machine places those fasteners.
    "hardware/printed-parts/enclosure/nameplate/nameplate.py": (
        "hardware/printed-parts/enclosure/nameplate/nameplate-001.stl",
        "hardware/printed-parts/enclosure/nameplate/nameplate-receiver.stl",
        "hardware/printed-parts/enclosure/nameplate/nameplate-001.step.mesh",
        "hardware/printed-parts/enclosure/nameplate/nameplate-receiver.step.mesh",
        "hardware/printed-parts/enclosure/nameplate/nameplate-fasteners.step",
        "hardware/printed-parts/enclosure/nameplate/nameplate-fasteners.step.mesh",
        "hardware/printed-parts/enclosure/nameplate/nameplate-fasteners.step.npz",
    ),
    # Current payloads need no rewrite; a clean run still owes every view.
    "hardware/printed-parts/zone-c/funnel-mold/funnel_mold.py": tuple(
        f"hardware/printed-parts/zone-c/funnel-mold/{name}.step.mesh"
        for name in ("assembly", "backs", "cavity", "core", "funnel", "overview", "rod", "section")
    ),
}

# Outputs whose bytes cross between build actions without becoming public artifacts.
ACTION_INTERMEDIATE = frozenset()

#: ONE WALK ANSWERS WHICH `.step` ON THIS DISK IS A GENERATED SOLID, and `pack.py` is where it
#: lives — `pack.py --check` holds that same walk against the outputs `graph.json` declares, so
#: the solids a bundle ships and the solids an action is filled from are one reading. Its
#: directory's hyphen keeps it out of a dotted import, so the path goes on `sys.path` and
#: `tracked` imports it by name.
sys.path.append(str(_ROOT / "tools" / "cad-artifacts"))


def tracked() -> list:
    import pack
    config = _publication_config(pack)
    return _native("inventory-tracked", root=str(_ROOT), publication_config=config)


def _together(writes: dict) -> list:
    return _native("inventory-together", writes={name: list(paths) for name, paths in writes.items()})


def inventory(files=None) -> dict:
    files = list(files or tracked())
    try:
        rows = _native("inventory", root=str(_ROOT), graph_path=str(GRAPH), files=files)
    except ValueError as error:
        raise SystemExit(str(error).removeprefix("build-data: ")) from error
    return {tuple(generators): entry for generators, entry in rows}


def main() -> int:
    inv = inventory()
    solids = sum(len(v["solids"]) for v in inv.values())
    docs = sum(len(v["docs"]) for v in inv.values())
    gens = sum(len(k) for k in inv)
    print(f"  {len(inv)} steps over {gens} generators, {solids} solids, {docs} doc files")
    for k in sorted(inv):
        if len(k) > 1:
            print("  one step: " + ", ".join(Path(g).name for g in k))
    return 0




def _native_config():
    """Marshal the authored input groups and their Python container types."""
    return dict(runtime_reads=list(RUNTIME_READS), rust_runtime_reads=list(RUST_RUNTIME_READS),
                inert_suffixes=BUILD_INERT_SUFFIXES, inert_basenames=list(BUILD_INERT_BASENAMES),
                implicit_solids=IMPLICIT_SOLIDS)


def _publication_config(pack):
    return pack._native_config()


def _native(op, **fields):
    sys.path.insert(0, str(_ROOT / "hardware/scripts"))
    from _build_data import request
    return request(op, config=_native_config(), **fields)

if __name__ == "__main__":
    raise SystemExit(main())
