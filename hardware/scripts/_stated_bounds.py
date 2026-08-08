"""_stated_bounds — the bounds a module states about its own constants, read at import.

A generator's constants carry claims about each other: a screw is long enough for its insert, a
lane is wide enough for its bore, two lanes stand far enough apart for the bodies on them. Those
claims are settled the moment the module is read, before any solid exists — so they have no
assembly to hang a reading on and no build to be measured during. This is the ledger they record
into instead. `enclosure_assembly.carry_stated_bounds` drains it onto the assembly beside the
bounds the machine measures at every build, and `_scorecard._bounds` renders one gate row apiece.

A VIOLATED BOUND IS A THING TO LOOK AT, and what a reader looks at is the STEP, the three
elevations and the scorecard a run writes. A guard that raises at import destroys all four
before the build starts, leaving the only account of the fault in a terminal nobody commits.
So a bound here never stops the module: the constants stand as written, the geometry comes out
as those constants describe it, and the fault is a red row on the committed card carrying the
message the bound wrote — beside the clashes and the open leads the same geometry produces in
`pack-closes` and the rest. Two bodies packed nearer than they are wide come out overlapping,
which the card can show a volume and a location for; a raise can only say so.

An `assert` is the same fault twice over, because `python -O` strips it: build-killing under
one interpreter and absent under another, which is the pair of failure modes a check must not
have. A bound recorded here reads the same either way.

Two entry points, both thin:

    _bounds.state("id", "label", "target", ok, "what went wrong")

for a bound with one reading, and

    room = _bounds.bound("id", "label", "target")
    for name in stations:
        room(clear(name) >= gap, f"{name} stands {clear(name):.2f} mm off its neighbour")

for a bound stated once over a population — one card row, its value the tally, its detail the
notes the failing readings wrote. Both hand back the reading, so a caller whose next line
cannot run on a violated bound can branch on it rather than proceeding into a lookup that
is not there.
"""

from collections import namedtuple

Bound = namedtuple("Bound", "id label ok value target detail")

# Every bound stated so far, in the order the imports stated them. Live objects: a bound over a
# population is appended when it opens and its tally fills in as the readings arrive.
BOUNDS: list = []


class StatedBound:
    """One bound and every reading taken against it.

    `ok` is true while every reading is, `value` tallies them, and `detail` carries the note
    each failing reading wrote — verbatim, because the note is the whole account of the fault
    and the card is where it has to arrive."""

    def __init__(self, id: str, label: str, target: str):
        self.id, self.label, self.target = id, label, target
        self.held = self.total = 0
        self.detail: list = []

    def __call__(self, ok, note: str = "") -> bool:
        """Take one reading. Hands back the reading itself."""
        ok = bool(ok)
        self.total += 1
        if ok:
            self.held += 1
        elif note:
            self.detail.append(note)
        return ok

    @property
    def ok(self) -> bool:
        """A bound with no readings HOLDS. Its population is empty — a table with no stations
        states nothing about them — and that is a different claim from a reading that failed."""
        return self.held == self.total

    @property
    def value(self) -> str:
        if self.total == 1:
            return "holds" if self.ok else "open"
        return f"{self.held}/{self.total} hold"

    def record(self) -> Bound:
        return Bound(self.id, self.label, self.ok, self.value, self.target, list(self.detail))


def bound(id: str, label: str, target: str) -> StatedBound:
    """Open one stated bound and hand back the recorder its readings are taken with."""
    b = StatedBound(id, label, target)
    BOUNDS[:] = [x for x in BOUNDS if x.id != id] + [b]
    return b


def state(id: str, label: str, target: str, ok, note: str = "") -> bool:
    """One bound with a single reading, stated and read in one line."""
    return bound(id, label, target)(ok, note)


def records() -> list:
    """Every stated bound as a plain `Bound` tuple, for a ledger that renders them."""
    return [b.record() for b in BOUNDS]


def report() -> int:
    """The stated bounds, printed — the control a module runs on its own. 0 when every one
    holds, 1 when any is open, so a caller that wants an exit code has one without any of
    them having stopped an import."""
    open_ = [b for b in BOUNDS if not b.ok]
    for b in BOUNDS:
        print(f"  {'OK  ' if b.ok else 'OPEN'} {b.id:28} {b.value:12} {b.label}")
        for line in b.detail:
            print(f"         {line}")
    print(f"\n{len(BOUNDS) - len(open_)}/{len(BOUNDS)} stated bounds hold")
    return 1 if open_ else 0
