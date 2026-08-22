"""Build the quick start's product-derived artwork.

Focused customer views come from production CAD through ``_cad_art``. The two faucet-screen
images are decoded from the RGB565 arrays compiled into faucet firmware, and port colors come
from the rear-panel model's single source of truth.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from PIL import Image


HERE = Path(__file__).resolve().parent
HARDWARE = next(p for p in HERE.parents if p.name == "hardware")
REPO_ROOT = HARDWARE.parent
ART = HERE / "art"

sys.path.insert(0, str(HARDWARE / "scripts"))
from _cadq_export import note_read, note_write  # noqa: E402

import _cad_art  # noqa: E402


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
    decode_rgb565_header(SCREEN_HEADERS[0], ART / "flavor-1.png")
    decode_rgb565_header(SCREEN_HEADERS[1], ART / "flavor-2.png")
    write_colors()


if __name__ == "__main__":
    main()
