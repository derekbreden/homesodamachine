"""What is printed: one holder per row, and the build that cuts and checks them all.

Run from the repository root:

    tools/cad-venv/bin/python hardware/printed-parts/shop-storage/holders.py

Every holder is one Gridfinity module. It stands anywhere a baseplate reaches, it prints
on its own feet without support, and it is the unit of being wrong: a figure that turns
out badly costs one module and not a column of them.

The build cuts each holder, runs its shape's own checks against everything the holder is
said to take, writes one coloured STEP per holder, and rewrites this directory's README.
A holder whose contents do not fit does not export — the check raises and the build stops
with the holder, the content and the two figures that disagree.
"""

import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

sys.path.insert(0, str(next(p for p in Path(__file__).resolve().parents if p.name == "hardware") / "scripts"))
import _rust_part
_rust_part.start()

import cadquery as cq  # noqa: E402

import _holder as H  # noqa: E402
import _kit  # noqa: E402
import catalog as C  # noqa: E402
from _bound import EXACT, Heap  # noqa: E402


here = Path(__file__).resolve().parent
out_dir = here / "holders"


@dataclass
class Holder:
    """One printed module.

    `takes` is what goes in it, in reading order — compartment by compartment for a tub,
    slot by slot for a comb, row by row for an index. `note` is the one line the README
    carries about why it is this shape.
    """

    name: str
    shape: str
    x_u: int
    y_u: int
    height_u: int
    takes: tuple = ()
    note: str = ""
    opts: dict = field(default_factory=dict)

    def __post_init__(self):
        result = _reference_data('holders', 'Holder',
            (self.name, self.shape, self.x_u, self.y_u, self.height_u,
             self.takes, self.note, self.opts), {})
        self.takes = result.takes

    @property
    def cells(self):
        return _reference_data('_bound', 'attribute', (self, 'cells'), {})


# ============================================================
# THE DOCK
# ============================================================


import pathlib as _reference_pathlib
_reference_hardware = next(p for p in _reference_pathlib.Path(__file__).resolve().parents if p.name == 'hardware')
import sys as _reference_sys
_reference_sys.path.insert(0, str(_reference_hardware / 'reference'))
from _reference_data import data as _reference_data, register_types
register_types(Holder=Holder)
_reference_values = _reference_data('holders')
globals().update({name: _reference_values[name] for name in ('DOCKS', 'CRADLES', 'COMBS', 'INDEXES', 'TUBS', 'HOLDERS')})
_holder_instances = {holder.name: holder for holder in HOLDERS}
for _group in ('DOCKS', 'CRADLES', 'COMBS', 'INDEXES', 'TUBS'):
    globals()[_group] = [_holder_instances[holder.name] for holder in globals()[_group]]



# ============================================================
# CRADLES — round stock, and not one figure read for a fit
# ============================================================



# ============================================================
# COMBS — tools that stand, held by a throat and a taper
# ============================================================



# ============================================================
# INDEXES — a bore is cut to a size, so every figure is a standard's
# ============================================================



# ============================================================
# TUBS — everything loose, and everything that just stands
# ============================================================





# ============================================================
# BUILD
# ============================================================

