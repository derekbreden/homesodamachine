"""Removable silicone funnel with an integral roof apron.

The collar center is the origin; z=0 is the frame-bearing brim underside. The brim,
collar and normal ramp wall lead to a substantial silicone plug, a 36 mm wide
square-cornered rectangle centred on the outlet. Its flat underside bears on
the elbow cradle's two hook tops. Its walls run up into
the bowl's underside, so none of its top shows. A straight 6 mm bore grips the
1/4-inch elbow stem over its complete insertion depth. The frame's through
hole passes the stem through the rigid frame.
"""

import argparse
import sys
from pathlib import Path

_here = Path(__file__).resolve()
_repo = next(p for p in _here.parents if any(
    (p / 'hardware/scripts' / helper).is_file()
    for helper in ('_rust_part.py', '_cadq_export.py')))
# _repo is this EDITION's root; tools/ is shared machinery with one copy at the
# repo root, so it gets its own anchor rather than a tools/ per edition.
_tools = next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"
sys.path.insert(0, str(_repo / "hardware" / "scripts"))
sys.path.insert(0, str(_tools))


def __getattr__(name):
    if name != "elbow_cradle":
        raise AttributeError(name)
    import elbow_cradle
    globals()[name] = elbow_cradle
    return elbow_cradle


# The enclosure recorder binds this leaf to its numeric construction graph.
brim_plan = None


# --- funnel parameters ------------------------------------------------------
collar_w = 165.0  # collar footprint in X, inside the top-wall frame
# Collar and frame reach toward the display, in Y−: the brim's front edge stands one running
# fit behind the display wall, and that wall 3 mm behind the display's PCB pocket.
forward_extension = 41.6085
aft_extension = 35.0
collar_d = 81.78301584656256 + forward_extension + aft_extension  # collar footprint in Y
mouth_corner_r = 14.0
collar_corner_r = mouth_corner_r + 6.0
brim_corner_r = collar_corner_r + 7.0
brim_margin = 7.0  # top-wall frame between the collar and its outer boundary
brim_overhang = 7.0  # flange reach beyond the collar on each side
brim_thickness = 6.0  # frame-bearing underside to the enclosure roof
apron_rise = 3.0  # mouth and cover seat above the enclosure roof
apron_width = 215.0  # complete enclosure width; overflow reaches the exterior sides
apron_depth = collar_d + 32.0
apron_y = 3.0
apron_corner_r = 6.0
collar_wall = 6.0  # vertical collar wall and normal ramp-wall thickness
capacity_ml = 698.21  # nominal cavity to the mouth rim
chute_h = 23.485946291005064  # brim top to inner ramp start
neck_dx = 0.0  # the outlet stands on the collar's centre
neck_dy = 0.0  # outlet on the collar centre
spout_id = 6.0  # straight outlet, formed by a stock 6 mm steel rod
spout_wall = 4.5  # minimum radial stock around the throat
# Ramp and outlet elevations are independent of the plug's lower face.
_ramp_rise = 14.199233063709995
plug_width = 36.0  # the plug rectangle's X width; its underside spans the cradle's hooks
# The block's top lies wholly inside the bowl; its lower plane bears on the cradle's hooks.
plug_lift = 3.15  # block underside above the frame's socket-floor datum
plug_height = 16.0 - plug_lift
drop = 46.1  # brim underside to the frame's socket-floor datum
sealing_id = spout_id
spout_land_z = brim_thickness - chute_h - _ramp_rise
# The uncut elbow stem reaches the bowl opening through the complete straight bore.
stem_engagement = spout_land_z + drop - plug_lift
sealing_land = stem_engagement

# The drain, in the funnel's own frame: the bore's exit on the plug's bottom face. World
# position = this + the funnel's placement; it rides the part.
drain_local = (neck_dx, neck_dy, -drop + plug_lift)


def numbers():
    """The authored funnel primitives, in the brim-bearing coordinate frame."""
    import elbow_cradle
    from _materials import M_SILICONE_BLACK, linear
    from _payload_rules import LINEAR_DEFLECTION_RATIO
    return {
        'bore_size': [collar_w-2*collar_wall, collar_d-2*collar_wall],
        'mouth_radius': mouth_corner_r,
        'ramp_z': [brim_thickness-chute_h, spout_land_z],
        'bore_radius': spout_id/2, 'drain_xy': [neck_dx, neck_dy], 'collar_wall': collar_wall,
        'end_z': -drop+plug_lift, 'top_z': brim_thickness+apron_rise,
        'spout_radius': spout_id/2+spout_wall,
        'brim_size': [collar_w+2*brim_overhang, collar_d+2*brim_overhang],
        'brim_radius': brim_corner_r, 'brim_height': brim_thickness,
        'apron_size': [apron_width, apron_depth], 'apron_y': apron_y,
        'apron_radius': apron_corner_r, 'apron_z': [brim_thickness, brim_thickness+apron_rise],
        'plug_size': [plug_width, 2*elbow_cradle.plug_half_length(plug_width/2)],
        'plug_height': plug_height, 'color': list(linear(M_SILICONE_BLACK)),
        'viewer_deflection_ratio': LINEAR_DEFLECTION_RATIO,
    }


def _document(fill):
    import elbow_cradle
    from docgen import substitute_md
    total = brim_thickness+apron_rise-(-drop+plug_lift)
    substitute_md(
        _here.parent / "README.md",
        variables={
            "FUNNEL_PLUG": f"{plug_width:g} × "
                           f"{2 * elbow_cradle.plug_half_length(plug_width / 2):.1f} mm",

            "FUNNEL_CHUTE": f"{chute_h:g} mm",
            "FUNNEL_DROP_UNDER": f"{drop:g} mm",
            "FUNNEL_DROP": f"{total:.0f} mm",
            "FUNNEL_CAP": f"{fill / 1000.0:.0f} mL",
            "FUNNEL_HOLD": f"{brim_overhang:g} mm",
            "FUNNEL_MARGIN": f"{brim_margin:g} mm",
        },
    )
    print("-> README.md")


def main(output=None):
    import _rust_part
    out = Path(output) if output is not None else _here.parent
    out.mkdir(parents=True, exist_ok=True)
    said = _rust_part.cut('funnel', 'funnel', numbers(), out)
    _document(said['bodies'][0]['fill_mm3'])
    print(f"-> funnel STEP, fine model and payload; {said['bodies'][0]['volume']:.1f} mm3")


if __name__ == "__main__":
    import _rust_part
    _rust_part.start()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    options = parser.parse_args()
    main(options.output)
