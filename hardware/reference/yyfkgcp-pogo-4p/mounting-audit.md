# Pump cartridge magnetic contacts

The current mechanism uses one [YYFKGCP four-pin pair with ears](https://www.amazon.com/dp/B0GCBNTBT8?th=1).
The female pad half mounts in the pump cap's aft face; the male spring-pin half mounts in
front-top's bay bulkhead. Each purchased half contains two magnets. The printed parts
provide screw-fastened seats and lead passages. A separate
[RC62 retention pair](../../printed-parts/enclosure/enclosure/magnet-retention/README.md)
is embedded in the lower cartridge cradle and front-top at tube height, below
the pogo row. Each of those two prints pauses for insertion of one ring; the
pump cap contains only its purchased connector magnets.

The [native audit](mounting-audit.json) reads the current exports and the production placement
functions. It checks all four nominal pin/pad stations, spring travel, clearances to both
printed parts and the current seat/lead cutters. Reproduce it without regenerating CAD:

```sh
tools/cad-venv/bin/python hardware/reference/yyfkgcp-pogo-4p/audit_mounting.py
```

## Build stock and tools

A build uses one purchased connector pair, four M1.4 × 4 × Ø2.3 inserts and four
M1.4 × 8 socket-head screws. The [purchase ledger](../../ledger/purchases.md)
records the delivered connector supply and the two fastener packs on order for
2026-10-07. Their pack quantities are 200 inserts and 50 screws.

The screws require a hand-operated 1.3 mm hex driver. The supplier's package
contents describe 50 screws, with no driver stated. The acquired PixelDrive and
2.5/4 mm bits do not supply this size; [tool stock](../../ledger/tools.md#shop--bench-infrastructure)
lists the Wiha 26313 on order for 2026-10-05, verified against Amazon
order 112-9011811-0810621. Seat the ears square by
hand; there is no qualified powered torque for the M1.4 joint.

The acquired FX-888D and VECO-T T18 I/LB fine tips provide the insertion-tool
candidates. The M2–M8 heat-set kit does not cover M1.4. Cold-check the selected
tip through the Ø2.6 entry, with no printed-wall contact, and calibrate the
insert-top depth to 5.00 mm before heating, as specified in
[enclosure assembly](../../assembly/enclosure-mechanical.md). The existing
coupon checks both insert installation and connector face position.

## Current protection

Each purchased contact is specified for 2 A at 12 V. The pump's ~0.8 A normal
current does not establish startup or jam current. In the current
[PCB source](../../pcb/pcba/pcba.tsx), U11/U12 ISEN connect directly to ground
and VREF connects to 3V3. Texas Instruments' [DRV8870 data sheet, §§7.4.2 and
7.3.5.2](https://www.ti.com/lit/ds/symlink/drv8870.pdf) identifies this as PWM
without adjustable current regulation; the driver's overcurrent protection is
not a 2 A contact limit. The 12 V supply can source 6.7 A for the appliance and
does not provide a per-contact bound.

Contact-current protection is open. A complete implementation needs a current
limit whose worst-case threshold and transient response stay within the
connector's supported current envelope while allowing the pump to start, or a
connector with documented capacity for the actual motor current. No startup,
jam-current or installed contact-resistance result is recorded. The routing
and motor-pair mapping remain four separate H-bridge conductors; contacts are
not paralleled. The service joint is mated and parted with appliance power removed.

## Seating and dimensional allowance

The founder reports successful connector fit and mating/compression in the
printed test piece on 2026-10-04. That result is accepted in the
[physical record](physical-observations.json); the report is qualitative and
belongs to the printed test piece.

The cartridge tubes bottom in the tee bodies at full seat. The flat cap and bulkhead planes
have 0.246 mm nominal separation. Both connector ear plates bear on steps 3.00 mm behind
their printed faces. Two M1.4×8 screws per half clamp each 1.00 mm ear plate onto that datum.
Each M1.4×4 insert starts 2.00 mm behind the datum, 5.00 mm inside the mating face,
and occupies depths 5.00–9.00 mm. The Ø2.00 pilot ends at 10.50 mm; the screw tip
ends at 10.00 mm, leaving 0.50 mm clearance with complete insert engagement.
The Ø2.60 entry passes the whole knurl. Screw heads finish 0.60 mm behind the mating faces. The insert fit and
printed fastening capacity have no reported physical result.

The [Prime listing](https://www.amazon.com/dp/B0GCBNTBT8?th=1), checked on 2026-10-03,
shows 5.00±0.15 mm male tip height over the back of a 4.00 mm body. Its general tolerance
is ±0.05 mm. Independent extremes therefore permit 0.80–1.20 mm unloaded pin protrusion.
The drawing specifies 1.10 mm total stroke and cautions against overcompression.

The [coupon criterion](../../printed-parts/enclosure/enclosure/contact-pair-coupon/README.md)
allows ±0.05 mm installed face error per half. Including drawing extremes gives
0.454–1.054 mm compression at the nominal frame position. The upper extreme leaves only
0.046 mm for additional closing error. This is a conditional drawing calculation. The
complete printed frame's position error, contact tilt and delivered component dimensions
are unmeasured. The controlling installed quantity for each pin is its unloaded protrusion
minus its assembled plastic-face gap, greater than zero and less than 1.10 mm. Face
flushness alone does not establish that condition.

For a local unpowered mating check, two equal nonconductive shims measured at 0.25–0.30 mm
keep the housings parallel, clear of maximum stroke, with all drawing-extreme pins reaching
their pads. Place them beside the contact row without covering pins or magnets. Closing
the plastic faces to zero gap can overcompress a maximum-drawing pin.

## Magnet orientation and load path

Use the pair's attracting orientation. Mark the corresponding ends of both halves that
will stand at machine −X before soldering or mounting. Viewed in machine coordinates,
both contact rows keep the same conductor order. Face-on drawings have opposite viewing
directions when installed; copying their left-to-right labels independently can reverse
the contact order. The [DC-5 schedule](../../wiring/ac-wiring-schedule.md) defines the mapping.

The cartridge floor and fitted wells carry weight and locate the pumps. The tube stops set
full insertion; the collets capture the four tubes. The connector's magnets pull its two
halves together against the four pogo springs, and their force reaches the printed parts
through the connector bodies, ear plates, screws and inserts. They have no specified pull
force at the installed gap and do not establish whole-cartridge retention or vibration
reliability. The seller's 45±10 gf spring figure applies at its stated working height;
there is no force curve for this installed compression. Its 30 mΩ figure and 10,000-cycle
claim are connector specifications, not results for the assembled machine.

The separate RC62 pair attracts along Y at X0, Z186.174 mm, on the four tube axes.
Its nominal attracting-face separation is 2.646 mm through the two 1.20 mm covers
and frame gap. Its load path enters the cradle and fixed bulkhead at tube height.
The [retention geometry check](../../printed-parts/enclosure/enclosure/magnet-retention/geometry-check.json)
does not establish its installed pull, cover strength or ability to overcome the
tube insertion force and pogo springs. The existing seating stops and the
compression limits above remain controlling.

Remove appliance power before cartridge insertion or withdrawal. Straight withdrawal
separates the contacts head-on. The four cartridge leads remain on the pump tabs and move
with the cap; the fixed leads stay in the bulkhead passage and ridge clip. Solder joints
need individual insulation and mechanical strain relief. Keep neighboring tails, screws
and magnets clear of the conductors. The printed crown grooves and bore provide routing
space; their geometry does not prove assembled lead retention.

## Print and physical evidence

The male seat prints with front-top in +Z; the female seat prints crown-down with the cap.
The [H2C coupon record](../../printed-parts/enclosure/enclosure/contact-pair-coupon/h2c-print/README.md)
binds an unsupported local trial to a completed task. The founder's
[physical report](physical-observations.json) accepts connector fit and
mating/compression in the printed test piece; no roof measurement is reported. Its longest bridge paths are about 23 mm; the documented clearance
measurement addresses roof sag. The [current full front-top review](../../printed-parts/enclosure/tee-readiness/full-enclosure-print/native-slice-reviews/2026-10-03-enclosure-front-top-current-h2c-v17/README.md)
contains supported functional seats with removal routes through the empty bay. Its recipe
is separate from the unsupported coupon trial and retains its frozen geometry.
The [RC62 front-top source](../../printed-parts/enclosure/enclosure/magnet-retention/front-top-pause.3mf)
has its own current mesh, one insertion pause and a locally blocked pocket roof.
The lower cradle has the matching paused source. Insert each retention ring during
its owning print; clear the accessible supports before threaded inserts, connectors
or pumps are installed.

The [physical record](physical-observations.json) accepts the founder's
successful connector fit and mating/compression check in the printed test piece.
It keeps that observation separate from printer completion and the accepted
pump-holder fit. Numerical full-enclosure compression, four-channel continuity,
magnetic retention, operating contact resistance and lifetime remain unmeasured.
