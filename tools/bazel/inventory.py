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
    "hardware/install-guide/plumbing/plumbing_scenes.py": tuple(
        f"hardware/install-guide/plumbing/out/{name}.step.{suffix}"
        for name in ("plumbing-valve-on", "plumbing-valve-off", "plumbing-pre-tee",
                     "plumbing-tee-installed")
        for suffix in ("mesh", "npz")
    ),
    "hardware/install-guide/plumbing/modern/render_modern_tee.py": (
        "hardware/install-guide/plumbing/modern/out/modern-water-on.step",
        "hardware/install-guide/plumbing/modern/out/modern-water-on.step.mesh",
        "hardware/install-guide/plumbing/modern/out/modern-water-on.step.npz",
    ),
    "hardware/printed-parts/soda-bend-holder/soda_bend_holder.py": tuple(
        f"hardware/printed-parts/soda-bend-holder/soda-bend-holder.{suffix}"
        for suffix in ("step", "stl", "step.mesh")
    ),
    "hardware/printed-parts/enclosure/rear-identification/rear_identification.py": tuple(
        f"hardware/printed-parts/enclosure/rear-identification/rear-label-{station}.{suffix}"
        for station in ("water", "co2", "drain", "carb", "flavor-a", "flavor-b")
        for suffix in ("step", "stl", "step.mesh")
    ),
    "hardware/printed-parts/asse-straight-cuffs/asse_straight_cuffs.py": tuple(
        f"hardware/printed-parts/asse-straight-cuffs/asse-{side}-cuff.{suffix}"
        for side in ("inlet", "outlet")
        for suffix in ("step", "stl", "step.mesh")
    ),
    "hardware/printed-parts/asse-drain-adapter/asse_drain_adapter.py": (
        "hardware/printed-parts/asse-drain-adapter/asse-drain-adapter.stl",
        "hardware/printed-parts/asse-drain-adapter/asse-drain-adapter.step.mesh",
    ),
    "hardware/printed-parts/diaphragm-pump-sleeve/diaphragm_pump_sleeve.py": (
        "hardware/printed-parts/diaphragm-pump-sleeve/diaphragm-pump-sleeve.stl",
        "hardware/printed-parts/diaphragm-pump-sleeve/diaphragm-pump-sleeve.step.mesh",
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
    # And its two viewer payloads, which `_write_mesh_payload` leaves unwritten when the bytes
    # already stand.
    "hardware/printed-parts/enclosure/nameplate/nameplate.py": (
        "hardware/printed-parts/enclosure/nameplate/nameplate-001.stl",
        "hardware/printed-parts/enclosure/nameplate/nameplate-receiver.stl",
        "hardware/printed-parts/enclosure/nameplate/nameplate-001.step.mesh",
        "hardware/printed-parts/enclosure/nameplate/nameplate-receiver.step.mesh",
    ),
    "hardware/printed-parts/faucet/lever-replica/lever_replica.py": (
        "hardware/printed-parts/faucet/lever-replica/lever-replica.stl",
        "hardware/printed-parts/faucet/lever-replica/lever-replica-side-down.stl",
    ),
    "hardware/printed-parts/cold-core/magnetic-float/magnetic_float.py": tuple(
        f"hardware/printed-parts/cold-core/magnetic-float/{name}.step.mesh"
        for name in ("body-petg", "body-aero", "insert-aero",
                     "magnet", "magnetic-float", "section", "exploded")
    ),
    "hardware/printed-parts/cold-core/magnetic-float/all-aero/all_aero_float.py": tuple(
        f"hardware/printed-parts/cold-core/magnetic-float/all-aero/{name}.step.mesh"
        for name in ("float-aero", "assembly", "section", "insertion")
    ),
    # Current payloads need no rewrite; a clean run still owes every view.
    "hardware/printed-parts/zone-c/funnel-mold/funnel_mold.py": tuple(
        f"hardware/printed-parts/zone-c/funnel-mold/{name}.step.mesh"
        for name in ("assembly", "backs", "cavity", "core", "funnel", "overview", "rod", "section")
    ),
    "hardware/cold-core-layout/cold_core_assembly.py": (
        "hardware/cold-core-layout/cold-core-assembly.step.mesh",
    ),
    "hardware/printed-parts/cold-core/foam-cap/foam_cap.py": tuple(
        f"hardware/printed-parts/cold-core/foam-cap/pump-snap-cap.{suffix}"
        for suffix in ("step", "stl", "step.mesh")
    ),
    "hardware/printed-parts/enclosure/rear-equipment-caps/rear_equipment_caps.py": tuple(
        f"hardware/printed-parts/enclosure/rear-equipment-caps/{name}.stl"
        for name in ("asse-snap-cap", "pisco-snap-cap", "meter-snap-cap", "regulator-snap-cap")
    ),
    "hardware/manifold-layout/enclosure_assembly.py": (
        "hardware/manifold-layout/enclosure-assembly.step.mesh",
        "hardware/wiring/enclosure-wiring.step.mesh",
    ),
    "hardware/manifold-layout/manifold_layout.py": (
        "hardware/manifold-layout/manifold-layout.step.mesh",
    ),
    "hardware/faucet-layout/faucet_assembly.py": (
        "hardware/faucet-layout/faucet-assembly.step.mesh",
    ),
    "hardware/faucet-layout/faucet_industrial_assembly.py": (
        "hardware/faucet-layout/faucet-industrial-assembly.step.mesh",
    ),
    # The assembled shell starts as a CAD payload; the faucet payload action
    # replaces both piece surfaces with their checked printable meshes.
    "hardware/printed-parts/faucet/faucet-shell/faucet_shell.py": (
        "hardware/printed-parts/faucet/faucet-shell/faucet-shell.step.mesh",
    ),
}

