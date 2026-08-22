"""The cold core's exact viewer colours, without building its geometry.

The cold-core producer and the scene composer meet at a mesh payload.  RGB is carried by that
payload because it is part of the STEP/viewer surface; alpha is a material fact that STEP does
not carry.  Both sides therefore read the same constants here.  Importing this module creates
colours and nothing else: no STEP is opened and no CadQuery solid is made.
"""

from __future__ import annotations

import sys
from pathlib import Path

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
if str(_hw / "scripts") not in sys.path:
    sys.path.insert(0, str(_hw / "scripts"))

import _materials as _mat                              # noqa: E402
import _routing                                        # noqa: E402


FOAM_COLORS = {
    "foam-shell": _mat.C_FOAM_SHELL,
    "foam-cap-top": _mat.C_CAP_TOP,
    "foam-cap-lid-top": _mat.C_CAP_LID_TOP,
    "foam-cap-bottom": _mat.C_CAP_BOTTOM,
    "foam-cap-lid-bottom": _mat.C_CAP_LID_BOTTOM,
}

ROUTE_SPOOLS = {
    "water-in": "white",
    "carb-water-out": "blue",
    "co2-in": "red",
    "prv-vent": "black",
    "reservoir-a": "black",
    "reservoir-a-fill": "black",
    "reservoir-b": "black",
    "reservoir-b-fill": "black",
}
ROUTE_COLORS = {name: _routing.color(spool) for name, spool in ROUTE_SPOOLS.items()}


def colour_for(name: str):
    """The material colour for one exact cold-core body or `line-<route>` leaf."""
    if name.startswith("line-"):
        route = name.removeprefix("line-")
        try:
            return ROUTE_COLORS[route]
        except KeyError as exc:
            raise KeyError(f"{name!r}: no cold-core route colour") from exc
    if name in FOAM_COLORS:
        return FOAM_COLORS[name]
    if name == "reed-bridge":
        return _mat.M_PETG_BLACK
    if name == "prv-shroud":
        return _mat.C_SHROUD
    if name == "prv-sv125":
        return _mat.M_BRASS
    if name.startswith("endcap"):
        return _mat.M_STAINLESS
    if name.startswith("vessel-elbow"):
        return _mat.M_STAINLESS
    if name.startswith("collet-"):
        return _mat.M_JG_BLACK_PP
    if name.endswith("-cap"):
        return _mat.C_RES_CAP
    if name.startswith("reservoir"):
        return _mat.C_RESERVOIR
    if name.startswith("copper-plug"):
        return _mat.C_PLUG
    if name.startswith("evap-"):
        return _mat.M_COPPER
    if name.startswith("sparge-silicone"):
        return _mat.C_SILICONE
    if name.startswith("sparge-stone"):
        return _mat.M_SINTERED_SS
    if name.startswith("sparge-"):
        return _mat.M_STAINLESS
    if name.startswith("bulkhead-seal"):
        return _mat.C_SILICONE
    if name.startswith("bulkhead-"):
        return _mat.M_JG_WHITE_PP
    if name.startswith("vent-membrane"):
        return _mat.M_PTFE_WHITE
    if name.startswith("float-rod"):
        return _mat.M_STAINLESS
    if name.startswith("float-"):
        return _mat.M_STAINLESS
    if name.startswith("reed-"):
        return _mat.C_REED
    if name.startswith("probe-"):
        return _mat.M_EPOXY_BLACK
    return _mat.M_STAINLESS
