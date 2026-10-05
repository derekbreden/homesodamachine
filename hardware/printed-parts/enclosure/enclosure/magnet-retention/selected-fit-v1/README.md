# Selected-fit insertion timing slices

These revisions prepare the current enclosure front top on H2C and the pump
cradle alone on Mark2. The cap is excluded. Both pieces use the selected
[C3 magnet fit and V69 valve sockets](../fit-coupons/physical-fit-selection.json),
with independent 0.48 mm nominal RC62 roof air (0.38 mm at maximum specified OD).
V70 is an explicitly chosen conditional valve alternative; these revisions use
V69.

Preparation requires passing current retention geometry and solid-host records
bound to each exported STEP/STL. The front top has one positive exterior and
one completely contained, inward-wound C3 cavity. Only current declared insert,
rail and seam host modifiers are included. The cradle has one current model;
the frozen paired project's settings and grip ranges supply its process input.

Both use black PET-GF, the fixed left hardened standard-flow 0.4 mm nozzle,
Textured PEI, a 0.20 mm first layer and ordinary 0.24 mm layers. The cradle
retains 0.08 mm only at its real inward lower hand-pocket rim, with six walls
through the ordinary upper additive transition. The front top retains its
inward/top show-round band. Functional supports retain 0.30 mm bottom Z and
0.50 mm object XY gaps; the RC62 roof is blocked from support. Mark2 uses
color `161616` with +0.04 mm requested / +0.02 mm emitted trim; H2C uses
`000000` with +0.18 / +0.16 mm.

Prepare or slice one part at a time after the geometry records match:

```sh
HSM_NO_BUILD_LOCK=1 PYTHONPATH=.cache/frame-seam-square/runtime tools/cad-venv/bin/python hardware/printed-parts/enclosure/enclosure/magnet-retention/selected-fit-v1/prepare.py pump-cartridge --slice
HSM_NO_BUILD_LOCK=1 PYTHONPATH=.cache/frame-seam-square/runtime tools/cad-venv/bin/python hardware/printed-parts/enclosure/enclosure/magnet-retention/selected-fit-v1/prepare.py front-top --slice
```

Omitting `--slice` prepares only. `--prepared --slice` slices the existing
unsliced preparation. Existing per-part preparation and native output folders
are immutable; a new trial needs a fresh revision.

The [Mark2 cradle preparation](mark2-v6/preparation.json) and
[H2C front-top preparation](h2c-v20/preparation.json) bind each current source,
project, print pose, process settings, host and programmed insertion boundary.
Their native timing results are recorded after slicing:

| Piece | Printer | Native pause forecast | Record and launch scope |
| --- | --- | --- | --- |
| Pump cradle alone | Mark2 | About 4 h 47 m | [Forecast](mark2-v6/pause-forecast.json); [separately scheduled launch](mark2-v6/launch-plan.json) |
| Enclosure front top | H2C | About 4 h 49 m | [Forecast](h2c-v20/pause-forecast.json); [separately scheduled launch](h2c-v20/launch-plan.json) |

The cradle pauses before print Z31.16 mm and the front top before Z36.44 mm.
The initial emitted countdowns are 4 h 46 m and 4 h 48 m respectively, one
minute below the total-minus-remainder estimates in the table.

The forecast subtracts the native pause-list remaining minutes from the native
total prediction, rounds the elapsed time to minutes, and compares it with the
initial emitted `M73 C` countdown. Both inputs are estimates. Heating,
calibration and physical printing can shift the actual pause. An insertion
instruction requires an observed matching programmed pause.

```sh
tools/cad-venv/bin/python hardware/printed-parts/enclosure/enclosure/magnet-retention/selected-fit-v1/review_timing.py pump-cartridge --retention
tools/cad-venv/bin/python hardware/printed-parts/enclosure/enclosure/magnet-retention/selected-fit-v1/review_timing.py front-top --retention
```

The review binds native archive/G-code hashes, the one model without a cap,
current hosts, left nozzle, color, trim and one `M400 U1` pause. The retention
option also checks the emitted open rim, pocket support exclusion, closing
paths, dense hosts and layer bands. It does not qualify physical grip, roof
quality or strength. Preparation and review perform no printer action.
The [shared timed launch record](timed-launch-plan.json) binds the accepted H2C
front-top task 1310609527 and Mark2 cradle task 1310615503, with one Send per
archive. Scheduled checks are stopped at Derek’s request. The
[manual Mark2 forecast](mark2-v6/launch.json) uses its 9:42 am CDT reading and
the frozen pause remainder to estimate insertion near **1:20 pm CDT** on
October 5, 2026. This is an estimate, not a pause observation. No additional
Send or automatic resume is authorized.

Derek accepts the [first covering layer above the front-top magnet](h2c-v20/physical-acceptance.json),
with two close-up photos. The result applies to this H2C C3/V69 print’s initial
over-magnet surface. Finished pocket rattle, magnetic retention and full-assembly
fit remain separate observations.

The [pair polarity record](polarity-record.json) tracks these two inserted RC62
rings separately from the C3 fit label. Their actual installed polarities have
no verification result. The [MASTER-dot procedure](../README.md#pole-marking-and-pair-tracking)
defines a fixed reference ring, a check through the mating covers and the CR/FT
marking rule for subsequent insertions.
