# Enclosure layer policy

The cartridge upper hand-pocket transition and both bottom handhold transitions
print at 0.24 mm, with six walls only through their declared expanding bands.
The cartridge's lower inward/top hand-pocket rim keeps 0.08 mm. The first bed
layer is 0.20 mm. The cap uses its retained production orientation and ordinary
layer settings.

The bottom flutes fade 1.2 mm of decorative relief over a 5 mm rise. Their
smoothstep fade has a maximum nominal inward change of 0.0864 mm per 0.24 mm
layer. The [current mesh sections](current-bottom-sections.json) bind measured
straight handhold stations; full corners and support contacts are checked in
each native slice. That fade uses ordinary layers.

The [layer policy](layer-policy.json) binds the relevant source functions, mesh
hashes and saved band declarations. The [archived native layer readings](existing-layer-audit.json)
are evidence of the inherited settings, with each archive identified by its
digest. Geometry exports remain frozen.

`prepare.py` creates separate immutable projects. The cartridge project retains
the reviewed RC62 pause, mesh members, solid hosts, support paint, layout and
printer settings. Its upper transition uses 0.24 mm. Each bottom project uses
the current published mesh, current complete insert-host modifiers and the
production support paint for the flat lifting ceilings and accessible grip
slots. These are preparation and slice commands; they do not control printers.

The intended result is an ordinary-layer surface through the additive edges
without unnecessary fine-layer deposition. Native paths establish layer
heights, wall scope, bead overlap and support clearance. Surface quality,
support removal, magnet grip and fastener strength require physical evidence;
these slice reviews do not qualify them. The accepted
[tee-carrier transition](../../tee-carrier/physical-acceptance.json) is the physical
profile reference. The
[cartridge result](../magnet-retention/v4/physical-result.json) keeps the RC62
grip issue open pending the separate fit samples.

Full-part print preparations are deferred. The centered magnet and valve fit
plates are the next prints. The cartridge native review passes; the front-bottom
full review and back-bottom preparation and slice remain pending. A future
full-part start requires a fresh printer reading and material mapping, review
of the exact archive, and the shared-circuit spacing. The cartridge candidate
retains its saved black colour mapping; it requires fresh material matching
before a future start.
