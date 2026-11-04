"""
Coil winding mandrel.

Hollow PETG cylinder for hand-winding 1/4" OD copper around the 5"
round 316L carbonator. [5 mm](WALL) solid PETG wall, with a shallow
helical guide groove [1 mm](GROOVE_DEPTH) deep that cradles the copper.

The undersized groove is a rough-forming aid. Feed material from the long
ends while setting the finished diameter, pitch and turn count on the vessel
fixture. EVAP-01 and cold-core-layout/_coil.py define the production coil,
including its opposite tangent exits and complete R15 tail forms.

The Rust cold-core scalar recipe derives the winding dimensions and stub
allowances. This interface supplies them to the part program and Python readers;
`coil_mandrel.rs` cuts the STEP, payload and STL on the kernel.
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve()
sys.path.insert(
    0,
    str(next(p for p in _here.parents if p.name == "hardware") / "scripts"),
)
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "printed-parts") / "cadlib"))
sys.path.insert(0, str(_here.parents[1]))
if __name__ == "__main__":
    import _rust_part
    _rust_part.start()

from docgen import substitute_py_comments
from _cold_core_interface import evap_tail_low_z, evap_tail_high_z


_layout = next(p for p in _here.parents if p.name == "hardware") / "cold-core-layout"
if str(_layout) not in sys.path:
    sys.path.insert(0, str(_layout))
from _cold_core_data import read as _read


def _recipe(op, **inputs):
    return _read(op, evap_tail_low_z=evap_tail_low_z,
                 evap_tail_high_z=evap_tail_high_z, **inputs)


globals().update(_recipe("mandrel"))
for _name in ("mandrel_r_range", "mandrel_z_range", "lower_handle_z_range",
              "wind_z_range", "upper_handle_z_range"):
    globals()[_name] = tuple(globals()[_name])


def __getattr__(name):
    if name in {"M_PETG_BLACK", "linear"}:
        import _materials
        return getattr(_materials, name)
    raise AttributeError(name)


def numbers():
    """What `coil_mandrel.rs` cuts the mandrel from, and the body's name and colour."""
    from _materials import M_PETG_BLACK, linear
    return _recipe("mandrel-numbers", color=list(linear(M_PETG_BLACK)))


def main():
    print(_recipe("mandrel-report"), end="")

    said = _rust_part.cut("cold-core", "coil-mandrel", numbers(), _here.parent)
    body = said["bodies"][0]
    (xmin, ymin, zmin), (xmax, ymax, zmax) = body["min"], body["max"]
    print(f"\nResult: X[{xmin:.1f},{xmax:.1f}] Y[{ymin:.1f},{ymax:.1f}] Z[{zmin:.1f},{zmax:.1f}], "
          f"V={body['volume']:.0f} mm^3, {body['triangles']} triangles")
    print("-> " + ", ".join(said["files"]))

    variables = _recipe("mandrel-variables")
    substitute_py_comments(
        Path(__file__),
        variables=variables,
    )
    print(f"-> {Path(__file__).name}")


if __name__ == "__main__":
    main()
