"""What a scorecard row is, and the ladder a bend radius is graded on.

Two assemblies write a card — `manifold-layout/_scorecard.py` for the appliance and
`cold-core-layout/_cold_scorecard.py` for the core — and a row means the same thing on both,
so the viewer reads one shape off either sidecar (`web/contracts/scorecard-sidecar.js`).
"""

from dataclasses import dataclass, field


@dataclass
class Check:
    id: str
    label: str
    kind: str            # "gate" | "goal"
    status: str          # "pass" | "fail" | "warn"
    value: str
    target: str
    detail: list = field(default_factory=list)
    active: bool = True


def verdict(ok: bool) -> str:
    return "pass" if ok else "fail"


# Grade bands on `radius ÷ the stock's minimum`. B is the requirement — a run AT its stock's
# floor is buildable and nothing more; A is the room that survives a part moving a millimetre.
GRADE_BANDS = ((1.5, "A"), (1.0, "B"), (0.75, "C"), (0.5, "D"), (0.0, "F"))


def grade_of(ratio: float) -> str:
    return next(g for lo, g in GRADE_BANDS if ratio >= lo)
