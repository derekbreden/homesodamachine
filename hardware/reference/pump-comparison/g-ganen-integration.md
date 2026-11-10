# G Ganen enclosure integration map

The selected received pump is **G Ganen B07F35PTFR**. Its measured housing,
independent barbs and purchased removable sliders belong to
[the reference](../g-ganen-pump/README.md). The complete rubber foot-and-leg
assemblies slide out of the fixed rails and are absent from production.

The [native equipment constructor](/tools/hsm/machine-data/src/equipment.rs)
selects the bare pump replica. The scene key is `g-ganen-pump`;
[above-core.json](../../manifold-layout/above-core.json) owns its world pose.
Suction faces east and discharge west.

| Consumer | Current contract |
|---|---|
| [Native equipment](/tools/hsm/machine-data/src/equipment.rs) | Casing, motor, rails, switch and barbs, excluding removable rubber sliders |
| [Foam cap and pump snap cap](/hardware/printed-parts/cold-core/foam-cap/foam_cap.rs) | Integral motor seat, fixed-rail admission and removable snap retention |
| [Native rear plumbing](/tools/hsm/layout-data/src/rear.rs) | Clamped pump joints, discharge check and continuous water-in route |
| [Native geometry queries](/tools/hsm/README.md) | Measurements of the current exported assembly |

The [installation procedure](../g-ganen-pump/installation/README.md) describes the
bearing geometry and service sequence. The
[mechanical records](../../mechanical-qualification/enclosure-above-core/README.md)
bind their observations to the identified geometry and print inputs. Snap retention,
vibration, printed force and hydraulic performance require the physical article.

The two front flavor pumps have their own cradle and retainer. Their accepted
local bearing surfaces retain their specifically bound qualification.
