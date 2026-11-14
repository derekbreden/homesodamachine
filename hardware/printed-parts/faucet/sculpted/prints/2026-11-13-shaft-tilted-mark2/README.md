# Sculpted faucet shaft trial for Mark2

Open the [print-ready archive](sculpted-faucet-shaft-tilted-black-mark2-ready.gcode.3mf)
in Bambu Studio Preview. It contains the complete plate of base, separate dispense tip,
display cover, mounting plate and lever. The [editable project](sculpted-faucet-shaft-tilted-black-mark2.3mf)
contains their physical meshes, positions and native support settings. The executable contains
the inclined, graded and interleaved paths.

The plate uses black Polymaker PET-GF on the left hardened nozzle and textured PEI.
The saved Bambu filament preset identifies the external spool as PET-CF. Keep smooth
timelapse off when running the archive. The custom order disables native power-loss
recovery and per-layer camera calls.

## Base and plate sequence

The base starts with its bed-rooted scaffold, sloped roof and backed foot courses. The
removable support plugs meet the outer counterbore only. The inner counterbore and pilot
are formed by their part paths. The [foot join reading](foot-join.json) checks the bearing
under the first slice-generated walls and the start of the internal support that rises through
the lower base.

The slicer generates the foot-to-shaft model paths with the mounting face flat in its
coordinate system. The path transform carries that incline into the printed shaft and eases it
to level inside the straight section. One internal bridge course joins the independently sliced
infill patterns across that seam, following the shaft walls around the open bore. The
[transition receipt](shaft-transition.json) records the selected height field, pitch and source slices.
The [shaft join reading](shaft-join.json) measures the emitted bridge landings and the first
level walls and infill. The [recovery receipt](shaft-join-recovery.json) records the
localized cooling and feed limit on the first courses over that bridge. The native
level slice supplies the upper bend and mating socket of the base. The base uses an
ordinary rear seam, with the native seam paint.

The scaffold and the other four objects share the first bed course. The low mounting
plate and lever finish alongside the scaffold and foot. The display cover and the separate
dispense tip advance in bands as there is room under the toolhead. The
[companion road reading](companion-deposition.json) compares their path coordinates,
extrusion, feed, acceleration and fan commands with their source plate.

The tip carries the [trial display-pocket backing](https://github.com/derekbredensteiner/homesodamachine/blob/c6cecb9b0acfdb41efaf5bbf9d7ee2777fda6d54/hardware/printed-parts/faucet/sculpted/prints/2026-11-13-dispense-face-sloped-foot-mark2/head/dispense-face-review.json).
The cover uses its fitted mesh. Compare the fore and aft seating faces with the
[approved print](https://github.com/derekbredensteiner/homesodamachine/blob/c8667107f964589be7dc69f8fb924f69a12729b3/hardware/printed-parts/faucet/sculpted/prints/2026-11-13-sloped-underside-complete-mark2/physical-result/physical-result.json).
Check release at the counterbores, finish at both shaft joins, and seating at the upper socket
and cover.

## Verification

The [plate receipt](plate.json) binds the executable, editable project and timeline
to their motion and inputs. Playback estimates commanded motion with acceleration and
excludes firmware startup, temperature waits and park macros. The native preview thumbnails
show the source plate layout. Use the interactive timeline to see the chronological order.
The [head replay](head-replay.json) uses the photo-derived
[left-active H2C head envelope](../../../../../reference/h2c-toolhead/README.md) and
nominal deposited beads. Finish, adhesion, and release remain physical results. The plate
awaits its first print.

[Reproduce the trial](stage/REPRODUCE.md) from the recorded native inputs and local
stages.
