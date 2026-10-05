"""Record kinds written to a session's `events.jsonl`: the observation schema.

Every record carries `kind`, `rec` (the writer's sequence number), `mono_ns`
(host `time.monotonic_ns()` of the event) and `wall_ns`. Frames, moves, probe
channels and observations therefore sort onto one monotonic timeline.
`validate()` checks a record against its kind's required fields and the types
of any documented optional fields present; unknown kinds and missing or
mistyped fields are errors. `json_schema()` renders the same definitions as a
JSON Schema document (observation-schema.json beside this package).

Move receipts map the controls `Client.move()` call as follows (see
`controls.receipt_from_client_move`): move_command.issued_mono_ns is stamped
before the call; move_ack.ack_mono_ns is the Client log's host receipt of the
`ack` reply whose `op` is MOVE6 and whose sequence is the move's;
move_complete.complete_mono_ns is the host receipt of the first later reply
whose `completed_seq` is that sequence (the stamp after `move()` returned when
no log is available); status `unverified` marks a move the Client completed
whose log lacks that command, ack or completion; controller_time_us is
the device's `completed_us`; completion_mapped_mono_ns is that device time on
the host clock through the clock map fitted from `clock_exchange` records,
with its uncertainty; reported_counts is the returned status `count`;
driver_state is the `drivers()` rows read after the move; controller holds
every other field of the returned status (state, fault, health, profile,
current_scales, configured_vsense, vsense, microsteps, max_rate, vm_epoch,
timer_ticks). move_ack.vm_epoch and
move_complete.vm_epoch carry the controller's supply epoch, so a supply cycle
between two receipts, and therefore between the frames around them, is visible.
"""

from __future__ import annotations

import math
from numbers import Integral, Real

INT = "int"
NUM = "num"
STR = "str"
BOOL = "bool"
LIST = "list"
DICT = "dict"
OPT = "?"            # suffix: field may be null
COUNTS6 = "counts6"  # six integers
DIR6 = "dir6"        # six values in {-1, 0, 1}

COMMON = {"kind": STR, "rec": INT, "mono_ns": INT, "wall_ns": INT}

KINDS: dict[str, dict[str, str]] = {
    "session_note": {"text": STR, "author": STR},
    "camera": {"camera_id": STR, "unique_id": STR, "name": STR, "role": STR,
               "requested_format": DICT, "source_info": DICT},
    "source_event": {"camera_id": STR, "event": STR, "detail": DICT},
    "optics": {"camera_id": STR, "optics_id": STR, "source": STR, "state": DICT,
               "gate_ok": BOOL, "gate_reasons": LIST, "warnings": LIST, "context": STR},
    "frame": {"camera_id": STR, "seq": INT, "source_seq": INT + OPT, "recv_mono_ns": INT,
              "recv_wall_ns": INT, "device_pts_ns": INT + OPT, "source_host_ns": INT + OPT,
              "codec": STR, "width": INT + OPT, "height": INT + OPT, "bytes": INT,
              "dims_verified": BOOL, "native_4k": BOOL, "stored": BOOL, "file": STR + OPT,
              "measurement": BOOL, "window_id": STR + OPT, "optics_id": STR + OPT,
              "excluded_reasons": LIST},
    "frame_gap": {"camera_id": STR, "after_seq": INT + OPT, "missing_estimate": INT,
                  "evidence": STR, "detail": DICT},
    "measurement_start": {"window_id": STR, "trial_id": STR + OPT, "purpose": STR,
                          "cameras": LIST, "optics_ids": DICT, "measurement": BOOL,
                          "reasons": DICT},
    "measurement_end": {"window_id": STR, "frames": DICT, "optics_unchanged": BOOL + OPT,
                        "changed_fields": DICT, "valid": BOOL, "reasons": LIST},
    "measurement_refused": {"trial_id": STR + OPT, "purpose": STR, "reasons": DICT},
    "move_command": {"cmd_id": STR, "counts": COUNTS6, "duration_us": INT, "purpose": STR,
                     "trial_id": STR + OPT, "backend": STR, "issued_mono_ns": INT,
                     "issued_wall_ns": INT},
    "move_ack": {"cmd_id": STR, "accepted": BOOL, "reason": STR + OPT, "ack_mono_ns": INT,
                 "controller_time_us": INT + OPT},
    "move_complete": {"cmd_id": STR, "status": STR, "complete_mono_ns": INT,
                      "controller_time_us": INT + OPT, "reported_counts": LIST + OPT,
                      "driver_state": LIST + OPT, "fault": STR + OPT},
    "controller_status": {"detail": DICT},
    "clock_exchange": {"host_send_ns": INT, "host_recv_ns": INT, "controller_us": INT},
    "trial_start": {"trial_id": STR, "purpose": STR, "plan": DICT, "direction_state": DIR6},
    "trial_end": {"trial_id": STR, "outcome": STR, "reason": STR + OPT},
    "observation": {"obs_id": STR, "trial_id": STR + OPT, "prev_obs_id": STR + OPT,
                    "cmd_ids": LIST, "t_start_ns": INT, "t_end_ns": INT, "values": DICT,
                    "sigma": DICT, "confidence": DICT, "n_frames": DICT, "frames": DICT,
                    "source": STR, "extractors": DICT},
    "proposal": {"proposal": DICT},
    "probe_sample": {"channel": STR, "value": NUM, "units": STR, "sample_mono_ns": INT,
                     "source": STR},
    "table_encoder": {"counts": INT, "counts_per_rev": INT, "sample_mono_ns": INT,
                      "source": STR},
    "cool_reference": {"channel": STR, "value": NUM, "units": STR, "sample_mono_ns": INT,
                       "source": STR},
}

