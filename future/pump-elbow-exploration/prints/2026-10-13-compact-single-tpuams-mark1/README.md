# Single compact elbow in TPU for AMS — Mark1

Mark1 accepted task **1337417293** on **2026-10-13 at 20:19:42 CDT**.
The [launch receipt](launch.json) binds the submitted archive and G-code.
**Outcome: reported too stiff.** The [physical result](physical-result.json)
records the material-compliance rejection. The specimen is the rounded-heel,
smooth-neck V-shaped elbow with its original integral flat foot. It uses the
11 mm barb / 15 mm tube insertion depths and exposed circular clamp seats.
The plate contains one body, one volume, one object and one instance.

The selected material is Bambu TPU for AMS, Shore 68D. The manufacturer's
H2C 0.6 mm recipe uses 230°C nozzle, 35°C textured PEI, flow ratio 0.97,
12 mm³/s maximum flow and 0.4 mm retraction. The controlled process requests
six walls, 100% infill, 0.20 mm first / 0.12 mm normal layers, 0.62 mm beads,
25 mm/s walls and a 5 mm outer brim. Spiral mode and supports are off.
Mark1's +0.18 mm user trim emits `G29.1 Z0.16`.

Native estimate: **43.5 minutes / 4.31 g**, 184 layers. The mesh is one closed,
consistently oriented body with 88.885 mm² flat bed contact. Printing success,
barb insertion force, socket fit, clamp response and sealing are unmeasured.
The material is rejected for the reported stiffness. No pressure or retained
grip result is established.

- [Editable project](2026-10-13-compact-single-elbow-tpuams-right06-z018-mark1.3mf)
- [Native archive](https://github.com/derekbreden/homesodamachine/blob/33d50d2ecd2a0fb6b518483a44c8031e3a0c1617/future/pump-elbow-exploration/prints/2026-10-13-compact-single-tpuams-mark1/2026-10-13-compact-single-elbow-tpuams-right06-z018-mark1.gcode.3mf)
- [Native readback](2026-10-13-compact-single-elbow-tpuams-right06-z018-mark1.readiness.json)
- [Print mesh](compact-single-elbow-print.stl) and [source snapshot](elbow-source.txt)

The saved colour is the right external spool's reported `161616`; its current
material identifier is `GFU02` / `TPU-AMS`. Derek reports it loaded on the right 0.6 mm hotend. The
[preparation reading](preparation-printer-status.json) shows both heater targets
at zero before submission. The launch receipt confirms the new job accepted
with the matching external-spool type and colour.

[Bambu technical data](https://store.bblcdn.eu/s8/default/0b83dc5419534babb4287686cb8c7375/Bambu_TPU_for_AMS_Technical_Data_Sheet.pdf)
supplies the grade and printing guidance, with no sealing rating for this part.
