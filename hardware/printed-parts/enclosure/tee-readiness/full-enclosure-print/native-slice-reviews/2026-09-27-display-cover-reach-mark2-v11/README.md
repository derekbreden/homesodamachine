# Machine display cover reach trial · Mark2

Completed as task **1289413482**, confirmed FINISH at 58/58 layers with no printer errors on 2026-09-28. The launch used the [shared-circuit startup stagger](../2026-09-28-shared-circuit-stagger/README.md).

**Provisionally accepted:** Derek calls this cover workable and good enough for now.
Further tuning is deferred. The [physical acceptance](../../../../display-cover/reach-trial/physical-acceptance.json)
identifies the accepted +0.5 mm reach / 0.9 mm skirt-inset pair with the printed receiver.

One cover with **0.5 mm extra hook reach** and both straight leaves inset **0.9 mm per side**. Nominal clearance beneath the receiver ledges is **0.98 mm**. Each hook overlaps 1.3 mm when centered and at least 1.0 mm at full lateral float. The bezel and window retain their shape. The [existing receiver](../2026-09-25-display-receiver-trial-mark2-v1/README.md) is the mating test piece.

The fit targets are for both hooks to clear their ledges, the leaves to return outward,
and the bezel to relax flat. Derek gives an overall workable-fit acceptance without
individual measurements. The nominal clearance permits 0.98 mm of lift before the
hooks bear. Retention force remains unmeasured.

Black PET-GF, left 0.4 mm Standard nozzle, face down, 0.24 mm layers with a 0.20 mm first layer, two walls, saved speeds and wall order, 15% infill overlap and Mark2's +0.04 mm requested Z trim. Two exposed bed-rooted supports carry the hook bearing faces; peel them outward before fitting the cover.

[Manifest](manifest.json), [geometry reading](geometry-check.json), [native verification](verification.json), [support review](support-removal-review.json) and [launch receipt](restart-1/launch.json) identify the printed geometry and settings. Geometry lint has zero open findings and six intentional faces answered.
