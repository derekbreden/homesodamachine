# Reservoir adhesion observations

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
trim for clear PETG. Retain the other physical settings while assessing this
correction. First-layer attachment and later corner lifting are separate
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

An explicit brim is a candidate if later corner lift remains after an attached
first layer. The current native G-code emits no brim despite the saved auto
brim setting. A cooling change needs a timing link to the affected feature:
normal cooling is off for three layers, then 20%, with local 90% overhang
cooling. [Prusa's warping guidance](https://help.prusa3d.com/article/warping_2011)
discusses bed contact, brim and thermal gradients; it does not establish this
reservoir's cause. No additional physical process change is selected for the
zero-trim retry.
