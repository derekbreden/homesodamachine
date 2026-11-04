"""Rust source geometry inputs for the maintained installed-wire kernel."""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from hardware.wiring.installed._wiring_data import read as _read


def numbers(routes, stock, *, components=()):
    return _read("wire_numbers", {"routes": routes, "stock": stock, "components": components})


def main():
    import argparse
    import _rust_part
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=ROOT / "hardware/wiring/installed-wire-geometry")
    args = parser.parse_args()
    return _read("build_wire_geometry", {"manifest": str(args.manifest.resolve()), "output": str(args.output.resolve())})


if __name__ == "__main__":
    main()
