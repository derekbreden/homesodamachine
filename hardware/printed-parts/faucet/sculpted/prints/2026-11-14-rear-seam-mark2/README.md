# Sculpted faucet rear seam on Mark2

The [complete review plate](sculpted-faucet-rear-seam-black-mark2-review.gcode.3mf)
carries the Sculpted base, tip, cover, mounting plate and lever in black PET-GF.
The base's inclined and graded courses follow the slicer's continuous exterior
wall laps with the seam on the rear meridian.

The [photographs and print observation](../2026-11-14-plug-ramp-mark2/physical-result/physical-result.json)
identify the front of the base below the lever opening. The [seam reading](seam-evidence.json)
checks the wall ends in that region and the extrusion in a representative lap
of the [packaged commands](retained-deposition.json). The retained deposition
includes the plug-ramp tip, the full-width cover and the mounting plate rings.

The [motion estimate](chronology.json) and [head replay](replay.json) describe
the packaged print body. The replay checks nominal printed roads against the
[H2C head model](../../../../../reference/h2c-toolhead/README.md). The rear seam's
surface finish remains to be checked on the print.

The [course angle study](tip-course-angle-study.json) compares courses through the
mating shoulder in the current pose. The [tip pose study](tip-pose-study.json)
checks native slicer support contacts on the rotated dispense nose.

The [run inputs](run-inputs.zip) retain the base's native slices, foundation,
continued courses and cooling template. The [plug ramp's saved inputs](../2026-11-14-plug-ramp-mark2/run-inputs.zip)
supply the editable project, tip donor, rings and native complete slice.
[Reproduce the plate](stage/REPRODUCE.md) from those inputs. The active run
uses `.cache/runs/faucet-base-seam-plate-20261114`, the first base comparison
uses `.cache/runs/faucet-base-seam-20261114`, and the deposited preview
uses `.cache/runs/faucet-base-seam-viz-20261114`.
