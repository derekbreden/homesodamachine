# Identification set on the glued Engineering Plate

The rear identification chips, serial nameplate and status plate share a face-up PETG
print on Mark One. The native archive emits no Z offset. The review records the emitted
command and confirms that the model geometry and extrusion toolpaths match the reviewed
identification set.

Black PETG Basic feeds the fixed left hotend from the AMS HT. White, blue and red PETG
Basic and clear PETG Translucent feed the right hotend rack from the AMS Pro. The preparation
and launch records name each material slot and the printer's accepted job.

The [physical result](physical-result.json) records the white-filament deposition and
extrusion-motor overload. The [drying record](drying/state.json) keeps the AMS temperature
and humidity readings beside the [post-drying launch](drying/launch.json). Its readings measure the air inside each
unit; elapsed drying time and temperature inform the restart together with that trend.

The [post-drying result](drying/physical-result.json) records the repeated overload and
removed white hotend. The [replacement-hotend trial](../2026-11-07-identification-set-mark1-white-spare/README.md)
uses an available spare for white PETG.
