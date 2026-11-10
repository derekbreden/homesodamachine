# Centered RC62 and valve fit trial

Both accepted jobs contain fit samples only, with no supports or insertion
pauses. Each full-bead envelope is at least 86.7 mm from the bed edges.
The [launch plan](launch-plan.json) records the exact task identities, one
Send per job, printer-specific trim and shared-circuit start spacing.

| Printer | Magnet labels | Valve labels | Native estimate | Receipt |
| --- | --- | --- | --- | --- |
| Mark2 | A1–A4, B1–B4, C0 | V72, V71, V70 | 1 h 39 m 20 s / 51.46 g | [Mark2](mark2-launch.json) |
| H2C | C1–C4, D1–D4, C0 | V70, V69, V68 | 1 h 38 m 32 s / 51.19 g | [H2C](h2c-launch.json) |

C0 and V70 repeat on both printers. The remaining variants cover all sixteen
X/Y magnet combinations and five progressively tighter valve sockets.
Read the [magnet fit procedure](../README.md) and
[valve fit procedure](https://github.com/derekbreden/homesodamachine/blob/b57b985c648c34346481a57fde897374b0e8f068/hardware/printed-parts/fixtures/valve-socket-fit/tighter-trial-v2/README.md)
after cooling. Report the preferred label and printer. These tests select a
preferred hand fit; roof quality, retention force and lifetime remain
unqualified.

The [Mark2 frozen preparation](mark2/README.md),
[H2C frozen preparation](h2c/README.md), and
[independent pair review](independent-plate-pair-review.json) bind the source
geometry, labels, native paths, ordinary layers and repeated controls. The
first layers are connected in the emitted paths; this does not establish
visual bed adhesion.

The [archive review source](https://github.com/derekbreden/homesodamachine/blob/0785c32f89a6e08609e5348aa2beb0096d560326/hardware/printed-parts/enclosure/enclosure/magnet-retention/fit-coupons/centered-trial-v4/review.py)
and [streamed-road reader](https://github.com/derekbreden/homesodamachine/blob/0785c32f89a6e08609e5348aa2beb0096d560326/hardware/printed-parts/enclosure/enclosure/support-bottom-gap/read_roads.py)
define the checks recorded for these frozen jobs. Current full-part preparation
and review use the [native enclosure workflow](../../../../trial-preparation/README.md).

The full front-top and funnel-frame prints are deferred. The independent
H2C retention job remains unsubmitted and unauthorized. No automatic resume
or additional job is authorized by either coupon completion.
