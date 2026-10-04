# Pump cartridge magnetic contacts

The current mechanism uses one [YYFKGCP four-pin pair with ears](https://www.amazon.com/dp/B0GCBNTBT8?th=1).
The female pad half mounts in the pump cap's aft face; the male spring-pin half mounts in
front-top's bay bulkhead. Each purchased half contains two magnets. The printed parts
provide screw-fastened seats and lead passages. They contain no separate retention magnet,
encapsulated ring or magnet-insertion pause.

The [native audit](mounting-audit.json) reads the current exports and the production placement
functions. It checks all four nominal pin/pad stations, spring travel, clearances to both
printed parts and the current seat/lead cutters. Reproduce it without regenerating CAD:

```sh
tools/cad-venv/bin/python hardware/reference/yyfkgcp-pogo-4p/audit_mounting.py
```

Both retained contact-coupon STEP crops also match the corresponding regions of the
current exported front-top and cap exactly in the native comparison. This preserves
their local seat geometry as evidence inputs; it does not transfer their unsupported
print recipe to the complete parts.

## Seating and dimensional allowance

The cartridge tubes bottom in the tee bodies at full seat. The flat cap and bulkhead planes
have 0.246 mm nominal separation. Both connector ear plates bear on steps 3.00 mm behind
their printed faces. Two M1.4×5 screws per half clamp each 1.00 mm ear plate onto that datum,
with 4.00 mm nominal engagement in the M1.4×4 inserts. The 5.00 mm insert pockets include
1.00 mm blind relief. Screw heads finish 0.60 mm behind the mating faces. The insert fit and
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

Remove appliance power before cartridge insertion or withdrawal. Straight withdrawal
separates the contacts head-on. The four cartridge leads remain on the pump tabs and move
with the cap; the fixed leads stay in the bulkhead passage and ridge clip. Solder joints
need individual insulation and mechanical strain relief. Keep neighboring tails, screws
and magnets clear of the conductors. The printed crown grooves and bore provide routing
space; their geometry does not prove assembled lead retention.

## Print and physical evidence

The male seat prints with front-top in +Z; the female seat prints crown-down with the cap.
The [H2C coupon record](../../printed-parts/enclosure/enclosure/contact-pair-coupon/h2c-print/README.md)
binds an unsupported local trial to a completed task. It does not record physical fit or
roof acceptance. Its longest bridge paths are about 23 mm; the documented clearance
measurement addresses roof sag. The [current full front-top review](../../printed-parts/enclosure/tee-readiness/full-enclosure-print/native-slice-reviews/2026-10-03-enclosure-front-top-current-h2c-v17/README.md)
contains supported functional seats with removal routes through the empty bay. Its recipe
is separate from the unsupported coupon trial. Clear supports before inserts, connectors
or pumps are installed. No loose magnet is inserted into either print.

The [physical record](physical-observations.json) keeps printer completion separate from
physical observations. The accepted pump-holder fit remains valid for its recorded holder
and does not qualify the connector. Installed compression, attracting orientation,
four-channel continuity, magnetic retention, operating contact resistance and lifetime
have no reported physical result. Those limits do not establish a failure or request a
new founder test. The existing coupon and full-assembly observations supply the appropriate
opportunity to resolve fit and connection before claiming acceptance.
