# Open snap section

This two-piece coupon lets you watch both hooks and the underside of the cover while pressing it into the receiver. The cover and receiver are each 12 mm long, about 29% of the full Pisco cover. Both ends expose the same cross section. The regulator is represented by a rounded post printed as part of the receiver.

![Open end with the cover lifted to show the hooks and the integral stop](section.png)

## First stop height

The two pieces use the fitted Pisco section at the widest part of the scanned regulator. The cover keeps the +0.40 mm crests, spring roots and saddle. The receiver keeps the original inclined catches and pocket roofs. The thinner axial section can take less hand force than the complete cover. [Production fit measurements](../../printed-parts/enclosure/rear-equipment-caps/production-fit.json) · [Flow-meter fit and cross-section photographs](../../printed-parts/enclosure/rear-equipment-caps/prints/2026-11-24-meter-040-relief-mark2/physical-result.json)

The center of the post stands **34.68 mm above the receiver’s flat print face**. At this height its rounded nose touches the center of the saddle at the same modeled closure as the two wing crests reach their pockets. That is 0.10 mm of travel from the cover’s nominal installed position. The 6 mm-wide post has a 5 mm nose radius and leaves 0.58 mm of modeled clearance at each shoulder when centered. This gives the cover a place to bear while leaving both wings free to bend. [Section dimensions and print orientations](parts/geometry.json)

Press the cover on from above with the receiver resting on its flat back. Look into an open end and press alternately over the two wings. Compare the gap at each tip, contact at the center post and whether either wing shifts and stays in a second position after release. A firm hold with a small visible gap is the equipment reference for this trial.

In the Mark2 bench test, the upper tip lifted under hand pressure. Both hooks stayed captured when Derek let go, and he saw the cover return to its previous position. He confirmed that the coupon reproduces the equipment fit. [Filmed result and four stills](prints/2026-11-24-mark2/physical-result.json)

## Proposed comparisons

Use the filmed pair as the control. A receiver with a shorter center post tests how much the saddle contributes to spring-back. Filling the square corner behind each lead-in tests how much of the old pocket the hook uses during entry and release. A cover with the retaining face relieved tests whether the wings can sit straighter and keep their grip. Each proposal changes one part and uses its original mate. [Proposed sections, clearances and Mark2 perimeter measurements](proposed-comparisons.json)

## Reproduce the pair

The source takes a constant section from the production bodies. To change only the center support in a later trial, change `FILLER_CONTACT_TRAVEL`. A larger value shortens the post and lets the cover travel farther before touching it. [Coupon source](coupon.rs)

```sh
tools/run -- cargo run --release --locked -j2 --manifest-path tools/hsm/Cargo.toml \
  -p hsm-sandbox --example open-snap-section -- hardware/print-tests/open-snap-section/parts
tools/run -- tools/hsm/target/release/enclosure-print-prep open-snap-section \
  --printer Mark2 --bed 'Textured PEI Plate' --slice --review
```

On the Mark2 plate the receiver sits on its flat back and the cover stands on one open end, matching their production layer directions. The third piece is a hollow cooling wall. Its wide section lasts until the fixed catches finish, then a narrow column continues alongside the center post. It gives the cover at least 23 seconds between layers and keeps the plate to about an hour. [Cooling measured from the toolpaths](prints/2026-11-24-mark2/cooling.json) · [Mark2 print record](prints/2026-11-24-mark2/print-job.json)