# Outputs whose bytes cross between build actions without becoming public artifacts.
ACTION_INTERMEDIATE = frozenset()

# ONE RUN THAT DOES TWO SEPARABLE JOBS IS TWO RULES, and each wrapper below is the real script
# an action runs for its half. The reading is still one traced run of the source; what a wrapper
# takes out of it is a pair of predicates — which writes are its, and which reads.
#
# A direct scene-render run can produce both media. The enclosure-assembly producer owns the
# public GLBs now, cutting them from the named machine it already has in memory. This synthetic
# card wrapper retains only the browser-driven PNG/JSON outputs from the shared trace, and every
# read that run took.
#
# The shared presentation writer supplies independent cold-core and faucet rules. The
# enclosure's Rust producer owns all its presentations without a separate normal co-writer.
# Each shared rule takes only its tree's payloads and inputs, plus common helper modules.
_FLUTE_ROOTS = {
    "hardware/scripts/flute_payload_cold_core.py": (
        "hardware/printed-parts/cold-core/foam-shell/",),
    "hardware/scripts/flute_payload_faucet.py": (
        "hardware/printed-parts/faucet/faucet-shell/",
        "hardware/printed-parts/faucet/faucet-display-cover/",
        "hardware/printed-parts/faucet/above-counter-plate/",
        "hardware/printed-parts/faucet/above-counter-gasket/",
    ),
}
# Generator-owned enclosure and cap surfaces remain outside every wrapper's shared inputs.
_FLUTE_TREES = tuple(sorted({r for roots in _FLUTE_ROOTS.values() for r in roots}
                           | {"hardware/printed-parts/enclosure/enclosure/",
                              "hardware/printed-parts/cold-core/foam-cap/",
                              "hardware/printed-parts/faucet/asse-vent-seals/"}))
# Sources inside the trees above that every wrapper reads besides its own tree's. The print
# payload program the wrappers share is outside them, in tools/hsm/print-payload.
_FLUTE_SHARED_SOURCES = frozenset()


def _one_tree(roots: tuple) -> tuple:
    return (lambda path: _native("inventory-one-tree", path=path, roots=roots, read=False),
            lambda path: _native("inventory-one-tree", path=path, roots=roots, read=True))


#: `{source: {wrapper: (takes_write, takes_read)}}`. A wrapper is a real script with its own
#: `__main__`; its graph entry is written from the source's trace and whatever a reading of the
#: wrapper itself left behind is dropped — `trace_inputs.main` says so at its entrance.
SPLIT_GENERATORS = {
    "hardware/scripts/flute_payload.py": {
        wrapper: _one_tree(roots) for wrapper, roots in _FLUTE_ROOTS.items()
    },
}


def _split_generators(graph: dict) -> dict:
    return _native("inventory-split", graph=graph)

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
                implicit_solids=IMPLICIT_SOLIDS, flute_roots=_FLUTE_ROOTS,
                flute_trees=_FLUTE_TREES, flute_shared=list(_FLUTE_SHARED_SOURCES))


def _publication_config(pack):
    return pack._native_config()


def _native(op, **fields):
    sys.path.insert(0, str(_ROOT / "hardware/scripts"))
    from _build_data import request
    return request(op, config=_native_config(), **fields)

if __name__ == "__main__":
    raise SystemExit(main())
