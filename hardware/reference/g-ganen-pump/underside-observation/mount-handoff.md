# Pump cradle and snap interface

The layout owns the integral lid seat and snap retention. The rigid purchased
reference supplies the measured motor axis, rails and wire-cover clearance.

- Motor diameter: 49.110244 mm; the per-face static allowance is `fits.slip`.
  A circular static mating diameter is 49.410244 mm before any supported-face
  allowance belonging to the chosen print orientation.
- Motor reference axis point: (35.832933, 0, 34.115971) mm, directed
  (0.9999954114, 0, −0.0030293806) toward the rear.
- The unobstructed measured barrel band is reference X25–60 mm. The complete
  lower outline includes the two fixed rails and central molded cover.
- The cover ends at approximately X64.7 mm. Its underside and finite end are
  retained in `rigid-underside.json`; loose leads beyond the end are flexible.
- The seat cavity opens along +Z for placement and removal. Its relief includes
  the fixed rail protrusions and the wire cover throughout that motion.
- The snap bears on the unobstructed upper motor can. The shared seat/cap
  construction and hooks are in `hardware/manifold-layout/rear_snaps.py`.

The installed pose, cap stock, snap extent and neighbouring-part checks belong
to the layout. The purchased reference retains its port tips, independent barb
axes, motor axis and datum frame. `parameter-check.json` records that equality.
`validation.json` binds the native STEP and viewer payload; `surface-check.json`
records the lower-casing comparison against disjoint native scan samples.

## Selected contact regions

The saddle occupies native X25–60 mm and the upper snap X35–51 mm, entirely
within the approved motor/cylinder area. Axial stops contact the fixed motor
rail ends. The forward switch/nose is unused as a support. The middle/head
underside between switch and motor is excluded from all mounting contact.

The forward stop spans native Y−29 to −26 mm, retaining 3 mm of stock.
Its source-profile clearance from the red head is at least 0.828 mm through
the near-seam axial travel; the head outer hull has 1.500 mm lateral clearance
and its side lug stands 6.001 mm above the stop. The middle/head also remains
at least 1.386 mm above the plain lid in the selected pose. These are source
layout bounds; the native mount export remains a separate check.

The annotated review is in [mount-review.json](mount-review.json), and the
bound source calculation is [mount-contact-check.json](mount-contact-check.json).

The matching reference STEP and mesh are exported and all 25 native bodies
(21 rigid, four removable reference sliders) are valid. The disjoint scan
comparison p95 is 0.235/0.169 mm for the two exposed views. The local cover
shoulder has a maximum mesh-to-scan deviation of 0.533 mm; the cover slot is
an open, nonbearing clearance room, separate from the motor and rail bearings.
