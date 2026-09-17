"""Publish the faucet's checked print meshes as viewer payloads.

The shell, display cover, above-counter plate and gasket use their actual
STLs. The assembled shell payload receives both printed shell surfaces.
The shared pipeline also handles the appliance's fluted parts; the faucet
itself has smooth CAD-native surfaces.
"""

import sys
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
    sys.exit(flute_payload.main(flute_payload.FAUCET_DIRS))
