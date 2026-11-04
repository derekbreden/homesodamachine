"""Scorecard row types and the Rust bend-radius grading ladder."""
from dataclasses import dataclass,field
from _shared_data import call

@dataclass
class Check:
    id: str
    label: str
    kind: str
    status: str
    value: str
    target: str
    detail: list = field(default_factory=list)
    active: bool = True

GRADE_BANDS = tuple(tuple(v) for v in call('scalar.constants',group='card')['GRADE_BANDS'])

def verdict(ok):
    return call('scalar.verdict',ok=bool(ok))

def grade_of(ratio):
    return call('scalar.grade',ratio=ratio,bands=GRADE_BANDS)
