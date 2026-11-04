"""Read build-cost and capacity figures from ledger sidecars in Rust."""
import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
_root = _here.parent
sys.path.insert(0, str(_root / "hardware/assembly"))
from _rust_docs import evaluate as _evaluate, update as _update

MD = _here / "target-market.md"
LEDGER = _root / "hardware/ledger"
WANTED = _evaluate("target-market", operation="settings")["exports"]["WANTED"]


def figures(stem):
    return _evaluate("target-market", {"stem": stem}, operation="figures")["exports"]["figures"]


def main():
    _update("target-market")


if __name__ == "__main__":
    main()
