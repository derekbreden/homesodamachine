"""Observation, move-receipt logging and local response learning for the gun positioner.

Every module here records or analyses; none of them can command laser emission.
Axis names, count units, bounds and the correction solver come from the
controls package in `firmware/src_gun_positioner/host/` (see `controls.py`).
Motion is reachable only through a `moves.PositionerBackend` that the caller
selects explicitly: the simulator, the record-only backend, or the thin
adapter over the controls `Client`.
"""

SCHEMA_VERSION = "gpobs/1"
TOOL_VERSION = "1.0"
