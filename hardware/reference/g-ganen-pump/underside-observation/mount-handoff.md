# Pump cradle and snap interface

The layout owns the integral lid seat and snap retention. The rigid purchased
reference supplies the measured motor axis, rails and wire-cover clearance.

- Motor diameter: 49.110244 mm; the per-face static allowance is `fits.slip`.
  A circular static mating diameter is 49.410244 mm before any supported-face
  allowance belonging to the chosen print orientation.
- Motor reference axis point: (35.832933, 0, 34.115971) mm, directed
  (0.9999954114, 0, −0.0030293806) toward the rear.
- The two exposed views supply the fixed rail profiles in reference X28–52 mm.
  The complete lower outline includes both fixed rails and the central cover.
- The cover ends at approximately X64.7 mm. Its lower face is level at native
  Z4.210583 mm, the measured rear-center height identified by Derek. Its finite
  end is retained in `rigid-underside.json`; leads beyond it are flexible.
- The seat cavity opens along +Z for placement and removal. Its relief includes
  the fixed rail protrusions and the wire cover throughout that motion.
- The snap bears on the unobstructed upper motor can. The shared seat/cap
  construction and hooks are in `hardware/manifold-layout/rear_snaps.py`.

The installed pose, cap stock, snap extent and neighbouring-part checks belong
to the layout. The purchased reference retains its port tips, independent barb
axes, motor axis and datum frame. `parameter-check.json` records that equality.
`validation.json` binds the native STEP and viewer payload; `surface-check.json`
records the fixed side-rail comparison against disjoint native scan samples.

## Selected contact regions

The saddle occupies native X16.75–77.75 mm and the continuous upper clip
X20–74.5 mm, within the approved motor/cylinder area. The catch pockets include
0.25 mm of axial clearance per end, with 3 mm of solid saddle beyond them.
Axial stops contact the fixed motor rail ends. The forward switch/nose is unused
as a support. The middle/head underside between switch and motor is excluded
from mounting contact.

The forward stop spans native Y−29 to −26 mm, retaining 3 mm of stock. The
installed pump pose, bearing, placement/removal, stops and neighbor clearances
are bound to their exported parts in the
[installation check](../installation/native-installation-check.json).

The annotated contact-region review is in [mount-review.json](mount-review.json).

The matching reference STEP and mesh are exported and all 25 native bodies
(21 rigid, four removable reference sliders) are valid. The disjoint scan
side-rail comparison p95 is 0.112/0.141 mm for the two exposed views. The level
cover floor uses the physical datum rather than a claim of scan agreement.
Its slot is an open, nonbearing clearance room, separate from the motor and
rail bearings.
