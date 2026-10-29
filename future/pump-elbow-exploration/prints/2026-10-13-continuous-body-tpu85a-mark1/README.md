# Continuous TPU pump elbows — Mark1 first article

Mark1 accepted task **1337197268** at **2026-10-13 18:37:14 CDT**. The
[launch receipt](launch.json) identifies the native archive and G-code hashes.
**Outcome: failed print, reported by Derek.** The
[physical result](physical-result.json) records that report. Failure mechanism,
socket fit, clamp handling and pressure sealing are unmeasured.

The plate carries two identical elbows. Each has an 11 mm deep Ø9 mm barb
socket and a 15 mm deep Ø6.1 mm tube socket. The large cuff meets a rounded
heel and a smooth reduction into the smaller leg. Its integral 88.9 mm² foot
rests on the bed; both sockets rise at 45°.

- [Editable project](2026-10-13-continuous-body-elbows-tpu85a-right06-z018-mark1.3mf)
- [Submitted native archive](https://github.com/derekbreden/homesodamachine/blob/33d50d2ecd2a0fb6b518483a44c8031e3a0c1617/future/pump-elbow-exploration/prints/2026-10-13-continuous-body-tpu85a-mark1/2026-10-13-continuous-body-elbows-tpu85a-right06-z018-mark1.gcode.3mf)
- [Recipe and mesh binding](2026-10-13-continuous-body-elbows-tpu85a-right06-z018-mark1.print.json)
- [Native slice readback](2026-10-13-continuous-body-elbows-tpu85a-right06-z018-mark1.readiness.json)
- [Exported print-source snapshot](elbow-source.txt)
- [Layer-section evidence](layer-sections.json) and
  [native deposition evidence](native-layer-support.json)

The loaded material is black TPU 85A through Mark1's right fixed 0.6 mm nozzle.
The recipe uses 0.20 mm first / 0.12 mm normal layers, six requested walls,
100% infill, spiral mode off, no supports and a 5 mm outer brim. It uses
225°C nozzle / 35°C textured PEI, 25 mm/s requested wall speed and the saved
2.2 mm³/s maximum flow. Mark1's +0.18 mm user Z trim emits `G29.1 Z0.16`.

Native estimate: **89 minutes, 8.57 g**, 184 layers. Model beads retain
2.06 mm clearance, and the complete bead envelope is at least 117.88 mm inside
the usable bed. Timelapse and bed leveling are On; flow and nozzle offset
calibration are Auto. Mark2's preceding acceptance was 17 minutes earlier.

The bounded support review found no detached material starts. A closing
stroke at the internal throat is approximately 0.23 mm per elbow, shorter
than its 0.536 mm emitted bead width. Inspect that closure and the open passage
with the printed article; geometry and slicing do not establish extrusion
continuity or a pressure rating.

Regenerate offline with `prepare_mark1.py` from the repository root. It writes
the native project and evidence here, without sending a print. The immutable
submitted archive and receipt identify the article under observation.
