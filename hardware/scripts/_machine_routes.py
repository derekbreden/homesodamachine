"""Scalar requests for Rust's installed warm-tube and insulation geometry."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path


def numbers(routes, *, insulation=None, components=None, name="machine-routes"):
    """Keep authored route order and existing world-placed equipment references.

    A component reference is ``{"model": fine_npz_path, "indices": [body_indices]}``.
    The insulation plan, palette and valve pose come from the equipment provider;
    no CAD builder or installed-placement calculation is repeated here.
    """
    return {"name": name, "routes": deepcopy(routes), "route_order": list(routes),
            "insulation": deepcopy(insulation), "components": deepcopy(components or {})}


def equipment_inputs(request, model, groups):
    """Select the holder and soft-neighbor groups from the equipment's fine model."""
    insulation = request.get("insulation")
    if insulation is None:
        insulation = next((row for row in request.get("items", ())
                           if row.get("op") == "insulation"), None)
    components = {}
    if insulation is not None:
        for name in ("soda-bend-holder", *insulation["neighbors"]):
            components[name] = {"model": str(Path(model)), "indices": list(groups[name])}
    return {"routes": request["routes"], "insulation": insulation,
            "components": components}


def build(output, routes, *, insulation=None, components=None, name="machine-routes"):
    """Write paired fine geometry and ordered named-body metadata through Rust."""
    import _rust_part

    return _rust_part.cut("machine", "machine-routes",
                          numbers(routes, insulation=insulation,
                                  components=components, name=name), Path(output))
