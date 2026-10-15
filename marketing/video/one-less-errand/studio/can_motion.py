"""Absolute-time blocking for the can-carrying routine.

The physical can and case never change size. ``can_actions`` on a story scene
can place contacts and removals on the recorded voice clock. All times are
seconds local to the scene. A repeat cycle has ``remove: [start, end]`` and
``restock: [start, end]``; ``final_remove`` clears the last case before the
question. The picture renderer and sound editor can use the same contact time.
"""
from __future__ import annotations

import math


SHOTS = ("case", "car", "kitchen", "shelf", "repeat", "question")


def ease(value: float) -> float:
    p = min(1.0, max(0.0, value))
    return p*p*(3-2*p)


def progress(time: float, start: float, end: float) -> float:
    if end <= start:
        return float(time >= end)
    return ease((time-start)/(end-start))


def span(actions, name, fallback):
    value = actions.get(name, fallback)
    if not isinstance(value, (tuple, list)) or len(value) != 2:
        raise ValueError(f"{name} must contain a start and end in local seconds")
    return tuple(float(item) for item in value)


def removal_offsets(time, interval):
    """Twelve full-size cans leave the shelf, foreground first."""
    start, end = interval
    spacing = max(.01, end-start)/15
    travel = max(.07, (end-start)-11*spacing)
    result = []
    for index in range(12):
        p = progress(time, start+index*spacing, start+index*spacing+travel)
        # Lift clear of the carton fold before advancing. Each column keeps
        # its own lane; the front row always leads the row behind it.
        lift = progress(p,0.0,.18)
        advance = progress(p,.18,1.0)
        # Once beyond the camera frustum, the can can be culled. No dissolve
        # or scale animation participates in its departure.
        result.append((p > .995, (0.0,-.80*advance,.030*lift)))
    return result


def state(shot: str, time: float, duration: float, actions=None):
    if shot not in SHOTS:
        raise ValueError(f"Unknown routine shot: {shot}")
    if duration <= 0 or not math.isfinite(time) or not math.isfinite(duration):
        raise ValueError("Time must be finite and duration positive")
    actions = actions or {}
    time = max(0.0, time)
    result = {"context": "shelf" if shot in ("repeat", "question") else shot,
              "context_offset": (0.0, 0.0, 0.0), "expand": 1.0, "packs": []}
    still_cans = [(False, (0.0, 0.0, 0.0)) for _ in range(12)]
    if shot == "question":
        return result
    if shot != "repeat":
        contact = float(actions.get("contact", min(.36, duration*.30)))
        if shot == "case":
            result["expand"] = progress(time, *span(actions, "expand", (0.0, duration*.66)))
            # A can on the cobalt stage becomes a case. The basket enters
            # below its loading arc; the carton clears the rim before the
            # declared landing, rather than passing through a steel wire.
            lift_start, crest = max(0.0, contact-.85), max(0.0, contact-.30)
            if time < crest:
                z = -.065+.245*progress(time,lift_start,crest)
            else:
                fall = min(1.0,max(0.0,(time-crest)/max(.001,contact-crest)))
                z = .180*(1-fall*fall)
            arrival = progress(time,max(0.0,contact-.68),max(0.0,contact-.19))
            result["context_offset"] = (.66*(1-arrival),0.0,0.0)
        else:
            # A short, grounded final set-down. The next context cuts to the
            # same physical pack, not to a miniature replacement.
            p = min(1.0, time/max(contact, .001))
            z = .032*(1-p*p) if p < 1.0 else 0.0
        result["packs"] = [{"index": 0, "offset": (0.0, 0.0, z), "cans": still_cans}]
        return result

    cycles = actions.get("cycles")
    if cycles is None:
        cycles = [
            {"remove": [duration*.01, duration*.18], "restock": [duration*.22, duration*.31]},
            {"remove": [duration*.33, duration*.48], "restock": [duration*.51, duration*.60]},
            {"remove": [duration*.63, duration*.77], "restock": [duration*.80, duration*.87]},
        ]
    arrivals = [None] + [span(cycle, "restock", (0.0, 0.0)) for cycle in cycles]
    removals = [span(cycle, "remove", (0.0, 0.0)) for cycle in cycles]
    removals.append(span(actions, "final_remove", (duration*.90, duration*.98)))
    for index, (arrival, removal) in enumerate(zip(arrivals, removals)):
        if arrival and time < arrival[0]:
            continue
        entering = progress(time, *arrival) if arrival else 1.0
        next_arrival = arrivals[index+1] if index+1 < len(arrivals) else None
        # The carton leaves after its final can; the next loaded carton
        # enters from the other side and settles at precisely the same mark.
        exit_start = removal[1]
        exit_end = next_arrival[0] if next_arrival else duration
        if exit_end <= exit_start:
            exit_end = exit_start+.08
        leaving = progress(time, exit_start, exit_end)
        if leaving >= .999:
            continue
        x = .64*(1-entering)-.64*leaving
        # Use the open front of the refrigerator, clearing its side returns
        # before crossing them laterally. The low arch also clears the trim.
        y = -.36*((1-entering)+leaving)
        z = .016*math.sin(math.pi*entering) if entering < 1 else 0.0
        if leaving > 0:
            z += .016*math.sin(math.pi*leaving)
        result["packs"].append({"index": index, "offset": (x, y, z),
                                 "cans": removal_offsets(time, removal)})
    return result


def contacts(shot: str, duration: float, actions=None):
    """Picture contacts for a sound editor, in local seconds."""
    actions = actions or {}
    if shot == "repeat":
        cycles = actions.get("cycles", [])
        return [(float(cycle["restock"][1]), f"case_restock_{index+1}")
                for index, cycle in enumerate(cycles)]
    if shot in ("case", "car", "kitchen", "shelf"):
        return [(float(actions.get("contact", min(.36, duration*.30))), f"case_{shot}")]
    return []
