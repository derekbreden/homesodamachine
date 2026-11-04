'Shared installation scene builders and presentation props.\n\nThe cabinet, countertop, CO2 cylinder, filter and power cord are illustration geometry.\nRendered scenes are written to art/; owner documents keep their own print snapshots.\n\n    tools/cad-venv/bin/python hardware/install-guide/_install_art.py\n    tools/cad-venv/bin/python hardware/install-guide/_install_art.py --list\n    tools/cad-venv/bin/python hardware/install-guide/_install_art.py opening cabinet-plan'
from __future__ import annotations
from pathlib import Path as _Path
import sys as _sys
_sys.path.insert(0,str(_Path(__file__).resolve().parents[2]/"hardware/scripts"))
from _guides_compiled import compiled as _compiled, bind as _bind

def _box(*args, **kwargs):
    return _compiled('_install_art',path=('_box',),args=args,kwargs=kwargs)

def _cyl(*args, **kwargs):
    'A cylinder of `length` from (x, y, z) along `axis`.'
    return _compiled('_install_art',path=('_cyl',),args=args,kwargs=kwargs)

def _run(*args, **kwargs):
    'A tube along axis-aligned segments, with a ball at each turn.'
    return _compiled('_install_art',path=('_run',),args=args,kwargs=kwargs)

def _bend(*args, **kwargs):
    'A tube along axis-aligned segments whose corners are swept, not broken.\n\nEach turn is a quarter arc of `radius` tangent to both legs, in whatever plane\nthe two legs span, sampled into stubs with a ball at each joint. `_run` puts\none ball at the corner itself, which is the kink the filter page tells you not\nto make. The pieces overlap in a compound rather than a boolean union: same\ncolour, one read, no solid modelling for a shape that is only looked at.'
    return _compiled('_install_art',path=('_bend',),args=args,kwargs=kwargs)

def _unit(*args, **kwargs):
    return _compiled('_install_art',path=('_unit',),args=args,kwargs=kwargs)

def _add(*args, **kwargs):
    return _compiled('_install_art',path=('_add',),args=args,kwargs=kwargs)

def _machine(*args, **kwargs):
    'The whole appliance with the colours its own payload carries.'
    return _compiled('_install_art',path=('_machine',),args=args,kwargs=kwargs)

def _hex(*args, **kwargs):
    'A hexagonal prism of `across_flats`, from (x, y, z) along `axis`.'
    return _compiled('_install_art',path=('_hex',),args=args,kwargs=kwargs)

def _floor(*args, **kwargs):
    return _compiled('_install_art',path=('_floor',),args=args,kwargs=kwargs)

def _rear_face(*args, **kwargs):
    "Add the machine's rear-visible bodies, colours and all."
    return _compiled('_install_art',path=('_rear_face',),args=args,kwargs=kwargs)

def _prism(*args, **kwargs):
    "A rounded rectangular prism on the show face's own plane, running `length` in +Y."
    return _compiled('_install_art',path=('_prism',),args=args,kwargs=kwargs)

def _cable(*args, **kwargs):
    'A round cord swept along a spline through `points`.'
    return _compiled('_install_art',path=('_cable',),args=args,kwargs=kwargs)

def _c13_cordset(*args, **kwargs):
    "The cord end on the inlet's mating axis, `gap` millimetres out from the show face.\n\nThe nose that enters the inlet's cavity, the moulding behind it, the strain relief and the\ncord. Its three contact slots stand where the inlet's own blades do."
    return _compiled('_install_art',path=('_c13_cordset',),args=args,kwargs=kwargs)

def s_cabinet_plan(*args, **kwargs):
    'The slot the appliance stands in, with the clearances lying on the cabinet floor.'
    return _compiled('_install_art',path=('s_cabinet_plan',),args=args,kwargs=kwargs)

def s_opening(*args, **kwargs):
    'The one cut, from above: a 1-3/8 inch circle, with what it has to accept over it.'
    return _compiled('_install_art',path=('s_opening',),args=args,kwargs=kwargs)

def s_filter_in_cabinet(*args, **kwargs):
    'The cartridge lying flat, the white run easing into both ends with no tight bend.'
    return _compiled('_install_art',path=('s_filter_in_cabinet',),args=args,kwargs=kwargs)

def s_collet_press(*args, **kwargs):
    'The little printed tool: what takes any 1/4 inch push fitting in this system apart.'
    return _compiled('_install_art',path=('s_collet_press',),args=args,kwargs=kwargs)

def s_the_back_face(*args, **kwargs):
    'Three rows of tube ports, with the power inlet and signal socket.'
    return _compiled('_install_art',path=('s_the_back_face',),args=args,kwargs=kwargs)

def s_the_socket(*args, **kwargs):
    "The top row's left-hand end with the cord home in it and its tail falling away.\n\nHome is the show face. The wall's opening is cut to the shroud alone and the shroud stands\n0.75 mm out of it, so the cordset's moulding comes to rest on the wall itself."
    return _compiled('_install_art',path=('s_the_socket',),args=args,kwargs=kwargs)

