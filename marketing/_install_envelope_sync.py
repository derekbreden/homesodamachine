"""Read the installation envelope through the Rust document interface."""
import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
_root = _here.parent
sys.path[:0] = [str(_root / "hardware/assembly"), str(_root / "hardware/scripts")]
import _facts
from _rust_docs import evaluate as _evaluate, update as _update

MD = _here / "install-envelope.md"
globals().update(_evaluate("install-envelope", operation="settings")["exports"])
UNIONS = tuple(UNIONS)
BULKHEAD_RINGS = tuple(BULKHEAD_RINGS)


def _inputs():
    facts = _facts.read()
    return {"rear": facts.box.outer[3], "bounds": facts.bodies}


def agreed(what, readings):
    return _evaluate("install-envelope", {"what": what, "readings": readings}, operation="agreed")["exports"]["value"]


def behind_the_rear_face():
    return tuple(_evaluate("install-envelope", _inputs())["exports"]["behind_the_rear_face"])


def main():
    _update("install-envelope", _inputs())


if __name__ == "__main__":
    main()
