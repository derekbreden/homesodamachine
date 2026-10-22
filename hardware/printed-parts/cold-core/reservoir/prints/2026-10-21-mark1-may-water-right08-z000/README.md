# May Water reservoir print on Mark1

Mark1 accepted task **1362179138** at **16:42:02 CDT on October 21, 2026**,
acknowledged `project_file` SUCCESS and entered PREPARE without print errors or
HMS alerts. [Launch receipt](launch.json) · [Preflight and Send dialog](preflight.json).

Plate 1 contains the current full-height **left reservoir and matching cap**,
through the **right 0.8 mm Standard-flow nozzle**, using Bambu PETG Translucent
Clear from **A1** with automatic refill. A2 is empty. The Send dialog visibly
mapped **A1 PETG R** and selected the mounted right **0.8 Standard** hotend.

The [May adaptation](adaptation.json) identifies the successful May 30 Water
recipe and the current 0.8 mm native machine base. Its process uses:

- **255/260 °C** first/subsequent nozzle, **70 °C** Textured PEI bed.
- **1.02 flow**, **21 mm³/s** volumetric ceiling.
- **0.30/0.24 mm** first/normal layers; **0.80 mm** line widths.
- Six requested Arachne walls, inner then outer; **100% zig-zag fill**, 15% overlap.
- Requested outer/inner walls **200/300 mm/s**, solid/top **250/200 mm/s**;
  actual motion remains bounded by flow, acceleration and cooling.
- Random seams, conditional scarf on all walls, **15% seam gap**.
- Ordinary cooling **10–20%**, first three layers off; **90%** overhang override,
  auxiliary off; May's 12-second layer-cooling threshold.
- **No brim**, **no model or support ironing**.
- **Zero added user Z trim**; native `G29.1 Z-0.02` is stock Textured PEI compensation.

Current **Tree(auto)/Default**, bed-only supports with 0.18 mm top/bottom contact
gaps serve this flat-floor body/cap geometry. May's normal support override
belonged to its raised slanted floor. Geometry and placement match the preceding
zero-trim trial. No geometry rebuild or publish is part of this recipe change.

The [native review](native-review.json) checks both plates, saved settings,
right-nozzle assignment, full-bead placement, layer heights, checksum, temperatures,
flow, trim, absence of brim/ironing, and bed-rooted supports. Plate 1 estimates
**5 h 42 min, 431.04 g and 833 layers**, with an empty plate-warning field.
Its nearest full-bead bed-edge inset is **70.519 mm** and cap/body gap is **10.042 mm**.
All seven detected supports start at the bed; six have no explicit interface label.

[prepare_recipe.py](prepare_recipe.py) declares the physical adaptation.
[prepare_launch.py](prepare_launch.py) selects the reviewed plate 1 and packages it
without changing a G-code byte. [Packaging hashes](packaging.json) bind the submitted
archive, named `2026-10-21-reservoir-left-cap-maywater-right08-z000-mark1.gcode.3mf`. The separate imported copy's embedded
G-code was verified before the single foreground Send through Bambu Connect.

The Send options for timelapse and bed leveling are **On**; flow dynamic and nozzle
offset calibration are **Auto**. Mark2 retained the same finished job for more than three minutes
before Send; the [preflight](preflight.json) records the shared-circuit interval.

At **16:48:41 CDT**, the same task reported RUNNING at layer **0/833**, with no
print error or HMS alert. The bed was **70/70 °C**, right nozzle **140/140 °C**
during cleaning and chamber **33 °C**. A1 was current/target, and the mounted right
hotend reported 0.8 mm. Updating Studio camera frames showed an empty plate during
startup. Runtime timelapse still reported disabled before deposition; the
[startup observation](startup.json) records that limit.

Startup acceptance establishes no first-layer adhesion, corner-flatness or water-hold
result. Those observations belong to this article. The canceled task 1359909015 and
its [curl/leak photographs](../2026-10-21-mark1-right08-z000/physical-result/physical-result.json)
retain their result. Its task-bound scheduled monitor remains paused.

## Physical result

Derek reports **“Leaks between infill and wall.”** Five off-plate photographs
show droplets along the floor-fill/perimeter boundary. This article's water hold
failed; fill height, duration and complete internal leak paths are unreported.
The retained task reports FINISH at 833/833 with no print error/HMS.
[Photographs and result](physical-result/physical-result.json) ·
[Floor geometry comparison](physical-result/floor-layout-comparison.json).
