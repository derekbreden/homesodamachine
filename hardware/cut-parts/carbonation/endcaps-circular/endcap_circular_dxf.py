'\nCarbonator end-cap disc — circular carbonator, 2 ports per cap.\n\nTwo identical discs per carbonator, each with 2x tap-drill holes for 1/4"-18 NPT.\n4 ports/carbonator split 2+2 across both caps.\n\n── Dimensions ──\n\n  Disc diameter:          (= tube ID 4.870" − 0.010" slip-fit)\n  Disc thickness:         (1/4" 316 SS, laser-cut)\n  Hole diameter:          (7/16" — tap drill for 1/4"-18 NPT)\n  Hole spacing:           (center-to-center along one axis)\n  Hole positions:      (-, 0) and (+, 0)\n\n── Rod register (in-house DRILLED secondary op — deliberately NOT in the cut) ──\n\n  The level-sensing float rod (1/8" 316L) is welded to the bottom plate and\n  its top end seats in a shallow blind register in the top plate\'s inside\n  face. That register is a BLIND hole — it must not pierce the plate, because\n  the plate is the 90 PSI pressure boundary (hydro 180 PSI). A laser DXF cuts\n  THROUGH, so the register cannot live in this cut file without breaching the\n  carbonator. It is drilled in-house on the WEN 4208T after the discs arrive; the\n  laser geometry below is unchanged, so existing discs need no re-cut.\n\n  Both discs are drilled identically (kept interchangeable): top plate captures\n  the rod tip, bottom plate seats/locates the rod base for its tack weld.\n\n  Register center:     (−, 0) on the −X axis, beyond P1.\n                       Radius = tube-ID radius \n                       minus, the shared Aero float guide datum.\n                       A 36 mm float has 2 mm nominal clearance from the wet wall;\n                       its 4.8 mm bore allows 0.8125 mm radial motion on the 1/8" rod.\n                       The external reed lies on this same azimuth. Exact metric\n                       radius is 41.849 mm. Liquid switching height needs calibration.\n  Register drill:      9/64"  — slip-fit on the 1/8" rod; snug, which\n                       self-locates the rod base in the bottom plate for its tack\n                       weld. Open the TOP plate\'s pocket to 5/32" (0.156") only if\n                       the cap fights to seat over the rod tip at closure (step 5).\n  Register depth:       blind, to the drill-point tip, from the inside face\n                       — leaves of the plate as intact pressure\n                       boundary. 135° split-point bit ⇒ ~0.07" of full-diameter\n                       pocket gripping the rod tip: ample, non-load-bearing capture.\n\n── Material ──\n\n  316 stainless steel, thick, laser-cut.\n\nUnits: inches.  DXF $INSUNITS = 1 (inches).\n'
from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_hardware = next(p for p in _Path(__file__).resolve().parents if p.name == "hardware")
_sys.path[:0] = [str(_hardware / "scripts"), str(_hardware / "cold-core-layout")]
from _cold_core_data import compiled as _compiled, member as _member

def __getattr__(name):
    if name == "__all__":
        return _compiled('endcap_circular_dxf', action="public-names")
    try:
        return _member('endcap_circular_dxf', name)
    except ValueError as error:
        raise AttributeError(name) from error

if __name__ == "__main__":
    import _rust_part
    _rust_part.start()
    _compiled('endcap_circular_dxf', action="main")
