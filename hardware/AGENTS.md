# Hardware

The [hardware map](README.md) describes the machine by subsystem. Check the
[answered concerns](concerns.md) before raising a concern with Derek.

## Design and fabrication

- For a part description or named feature, [find its source and build target](../tools/hsm/README.md#find-and-inspect-a-part).
  Measure positions, gaps and interference on the exported viewer meshes with
  [`hsm`](../tools/hsm/README.md). Show Derek a part or location in the existing published
  model using [`hsm-pick link`](../tools/hsm/inspection/README.md#picks-and-published-links).
- Start concepts, throwaway parts and studies in the [Rust sandbox](../tools/hsm/sandbox/README.md).
  For layout work, [place wiring around the finished mechanics](wiring/README.md#routing-and-assembly).
- Before rebuilding changed enclosure geometry, take the [before snapshot](../changes/README.md#recording-a-change).
  Publish with the [print build](../tools/hsm/print-build/README.md), then record the change from that snapshot.
- For FDM design, fit coupons, plate preparation or print diagnosis, start with
  [Printing the Machine](printing-the-machine/README.md), wherever the trial lives.
  For a requested dimensioned part drawing, use the [engineering drawing workflow](../tools/engineering-drawings/SKILL.md).

## Parts and bench work

- Look up what Derek owns in the [ledger](ledger/AGENTS.md). Apply the [sourcing rules](ledger/sourcing.md) when selecting a part.
- When Derek shares a print result or tries a made part in hand, [record the evidence](ledger/fitted.md).
- For readings on the physical machine, follow the [bench measurement procedure](README.md#bench-measurements).
