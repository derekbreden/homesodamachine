"""Registered under-sink cold-water hookup scenes for the Install guide.

The four scenes use one literal coordinate frame and one camera.  They show the
common older-home installation: a copper wall stub, quarter-turn angle stop,
existing braided 3/8-inch faucet supply, the John Guest Speedfit ASVPP1LF angle
stop adapter valve interposed in that 3/8-inch run, and the appliance's white
1/4-inch branch tube pushed into the adapter's collet.  Every instructional
object is CAD geometry; there are no labels, arrows, or raster additions.

Frame:
    +X = installer right
    +Y = out from the wall and into the cabinet
    +Z = up
    Y=0 = finished wall face

Run from the repository root:
    tools/cad-venv/bin/python hardware/install-guide/plumbing/plumbing_scenes.py
    tools/cad-venv/bin/python hardware/install-guide/plumbing/plumbing_scenes.py --render
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
    import _rust_part
    _rust_part.start()

from PIL import Image


HERE = Path(__file__).resolve().parent
HARDWARE = next(parent for parent in HERE.parents if parent.name == "hardware")
ROOT = HARDWARE.parent
OUT = HERE / "out"
ART = HERE / "art"

sys.path.insert(0, str(HARDWARE / "scripts"))
sys.path.insert(0, str(HARDWARE / "install-guide"))
import _hsm_render  # noqa: E402


# One explicit viewport for all four states.  The wall slab is also identical in every STEP,
# making their source bounds common even in a viewer that falls back to bounding-box framing.
RENDER_CAM = (1.05, 1.70, 0.62)
RENDER_TARGET = (10.0, 53.0, 160.0)
RENDER_UP = (0.0, 0.0, 1.0)
RENDER_ORTHO_SPAN = 105.0
RENDER_SIZE = "2000x1100"

SCENE_NAMES = (
    "plumbing-valve-on",
    "plumbing-valve-off",
    "plumbing-pre-tee",
    "plumbing-tee-installed",
)


# Scene dimensions, millimetres.
WALL_WIDTH = 500.0
WALL_BOTTOM = -80.0
WALL_HEIGHT = 450.0
WALL_THICKNESS = 18.0
STUB_CENTER = (0.0, 0.0, 112.0)
VALVE_AXIS_Y = 50.0
VALVE_CENTER_Z = STUB_CENTER[2]
VALVE_OUTLET_Z = 145.0

TEE_BOTTOM_Z = 132.0
TEE_TOP_FACE_Z = 193.0
TEE_BRANCH_FACE_X = 26.0
TEE_BRANCH_Z = 163.0

# The John Guest 1/4-inch push-fit port, at the figures
# `modern/render_modern_tee.py` takes from John Guest's published PP0208E drawing: collar,
# collet, socket and insertion depth are one family across every fitting on this water path,
# so the branch the customer pushes here is the branch they push on the modern sheet.
JG_TUBE_OD = 6.35
JG_SOCKET_D = 6.55
JG_INSERTION = 15.7
JG_COLLAR_D = 16.3
JG_COLLAR_LENGTH = 8.1
JG_COLLET_D = 9.7
JG_COLLET_BORE = 6.70
JG_COLLET_PROUD = 3.2


# Instruction-lighting materials.  The two hose systems remain literal: stainless braid for the
# pre-existing 3/8-inch faucet line and white polyethylene for the appliance's 1/4-inch branch.
# The adapter valve is John Guest's white polypropylene, at `_materials.M_JG_WHITE_PP`, on
# lead-free brass run threads, and its branch lever is the blue that range is moulded in.
C_WALL = (0.94, 0.935, 0.915, 1.0)
C_COPPER = (0.72, 0.31, 0.13, 1.0)
C_BRASS = (0.71, 0.46, 0.13, 1.0)
C_BRASS_LIGHT = (0.86, 0.62, 0.22, 1.0)
C_CHROME = (0.73, 0.76, 0.80, 1.0)
C_CHROME_DARK = (0.38, 0.41, 0.45, 1.0)
C_BRAID = (0.50, 0.53, 0.57, 1.0)
C_BRAID_HIGHLIGHT = (0.76, 0.79, 0.82, 1.0)
C_BRANCH = (0.94, 0.945, 0.94, 1.0)
C_HANDLE_BLUE = (0.035, 0.27, 0.73, 1.0)
C_GASKET = (0.035, 0.038, 0.043, 1.0)
C_JG_WHITE_PP = (0.90, 0.90, 0.87, 1.0)
C_JG_BLUE = (0.29, 0.50, 0.76, 1.0)


def _render(step_paths: dict[str, Path], art_dir: Path) -> None:
    jobs = []
    for name in SCENE_NAMES:
        jobs.append(
            {
                "step": step_paths[name].relative_to(HARDWARE).as_posix(),
                "out": str(art_dir / f"{name}.png"),
                "cam": RENDER_CAM,
                "target": RENDER_TARGET,
                "up": RENDER_UP,
                "span": RENDER_ORTHO_SPAN,
                "size": RENDER_SIZE,
                "bg": "#ffffff",
                "trim": False,
                "solid": True,
                "ortho": True,
                "ground": False,
                "fog": False,
            }
        )
    _hsm_render.render(jobs)
    expected_size = tuple(int(value) for value in RENDER_SIZE.split("x"))
    for name in SCENE_NAMES:
        path = art_dir / f"{name}.png"
        with Image.open(path) as image:
            if image.size != expected_size:
                raise RuntimeError(f"unexpected render size {image.size}: {path}")
            canonical = image.convert("RGBA")
            canonical.save(path, format="PNG", compress_level=9, optimize=False)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=OUT,
        help=f"STEP/PNG output directory (default: {OUT.relative_to(ROOT)})",
    )
    parser.add_argument(
        "--render",
        dest="render",
        action="store_true",
        help="render the four registered 2000x1100 instruction PNGs (the default)",
    )
    parser.add_argument(
        "--steps-only",
        dest="render",
        action="store_false",
        help="export only the STEP and mesh intermediates",
    )
    parser.add_argument(
        "--art-dir",
        type=Path,
        default=ART,
        help=f"PNG output directory (default: {ART.relative_to(ROOT)})",
    )
    parser.set_defaults(render=True)
    args = parser.parse_args()
    output_dir = args.out_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    from _plumbing_art_mesh import export
    step_paths = export(sys.modules[__name__], SCENE_NAMES, output_dir)

    if args.render:
        art_dir = args.art_dir.resolve()
        art_dir.mkdir(parents=True, exist_ok=True)
        _render(step_paths, art_dir)
        for name in SCENE_NAMES:
            print(f"rendered -> {art_dir / f'{name}.png'}")


_NATIVE_BUILDERS = (
    "_vector",
    "_unit",
    "_point_along",
    "_cylinder",
    "_cone",
    "_hex_prism",
    "_hex_nut",
    "_ring",
    "_round_sweep",
    "_add",
    "_add_threaded_nipple",
    "_add_static_wall",
    "_add_handle",
    "_add_angle_stop",
    "_add_faucet_supply",
    "_add_tee",
    "_add_appliance_branch",
    "_base_scene",
    "_direct_faucet_scene",
    "_pre_tee_scene",
    "_tee_installed_scene",
    "build_scenes",
)

def __getattr__(name):
    """Keep manual native builders outside the normal Rust scene driver."""
    if name not in _NATIVE_BUILDERS:
        raise AttributeError(name)
    from _plumbing_native import load
    native = load(sys.modules[__name__], 'legacy')
    globals().update({key: getattr(native, key) for key in _NATIVE_BUILDERS})
    return globals()[name]


if __name__ == "__main__":
    main()
