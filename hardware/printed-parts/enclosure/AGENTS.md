# Enclosure support work

Before changing an enclosure part, its placed component, or any down-facing enclosure
geometry, read **Support-removal strategy** in
[`enclosure/README.md`](enclosure/README.md#support-removal-strategy). Feature comments
describe their exact geometry; the README carries the policy.

Use a 0.20 mm first bed layer, followed by 0.08 mm across visible top/bottom rounds.
Those rounds print unsupported, including back-top's roof edges.
The tee-carrier low-force trial explicitly uses an additive print-bottom
chamfer/taper at 0.24 mm above the 0.20 mm first layer; its top rounds remain
0.08 mm. Follow `tee-carrier/low-force-trial/README.md` for that trial.
Check emitted first-to-second-layer perimeter overlap on expanding bottom rounds;
the 0.20-to-0.08 mm transition can require an attached first-layer brim. Verify the
brim's actual connection and coverage, and remove it before evaluating fit.
Retain supports for separate functional faces such as flat lifting ceilings and mounting
seats. Check the actual slice for contacts on the rounded show faces before sending it.
