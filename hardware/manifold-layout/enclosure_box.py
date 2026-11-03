"""Write the one placement-derived Box the enclosure producer consumes."""

import sys
from pathlib import Path


_HERE = Path(__file__).resolve()
_ROOT = next(p for p in _HERE.parents if (p / "hardware" / "scripts").is_dir())
sys.path.insert(0, str(_ROOT / "hardware" / "scripts"))
sys.path.insert(0, str(_ROOT / "hardware" / "printed-parts" / "enclosure" / "enclosure"))

import _box_spec  # noqa: E402


def main() -> None:
    from _machine_layout import plan
    from _enclosure_rust_driver import box_from_plan
    enclosure, box = box_from_plan(plan(stage='pack'))
    path = _box_spec.write(box, enclosure.BOUNDS)
    print(f"-> {path.relative_to(_ROOT)}")


if __name__ == "__main__":
    main()
