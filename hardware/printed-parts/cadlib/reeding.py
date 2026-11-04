"""Reeded textures — half-round flutes, and the warps that bend the path they run on.

A field here reads (ACROSS, ALONG): the distance across the flutes, which decides which
groove a point falls in, and the distance along them, which the warp reads. Both are
lengths in mm measured ON THE SURFACE being cut, never in the part's own frame — so one
field lays one texture on a flat tile (across = x, along = y) and on a standing wall
(across = arc length round the wall, along = height), and a flute crosses a corner
without a seam because arc length does not know the corner is there.

Every field returns a 0…1 depth fraction. How deep 1 is belongs to the caller.

WARPING IS A SHEAR, not new geometry: `chevron` and `wave` ask `groove` about
`across + warp(along)`. Every flute shifts by the same amount at a given `along`, so
they stay exactly parallel and cannot collide — but their spacing measured across the
flute closes by the cosine of the limb angle, so a warped flute reads tighter on its
runs than at its turns.

THE LIMB ANGLE IS THE CONSTRAINT. On a standing wall the warp tilts the groove's own
side surface off vertical by the steepest angle its path makes. A sine's steepest limb
is 2πA/L and a rounded triangle's is less, so `warp_wavelength` is sized off the SINE at
L ≥ 2πA — `limb_angle_deg` reports what a caller actually bought.

PIERCING IS THE SAME FIELD READ AS A MASK. `pierce` is a predicate over `across` and not
a depth: a slot narrower than the groove is struck down the groove's own floor, on the
same centres, and the caller cuts through whatever section stands under it. BOTH JAMBS
RUN WITH THE FLUTES and the groove carries on past both ends of the slot at full depth,
so a pierced field crosses no flute anywhere and owes no stop treatment at any edge it
makes. What the slot is measured against is the MULLION between two slots — `mullion`
and `pierce_max` — and not the section behind the groove floor.
"""

import numpy as np
from _scalar_provider import call as _rust_scalar

globals().update(_rust_scalar('scalar.constants',group='reeding'))

def _config():
    return {name:globals()[name] for name in ('flute_pitch','flute_width','warp_amplitude','warp_wavelength','chevron_sharpness','pierce_width','pierce_shell')}

def _tuples(value):
    return tuple(_tuples(v) for v in value) if isinstance(value,list) else value

def _field(name,**values):
    value = _rust_scalar('scalar.'+name,config=_config(),**values)
    result = np.asarray(value)
    return result[()] if result.ndim == 0 else result

def walk(segments,s):
    return _tuples(_rust_scalar('scalar.walk',segments=segments,distance=s))

def rounded_rect_segments(x_len,y_len,r):
    return _tuples(_rust_scalar('scalar.rounded_rect_segments',x_length=x_len,y_length=y_len,radius=r))

def groove(across,pitch=flute_pitch,width=flute_width):
    return _field('groove',across=across,pitch=pitch,width=width)

def _phase(along):
    return _field('phase',along=along)

def rounded_triangle(along):
    return _field('rounded_triangle',along=along)

def limb_angle_deg(slope_factor):
    return _rust_scalar('scalar.limb_angle',config=_config(),slope_factor=slope_factor)

def chevron_limb_deg():
    return _rust_scalar('scalar.chevron_limb',config=_config())

def wave_limb_deg():
    return _rust_scalar('scalar.wave_limb',config=_config())

def straight(across,along):
    return _field('straight',across=across)

def chevron(across,along):
    return _field('chevron',across=across,along=along)

def wave(across,along):
    return _field('wave',across=across,along=along)

def cross(across,along,pitch=6.,width=3.4):
    return _field('cross',across=across,along=along,pitch=pitch,width=width)

def pierce(across,pitch=flute_pitch,slot=pierce_width,every=1,datum=0.):
    return _field('pierce',across=across,pitch=pitch,slot=slot,every=every,datum=datum)

def mullion(pitch=flute_pitch,slot=pierce_width,every=1):
    return _rust_scalar('scalar.mullion',pitch=pitch,slot=slot,every=every)

def pierce_max(shell=pierce_shell,pitch=flute_pitch,every=1):
    return _rust_scalar('scalar.pierce_max',shell=shell,pitch=pitch,every=every)

def open_fraction(pitch=flute_pitch,slot=pierce_width,every=1):
    return _rust_scalar('scalar.open_fraction',pitch=pitch,slot=slot,every=every)
