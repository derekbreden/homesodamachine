# Cold-core bottom cap and lid

Both parts were accepted on October 31, 2026, in black Polymaker Fiberon
PET-GF15 through each printer's fixed left hardened 0.4 mm Standard hotend.

| Part | Printer | Task | Accepted, CDT | Native estimate | Layers |
| --- | --- | --- | --- | --- | --- |
| Bottom cap | Mark1 | 1395316228 | 19:06:53 | 3 h 53 min | 74 |
| Bottom lid | Mark2 | 1395322638 | 19:10:27 | 3 h 6 min | 23 |

The bottom cap prints with a 180° turn about X, its broad flat face on the
bed. The bottom lid prints as exported, on its flat Z0 face. Both use the
declared bottom-cap recipe: three Classic wall loops, 15% gyroid, a 0.20 mm
first layer and 0.24 mm ordinary layers, supports disabled and auto brim.
Ordinary and auxiliary cooling are off; bridge/overhang cooling is 70% at
50% unsupported width. No support roads were emitted.

Mark1 retains its +0.18 mm user Z trim, emitting `G29.1 Z0.16` on textured
PEI. Mark2 retains +0.04 mm, emitting `G29.1 Z0.02`. The complete bead
envelopes leave minimum bed margins of 21.208 mm and 21.197 mm respectively.
Both native reviews pass archive integrity, model correspondence, trim and
the 20 mm bed border.

Mark2's sender was invoked more than 188 seconds after Mark1's acceptance
reading, preserving the required 180-second startup spacing. Both send
dialogs retained timelapse On, bed leveling On, flow calibration Auto and
nozzle offset calibration Auto. At 19:10:52 CDT, both printers reported
RUNNING at layer 0 with print error 0 and empty HMS lists.

Each printer's directory retains its editable project, exact source and
archive hashes, selected settings, native review, launch receipt and startup
reading. The ready-to-send archives remain at the cache paths in the
preparation records.

- Mark1: [preparation](mark1/preparation.json), [settings](mark1/settings.json),
  [review](mark1/review.json), [launch](mark1/launch.json),
  [startup](mark1/startup.json).
- Mark2: [preparation](mark2/preparation.json), [settings](mark2/settings.json),
  [review](mark2/review.json), [launch](mark2/launch.json),
  [startup](mark2/startup.json).
