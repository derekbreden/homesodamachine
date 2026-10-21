# Reservoir adhesion observations

The zero-user-trim Mark1 retry, task **1359909015**, has **reported corner curl
and actual water leakage at many places**. Derek stopped it and identified
the [two photographs](../prints/2026-10-21-mark1-right08-z000/physical-result/physical-result.json)
as that most recent article. A distorted band is visible near the floor-to-wall
transition. Raised material reducing nozzle clearance is consistent with the
reported curl; a [solid-floor-to-wall transition](https://help.prusa3d.com/article/the-benchy-hull-line_124745)
can also create a band. The finished shape does not establish a lift layer.

Live observations through UI layer **526** did not detect the reported curl.
They covered exposed body/cap edges and left shadowed, occluded and reflective
underside contact unassessable. There is no complete attached baseline or
onset bracket. The [terminal record](../prints/2026-10-21-mark1-right08-z000/terminal-observation.json)
records cancellation and a failed final camera Play attempt; it supplies no
final chamber image. The task-bound monitor is **paused**.

Derek reports corner lifting on a previous reservoir, with onset guessed from the
finished shape at roughly layers 20–100. That interval is unverified. The
[investigation](investigation.json) identifies two downloaded Mark2 timelapses and
[the left](2026-10-06-left-contact-sheet.jpg) and
[right](2026-10-07-right-contact-sheet.jpg) sampled frames. The low camera angle,
reflections and cap occlusion prevent a reliable onset bracket. Frame numbers
are not established layer numbers. Full clips remain in the ignored
`.cache/reservoir-lifting/` directory with hashes in the investigation.

Mark1 task 1359853920 has a separate
[first-layer adhesion failure](../prints/2026-10-20-mark1-right08/physical-result/physical-result.json),
reported by Derek and documented in three photographs before removal. The
[retry](../prints/2026-10-21-mark1-right08-z000/README.md) uses zero added user Z
trim for clear PETG. First-layer attachment and later corner lifting are separate
observations; neither alone establishes the cause of the other.

## Live observations

Read the exact Mark1 task, layer, temperatures, fans, timelapse and error/HMS
status through `tools/bambu_printer.py`. Use `cua_repl` for Bambu Studio's Device
view and camera; verify the visible printer name and archive. Connect's device
page has status and filament controls but no live camera. Bambu Studio's camera
must be playing before treating its image as a live observation. In Device,
verify Mark1 at the upper left. If the preview is blurred and says it is
temporarily closed, click the green Play control at the lower left of the
camera image, allow initialization, and confirm changing frames. This method
produced updating startup frames for task 1359909015. If the view is unavailable, record that limit and do not substitute MQTT status for vision.

Examine cap and body separately. Record a repeatable underside-to-bed gap,
upward-curved bottom edge, displaced strand or nozzle contact with UTC/Central
time and exact reported layer. Mark glare or obscured edges unassessable.
Retain the last clearly attached and first clearly lifted observations to
bracket onset. Inspect every five minutes through layer 3, every ten minutes through layer
120, and then every thirty minutes if stable; stop the monitor when this specific task ends or
changes. Ordinary unchanged progress does not need a notification.

## Proposed next trial

**Flow 1.02** is supported by Derek. **No brim** is proposed: he reports the
large object separates from the brim during curl, with difficult bed cleanup
and a rough edge left after removal. His exact words and the recovered native
settings are in the [historical recipe review](historical-recipe-review.json).
The [next-trial discussion](next-trial-options.json) takes the successful May
Water recipe and ordinary Bambu motion settings as its reference. The saved
project and executable recipe remain frozen.

The current native G-code emits no brim despite the saved auto-brim setting.
Its [body cooling paths](body-cooling-paths.json) also show **90% fan commands
on the solid floor and early walls**, including layers 4 and 12–16. The
successful May recipe also saves **90% overhang cooling**. A supported-path
cooling review remains a hypothesis for the reported curl; no observed
fan-change-to-lift onset link establishes a required cooling change.

The recovered May 30 water-holding recipe used clear PETG, flow **1.02**,
**260 °C** after the first layer and a **21 mm³/s** ceiling through a 0.6 mm
nozzle. It requested **200/300 mm/s** outer/inner walls; these are requested
speeds, not measured motion. This failed recipe requests 30 mm/s with a
6 mm³/s ceiling. Installed Bambu 0.8 mm Standard presets save a **21 mm³/s**
ceiling for PETG Basic and **16 mm³/s** for Translucent, with ordinary high
requested speeds. The earlier proposed 12 mm³/s intermediate target has no
physical result supporting it. The historical review preserves exact preset
hashes and the accepted September 0.97 results.

May uses six requested Arachne walls, 0.60 mm lines, 100% zig-zag infill,
15% wall overlap, random seams, conditional scarf and a 15% seam gap. A
September agent's assertion that filament scarf `none` disables this enabled
process override is incorrect: Bambu's source selects the process scarf type
when the override is true. See the source-linked review. Historical emitted
scarf locations are unverified because the saved May project has no G-code.

Derek recalls the sphere trials as **Bambu defaults + higher flow + walls
without sparse infill**, with better results. Exact test-bound sphere settings
remain unrecovered. The April pressure-vessel chat is an initial design
discussion, and the Git record's printed-NPT-port leak does not establish a
failure of an unpierced sphere wall. Preserve the reported positive experience
without assigning missing numeric settings to it.

A walls-only reservoir candidate requires perimeter coverage of the modeled
wall thickness and a fully solid 3 mm floor. Zero sparse infill can express
that construction with appropriate bottom shells or verified perimeter
coverage. The May file's 100% infill and the sphere recollection are distinct
recipes; neither label establishes actual deposited continuity by itself.

A proposed 25 mm tall full-footprint body base retains the real floor,
fillets, corners and seam. The options specify a flatness check and one-hour
20 mm water-head screen using existing tools. That screen can reject floor
and lower-wall seepage before another full-height print; a pass does not
qualify the full reservoir, cap/gasket seal or cold service.
