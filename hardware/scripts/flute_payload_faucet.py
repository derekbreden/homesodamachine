"""Flute the faucet's base — the one printed piece that stands in the open on a counter.

A THIRD TREE, FOR THE SAME REASON THE OTHER TWO ARE APART. The box's six pieces and the cold
core's three are two rules because one rule over both comes back around on itself
(`flute_payload_enclosure.py`). This tree comes back around on nothing — no assembly under
`printed-parts/faucet/` reads a payload the box or the core writes — but the partition is the
same one either way: `inventory.py` writes all three entries out of one traced run of
`flute_payload.py`, on the directories `ENCLOSURE_DIRS`, `COLD_CORE_DIRS` and `FAUCET_DIRS`
name. A run over this tree opens `faucet-shell-base.step` beside its printed mesh, cuts the
payload the viewer draws, and grafts that surface into `faucet-shell.step.mesh` — the two
pieces as assembled, which is what `faucet-assembly` and `/3d` open.

THE ASSEMBLED PAYLOAD IS THIS ACTION'S OUTPUT, so a clean sandbox cannot also receive the old
copy as an input. Its STEP is the host: `import_assembly` reads the names, placements and
colours that the viewer would read, and `_seed_host` tessellates those bodies before the flute
surface replaces the base. A hand run normally finds the current payload already beside the
STEP and leaves its bytes alone until `graft` decides they differ.
"""

from pathlib import Path

import cadquery as cq

import flute_payload
from _cadq_export import import_assembly


def _seed_host(step: Path) -> Path:
    """Make the smooth assembled payload from `step` when no prior payload is present."""
    payload = step.with_name(step.name + ".mesh")
    if payload.is_file():
        return payload

    bodies = import_assembly(step)
    if not bodies:
        raise ValueError(f"{step.name}: no named bodies to seed its assembled payload")
    host = cq.Assembly(name=step.stem)
    for name, (shape, _color) in sorted(bodies.items()):
        host.add(shape, name=name)
    meshes = flute_payload._mesh_payload.from_assembly(host)
    if not meshes:
        raise ValueError(f"{step.name}: its named bodies tessellated to no payload meshes")
    # Both printed shell pieces carry the same PET-GF black. Read its exact linear viewer
    # colour from the one-body STEP instead of round-tripping XCAF's already-linear value
    # through `cq.Color`, which would apply the sRGB transfer a second time.
    _name, color = flute_payload.solid_identity(step.with_name("faucet-shell-base.step"))
    for mesh in meshes:
        mesh["color"] = color
    flute_payload._mesh_payload.write(
        meshes,
        str(payload),
        src=flute_payload._mesh_payload.source_digest(step),
    )
    return payload


if __name__ == "__main__":
    _seed_host(flute_payload.FAUCET_DIRS[0] / "faucet-shell.step")
    raise SystemExit(flute_payload.main(flute_payload.FAUCET_DIRS))
