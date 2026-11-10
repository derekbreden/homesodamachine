# Valve seat

Four blind sockets locate the Beduan valve's corner posts. The valve's round body
lands on the surrounding face; the socket floors leave air beneath the post tips.
The sockets set the valve's position and hand fit. The enclosure trays' zip-tie
paths provide their positive retention.

[numbers.rs](numbers.rs) defines the shared seat and Beduan dimensions. The
[enclosure valve decks](../enclosure/enclosure/quadrants/valves.rs),
[back-top seats](../enclosure/enclosure/back-top/rear.rs) and
[cold-core lid](../cold-core/foam-cap/foam_cap.rs) construct them in their native
production pieces. Each seat retains its bearing face, blind floors, post
sockets and open channel along the valve's port axis.

The [printed fit selection](../enclosure/enclosure/magnet-retention/fit-coupons/physical-fit-selection.json)
sets **V69 / 6.90 mm** as the default socket. **V70 / 7.00 mm** is an explicitly
selected alternate to try when a valve or print orientation does not fit V69
well; the builder never switches sizes automatically. The valve's catalog post
diameter and pitch remain the reference hardware dimensions. Holder outlines,
body bearing faces, port clearance, socket depth and blind floors stay on their
own dimensions when the bore changes.

The [selected geometry check](../enclosure/enclosure/magnet-retention/fit-coupons/selected-geometry-check.json)
verifies the native socket cuts, exterior envelope, bearing and blind-floor
datums, port clearance and shared cold-core stock datum.

The preferred hand fit belongs to the tested valve and upright enclosure-oriented
PET-GF panel. The cold-core lid's V-B wall and other print orientations require their
own installed fit observation. No insertion force, retention load or lifetime
is established by the selected bore.

The [cold-core top lid](/hardware/printed-parts/cold-core/foam-cap/foam_cap.rs)
carries V-B's integral upright socket wall (`_above_core_mounts.valve_support`), the
lid's only valve seat; V-A and V-K seat in back-top's integral sidewall seats. The
lid's pour opening and vents remain accessible.
