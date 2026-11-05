'\nCarbonator end-cap — 3D solid for CNC machining quotes.\n\nThe complete machined cap: the × 1/4" 316 SS disc, the two 1/4"-18 NPT\ntap-drill through-holes, AND the blind level-sensing rod register. This is the\nquote artifact for CNC vendors (Xometry / Protolabs / Fictiv / RapidDirect),\nwhere the register IS a machined feature — unlike the laser cut file\n`endcap-circular-2hole.dxf`, which omits it because a laser cuts only THROUGH\nand a through-hole there would breach the 90 PSI pressure boundary.\n\nOne part covers both caps: the top and bottom plates are this identical\ngeometry (the top-plate register captures the float-rod tip; the bottom-plate\nregister seats it for the tack weld). The two holes are modelled at tap-drill\ndiameter — the vendor taps 1/4"-18 NPT per the drawing callout.\n\n── Geometry (built in mm; the cap\'s source specs are in inches) ──\n\n  Disc:            Ø ×  (4.860" × 1/4", = tube ID 4.870" − 0.010")\n  NPT tap-drill:   2× Ø  (7/16") THRU, at X = ± (±0.750")\n  Rod register:    Ø (9/64") blind, (0.100") deep, at\n                   (−, 0) on the inside (+Z) face — leaves \n                   (0.150") of plate as intact pressure boundary.\n\nThe register sits on the +Z face = the carbonator INSIDE face; the −Z face is the\nplain outside face. STEP is exported in millimetres (CadQuery / CNC default).\n\nUnits: millimetres.\n'
from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_hardware = next(p for p in _Path(__file__).resolve().parents if p.name == "hardware")
_sys.path[:0] = [str(_hardware / "scripts"), str(_hardware / "cold-core-layout")]
from _cold_core_data import compiled as _compiled, member as _member

def __getattr__(name):
    if name == "__all__":
        return _compiled('endcap_circular_step', action="public-names")
    try:
        return _member('endcap_circular_step', name)
    except ValueError as error:
        raise AttributeError(name) from error

if __name__ == "__main__":
    import _rust_part
    _rust_part.start()
    _compiled('endcap_circular_step', action="main")
