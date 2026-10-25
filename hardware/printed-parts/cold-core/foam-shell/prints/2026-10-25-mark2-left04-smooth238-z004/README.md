# Smooth 2.38 mm cold-core shell on Mark2

Accepted as task **1375153599** at **2026-10-25 16:26:12 CDT / 21:26:12 UTC**.
The printer acknowledged SUCCESS and reported PREPARE, print error 0, HMS empty.

The shell is smooth with nominal 2.38 mm standing walls and a 2.0 mm floor.
Its 282.4 × 180.4 mm casing reserves 0.30 mm per outside face for foil tape.
Reservoir cavity profiles, reed slots, clamp axes, port coordinates and stack
planes are bound in the [integration receipt](../../../casing-integration-review.json).
Both reservoir bodies and caps clear the finished shell in the native check.

| Setting | Value |
| --- | --- |
| Hotend | Fixed left, hardened 0.4 mm Standard |
| Material | Black Fiberon PET-GF15; external 254, printer PET-CF #161616 |
| Process | Classic, 3 wall loops; 0.42 mm outer / 0.45 mm inner |
| Layers | 0.20 mm first, 0.24 mm ordinary; 889 layers |
| Thick regions | 15% gyroid |
| Temperatures | 265 °C first / 280 °C later; textured PEI 80 °C; chamber unheated |
| Cooling | Ordinary/auxiliary off; 70% bridge/overhang at 50% unsupported width |
| Flow | 0.9555 ratio, 18 mm³/s maximum |
| Z trim | Mark2 +0.04 mm user trim; G29.1 Z0.02 on textured PEI |
| Support | Off; no emitted support bodies |
| Minimum emitted bed margin | 21.183 mm |
| Native estimate | 23 h 4 min 46 s |
| Launch options | Timelapse On, bed leveling On, flow calibration Auto, nozzle offset Auto |

[Native review](native-review.json), [wall-path review](wall-path-review.json),
[settings](settings.json), [preparation](preparation.json),
[prelaunch](prelaunch.json), [launch receipt](launch.json) and
[startup readback](postlaunch.json) bind this job.
All 30 sampled ordinary wall sections contain six perimeter paths. Feature
junctions and hardware hosts retain their local filling paths and stock.

Mark1's latest known accepted start was task 1374963298 at 20:18:16 UTC.
Its agent confirmed no subsequent start or resume by that session. No Mark1
start/resume is to occur before 21:29:12 UTC, 180 seconds after this acceptance.

At **16:48:22 CDT**, [first-layer readback](first-layer.json) reported RUNNING,
layer 1/889, 265 °C nozzle and 80 °C bed, print error 0. HMS
**0C00010000020017** identifies a dirty nozzle-camera lens, which may affect
AI monitoring. The print is continuing; Derek was notified. No first-layer
surface or adhesion acceptance is inferred from the status.
