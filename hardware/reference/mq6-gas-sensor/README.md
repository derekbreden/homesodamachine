# MQ-6 gas sensor module

`model.rs` draws the ACEIRMC module's board, header pins and stepped sensor exterior
for the machine viewer. The source preserves the board, pin and can datums used by
the printed cradle. The PCB retains the `mq6-gas-sensor` body identity; `sensor-base`,
`sensor-cap` and `header-pins` carry the other material regions.

The [Winsen mechanical drawing](https://www.winsen-sensor.com/d/files/manual/mq-6.pdf)
establishes the sensor's wide cylindrical base, annular shoulder and tapered mesh
cap. Its undimensioned shoulders are idealized from the drawing's proportions
inside the repository's existing can envelope. Their proportions do not establish
the received module's contact geometry. The wire weave and internal sensing
elements are omitted.

The purchase identity is ACEIRMC `B0978JSCZ8`. No received-board photograph or
matching carrier drawing accompanies this reference. Adjustment-pot, comparator
and LED placement remain unmodeled. The board envelope is suitable for its current
edge cradle; a part that conforms to those omitted components needs evidence from
the received board.

[`replica-evidence.json`](replica-evidence.json) records the source and dimensional
basis. [`reference-parameters.json`](reference-parameters.json) retains the board
station consumed by its mount.
