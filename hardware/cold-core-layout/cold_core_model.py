"""Materialize the cold core's fine source-frame geometry for machine composition."""
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
_ROOT = next(p for p in _HERE.parents if (p / "hardware" / "scripts").is_dir())
sys.path.insert(0, str(_ROOT / "hardware" / "scripts"))

if __name__ == "__main__":
    import meshcad
    meshcad.activate()

import cold_core_assembly as core


def main():
    path = core.write_model(core.build_assembly())
    print(f"-> {path.relative_to(_ROOT)}")


if __name__ == "__main__":
    main()
