# Pump cartridge magnetic contacts

The current mechanism uses one [YYFKGCP four-pin pair with ears](https://www.amazon.com/dp/B0GCBNTBT8?th=1).
The female pad half mounts in the pump cap's aft face; the male spring-pin half mounts in
front-top's bay bulkhead. Each purchased half contains two magnets. The printed parts
provide recessed screw-fastened seats and lead passages. A separate
[six-pair SB443-IN array](../../printed-parts/enclosure/pump-dock/magnet-retention.md)
retains the lower cartridge cradle against the fixed receiver wall at the fluid-port
row, below the pogo row. Grooved rails and mechanically keyed, room-cured DP420
Off-White bedding capture those post-print-loaded blocks. Their pole faces are
gauged against the actual seated frame before cure. The pump cap contains its
purchased connector magnets.

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
tip through the 2.6 mm wide loading stadium, with no printed-wall contact, and calibrate the
insert-top depth to 7.375 mm from the printed host face before heating, as specified in
[enclosure assembly](../../assembly/enclosure-mechanical.md). The existing
coupon retains its recorded seat geometry and connector-fit acceptance. Its result
does not establish the deeper current installation or the actual T18 tool profile/cold fit.

## Current protection

Each purchased contact is specified for 2 A at 12 V and carries one pump's whole
motor current; the four contacts are four separate H-bridge conductors, not
paralleled. In the [PCB source](../../pcb/pcba/pcba.tsx), each DRV8870's ISEN pin
returns to ground through its own 0.2 Ω ±1 % sense resistor (R28 on U11, R29 on U12;
1 W, ±50 ppm/°C, [`C5127778`](../../pcb/pcba/jlcpcb-parts.md)), and VREF connects to
3V3. Texas Instruments' [DRV8870 data sheet, §7.3.3 and
§6.5](https://www.ti.com/lit/ds/symlink/drv8870.pdf) sets the trip at
VREF / (A_V × R_ISEN): 1.65 A nominal, 1.54–1.81 A across the ISEN gain A_V of
9.4–10.4, the AMS1117's ±2 % on 3V3 and the resistor's ±1 %. At the trip the bridge
brakes on both low-side switches for 25 µs and drives again, so a starting or jammed
pump is held there, and the current circulating through the brake keeps the contacts
at the trip current. The appliance drives each pump at full duty, a static input that
§7.4.3 regulates the same way. Boards from the first two JLCPCB batches ground ISEN;
their bound is the driver's 3.7–6.4 A overcurrent protection.

A primed head starts against the trip current, about twice the ~0.8 A it runs at.
No start under it is recorded, and a head that does not start delivers no flavor.
The observation is one start on a board of this revision, with the cartridge seated,
the channel primed, and the pump and its syrup at the coldest the cabinet is expected
to hold them: hold Prime on the machine display and film the head with a phone, sound
on. The motor sounds as soon as its bridge drives, turning or not. It passes when the
head turns at its steady rate within 1 s of that first sound. A head that hums without
turning, or is still gathering speed at 1 s, means the trip is too low for it. No
jam-current or installed contact-resistance result is recorded.
The service joint is mated and parted with appliance power removed.

## Seating and dimensional allowance

The founder reports successful connector fit and mating/compression in the
printed test piece on 2026-10-04. That result is accepted in the
[physical record](physical-observations.json); the report is qualitative and
belongs to the printed test piece.

The dedicated outboard PET-GF stop lands seat against the retained lower cradle
to set full insertion. The four prepared stems enter
permanent TPU receivers and finish 0.50 mm before their internal shoulders. The flat
cap and bulkhead planes have 0.250 mm nominal separation. Each connector face is
recessed 0.125 mm, giving a 0.500 mm nominal contact-face gap. Both connector ear
plates bear 3.00 mm behind their connector faces, 3.125 mm behind the printed host
faces. Two M1.4×8 screws per half clamp each 1.00 mm ear plate onto that datum.
Each M1.4×4 insert starts 4.25 mm behind the datum, 7.375 mm inside the printed face,
and occupies depths 7.375–11.375 mm. The Ø2.00 pilot ends at 12.875 mm; the screw tip
ends at 10.125 mm, leaving 2.750 mm clearance and 2.750 mm thread engagement in the 4 mm insert.
The 2.60 mm wide loading stadium passes the whole knurl. Screw heads finish 0.60 mm behind the connector faces. The insert fit and
printed fastening capacity have no reported physical result.

The [Prime listing](https://www.amazon.com/dp/B0GCBNTBT8?th=1), checked on 2026-10-03,
shows 5.00±0.15 mm male tip height over the back of a 4.00 mm body. Its general tolerance
is ±0.05 mm. Independent extremes therefore permit 0.80–1.20 mm unloaded pin protrusion.
The drawing specifies 1.10 mm total stroke and cautions against overcompression.

Use ±0.05 mm installed face error per half about the specified recess, matching the
position budget in the [coupon criterion](../../printed-parts/enclosure/enclosure/contact-pair-coupon/README.md).
Including drawing extremes gives 0.200–0.800 mm compression at the nominal frame
position. The upper extreme leaves 0.300 mm for additional closing error before
full stroke. This is a conditional drawing calculation; the accepted coupon keeps
its own seat geometry and does not qualify the complete recessed seats. The
complete printed frame's position error, contact tilt and delivered component dimensions
are unmeasured. The controlling installed quantity for each pin is its unloaded protrusion
minus its assembled plastic-face gap, greater than zero and less than 1.10 mm. Face
position alone does not establish that condition.

For a local unpowered mating check, two equal nonconductive shims measured at 0.50 mm
keep the housings parallel, clear of maximum stroke, with all drawing-extreme pins reaching
their pads. Place them beside the contact row without covering pins or magnets. Closing
the plastic faces to zero gap can overcompress a maximum-drawing pin.

## Magnet orientation and load path

Use the pair's attracting orientation. Mark the corresponding ends of both halves that
will stand at machine −X before soldering or mounting. Viewed in machine coordinates,
both contact rows keep the same conductor order. Face-on drawings have opposite viewing
directions when installed; copying their left-to-right labels independently can reverse
the contact order. The [DC-5 schedule](../../wiring/ac-wiring-schedule.md) defines the mapping.

The cartridge floor and fitted wells carry weight and locate the pumps. Its rigid
stop lands set full insertion; the four prepared flanged stems remain captured
in the cradle and enter the stationary TPU receivers. The connector's magnets pull its two
halves together against the four pogo springs, and their force reaches the printed parts
through the connector bodies, ear plates, screws and inserts. They have no specified pull
force at the installed gap and do not establish whole-cartridge retention or vibration
reliability. The seller's 45±10 gf spring figure applies at its stated working height;
there is no force curve for this installed compression. Its 30 mΩ figure and 10,000-cycle
claim are connector specifications, not results for the assembled machine.

The separate SB443-IN array attracts along Y in two three-high columns per half,
between the four receiver axes. Its load path enters the cradle and fixed wall
through the grooved rails and mechanically keyed bedding. The
[retention geometry record](../../printed-parts/enclosure/pump-dock/magnet-geometry.json)
does not establish installed pull, printed-mount strength or the force required
to seat all four fluid joints and pogo springs. The rigid seating faces and the
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
measurement addresses roof sag. The [identified v17 full front-top review](../../printed-parts/enclosure/tee-readiness/full-enclosure-print/native-slice-reviews/2026-10-03-enclosure-front-top-current-h2c-v17/README.md)
contains supported functional seats with removal routes through the empty bay. Its recipe
is separate from the unsupported coupon trial and retains its frozen geometry.
The [RC62 print records](../../printed-parts/enclosure/enclosure/magnet-retention/README.md)
retain their identified ring pockets, covering layers and physical observations.
The current SB443-IN array is installed after printing under its
[factory mounting procedure](../../printed-parts/enclosure/pump-dock/magnet-retention.md).
Clear the accessible supports before threaded inserts, connectors or pumps are installed.

The [physical record](physical-observations.json) accepts the founder's
successful connector fit and mating/compression check in the printed test piece.
It keeps that observation separate from printer completion and the accepted
pump-holder fit. Numerical full-enclosure compression, four-channel continuity,
magnetic retention, operating contact resistance and lifetime remain unmeasured.
