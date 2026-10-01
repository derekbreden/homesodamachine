# Grip receiver bridge trial

The receiver coupons retain the accepted curved exterior and the shared
enclosure's corrected front/back seam. The backing tab has 0.50 mm below the
supported roof. The complete 12 mm lifting roof remains intact.

Native support paint excludes only the narrow end-wing slot roofs, approximately
16 mm² per coupon. Those roofs span the 5.30 mm slot width as bridges. The broad
lifting ceilings retain the shared PET-GF tree supports. Physical bridge finish,
wing insertion and retention remain to be tested.

| Printer | Coupon | Native estimate | Requested Z trim |
|---|---|---:|---:|
| H2C | Front receiver | 29 min 46 sec | +0.18 mm |
| Mark2 | Back receiver | 35 min 44 sec | +0.04 mm |

Both use black PET-GF through the fixed left hardened 0.4 mm nozzle, a 0.20 mm
first layer and 0.24 mm subsequent layers. The six-wall band is limited to print
Z35.0–41.5 mm. Saved speeds, wall order, 15% infill overlap and normal tree
support separations are retained. Launch options are Timelapse On, Bed Leveling
On, Flow Calibration Auto and Nozzle Offset Calibration Auto. Starts must be
at least 180 seconds apart.

`prepare.py H2C` and `prepare.py Mark2` create separate native archives under
`.cache/prints`. `verify.py` reads their actual G-code, checks every support road
including those without object labels, verifies the slot is empty of support,
and checks first-layer support and the bridge roof paths. Printer-specific
`preflight.json` files contain archive hashes and measured coverage. Launch
records establish whether a prepared archive was actually sent.
