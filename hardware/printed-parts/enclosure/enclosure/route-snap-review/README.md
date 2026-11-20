# Integral tube and cable routing clips

The back-top carries the reservoir A fill tube in one east-wall snap and grows
cable hooks from its wall stock. The [routing source](../quadrants/routes.rs)
locates the seat and hooks. The [cable sites](../../../../../tools/hsm/assembly-docs/src/wiring/cable-sites.json)
and [route dressing](../../../../../tools/hsm/assembly-docs/src/wiring/routes.rs)
locate the retained conductors.

## Fill tube seat

The tube lies horizontally along the east wall, with its snap mouth facing the
interior. Back-top prints ceiling-down, so the wings stack vertically in the
printing pose. The lower wing reaches the wall through a corbel. The upper wing
is free to flex and has the source-selected spring section and jaw opening. The
[production print features](../enclosure-back-top.print-features.json) carry
separate removable support strips under that wing. Their breakaway feet start
on the lower wing, and a screwdriver can reach them through the open mouth.

The [hand-fit record](https://github.com/derekbreden/homesodamachine/blob/9f92649048b4168ef0ad479a5773a7d12fb22977/hardware/print-tests/tube-snap-corbel/prints/2026-11-20-mark1-upper-wing-support/physical-result/physical-result.json)
accepts the fill tube in a printed crop of the production seat. It does not
establish the complete back-top's cleanup or the support strips' release.

## Other tube clips

The [cold-core lid](../../../cold-core/foam-cap/README.md) carries the other
integral clips for horizontal tube runs. Their mouths face away from the lid,
and the lid prints on its flat underside. Both jaws therefore stand side by
side at the same print height. They have no lower wing from which to support
an upper wing. Their [clip source](../../../cold-core/foam-cap/numbers/clips.rs)
owns their sections independently of the back-top snap.

## Cable hooks

Keep the relay ribbon's insulated web flat in its hook, with its conductors
stacked across the seat height. Finish braid and heat shrink outside the
retained straight span. The connector order through the web is GND, V5, IO2,
IO19 from installed positive Z to negative Z. The V-K hook holds
`J2-positive-K`. The [cable preparation instructions](../../../../assembly/cable-assemblies.md#back-top-clip-preparation-and-service)
cover dressing and release. The [combined coupon result](https://github.com/derekbreden/homesodamachine/blob/1f49ea24e261b5b74e8b82d8c3e9ac5690736952/future/snap-fit-tests/2026-10-26-mark2-combined/physical-result.json)
accepts the relay ribbon's fit and qualitative retention; the other cable
hooks remain provisional.

## Installation and service

Seat the reservoir fill tube in the east-wall snap while back-top is open.
Release tubes and cables from their clips before sliding back-top during
opening, and support the free runs while separating the inter-quadrant
connections in the [wiring sequence](../../../../assembly/wiring.md). The open
mouth gives access for release; no separate tool pocket is part of the snap.