def build(holder):
    """Cut one holder and check it against everything it is said to take."""
    tall = holder.height_u if holder.height_u is not None else "?"
    print(f"\n{holder.name}  [{holder.shape}]  {holder.x_u}x{holder.y_u}x{tall}")
    opts = dict(holder.opts)

    if holder.shape == "dock":
        shape = H.dock(holder.x_u, holder.y_u)

    elif holder.shape == "tub":
        length_div = opts.get("length_div", 0)
        width_div = opts.get("width_div", 0)
        if holder.height_u is None:
            holder.height_u = H.tub_height_for(
                holder.x_u, holder.y_u, holder.takes, length_div, width_div
            )
            print(f"   {holder.name}: {holder.height_u} units deep, from its contents")
        shape = H.tub(holder.x_u, holder.y_u, holder.height_u, **opts)
        cells = (length_div + 1) * (width_div + 1)
        if len(holder.takes) > cells:
            raise ValueError(
                f"{holder.name}: {len(holder.takes)} things into {cells} compartments"
            )
        for env in holder.takes:
            check = H.assert_heap_fits if isinstance(env, Heap) else H.assert_tub_takes
            check(holder.name, env, holder.x_u, holder.y_u, holder.height_u,
                  length_div, width_div)

    elif holder.shape == "cradle":
        shape = H.cradle(holder.x_u, holder.y_u, holder.height_u)
        for env in holder.takes:
            H.assert_cradle_takes(holder.name, env, holder.x_u, holder.y_u, holder.height_u)

    elif holder.shape == "spacer":
        width = opts.pop("width")
        shape = H.spacer(width, holder.x_u, holder.y_u, holder.height_u)

    elif holder.shape == "comb":
        mouths = [H.slot_mouth_for(env) for env in holder.takes]
        shape = H.comb(holder.x_u, holder.y_u, holder.height_u, mouths, **opts)
        for env, mouth in zip(holder.takes, mouths):
            H.assert_comb_takes(holder.name, env, holder.y_u, holder.height_u,
                                mouth, **opts)

    elif holder.shape == "index":
        shape, placed = H.index(holder.x_u, holder.y_u, holder.height_u, opts["rows"])
        seen = []
        for env, _x, _y, _d in placed:
            if env not in seen:
                seen.append(env)
        for env in seen:
            H.assert_index_holds(holder.name, env, holder.height_u)

    else:
        raise ValueError(f"{holder.name}: {holder.shape} is not a holder shape")

    H.assert_printable(holder.name, shape)
    if holder.shape not in ("spacer", "dock"):
        H.assert_docks(holder.name, H.dock(holder.x_u, holder.y_u), shape)
    return shape


def sizes():
    return _reference_data('holders', 'sizes', (), {}, overrides={'HOLDERS': HOLDERS})


def cradle_witness(holder, shape, diameters):
    """The cradle with reels of several diameters lying in it, as one assembly.

    The claim a cradle makes is that it holds a reel at any radius without being told the
    radius. A picture of one reel does not show that; a picture of three does. The reels
    are witnesses and are not printed — each is placed by the geometry of a cylinder
    resting in a V, which is the same arithmetic the trough is cut by.
    """
    mouth, depth, run = H.cradle_trough(holder.x_u, holder.y_u, holder.height_u)
    top_z = _kit.top_reference_z(holder.height_u)

    assembly = cq.Assembly(name=f"{holder.name}-witness")
    assembly.add(shape, name=holder.name, color=_kit.kit_color)
    width = run / (len(diameters) + 1)
    for index, diameter in enumerate(diameters):
        radius = diameter / 2.0
        center_z = top_z + H.cradle_seat(mouth, depth, diameter)
        x = -run / 2.0 + width * (index + 1)
        reel = (
            cq.Workplane("YZ")
            .circle(radius)
            .extrude(width * 0.35, both=True)
            .translate((x, 0.0, center_z))
        )
        assembly.add(reel, name=f"reel-{diameter:.0f}",
                     color=cq.Color(0.80, 0.81, 0.83))
    return assembly


def figures():
    return _reference_data('holders', 'figures', (), {}, overrides={'HOLDERS': HOLDERS})


def parcels():
    return _reference_data('holders', 'parcels', (), {}, overrides={'HOLDERS': HOLDERS, 'COMBS': COMBS})


def _storage_inputs():
    import inspect
    from _materials import linear
    tub = inspect.signature(H.tub).parameters
    seated = inspect.signature(_kit.assert_seated).parameters
    return {'tub_defaults': {name: {'default': tub[name].default} for name in ('labels', 'scoops')},
            'seated_defaults': {'parameters': {name: {'default': seated[name].default}
                                                for name in ('max_overlap', 'max_gap')}},
            'kit_color': list(linear(_kit.kit_color)),
            'witness_color': list(linear(cq.Color(0.80, 0.81, 0.83)))}


def numbers():
    return _reference_data('holders', 'numbers', (), {}, inputs=_storage_inputs(),
                           overrides={'HOLDERS': HOLDERS})


def main():
    out_dir.mkdir(exist_ok=True)
    said = _rust_part.cut("tooling", "shop-storage", numbers(), out_dir)
    for body in said["bodies"][:len(HOLDERS)]:
        from _part_output import summary
        for line in summary(body, span_spec=".1f", shop=True)["lines"]:
            print(line)
    _kit.substitute_md(here / "README.md", variables=figures())
    print(f"\n{len(HOLDERS)} holders")

if __name__ == "__main__":
    if "--sizes" in sys.argv:
        sizes()
    elif "--parcels" in sys.argv:
        parcels()
    else:
        main()
