"""Merge the previous base and hardware with the current cover and shoulder courses."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from hashlib import sha256
import json
import math
from pathlib import Path
import re

START = '; MACHINE_START_GCODE_END'
END = '; MACHINE_END_GCODE_START'
LAYER = '; CHANGE_LAYER'
HEIGHT = '; Z_HEIGHT: '
PHASE = '; HSM_PHASE: '
TIP_PHASE = '; HSM_TIP_PHASE: '
TIP_COURSE = '; HSM_TIP_COURSE: '
TIP_BAND = '; HSM_TIP_BAND_Z: '
PLATE_RING = '; HSM_PLATE_RING_Z: '
ENTRY = '; HSM_ENTRY_XYZ: '
DEBT = '; HSM_ENTRY_RETRACT_MM: '
NEXT_GROUP = '; HSM_NEXT_GROUP: '
OBJECT = '; start printing object, unique label id: '
STOP = '; stop printing object, unique label id: '
END_LIFT = '; HSM_PHASE_TRAVEL: final clearance lift'
WORDS = re.compile(r'([XYZEFSIJP])\s*(-?(?:\d+(?:\.\d*)?|\.\d+))')
Z_MOVE = re.compile(r'^(G[01] Z)([.\d]+)(.*)$')
LEVEL_BOX = re.compile(r'^(\s*G29 A[12] O )X([-\d.]+) Y([-\d.]+) I([-\d.]+) J([-\d.]+)( R\s*)$')
MOTION = ('G0', 'G1', 'G2', 'G3')
BASE, TIP, COVER, PLATE, LEVER = 1901, 1902, 1903, 1904, 1905
MASK = dict(zip((BASE, TIP, COVER, PLATE, LEVER), ('AQ', 'Ag', 'BA', 'CA', 'EA')))
NAME = {BASE: 'base', TIP: 'tip', COVER: 'display cover', PLATE: 'mounting plate', LEVER: 'lever'}
BASELINE_Z_LIFT = 1.2
BED_LAYER = .2


@dataclass
class Modal:
    xyz: tuple[float, float, float] = (0., 0., 0.)
    feed: float = 1800.
    fan: float = 0.
    acceleration: float = 10000.
    feature: str = 'Custom'
    width: float = .42
    height: float = .24
    debt: float = 0.

    def apply(self, line):
        action = line.split(' ', 1)[0].strip()
        if action in MOTION:
            return self.motion(line, action)
        if line.startswith('; FEATURE: '):
            self.feature = line[11:].strip()
        elif line.startswith('; LINE_WIDTH: '):
            self.width = float(line.split(':', 1)[1])
        elif line.startswith('; LAYER_HEIGHT: '):
            self.height = float(line.split(':', 1)[1])
        elif action == 'M106':
            words = arguments(line)
            if words.get('P', 1) == 1:
                self.fan = words['S']
        elif action == 'M204' and line.startswith('M204 S'):
            self.acceleration = arguments(line)['S']
        return None

    def motion(self, line, action):
        w = arguments(line)
        start = self.xyz
        self.xyz = tuple(w.get(axis, start[i]) for i, axis in enumerate('XYZ'))
        self.feed = w.get('F', self.feed)
        e = w.get('E', 0.)
        if e <= 0 or (start[:2] == self.xyz[:2] and action in {'G0', 'G1'}):
            self.debt = max(0., self.debt - e)
            return None
        if self.debt > 1e-5:
            raise ValueError(f'Extrusion starts with {self.debt:g} mm retract debt at {start}: {line}')
        return start, self.xyz, e


@dataclass
class Band:
    tape: list[str]
    label: str
    phase: str
    obj: int
    z: float
    line: int
    start: int = -1
    end: int = -1
    entry: tuple = ()
    exit: tuple = ()
    lo: list[float] = field(default_factory=lambda: [math.inf]*3)
    hi: list[float] = field(default_factory=lambda: [-math.inf]*3)
    metadata: list[str] = field(default_factory=list)
    e: float = 0.
    roads: int = 0
    tip_band: float | None = None

    def note(self, index, modal, move):
        start, target, e = move
        if self.start < 0:
            self.start = index
            self.entry = (start, modal.feed, modal.fan, modal.acceleration, modal.feature, modal.width, modal.height)
        self.end = index
        self.exit = target
        for axis in range(3):
            self.lo[axis] = min(self.lo[axis], start[axis], target[axis])
            self.hi[axis] = max(self.hi[axis], start[axis], target[axis])
        self.e += e
        self.roads += 1

    @property
    def first_bed_course(self):
        return abs(self.lo[2] - BED_LAYER) < .0001 and abs(self.hi[2] - BED_LAYER) < .0001


def arguments(line):
    return {key: float(value) for key, value in WORDS.findall(line.split(';', 1)[0])}


def body(tape):
    first = next(i for i, line in enumerate(tape) if line.startswith(START))
    last = next(i for i, line in enumerate(tape) if line.startswith(END))
    return first+1, last


def read_reference(tape):
    """Read phase and physical stream order from the previous executable archive."""
    _, last = body(tape)
    first = next(i for i, line in enumerate(tape) if line.startswith(LAYER))
    start = next(i for i, line in enumerate(tape[:first]) if line.startswith('M1003 S0'))
    modal = Modal(xyz=(290., -.5, 6.2), debt=.8)
    bands, metadata = [], []
    band = None
    z = 0.
    label = phase = ''
    for i in range(first, last):
        line = tape[i]
        if line.startswith(END_LIFT):
            break
        if line.startswith(LAYER):
            band = None
            metadata = []
            label = phase = ''
        elif line.startswith(HEIGHT):
            z = float(line[len(HEIGHT):])
        elif line.startswith(NEXT_GROUP):
            label = line[len(NEXT_GROUP):].strip()
        elif line.startswith(PHASE):
            phase = line[len(PHASE):].strip()
        elif line.startswith(OBJECT):
            obj = int(line[len(OBJECT):])
            if not phase or not label:
                raise ValueError(f'Prior band lacks phase/label at {i+1}')
            band = Band(tape, label, phase, obj, z, i, metadata=metadata)
            bands.append(band)
        elif line.startswith(STOP):
            band = None
        elif phase and band is None and line.startswith('; ') and not line.startswith('; OBJECT_ID: '):
            metadata.append(line)
        move = modal.apply(line)
        if move is not None:
            if band is None:
                raise ValueError(f'Prior archive has unlabeled extrusion at {i+1}')
            band.note(i, modal, move)
    if not bands or any(band.start < 0 for band in bands):
        raise ValueError('Prior archive has an empty or missing object span')
    return tape[:start], bands, tape[last:]


def read_native(tape):
    """Match exact sliced cover and native continuation of the tip on the new plate."""
    first, last = body(tape)
    modal = Modal(xyz=(290., -.5, 6.2))
    bands = []
    band = None
    z = 0.
    for i in range(first, last):
        line = tape[i]
        if line.startswith(HEIGHT):
            z = float(line[len(HEIGHT):])
        elif line.startswith(OBJECT):
            obj = int(line[len(OBJECT):])
            phase = 'native tip upper' if obj == TIP else 'native display cover'
            band = Band(tape, NAME[obj], phase, obj, z, i)
            if obj in {TIP, COVER}:
                bands.append(band)
        elif line.startswith(STOP):
            band = None
        move = modal.apply(line)
        if move is not None and band is not None and band.obj in {TIP, COVER}:
            band.note(i, modal, move)
    return [band for band in bands if band.start >= 0]


def read_custom(tape, obj=TIP):
    """Read author-labeled tip or counterbore bands and their modal starts."""
    modal = Modal(debt=.8)
    bands = []
    band = None
    phase = ''
    for i, line in enumerate(tape):
        if line.startswith(TIP_PHASE):
            phase = line[len(TIP_PHASE):].strip()
        elif line.startswith(TIP_COURSE):
            if not phase:
                raise ValueError('Tip course appears before its phase declaration')
            course = line[len(TIP_COURSE):].strip()
            band = Band(tape, f'{phase} course {course}', phase, obj, 0., i, metadata=[line])
            bands.append(band)
        elif line.startswith(PLATE_RING):
            z = float(line[len(PLATE_RING):])
            phase = 'mounting plate counterbore supports'
            band = Band(tape, f'{phase} at Z{z:g}', phase, obj, z, i, metadata=[line])
            bands.append(band)
        elif line.startswith(ENTRY):
            modal = Modal(xyz=tuple(float(p) for p in line[len(ENTRY):].split()), debt=.8)
        elif line.startswith(DEBT):
            modal.debt = float(line[len(DEBT):])
        elif line.startswith(TIP_BAND):
            band.tip_band = float(line[len(TIP_BAND):])
            band.metadata.append(line)
        elif band is not None and band.start < 0 and line.startswith('; HSM_TIP_'):
            band.metadata.append(line)
        move = modal.apply(line)
        if move is not None:
            if band is None:
                raise ValueError(f'Tip donor has unlabeled extrusion at {i+1}')
            band.note(i, modal, move)
    for band in bands:
        if obj == PLATE and abs(band.z-band.hi[2]) > 1e-5:
            raise ValueError(f'Actual ring Z differs from declared Z in {band.label}')
        band.z = band.hi[2]
        if band.start < 0:
            raise ValueError(f'Empty tip band {band.label}')
    return bands


def tip_bands(scaffold, model, native):
    """Grow the scaffold and its model anchor before each dependent interface band."""
    if not scaffold and not model:
        return native
    if not scaffold:
        return model+native
    combined = scaffold + model
    if any(band.tip_band is not None for band in combined):
        early = [band for band in combined if band.tip_band is None]
        if any(band.phase != 'tip shoulder scaffold' and 'anchor' not in band.phase for band in early):
            raise ValueError('Every dependent shoulder group must have a band height')
        staged = sorted((band for band in combined if band.tip_band is not None), key=lambda band: band.tip_band)
        return sorted(early, key=lambda band: band.z) + staged + native
    roof = next((i for i, band in enumerate(scaffold) if 'roof' in band.phase), len(scaffold))
    anchor = next((i for i, band in enumerate(model) if 'anchor' not in band.phase), len(model))
    early = sorted(scaffold[:roof] + model[:anchor], key=lambda band: band.z)
    return early + scaffold[roof:] + model[anchor:] + native


def interleave(reference, replacements, plate_rings=()):
    """Use the previous plate's scheduling windows and keep the cover under the tip's travel envelope."""
    queues = {obj: list(bands) for obj, bands in replacements.items()}
    pending_first = {obj: [band for band in bands if band.first_bed_course] for obj, bands in queues.items()}
    for obj, bands in queues.items():
        first = pending_first[obj]
        if not first or bands[:len(first)] != first:
            raise ValueError(f'{NAME[obj]} does not start with its whole first bed layer')
        queues[obj] = bands[len(first):]
    i = Counter()
    first_obj = set()
    cursors = defaultdict(float)
    rings = iter(plate_rings)
    ring = next(rings, None)
    tip_floor = [math.inf]
    for candidate in reversed(queues[TIP]):
        tip_floor.append(min(candidate.lo[2], tip_floor[-1]))
    tip_floor.reverse()

    def through(obj, cap):
        bands = queues[obj]
        while i[obj] < len(bands) and bands[i[obj]].z <= cap + 1e-4:
            yield bands[i[obj]]
            i[obj] += 1

    def cover_limit():
        # The tip's right hotend can overfly the cover. Restrict the cover at each
        # visit by the lowest remaining tip deposition and the prior base cadence.
        return min(cursors[COVER], max(BED_LAYER, tip_floor[i[TIP]] + .6))

    for band in reference:
        if band.obj not in queues:
            if band.obj == PLATE:
                while ring is not None and ring.z <= band.z + 1e-4:
                    yield ring
                    ring = next(rings, None)
            yield band
            continue
        obj = band.obj
        if obj not in first_obj:
            first_obj.add(obj)
            yield from pending_first[obj]
        cursors[obj] = max(cursors[obj], band.z)
        if band.first_bed_course:
            continue
        if obj == COVER:
            yield from through(COVER, cover_limit())
            continue
        for candidate in through(TIP, cursors[TIP]):
            yield from through(COVER, cover_limit())
            yield candidate
    for obj, bands in queues.items():
        if not bands[i[obj]:]:
            continue
        pending = bands[i[obj]:]
        if pending[0].z < cursors[obj] - 3.:
            raise ValueError(f'Scheduling delays {pending[0].label} beneath the completed plate')
        yield from pending
    if ring is not None:
        raise ValueError('Counterbore support is taller than all mounting-plate courses')


def clearance(old, entry, terrain):
    """Lift over deposited stock in the rectangular swept left-active head envelope."""
    limits = (
        min(old[0], entry[0])-30., max(old[0], entry[0])+66.5,
        min(old[1], entry[1])-19., max(old[1], entry[1])+99.,
    )
    xmin, xmax, ymin, ymax = limits
    return max([old[2], entry[2]] + [
        hi[2] for lo, hi in terrain.values()
        if lo[0] <= xmax and xmin <= hi[0] and lo[1] <= ymax and ymin <= hi[1]
    ])


def emit_band(out, band, old, terrain):
    entry, feed, fan, acceleration, feature, width, height = band.entry
    lift = max(5., clearance(old, entry, terrain) + .8)
    if lift > 315.:
        raise ValueError(f'Lift exceeds the machine travel space: {lift}')
    out.write(f'{LAYER}\n{HEIGHT}{band.hi[2]:.5f}\n')
    out.write(f'; HSM_PHASE_TRAVEL: transfer between course groups\n{NEXT_GROUP}{band.label}\n')
    out.write(f'G1 Z{lift:.3f} F900\nG1 X{entry[0]:.5f} Y{entry[1]:.5f} F9000\nG1 Z{entry[2]:.5f} F900\n')
    out.write(f'{PHASE}{band.phase}\n')
    out.writelines(band.metadata)
    out.write(f'; OBJECT_ID: {band.obj}\n{OBJECT}{band.obj}\nM624 {MASK[band.obj]}AAAAAAAAA=\n')
    out.write(f'M106 S{fan:g}\nM204 S{acceleration:g}\nG1 E.8 F1800\nG1 F{feed:.5f}\n')
    out.write(f'; FEATURE: {feature}\n; LINE_WIDTH: {width:g}\n; LAYER_HEIGHT: {height:g}\n')
    camera = False
    for line in band.tape[band.start:band.end+1]:
        if line.startswith('; object ids of layer '):
            if camera:
                raise ValueError(f'Nested camera event in {band.label}')
            camera = True
            continue
        if camera:
            if line.lstrip().startswith(('G0 ', 'G1 ', 'G2 ', 'G3 ')):
                raise ValueError('Native camera callback contains a gantry move')
            if line.strip() == 'M625':
                camera = False
            continue
        if line.startswith(('M73 ', 'M991 ', 'M1003 ', 'M104 ')):
            continue
        if line.lstrip().startswith(('M624', 'M625', 'M622', 'M623', 'M971', 'M1004')):
            raise ValueError(f'Unexpected nested object or camera command in {band.label}: {line}')
        out.write(line)
    if camera:
        raise ValueError(f'Unterminated camera event in {band.label}')
    out.write(f'G1 E-.8 F1800\n{STOP}{band.obj}\nM625\n')
    return band.exit


def emit(output, startup, scheduled, footer):
    counts = Counter()
    filament = Counter()
    roads = Counter()
    terrain = {}
    pos = (290., -.5, 6.2)
    first_bed = set()
    heated = False
    groups = []
    with output.open('w') as out:
        out.writelines(startup)
        out.write(f'M1003 S0\n{PHASE}whole-plate first layer\nG1 E-.8 F1800\n')
        for band in scheduled:
            if not heated and not band.first_bed_course:
                if first_bed != set(NAME):
                    raise ValueError(f'First bed course is missing {set(NAME)-first_bed}')
                out.write('M109 S280 ; reach regular deposition temperature\n')
                heated = True
            if band.first_bed_course:
                if heated:
                    raise ValueError(f'Unexpected second start on the bed in {band.label}')
                first_bed.add(band.obj)
            pos = emit_band(out, band, pos, terrain)
            lo, hi = terrain.setdefault(band.obj, (list(band.lo), list(band.hi)))
            for axis in range(3):
                lo[axis] = min(lo[axis], band.lo[axis])
                hi[axis] = max(hi[axis], band.hi[axis])
            counts[band.phase] += 1
            filament[band.obj] += band.e
            roads[band.obj] += band.roads
            groups.append([band.phase, band.label, band.obj, band.z, band.lo, band.hi, band.line+1])
        top = max(bounds[1][2] for bounds in terrain.values())
        lifted = top + BASELINE_Z_LIFT
        if lifted >= 247.24:
            raise ValueError(f'Print height conflicts with inherited finish motion: {top}')
        out.write(f'{END_LIFT}\nG1 Z{lifted:.3f} F900\n')
        out.write('M1003 S0\nM106 S0\nM106 P2 S0\nM981 S0 P20000\n; FEATURE: Custom\n')
        for line in footer:
            match = Z_MOVE.match(line)
            if match and float(match[2]) < lifted:
                line = f'{match[1]}{lifted:.3f}{match[3]}\n'
            out.write(line)
    return {'counts_by_phase': counts, 'deposition_mm_filament': filament, 'deposition_roads': roads,
            'groups': groups, 'bounds_by_object_mm': terrain, 'sequenced_gcode_sha256': checksum(output)}


def leveling(startup, native, schedule):
    """Keep the proven launch sequence and include emitted contacts in its leveling window."""
    boxes = [m for line in startup+native[:2000] if (m := LEVEL_BOX.match(line))]
    if len(boxes) != 4:
        raise ValueError('Each complete stock startup must expose both bed leveling windows')
    origin = [min(float(m[2+i]) for m in boxes) for i in range(2)]
    upper = [max(float(m[2+i])+float(m[4+i]) for m in boxes) for i in range(2)]
    # The previous custom scaffold already uses the accepted bed compensation. Use only
    # new bed deposition to widen its window. The stock slice already covers same-group brims.
    for band in schedule:
        if band.obj not in {TIP, COVER} or not band.first_bed_course:
            continue
        for axis in range(2):
            origin[axis] = min(origin[axis], band.lo[axis])
            upper[axis] = max(upper[axis], band.hi[axis])
    old = next(m for line in startup if (m := LEVEL_BOX.match(line)))
    bounds = [*origin, *(upper[i]-origin[i] for i in range(2))]
    if any(abs(a-float(b)) > 1e-4 for a, b in zip(bounds, old.groups()[1:5])):
        def replace(line):
            match = LEVEL_BOX.match(line)
            if not match:
                return line
            terms = ' '.join(f'{word}{val:.5f}' for word,val in zip('XYIJ', bounds))
            return f'{match[1]}{terms}{match[6]}'
        startup = [replace(line) for line in startup]
    return startup, [origin, upper]


def checksum(path):
    return sha256(path.read_bytes()).hexdigest()


def lines(path):
    return path.read_text().splitlines(keepends=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('reference', type=Path)
    parser.add_argument('native', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--tip-scaffold', type=Path)
    parser.add_argument('--tip-model', type=Path)
    parser.add_argument('--plate-rings', type=Path)
    parser.add_argument('--tip-native-start-z', type=float, default=BED_LAYER)
    parser.add_argument('--entire-tip-custom', action='store_true')
    args = parser.parse_args()
    startup, reference, footer = read_reference(lines(args.reference))
    native_tape = lines(args.native)
    native = read_native(native_tape)
    if args.entire_tip_custom:
        if args.tip_model is None:
            raise ValueError('A complete tip replacement needs a custom model tape')
        tip = []
    else:
        tip = [band for band in native if band.obj == TIP and band.z >= args.tip_native_start_z-1e-5]
        if not tip or abs(tip[0].z - args.tip_native_start_z) > 1e-5:
            raise ValueError('The selected native tip continuation does not start on a donor layer')
    scaffold = read_custom(lines(args.tip_scaffold)) if args.tip_scaffold else []
    model = read_custom(lines(args.tip_model)) if args.tip_model else []
    rings = read_custom(lines(args.plate_rings), PLATE) if args.plate_rings else []
    if any(left.z >= right.z for left, right in zip(rings, rings[1:])):
        raise ValueError('Counterbore support courses must follow increasing Z')
    replacements = {TIP: tip_bands(scaffold, model, tip), COVER: [band for band in native if band.obj == COVER]}
    schedule = list(interleave(reference, replacements, rings))
    wanted = replacements[TIP]+replacements[COVER]+rings+[band for band in reference if band.obj not in replacements]
    if Counter(map(id, schedule)) != Counter(map(id, wanted)):
        raise ValueError('The sequence must emit each selected band once')
    startup, level_box = leveling(startup, native_tape, schedule)
    result = emit(args.output, startup, schedule, footer)
    source_hashes = {'reference': checksum(args.reference), 'native': checksum(args.native)}
    custom_sources = {'tip_scaffold': args.tip_scaffold, 'tip_model': args.tip_model, 'plate_rings': args.plate_rings}
    source_hashes.update({k: checksum(p) for k, p in custom_sources.items() if p})
    result['source_gcode_sha256'] = source_hashes
    result['first_native_tip_z_mm'] = args.tip_native_start_z if tip else None
    result['stock_leveling_window_xy_mm'] = level_box
    args.output.with_suffix('.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'groups'}, indent=2))


if __name__ == '__main__':
    main()
