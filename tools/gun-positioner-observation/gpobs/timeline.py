"""Frames and moves on one host monotonic timeline.

A frame's capture time is its presentation time where the source supplies one
(AVFoundation's, on the host clock), otherwise its receipt time minus a latency
allowance. Receipt time is always later than exposure, so using it unadjusted
would call frames exposed during motion "settled".

Labels, relative to the moves of a session:
    before_first_move   captured before any move was issued
    moving              issued <= t < completion receipt
    settling            completion <= t < completion + settle
    settled             after settle and before the next move was issued
    unknown_move_end    the move has no completion (fault, timeout, crash)
Controller times map onto the host clock with `clock.ClockMap` from the
session's `clock_exchange` records; the completion receipt is used here because
it is never earlier than the device's completion.

`supply_cycles` finds receipts whose controller `vm_epoch` differs from the
previous receipt's: the motor supply changed state somewhere between the two,
and frames captured in that interval are flagged by `frames_in_supply_cycles`.
"""

from __future__ import annotations

from bisect import bisect_right

from .clock import ClockExchange, ClockMap


def capture_time(frame: dict, latency_allowance_ns: int = 100_000_000) -> int:
    if frame.get("device_pts_ns") is not None:
        return frame["device_pts_ns"]
    return frame["recv_mono_ns"] - latency_allowance_ns


def move_intervals(records: list[dict]) -> list[dict]:
    cmds = [r for r in records if r["kind"] == "move_command"]
    done = {r["cmd_id"]: r for r in records if r["kind"] == "move_complete"}
    out = []
    for c in sorted(cmds, key=lambda r: r["issued_mono_ns"]):
        d = done.get(c["cmd_id"])
        out.append({"cmd_id": c["cmd_id"], "issued_ns": c["issued_mono_ns"],
                    "complete_ns": d["complete_mono_ns"] if d else None,
                    "status": d["status"] if d else "missing"})
    return out


def label_frames(frames: list[dict], moves: list[dict], settle_ns: int,
                 latency_allowance_ns: int = 100_000_000) -> dict[tuple[str, int], tuple[str, str | None]]:
    """{(camera_id, seq): (label, cmd_id of the governing move)}."""
    issued = [m["issued_ns"] for m in moves]
    out = {}
    for f in frames:
        t = capture_time(f, latency_allowance_ns)
        i = bisect_right(issued, t) - 1
        if i < 0:
            out[(f["camera_id"], f["seq"])] = ("before_first_move", None)
            continue
        m = moves[i]
        if m["complete_ns"] is None:
            label = "unknown_move_end"
        elif t < m["complete_ns"]:
            label = "moving"
        elif t < m["complete_ns"] + settle_ns:
            label = "settling"
        else:
            label = "settled"
        out[(f["camera_id"], f["seq"])] = (label, m["cmd_id"])
    return out


def settled_frames(frames: list[dict], moves: list[dict], cmd_id: str, settle_ns: int,
                   latency_allowance_ns: int = 100_000_000) -> list[dict]:
    labels = label_frames(frames, moves, settle_ns, latency_allowance_ns)
    return [f for f in frames if labels[(f["camera_id"], f["seq"])] == ("settled", cmd_id)]


def pair_frames(frames_a: list[dict], frames_b: list[dict], max_skew_ns: int,
                latency_allowance_ns: int = 100_000_000) -> list[tuple[dict, dict, int]]:
    """Associate frames of two cameras by capture time, each frame used at most once.

    Returns (frame_a, frame_b, skew_ns) for pairs whose capture times differ by
    at most `max_skew_ns`, in time order. Unpaired frames are left out.
    """
    a = sorted(frames_a, key=lambda f: capture_time(f, latency_allowance_ns))
    b = sorted(frames_b, key=lambda f: capture_time(f, latency_allowance_ns))
    tb = [capture_time(f, latency_allowance_ns) for f in b]
    used = set()
    pairs = []
    for fa in a:
        t = capture_time(fa, latency_allowance_ns)
        k = bisect_right(tb, t)
        best = None
        for j in (k - 1, k):
            if 0 <= j < len(b) and j not in used:
                skew = tb[j] - t
                if abs(skew) <= max_skew_ns and (best is None or abs(skew) < abs(best[1])):
                    best = (j, skew)
        if best is not None:
            used.add(best[0])
            pairs.append((fa, b[best[0]], int(best[1])))
    return pairs


def clock_map_from_records(records: list[dict], boot: str | None = None) -> ClockMap | None:
    ex = [ClockExchange(r["host_send_ns"], r["host_recv_ns"], r["controller_us"])
          for r in records if r["kind"] == "clock_exchange" and (boot is None or r.get("boot") == boot)]
    return ClockMap.fit(ex) if len(ex) >= 2 else None


def supply_cycles(records: list[dict]) -> list[dict]:
    """Intervals between consecutive move receipts whose controller vm_epoch differs."""
    receipts = sorted(((r["ack_mono_ns"] if r["kind"] == "move_ack" else r["complete_mono_ns"], r)
                       for r in records if r["kind"] in ("move_ack", "move_complete") and r.get("vm_epoch") is not None),
                      key=lambda x: x[0])
    out = []
    for (t0, a), (t1, b) in zip(receipts, receipts[1:]):
        if a["vm_epoch"] != b["vm_epoch"]:
            out.append({"after_ns": t0, "before_ns": t1, "from_epoch": a["vm_epoch"], "to_epoch": b["vm_epoch"],
                        "cmd_id": b["cmd_id"]})
    return out


def frames_in_supply_cycles(frames: list[dict], cycles: list[dict],
                            latency_allowance_ns: int = 100_000_000) -> list[tuple[str, int]]:
    """(camera_id, seq) of frames captured inside an interval where the supply epoch changed."""
    hit = []
    for f in frames:
        t = capture_time(f, latency_allowance_ns)
        if any(c["after_ns"] <= t <= c["before_ns"] for c in cycles):
            hit.append((f["camera_id"], f["seq"]))
    return hit
