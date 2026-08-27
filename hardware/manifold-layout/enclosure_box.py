"""Write the one placement-derived Box consumed by both enclosure producers."""

import sys
import tempfile
from pathlib import Path


_HERE = Path(__file__).resolve()
_ROOT = next(p for p in _HERE.parents if (p / "hardware" / "scripts").is_dir())
sys.path.insert(0, str(_ROOT / "hardware" / "scripts"))
sys.path.insert(0, str(_ROOT / "hardware" / "printed-parts" / "enclosure" / "enclosure"))

import _box_spec  # noqa: E402
import enclosure as _enc  # noqa: E402
import enclosure_assembly as _assembly  # noqa: E402


def main() -> None:
    _machine, _pack, box = _assembly.machine()
    box = _enc.documented(box)
    # Exercise the actual description, including its nested lists, ordered dictionaries and
    # named records, before publishing it as another action's input.
    with tempfile.TemporaryDirectory(prefix="hsm-enclosure-box-") as directory:
        probe = Path(directory) / "enclosure-box.json"
        _box_spec.write(box, _enc.BOUNDS, probe)
        restored, bounds = _box_spec.read(
            _enc.Box, _enc.Bound, (_enc.Pack, _enc.PortField, _enc.Nameplate), probe)
        if repr(restored) != repr(box) or repr(bounds) != repr(tuple(_enc.BOUNDS)):
            raise ValueError("enclosure-box serialization changed the live placement description")
    path = _box_spec.write(box, _enc.BOUNDS)
    print(f"-> {path.relative_to(_ROOT)}")


if __name__ == "__main__":
    main()