# Documented optional fields: validated when present.
OPTIONAL: dict[str, dict[str, str]] = {
    "move_command": {"max_rate": INT},
    "move_ack": {"vm_epoch": INT + OPT},
    "frame": {"subtype": STR + OPT},
    "measurement_end": {"gaps": DICT, "pairing": DICT},
    "move_complete": {"error": STR + OPT, "controller": DICT + OPT, "seq": INT + OPT,
                      "backend_issued_mono_ns": INT, "returned_mono_ns": INT, "vm_epoch": INT + OPT,
                      "completion_mapped_mono_ns": INT + OPT, "completion_mapping_uncertainty_ns": NUM + OPT},
    "clock_exchange": {"boot": STR + OPT},
    "observation": {"window_id": STR + OPT, "window_valid": BOOL + OPT, "frames_before_settle": DICT},
    "session_note": {},
}

ENUMS = {
    ("trial_end", "outcome"): {"completed", "aborted", "fault", "failed"},
    ("move_complete", "status"): {"done", "fault", "stopped", "rejected", "timeout",
                                  "unverified", "not_executed"},
    ("move_command", "purpose"): {"probe_jog", "engage", "correction", "reversal_takeup", "return"},
    ("probe_sample", "channel"): {"radial", "axial"},
    ("table_encoder", "source"): {"encoder", "camera_fiducial"},
    ("optics", "source"): {"visca_inquiry", "operator", "none"},
    ("frame", "codec"): {"jpeg", "gray8", "gray16", "nv12"},
}


def _check(value, spec: str) -> bool:
    optional = spec.endswith(OPT)
    base = spec[:-1] if optional else spec
    if value is None:
        return optional
    if base == INT:
        return isinstance(value, Integral) and not isinstance(value, bool)
    if base == NUM:
        return isinstance(value, Real) and not isinstance(value, bool) and math.isfinite(value)
    if base == STR:
        return isinstance(value, str)
    if base == BOOL:
        return isinstance(value, bool)
    if base == LIST:
        return isinstance(value, list)
    if base == DICT:
        return isinstance(value, dict)
    if base == COUNTS6:
        return (isinstance(value, list) and len(value) == 6
                and all(isinstance(v, Integral) and not isinstance(v, bool) for v in value))
    if base == DIR6:
        return isinstance(value, list) and len(value) == 6 and all(v in (-1, 0, 1) for v in value)
    raise ValueError(f"unknown field spec {spec}")


def validate(record: dict) -> list[str]:
    """Return a list of problems; an empty list means the record is valid."""
    errors = []
    kind = record.get("kind")
    if kind not in KINDS:
        return [f"unknown kind {kind!r}"]
    for field, spec in {**COMMON, **KINDS[kind]}.items():
        if field not in record:
            errors.append(f"{kind}: missing {field}")
        elif not _check(record[field], spec):
            errors.append(f"{kind}: {field}={record[field]!r} is not {spec}")
    for field, spec in OPTIONAL.get(kind, {}).items():
        if field in record and not _check(record[field], spec):
            errors.append(f"{kind}: {field}={record[field]!r} is not {spec}")
    for (k, field), allowed in ENUMS.items():
        if k == kind and field in record and record[field] not in allowed:
            errors.append(f"{kind}: {field}={record[field]!r} not in {sorted(allowed)}")
    return errors


def _json_type(spec: str) -> dict:
    optional = spec.endswith(OPT)
    base = spec[:-1] if optional else spec
    t = {INT: {"type": "integer"}, NUM: {"type": "number"}, STR: {"type": "string"},
         BOOL: {"type": "boolean"}, LIST: {"type": "array"}, DICT: {"type": "object"},
         COUNTS6: {"type": "array", "items": {"type": "integer"}, "minItems": 6, "maxItems": 6},
         DIR6: {"type": "array", "items": {"enum": [-1, 0, 1]}, "minItems": 6, "maxItems": 6}}[base]
    return {"anyOf": [t, {"type": "null"}]} if optional else t


def json_schema() -> dict:
    """The record definitions as a JSON Schema (draft 2020-12) document."""
    defs = {}
    for kind, fields in KINDS.items():
        props = {"kind": {"const": kind}}
        for name, spec in {**COMMON, **fields, **OPTIONAL.get(kind, {})}.items():
            if name == "kind":
                continue
            props[name] = _json_type(spec)
            allowed = ENUMS.get((kind, name))
            if allowed:
                props[name] = {**props[name], "enum": sorted(allowed)} if "anyOf" not in props[name] else \
                    {"anyOf": [{"enum": sorted(allowed)}, {"type": "null"}]}
        defs[kind] = {"type": "object", "properties": props,
                      "required": sorted({**COMMON, **fields}), "additionalProperties": True}
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "gpobs/1",
        "title": "Gun-positioner observation session record (events.jsonl line)",
        "description": __doc__.strip(),
        "oneOf": [{"$ref": f"#/$defs/{k}"} for k in KINDS],
        "$defs": defs,
    }
