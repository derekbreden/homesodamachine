"""Build the quick start's product-derived artwork.

Focused customer views come from production CAD through ``_cad_art``. The two faucet-screen
images are decoded from the RGB565 arrays compiled into faucet firmware, and port colors come
from the rear-panel model's single source of truth.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import cadquery as cq
from PIL import Image


HERE = Path(__file__).resolve().parent
HARDWARE = next(p for p in HERE.parents if p.name == "hardware")
REPO_ROOT = HARDWARE.parent
ART = HERE / "art"

sys.path.insert(0, str(HARDWARE / "scripts"))
from _cadq_export import note_read, note_write  # noqa: E402

import _cad_art  # noqa: E402


FAUCET_STEP = HARDWARE / "faucet-layout" / "faucet-assembly.step"
FAUCET_RENDERER_DIR = (
    HARDWARE / "printed-parts" / "enclosure" / "drawings" / "line-art"
)
SCREEN_HEADERS = (
    REPO_ROOT / "firmware" / "src_faucet" / "images" / "flavor0_faucet.h",
    REPO_ROOT / "firmware" / "src_faucet" / "images" / "flavor1_faucet.h",
)
PORT_DIMENSIONS = (
    HARDWARE
    / "printed-parts"
    / "enclosure"
    / "back-panel"
    / "_back_panel_dimensions.py"
)
UNDER_COUNTER_PLATE = (
    HARDWARE
    / "cut-parts"
    / "faucet"
    / "touch-flo-under-counter-plate"
    / "touch-flo-under-counter-plate.dxf"
)


def render_faucet() -> None:
    """Render the exact faucet, counter, mounting stack and umbilical."""
    sys.path.insert(0, str(FAUCET_RENDERER_DIR))
    import _blender_render as blender  # noqa: E402

    note_read(FAUCET_STEP)
    note_read(FAUCET_RENDERER_DIR / "_blender_render.py")
    note_read(FAUCET_RENDERER_DIR / "_blender_scene.py")
    faucet = cq.importers.importStep(str(FAUCET_STEP))
    target = ART / "faucet-install.svg"
    blender.render_iso(
        faucet,
        [],
        view="front",
        out_svg=target,
        image_height=800,
        stroke_width=2.2,
        margin=30,
    )
    text = target.read_text()
    target.write_text("\n".join(line.rstrip() for line in text.splitlines()) + "\n")
    note_write(target)


def decode_rgb565_header(source: Path, target: Path) -> None:
    """Decode one 172 x 320 firmware image into a browser-ready PNG."""
    note_read(source)
    text = source.read_text()
    body = text[text.index("{") + 1 : text.rindex("}")]
    words = [int(v, 16) for v in re.findall(r"0x([0-9a-fA-F]{4})", body)]
    width, height = 172, 320
    if len(words) != width * height:
        raise ValueError(f"{source}: expected {width * height} pixels, found {len(words)}")

    rgb = []
    for value in words:
        r = ((value >> 11) & 0x1F) * 255 // 31
        g = ((value >> 5) & 0x3F) * 255 // 63
        b = (value & 0x1F) * 255 // 31
        rgb.append((r, g, b))
    image = Image.new("RGB", (width, height))
    image.putdata(rgb)
    image.save(target, format="PNG", optimize=True)
    note_write(target)


def render_under_counter_plate() -> None:
    """Render the exact laser-cut keyhole plate as clean top-view line art."""
    import ezdxf
    from ezdxf.addons.drawing import Frontend, RenderContext, config, layout, svg

    note_read(UNDER_COUNTER_PLATE)
    document = ezdxf.readfile(UNDER_COUNTER_PLATE)
    backend = svg.SVGBackend()
    drawing_config = config.Configuration(
        color_policy=config.ColorPolicy.BLACK,
        background_policy=config.BackgroundPolicy.OFF,
        lineweight_policy=config.LineweightPolicy.RELATIVE,
    )
    Frontend(RenderContext(document), backend, drawing_config).draw_layout(
        document.modelspace()
    )
    text = backend.get_string(
        layout.Page(80, 80, units=layout.Units.mm),
        settings=layout.Settings(
            fit_page=True,
            output_coordinate_space=800,
            output_layers=False,
        ),
        xml_declaration=False,
    )
    text = text.replace("stroke-width: 0;", "stroke-width: 8;")
    target = ART / "under-counter-plate.svg"
    target.write_text(text)
    note_write(target)


def write_colors() -> None:
    """Carry the physical port colors straight into the printed sheet."""
    note_read(PORT_DIMENSIONS)
    sys.path.insert(0, str(PORT_DIMENSIONS.parent))
    from _back_panel_dimensions import port_color_hex  # noqa: E402

    text = ":root {\n" + "".join(
        f"  --{name}: {port_color_hex(fluid)};\n"
        for name, fluid in (
            ("co2", "co2"),
            ("soda", "carb"),
            ("tap", "water"),
            ("flavor", "flavor"),
        )
    ) + "}\n"
    target = ART / "colors.css"
    target.write_text(text)
    note_write(target)


def main() -> None:
    ART.mkdir(parents=True, exist_ok=True)
    _cad_art.main()
    render_faucet()
    render_under_counter_plate()
    decode_rgb565_header(SCREEN_HEADERS[0], ART / "flavor-1.png")
    decode_rgb565_header(SCREEN_HEADERS[1], ART / "flavor-2.png")
    write_colors()


if __name__ == "__main__":
    main()
