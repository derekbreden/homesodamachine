# Fixed underside and removable sliders

Derek's photographs identify the purchased pump's rigid and flexible parts.
[photos.json](photos.json) retains their original bytes' SHA-256 values and chat
provenance. Photos 1–5 show the rubber sliders installed; photos 6–9 show the
fixed casing with all four sliders removed.

- Two fixed longitudinal rails remain beside the motor. Their channels and
  longitudinal openings are visible with the sliders removed.
- A separate, straight molded wire cover runs along the motor underside. Its
  lower face projects 1 mm farther down at its front than its rear: native
  Z3.210583 mm at X0 and Z4.210583 mm at rear-center X64.65. Derek's physical
  observation supplies the front projection; the registered scan supplies the
  rear height. Its finite ends and side edges belong to the rigid casing.
- The red and green leads emerging from the cover and rear cap are flexible.
  Their loops and crossings do not describe the rigid casing surface.
- The circular rear cap and the cylindrical motor can have distinct boundaries.
  Leads passing across either surface do not extend those boundaries.

The photographs establish feature identity and visible continuity. Dimensions
use the three archived native scans and their retained unit-scale rigid
registrations in [registered-measurements.json](../registered-measurements.json).
Photograph pixels are not a dimensional calibration.

## Mounting contact

The selected saddle and snap bear in the approved motor/cylinder region. The
middle/head underside is excluded from mounting contact. The clean forward tip
is unused as a support. The axial stops act only on the fixed motor rail ends.
The annotated [mount review](mount-review.json) records the selected regions;
the [native installation check](../installation/native-installation-check.json)
records installed contact, clearance and placement/removal checks against the
exported mount.

The fixed side-rail mesh agrees with 728 and 922 disjoint scan points at median
distances 0.029 and 0.032 mm, with p95 distances 0.112 and 0.141 mm. These are
scan comparisons in X28–52 and |Y|14–28, not absolute scanner accuracy or a
physical snap-fit test. The center cover is excluded from those residuals;
its sloping face uses the physical datum in
[rigid-underside.json](rigid-underside.json). [surface-check.json](surface-check.json)
binds the rail readings to the viewer payload and native parameter inputs.

The cover is the bare pump's lowest rigid surface. Its first modeled station
at X1 has native Z3.226051 mm. The selected pump origin Z250.447963 mm leaves
0.274013 mm above the plain lid at Z253.4 mm. The installed mount and neighbor
clearances require their own layout export.
