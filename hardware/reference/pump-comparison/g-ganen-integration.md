# G Ganen enclosure integration map

The selected received pump is **G Ganen B07F35PTFR**. Its measured housing,
independent barbs and purchased removable sliders belong to
[the reference](../g-ganen-pump/README.md). The complete rubber foot-and-leg
assemblies slide out of the fixed rails and are absent from production.

[The installation API](../g-ganen-pump/installation/g_ganen_installation.py)
supplies the bare fixed pump and independent ports. The scene key is
`g-ganen-pump`; [above-core.json](../../manifold-layout/above-core.json) owns its
+90° yaw and world pose. Suction faces east and discharge west.

| Consumer | Current contract |
|---|---|
| `above_core_parts.pump_native` | Fixed casing, motor, rails, switch and barbs, with no rubber sliders |
| `_above_core_mounts.pump_cradle` | Integral rear casing bearing; front casing bears directly on the plain lid |
| `_above_core_mounts.pump_tie_cuts` | Underside-open lanes for two loops, each using two joined 8-inch wide ties |
| `enclosure_assembly.pump_mount_rows` | Empty: no pump screws or internal cup columns |
| `rear_plumbing` | Clamped PVC/reducer joints, discharge check and continuous water-in bend |
| `_scorecard.pump_cap_contact` | Complete bare rigid pump against installed core material |
| The BOM program and assembly instructions | Four owned wide ties and the bare-casing mounting sequence |

The [installation procedure](../g-ganen-pump/installation/README.md) gives the
native datum, bearing height, strap routing and replacement sequence. The
[mechanical records](../../mechanical-qualification/enclosure-above-core/README.md)
describe their nominal geometry and exact print inputs. Strap retention,
vibration, printed force and hydraulic performance require the physical article.

The two front flavor pumps have their own cradle and retainer. Their accepted
local bearing surfaces retain their specifically bound qualification.