def s_nameplate(*args, **kwargs):
    'The plate the back cover sends the reader to, with the serial and its link on it.'
    return _compiled('_install_art',path=('s_nameplate',),args=args,kwargs=kwargs)

def s_plate_sideways(*args, **kwargs):
    "The under-counter plate coming in from the side, which is the only way it goes on.\n\nSeen from under the counter on the plate's own side, so both mouths and all three lines\nare in the open. The plate stands off at -X with both mouths toward the shank and the\nflavor pair, the washer and nut hang at the bottom of the shank below the gap it slides\nthrough, and the seat itself is the install guide's frame."
    return _compiled('_install_art',path=('s_plate_sideways',),args=args,kwargs=kwargs)

def s_bottle_in_funnel(*args, **kwargs):
    "The one action after the last push: a 440 mL bottle tipped past level over the funnel.\n\nThe funnel's lift-off cover comes off for every fill, so the machine stands here without it."
    return _compiled('_install_art',path=('s_bottle_in_funnel',),args=args,kwargs=kwargs)

def _load_regulator(*args, **kwargs):
    'The shipped Taprite 3741, its PI010822S in the outlet port.'
    return _compiled('_install_art',path=('_load_regulator',),args=args,kwargs=kwargs)

def _co2_tether(*args, **kwargs):
    "The red tether out of the regulator's push-fit mouth: down `drop`, then `run` along +X."
    return _compiled('_install_art',path=('_co2_tether',),args=args,kwargs=kwargs)

def s_regulator(*args, **kwargs):
    "The two dials, the locked adjusting screw and the red tether in the outlet's push-fit."
    return _compiled('_install_art',path=('s_regulator',),args=args,kwargs=kwargs)

def _load(*args, **kwargs):
    return _compiled('_install_art',path=('_load',),args=args,kwargs=kwargs)

def render(*args, **kwargs):
    return _compiled('_install_art',path=('render',),args=args,kwargs=kwargs)

def main(*args, **kwargs):
    return _compiled('_install_art',path=('main',),args=args,kwargs=kwargs)

__all__ = ['annotations', 'json', 'os', 'sys', 'tempfile', 'Path', 'math', 'HERE', 'HARDWARE', 'ROOT', 'ART', 'OUT', 'cq', 'import_step', 'note_read', 'note_write', 'xz_plane_y_up', 'MACHINE_MESH', 'MACHINE_FACTS', 'COLLET_PRESS', 'REGULATOR_DIR', 'PLUMBING_DIR', 'MODERN_DIR', 'C14_SOURCE', 'BOX_X0', 'BOX_X1', 'BOX_Y0', 'BOX_Y1', 'BOX_Z0', 'BOX_Z1', 'BOX_MID_X', 'FUNNEL_BOUNDS', 'FUNNEL_MOUTH', 'PORT_FACE_Y', 'PORT_Z_UPPER', 'PORT_Z_LOWER', 'PORT_X_WEST', 'PORT_X_EAST', 'CLEAR_BEHIND', 'CLEAR_SIDE', 'CYLINDER_LANE', 'CYLINDER_D', 'CYLINDER_H', 'FILTER_D', 'FILTER_L', 'BOTTLE_D', 'BOTTLE_H', 'BOTTLE_NECK_D', 'BOTTLE_NECK_H', 'TUBE_D', 'BOTTLE_TIP', 'BOTTLE_CLEARANCE', 'STONE', 'CABINET', 'CORAL', 'STEEL', 'BRASS', 'WHITE_TUBE', 'RED_TUBE', 'BLUE_TUBE', 'BLACK_PART', 'CONCENTRATE', 'BOTTLE_PET', 'FILTER_BODY', 'FILTER_CAP', 'PRINTED', 'CYLINDER', 'ACETAL_GRAY', 'REAR_CHILDREN', 'REAR_RING_PREFIX', 'REAR_FACE_Y', 'C14_STATION', 'C13_SLIP', 'C13_WALL', 'C13_BODY_LEN', 'C13_NOSE_LEN', 'C13_BOOT_LEN', 'C13_BOOT_D', 'C13_CABLE_D', 'CORDSET', 's_cabinet_plan', 's_opening', 's_filter_in_cabinet', 's_collet_press', 's_the_back_face', 's_the_socket', 's_nameplate', 'PLATE_STANDOFF_X', 'WASHER_T', 'NUT_H', 'NUT_STEEL', 'PLATE_STEEL', 'BLACK_PART_LIT', 's_plate_sideways', 's_bottle_in_funnel', 'TETHER_IN_MOUTH', 's_regulator', 'SCENES', 'render', 'main']
_bind('_install_art',globals())

if __name__ == '__main__':
    _compiled('_install_art','main')
