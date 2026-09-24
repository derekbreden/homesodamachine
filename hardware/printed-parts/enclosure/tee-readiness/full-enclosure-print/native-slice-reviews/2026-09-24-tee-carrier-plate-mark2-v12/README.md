# Tee carrier: fan-off thermal trial

Mark2 task `1278660260` prints one unsupported carrier in black PET-GF.
The [printer receipt](sender-receipt.json) verifies acceptance; the [subsequent reading](mark2-launch.json)
records the observed startup/printing state; [completion](completion.json) confirms 189/189 layers.
**Physical result rejected:** Derek reports
“That turned out worse. Exploded basically.” [Physical result](physical-result.json).
Deposited edges retreat inward, leaving subsequent perimeter paths in air. The intact interior
recovers outward as the curve becomes steeper. [Photos and detailed observation](../../../../tee-carrier/physical-observations/2026-09-24-v12/README.md)
record that failure sequence. Part cooling off is rejected for this carrier at these settings;
the cause of the deformation remains unconfirmed. This configuration is not a recommendation
for other rounds.

The [completed v11 surface](../../../../tee-carrier/physical-observations/2026-09-24-v11/README.md)
has a clean upper curve and localized lower-curve curling around layers 20–30. The fan-off
trial addresses the hypothesis that forced cooling contributes to differential contraction
of that thin, expanding curve. Its markedly worse result rejects fan removal as the remedy
for this configuration. The cause remains unconfirmed.

The only slicer setting changes are `fan_max_speed: 70 → 0` and
`enable_overhang_bridge_fan: 1 → 0`. Emitted part and auxiliary fan commands remain off
throughout the model. Native startup maintenance and hotend cooling are preserved.
Nozzle temperature is 265°C on the first layer and 280°C thereafter; the bed is 80°C,
with no active chamber heat. [Polymaker's PET-GF15 data sheet](https://fiberon.polymaker.com/wp-content/uploads/TDS_FIBERON-PET-GF15_V1.0_EN.pdf)
specifies cooling off, a 280–310°C nozzle, a 70–80°C bed and room-temperature chamber.
The first-layer setting is retained to isolate the cooling change.

All 189 layer heights match v11: 76 layers at 0.08 mm to Z 6.08, 37 at 0.24 mm to Z 14.96,
and 76 at 0.08 mm to Z 21.04. The complete visible R6 rounds are covered at 0.08 mm,
including the first layer. There are zero support paths/bodies and one plate object.
Geometry and placement are identical; native toolpath order is not asserted identical.
Mark2's requested +0.04 mm trim emits +0.02 mm for Textured PEI.

Bambu Studio 02.08.02.61 reports success with no warnings, **2 h 5 m 46 s** total estimate
and **44.93 g**. [Verification](verification.json) binds the settings, layer spans and
fan commands to the archive and embedded G-code hashes.

The initial send was rejected as invalid 3MF. A fresh import with an additional 20-second
settling wait accepted the exact same archive; the reason for the transient rejection
is unconfirmed. [Submission record](submission.json).

![Carrier-only native preview](preview.png)
