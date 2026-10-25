# Rear identification

Six 32 × 2 mm colour chips identify the selected two-column, three-row rear
port grid. TAP and OVER use white, SODA blue, CO2 red and both FLAVOR ports
black, with contrasting lettering. Helvetica Bold at 4.6 mm gives a maximum
3.50 mm cap height. The common rise is 16.624 mm; the upper pair finish at
the 355 mm roof. The rounded lower corners and flange bores come from the
shared [bulkhead label interface](../bulkhead-ring/bulkhead_ring.py).

Each chip's face sits on the fitting's existing Y471.3 flange plane. A 2 mm
recess leaves 4 mm of printed wall between its floor and the Y465.3 nut
plane. The chip and wall retain a 6 mm clamped stack. Pockets have 0.15 mm
side clearance and preserve at least 3.64 mm of wall between rows.

Print the chips face up, with the native Y0 back face on the bed and +Y
upward, using the shared two-colour label process. The 0.48 mm raised word
uses two 0.24 mm layers above the flush fitting face. The accepted TAP/FLAVOR
[appearance record](../tee-readiness/full-enclosure-print/native-slice-reviews/2026-09-30-bulkhead-raised-mark2-v2/physical-result.json)
covers the 2 mm chip and raised-letter process; it does not qualify this
smaller 4.6 mm type or the new installed mounting fit.

The unchanged [accepted flat-wing nameplate](../nameplate/README.md) sits at
world X−38/Z228 with its face at Y473.5. Its broad plain field stands 2.2 mm
above the rear wall. The full 3.6 mm receiver backing begins at Y466.39,
leaving 1.09 mm to the cold-core shell. Both accepted retaining lips and
their print smooth lands remain complete. The plate takes no screws.

[`rear_identification.py`](rear_identification.py) provides installed parts,
shell recesses/receiver and print smooth lands from one source. Its main
emits the six compact two-colour chip STEP/STL pairs. The nameplate uses the
existing unit-0001 part. The [native review](native-review.json) records zero
contact with C14, RJ11, all six bulkheads and their nuts. These are CAD
clearances. Conservative bounds for all 102 installed conductor routes also
clear the complete receiver region. The accepted receiver-coupon fit retains its own scope, and
physical fit in this enclosure is unmeasured.
