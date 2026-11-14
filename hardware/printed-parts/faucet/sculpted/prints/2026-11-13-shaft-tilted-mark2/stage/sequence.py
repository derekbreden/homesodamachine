"""Compose the base and its companions from same-stream deposition groups, with lifted entries."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from hashlib import sha256
from pathlib import Path
import argparse
import json
import math
import re

AXES = "XYZ"
WORDS = re.compile(r"([XYZEFIJS])(-?(?:\d+(?:\.\d*)?|\.\d+))")
COURSE = re.compile(r"^; (?:scaffold layer|sloped course|transition course|whole-base course|exterior scaffold layer|underside roof course) (\d+) of (\d+)")
START = "; MACHINE_START_GCODE_END"
END = "; MACHINE_END_GCODE_START"
BASE = 1901
LABELS = {1901: "AQAAAAAAAAA=", 1902: "AgAAAAAAAAA=", 1903: "BAAAAAAAAAA=", 1904: "CAAAAAAAAAA=", 1905: "EAAAAAAAAAA="}
PLATE_PARTS = {1902: "tip", 1903: "display cover", 1904: "mounting plate", 1905: "lever"}


@dataclass
class Modal:
    xyz: tuple[float, float, float] = (0.0, 0.0, 0.0)
    feed: float = 1800.0
    fan: float = 0.0
    acceleration: float = 10000.0
    feature: str = "Custom"
    width: float = 0.42
    bead_height: float = 0.24
    debt: float = 0.8

    def apply(self, text):
        if text.startswith("; FEATURE: "):
            self.feature = text[11:].strip()
        if text.startswith("; LINE_WIDTH: "):
            self.width = float(text.split(":", 1)[1])
        if text.startswith("; LAYER_HEIGHT: "):
            self.bead_height = float(text.split(":", 1)[1])
        line = text.split(";", 1)[0].strip()
        action = line.split(" ", 1)[0]
        if action == "M106":
            w = dict((k, float(v)) for k,v in re.findall(r"([PS])\s*(-?(?:\d+(?:\.\d*)?|\.\d+))", line))
            if w.get("P", 1) == 1:
                self.fan = w["S"]
        if action == "M204" and "S" in line:
            self.acceleration = float(dict(WORDS.findall(line))["S"])
        if action not in {"G0", "G1", "G2", "G3"}:
            return None
        w = {k: float(v) for k,v in WORDS.findall(line)}
        start = self.xyz
        target = tuple(w.get(k, start[j]) for j,k in enumerate(AXES))
        self.xyz = target
        self.feed = w.get("F", self.feed)
        e = w.get("E", 0.0)
        if start == target:
            self.debt = max(0.0, self.debt - e)
            return None
        if e <= 0 or (start[:2] == target[:2] and action in {"G0", "G1"}):
            self.debt = max(0.0, self.debt - e)
            return None
        if self.debt > 1e-6:
            raise ValueError(f"deposition starts retracted by {self.debt:g} at {start}: {text}")
        return start, target, e


@dataclass
class Span:
    lines: list[str]
    group: str
    label: str
    level: float
    object_id: int
    begin: int = -1
    end: int = -1
    lo: list[float] = field(default_factory=lambda: [math.inf]*3)
    hi: list[float] = field(default_factory=lambda: [-math.inf]*3)
    entry: tuple = ()
    exit: tuple = ()
    commands: int = 0
    source_phase: str | None = None
    upper_native_z: float | None = None
    e: float = 0.0

    def note(self, index, modal, move):
        start, target, e = move
        if self.begin == -1:
            self.begin = index
            self.entry = (start, modal.feed, modal.fan, modal.acceleration, modal.feature, modal.width, modal.bead_height)
        self.end = index
        self.exit = target
        for j in range(3):
            self.lo[j] = min(self.lo[j], start[j], target[j])
            self.hi[j] = max(self.hi[j], start[j], target[j])
        self.commands += 1
        self.e += e


def read_staged(lines):
    """Read the authored preamble and the native objects in their original modal contexts."""
    startup = next(i for i,l in enumerate(lines) if l.startswith(START))
    footer = next(i for i,l in enumerate(lines) if l.startswith(END))
    first = next(i for i,l in enumerate(lines[startup:footer], startup) if l.startswith("; CHANGE_LAYER"))
    modal = Modal()
    modal.debt = 0.0                   # native first-layer explicit retraction follows this delimiter
    authored, native = [], []
    seg = None
    group = "startup"
    z = 0.20
    for i in range(first, footer):
        l = lines[i]
        if l.startswith("; ===== sloped underside"):
            group = "scaffold"
            seg = None
        elif l.startswith("; ===== end of the sloped underside"):
            group = "native"
            seg = None
        elif group == "native" and l.startswith("; CHANGE_LAYER"):
            seg = None
        elif group == "native" and l.startswith("; Z_HEIGHT: "):
            z = float(l.split(":")[1])
        elif group == "native" and l.startswith("; start printing object, unique label id: "):
            object_id = int(l.split()[-1])
            seg = Span(lines, "native", PLATE_PARTS.get(object_id, "base"), z, object_id)
            native.append(seg)
        elif group != "native":
            match = COURSE.match(l)
            marker = l[2:].strip()
            if match or marker in {"underside roof", "underside deck bedding"}:
                k = int(match.group(1)) if match else 0
                kind = marker.rsplit(" ", 3)[0] if match else marker
                seg = Span(lines, kind, marker, k, BASE)
                authored.append(seg)
        try:
            move = modal.apply(l)
        except ValueError as error:
            raise ValueError(f"line {i+1}: {error}") from error
        if move is not None:
            if seg is None:
                raise ValueError(f"unowned deposition at {i+1}: {l}")
            seg.note(i, modal, move)
    # The machine warm-up footer is byte-identical. The first actual model move repositions
    # above the purge line before it descends, with the native first-layer retraction consumed once.
    return lines[:first], [s for s in authored if s.begin >= 0], [s for s in native if s.begin >= 0], lines[footer:]


def read_donor(lines):
    modal = Modal()
    spans = []
    seg = None
    phase = "native base along the mounting incline"
    upper_native_z = None
    for i, l in enumerate(lines):
        if l.startswith("; HSM_DONOR_PHASE: "):
            phase = l.split(":", 1)[1].strip()
            upper_native_z = None
        if l.startswith("; HSM_UPPER_NATIVE_Z: "):
            upper_native_z = float(l.split(":", 1)[1])
        if COURSE.match(l):
            seg = Span(lines, "whole base", l[2:].strip(), 0.0, BASE, source_phase=phase, upper_native_z=upper_native_z)
            spans.append(seg)
        if l.startswith("; HSM_NORMAL_Z: "):
            seg.level = float(l.split(":")[1])
        if l.startswith("; HSM_ENTRY_XYZ: "):
            modal = Modal(xyz=tuple(float(v) for v in l.split(":",1)[1].split()))
        if l.startswith("; HSM_ENTRY_RETRACT_MM: "):
            modal.debt = float(l.split(":",1)[1])
        move = modal.apply(l)
        if move is not None:
            seg.note(i, modal, move)
    return [s for s in spans if s.begin >= 0]


def clearance_height(old, entry, terrain):
    """Upper-bound prior height in the conservative swept XY head envelope."""
    xmin = min(old[0], entry[0]) - 30.0
    xmax = max(old[0], entry[0]) + 66.5
    ymin = min(old[1], entry[1]) - 19.0
    ymax = max(old[1], entry[1]) + 99.0
    top = 0.0
    for lo, hi in terrain.values():
        if lo[0] <= xmax and xmin <= hi[0] and lo[1] <= ymax and ymin <= hi[1]:
            top = max(top, hi[2])
    return max(top, old[2], entry[2])


def move_band(out, span, old, terrain):
    """Use the exact start state and keep all motion between the first and last deposit."""
    entry, feed, fan, accel, feature, width, height = span.entry
    high = max(clearance_height(old, entry, terrain)+0.8, 5.0)
    if high > 315.0:
        raise ValueError(f"merge move would exceed travel limit: {high}")
    out.write(f"; HSM_PHASE_TRAVEL: transfer between course groups\n; HSM_NEXT_GROUP: {span.label}\n")
    out.write(f"G1 Z{high:.3f} F900\nG1 X{entry[0]:.5f} Y{entry[1]:.5f} F9000\n")
    out.write(f"G1 Z{entry[2]:.5f} F900\n")
    out.write(f"; HSM_PHASE: {phase_name(span)}\n")
    if span.group != "native":
        out.write(f"; {span.label}\n")
    if span.group == "whole base":
        out.write(f"; HSM_DONOR_PHASE: {span.source_phase}\n")
        if span.upper_native_z is not None:
            out.write(f"; HSM_UPPER_NATIVE_Z: {span.upper_native_z:.5f}\n")
        else:
            out.write(f"; HSM_NORMAL_Z: {span.level:.5f}\n")
    out.write(f"; OBJECT_ID: {span.object_id}\n; start printing object, unique label id: {span.object_id}\n")
    out.write(f"M624 {LABELS[span.object_id]}\n")
    out.write(f"M106 S{fan:g}\nM204 S{accel:g}\nG1 E.8 F1800\nG1 F{feed:.5f}\n")
    out.write(f"; FEATURE: {feature}\n; LINE_WIDTH: {width:g}\n; LAYER_HEIGHT: {height:g}\n")
    suppressed_camera = False
    for line in span.lines[span.begin:span.end+1]:
        if line.startswith("; object ids of layer "):
            if suppressed_camera:
                raise ValueError("nested native camera events")
            suppressed_camera = True
            continue
        if suppressed_camera:
            if line.lstrip().startswith(("G0 ","G1 ","G2 ","G3 ")):
                raise ValueError("native camera callback moves the gantry")
            if line.strip() == "M625":
                suppressed_camera = False
            continue
        if line.startswith(("M73 ", "M991 ", "M1003 ", "M104 ")):
            continue
        if line.lstrip().startswith(("M624", "M625", "M622", "M623", "M971", "M1004")):
            raise ValueError(f"unexpected camera/object delimiter in {span.label}: {line}")
        out.write(line)
    if suppressed_camera:
        raise ValueError(f"unterminated camera event in {span.label}")
    out.write(f"G1 E-.8 F1800\n; stop printing object, unique label id: {span.object_id}\nM625\n")
    return span.exit


def phase_name(span):
    if span.group == "native":
        return "inclined-base conventional handoff" if span.object_id == BASE else "native companions"
    if span.group == "whole base":
        return span.source_phase
    return span.group


def interleave(authored, native, donor):
    """Finish each source's own layer order. Cadence limits how far each front gets ahead."""
    # One free-standing scaffold layer and all four native first layers share the bed and heat.
    first = [s for s in native if s.level <= 0.201]
    if {s.object_id for s in first} != set(PLATE_PARTS):
        raise ValueError("all four companions must have native first courses")
    yield authored[0]
    yield from first
    # Retain each native object's source-ordered toolpaths. The short, front pair can
    # finish while the foot grows. The neighboring tip and cover grow more cautiously.
    early = set(id(s) for s in first)
    back = [s for s in native if s.object_id in {1902, 1903} and id(s) not in early]
    front = [s for s in native if s.object_id in {1904, 1905} and id(s) not in early]
    pending = [s for s in native if s.object_id == BASE]
    bi = fi = 0

    def native_to(back_limit, front_limit):
        nonlocal bi, fi
        elected = []
        while bi < len(back) and back[bi].level <= back_limit:
            elected.append(back[bi])
            bi += 1
        while fi < len(front) and front[fi].level <= front_limit:
            elected.append(front[fi])
            fi += 1
        yield from sorted(elected, key=lambda s: s.begin)

    caps = {5:(0.44,0.44), 9:(0.92,0.92), 14:(1.64,1.64),
            20:(2.36,2.36), 28:(3.08,3.08), 36:(3.56,3.80),
            43:(3.80,4.76), 52:(4.04,5.48), 61:(4.25,6.20)}
    for s in authored[1:]:
        if s.group == "scaffold layer" and s.level in caps:
            back_lim, front_lim = caps[s.level]
            if donor:
                yield from native_to(back_lim,front_lim)
            else:
                yield from native_to(min(back_lim,3.56),min(front_lim,3.56))
        if donor and s.group.startswith("underside roof"):
            # The tall side of the roof builds within the scaffold. The short side still
            # reaches the bed, so the close tip's early height remains capped.
            yield from native_to(4.25 + 0.24*max(s.level-1,0), 6.44 + 0.48*s.level)
        if donor and s.group == "sloped course":
            # Start the short parts' next bands between successive backed foot courses.
            # The head's right-hand lower envelope limits the tip while the foot is low.
            yield from native_to(4.73 + 0.24*(s.level-1), 7.88 + 0.35*(s.level-1))
        yield s

    if not donor:
        yield from sorted(back[bi:] + front[fi:] + pending, key=lambda s: s.begin)
        return
    for i, s in enumerate(donor):
        # Pair short bands of the completed inclined front with the ordinary plate.
        if i % 7 == 0:
            yield from native_to(max(8.0,s.lo[2]+1.0), max(12.20,s.lo[2]+1.0))
        yield s
    yield from sorted(back[bi:] + front[fi:], key=lambda s: s.begin)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("--donor", type=Path)
    args = parser.parse_args()
    source = args.source.read_text().splitlines(keepends=True)
    startup, authored, native, footer = read_staged(source)
    donor = read_donor(args.donor.read_text().splitlines(keepends=True)) if args.donor else []
    if donor:
        native = [s for s in native if s.object_id != BASE]
    if not authored or authored[0].group != "scaffold layer":
        raise ValueError("the authored stream needs a marked first scaffold layer")
    schedule = list(interleave(authored, native, donor))
    want = Counter(id(s) for s in authored + native + donor)
    if Counter(id(s) for s in schedule) != want:
        raise ValueError("each selected group must print once")
    front = Counter()
    result = {"groups": [], "counts_by_phase": {}, "deposition_mm_filament": {}}
    terrain = {}
    model_height = 0.0
    pos = (290.0, -0.5, 6.2)
    heat = 265
    with args.out.open("w") as out:
        out.writelines(startup)
        out.write("M1003 S0\n; HSM_PHASE: whole-plate first layer\n")
        out.write("G1 E-.8 F1800\n")
        for span in schedule:
            if heat == 265 and span.group in {"scaffold layer", "exterior scaffold layer"} and span.level > 1:
                out.write("M109 S280 ; reach regular deposition temperature\n")
                heat = 280
            if span.group == "native":
                tag = span.object_id
                if span.level < front[tag]:
                    raise ValueError("native object course order reversed")
                front[tag] = span.level
            out.write(f"; CHANGE_LAYER\n; Z_HEIGHT: {span.hi[2]:.5f}\n")
            pos = move_band(out, span, pos, terrain)
            lo, hi = terrain.setdefault(span.object_id, (list(span.lo), list(span.hi)))
            for axis in range(3):
                lo[axis] = min(lo[axis], span.lo[axis])
                hi[axis] = max(hi[axis], span.hi[axis])
            model_height = max(model_height, span.hi[2])
            name = phase_name(span)
            result["counts_by_phase"][name] = result["counts_by_phase"].get(name, 0)+1
            e = result["deposition_mm_filament"]
            e[str(span.object_id)] = e.get(str(span.object_id), 0.) + span.e
            result["groups"].append([name, span.label, span.object_id, span.level, span.lo, span.hi])
        end_lift = model_height + 1.2
        out.write(f"; HSM_PHASE_TRAVEL: final clearance lift\nG1 Z{end_lift:.3f} F900\n")
        out.write("M1003 S0\nM106 S0\nM106 P2 S0\nM981 S0 P20000\n; FEATURE: Custom\n")
        end_motion = re.compile(r"^(G[01] Z)([.\d]+)(.*)$")
        if model_height + 0.4 > 245.640001:
            raise ValueError("the actual print rise requires revisiting the native finish positions")
        # Carry the lifted Z into the first native finish position rather than dipping back.
        for line in footer:
            match = end_motion.match(line)
            if match and float(match.group(2)) < end_lift:
                line = f"{match.group(1)}{end_lift:.3f}{match.group(3)}\n"
            out.write(line)
    result["source_gcode_sha256"] = sha256(args.source.read_bytes()).hexdigest()
    if args.donor:
        result["inclined_donor_sha256"] = sha256(args.donor.read_bytes()).hexdigest()
    result["sequenced_gcode_sha256"] = sha256(args.out.read_bytes()).hexdigest()
    args.out.with_suffix(".json").write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k!="groups"}, indent=2))


if __name__ == "__main__":
    main()
