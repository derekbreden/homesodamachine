#!/usr/bin/env python3
"""check_show_faces.py — every show face this machine has, fluted or a stated reveal.

    tools/cad-venv/bin/python hardware/scripts/check_show_faces.py
    tools/cad-venv/bin/python hardware/scripts/check_show_faces.py selftest

`check_flutes.py` ASKS THE OTHER HALF OF THIS. It holds an EXISTING payload against the print
it was cut from, so a piece that lost its flutes goes red — and a piece that never had them is
invisible to it, because there is nothing to compare. Which is the question that matters for a
part standing on a counter: not "did the surface survive" but "should this face have carried
the field at all".

WHAT DECIDES IT IS THE FIELD'S OWN ARITHMETIC. `flute_skin._depth_field` ramps on
`smoothstep(far / flute_rise)`, where `far` is how far a station stands from the nearest edge
of the show face. A band's two faces are both edges, so its deepest station stands half the
height from one and reaches `flute_depth` only once that clears `flute_rise` — under
`2 * flute_rise` of run the whole band is ramp and the groove that lands is shallower than the
layer it would have hidden. Every bound below is stated against that one threshold, in the
module that owns the piece.

AND A SECOND REASON BARS SOME FACES AT ANY HEIGHT, which is why the bounds live beside the
geometry rather than in a table here: a gasket land, a mating face and an optical window are
facts about the part and not about the field. The prose at each bound carries them.

THE MODULES ARE NAMED AND NOT WALKED. A bound is recorded when its module is imported
(`_stated_bounds`), so a show piece whose module nobody opens states nothing and reads green by
absence. `SHOW_MODULES` is that list, and adding a piece that carries or refuses the field
means adding it here — which is the one place this check can be wrong, and is a line of code
rather than a habit.
"""

from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
_ROOT = _HERE.parents[2]
sys.path.insert(0, str(_HERE.parent))

import _stated_bounds as _bounds  # noqa: E402

#: Every module that states a bound about a show face, by the piece it owns. The cold core's
#: interface states the core's stack; `faucet_shell` states the counter run the faucet stands
#: on; the two satellites let into the box's faces state their own.
SHOW_MODULES = (
    ("the cold core's stack", "hardware/printed-parts/cold-core", "_cold_core_interface"),
    ("the faucet's counter run", "hardware/printed-parts/faucet/faucet-shell", "faucet_shell"),
    ("the display cover", "hardware/printed-parts/enclosure/display-cover", "display_cover"),
    ("the ceiling panel", "hardware/printed-parts/enclosure/ceiling-panel", "ceiling_panel"),
)


def about_the_field(bound) -> bool:
    """Whether a stated bound is one of these — a rule and not a list.

    A bound this check reports either names the field outright or states that a face is a
    reveal instead of carrying it. Anything else a show module happens to state about its own
    constants is that module's business and belongs on the machine's card, not here."""
    return "flute" in bound.id or bound.id.endswith("-reveal")


def load() -> list:
    """Import every show module and hand back the bounds they recorded."""
    for _what, where, module in SHOW_MODULES:
        sys.path.insert(0, str(_ROOT / where))
        __import__(module)
    return [b for b in _bounds.records() if about_the_field(b)]


def main() -> int:
    seen = load()
    if not seen:
        print("  no show module stated a bound about the field")
        print("  SHOW_MODULES names which modules are asked; none of them answered")
        return 1
    open_ = [b for b in seen if not b.ok]
    for b in seen:
        print(f"  {'ok  ' if b.ok else 'OPEN'} {b.id:24} {b.value:12} {b.label}")
        for line in b.detail:
            print(f"         {line}")
    print(f"\nshow faces: {len(seen) - len(open_)}/{len(seen)} bounds hold over "
          f"{len(SHOW_MODULES)} module(s)")
    return 1 if open_ else 0


def selftest() -> int:
    """The threshold, held both ways against the field's own reach."""
    sys.path.insert(0, str(_ROOT / "hardware/printed-parts/enclosure/enclosure"))
    import _enclosure_interface as _iface

    holds = 0
    ok = True

    def hold(name, got):
        nonlocal holds, ok
        holds += 1
        ok &= bool(got)
        print(f"  {'ok  ' if got else 'FAIL'} {name}")

    reach, depth, rise = _iface.flute_reach, _iface.flute_depth, _iface.flute_rise
    hold("a band with no height takes no groove", reach(0.0) == 0.0)
    hold("a band one rise tall is still all ramp", reach(rise) < depth)
    hold("a hair under the threshold is a hair under full depth",
         reach(2.0 * rise - 0.1) < depth)
    hold("at the threshold the field reaches its full depth", reach(2.0 * rise) >= depth)
    hold("and no taller band takes more than that", reach(40.0) == reach(2.0 * rise))
    hold("the reach rises with the band", reach(3.0) < reach(5.2) < reach(9.9))
    # AND THE READING IS THE ONE THE CUT FIELD GIVES. The sweep that settled these bands cut
    # the box's own field into the built solids and measured what landed: the above-counter
    # plate's 4 mm band came back at 0.422 mm, which is this expression to three decimals.
    hold("it agrees with the field cut into a solid", round(reach(4.0), 3) == 0.422)

    seen = load()
    hold("every show module states at least one bound about the field", len(seen) >= 4)
    hold("and a bound that is not about the field is not reported",
         all(about_the_field(b) for b in seen))
    print(f"check_show_faces selftest {holds}/{holds}" if ok
          else "check_show_faces selftest FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(selftest() if sys.argv[1:] == ["selftest"] else main())
