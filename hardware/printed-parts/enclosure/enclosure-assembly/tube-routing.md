# Routing lines in the enclosure (`route`)

Every line the box carries is a `route(...)` in [`_lines.py`](_lines.py), built with the kit in
[`_routing.py`](_routing.py). Precedent: the board's
[`hand-routing.md`](/hardware/pcb/pcba/hand-routing.md).

## Writing a run

```python
route("refrig-1", "compressor-shroud.refrig-discharge",
      {"x": slot},                    # across into the condenser channel
      cond.y("refrig-inlet"),         # forward to the inlet's station
      cond.z("refrig-inlet"),         # up the channel to its height
      "condenser+fan.refrig-inlet")
```

A port anchor at each end, one-dimensional constraints between. Each constraint supplies one
coordinate; the other two carry over from the point before, so a waypoint moves along one axis
and every corner is square.

`F.x/y/z(port, d)` is the plane `d` along a world axis from that port. `F.out(port, d)` steps `d`
along the port's own face normal. `F.face("x+", gap)` sits `gap` clear of the component's +X body
face. `channel(a, b, bias)` positions a run between two faces — centred at bias 0, hugging one at
±1. A frame's box comes off the placed solid and its ports off `scorecard.PORTS`.

The exit stub off the source port and the approach stub into the destination are emitted by
`route`, along each port's face normal, one bend radius by default. `stub=(exit, approach)` sets
them separately.

## Bends

Each interior corner is a tangent arc of `bend` radius (`BEND_RATIO × Ø`, seeded at 2×OD =
12.7 mm for 1/4"), backed off `r·tan(θ/2)` down each leg. `Run.length` is the developed
centreline — the length of stock the run cuts.

A leg between two 90° corners is 2R = 25.4 mm. A corridor carries a turn one bend radius after
the face its port leaves.

`route` raises on a leg shorter than the tangents its two ends demand, on a close leaving more
than one coordinate differing from the approach point, and on a close nearer the port than its
own approach stub. Each guard has a defect and a control in
[`scorecard_selftest.py`](scorecard_selftest.py).

## `BLOCKED`

Connections the pack does not carry, each recorded with the measurement that blocks it. They stay
counted against the `routed` axis and print on every run.

## Running it

```
tools/cad-venv/bin/python enclosure_assembly.py
```

Per routed line: Ø, developed length, bend count and radius, and the tightest gap to a part it
does not terminate on. Per blocked line: the measurement. `routed` on the scorecard counts the
paths `_lines.py` builds. The runs render into `enclosure-assembly.step` in copper.

Line clearance is reported, not gated.
