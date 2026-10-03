# ASA Aero and the magnetic float

Sizing and preset evidence for the [PETG-shell bench reference](petg-bench-reference.md).
The current ASA-only float's dimensions and buoyancy model are in
[all-aero/README.md](all-aero/README.md).

Research checked 2026-09-28. [Calculation and preset evidence](asa-aero-research.json).

**Bambu ASA Aero supports a buoyant float at the standard H2C filament settings.**
The 36 × 60.06 mm float with its specified PETG shell has **4.96 g reserve lift**
at a working foam density of 0.55 g/cm³. The independently checked print paths
predict **5.43 g reserve lift**. Both predictions assume an intact sealed shell
at the intended external dimensions.

## Material and manufacturer recipe

The [purchase ledger](../../../ledger/purchases.md#15-3d-printing-equipment-and-filaments-bambu-lab-direct)
records **Bambu ASA Aero White 46100**, two 1 kg spools, order
us718417332286169089. Studio identifies this material as **GFB02**.

The installed Studio 02.08.02.61 preset
`Bambu ASA-Aero @BBL H2C 0.4 nozzle` resolves to:

| Setting | Value |
| --- | --- |
| Nozzle | 0.4 mm standard flow, right side |
| Temperature, first / subsequent layers | 270 / 270 °C |
| Flow ratio | 0.52 |
| Unexpanded filament density for mass accounting | 0.99 g/cm³ |
| Maximum volumetric speed | 12 mm³/s |
| Engineering / smooth PEI / textured PEI bed | 90 °C |
| Chamber | 60 °C |
| Part cooling | 30–50%, first three layers off |
| Auxiliary fan | Off |
| Retraction / wipe | 1.5 / 5 mm |

The float project preserves these filament values. The
[public H2C preset](https://github.com/bambulab/BambuStudio/blob/master/resources/profiles/BBL/filament/Bambu%20ASA-Aero%20%40BBL%20H2C%200.4%20nozzle.json)
and Bambu's [example project](https://wiki.bambulab.com/filament-acc/filament/asa-aero-printing-guide/asa-aero.3mf)
also specify 270 °C and 0.52 flow.

The [ASA Aero guide](https://wiki.bambulab.com/en/filament-acc/filament/asa-aero-printing-guide)
supplies 0.20 mm layers, 0.48 mm lines, ordinary wall/infill speeds of 80 mm/s,
normal acceleration 5,000 mm/s² and outer-wall acceleration 3,000 mm/s².
The guide prefers Engineering or smooth PEI with glue; textured PEI can tear
foam on removal. Single-object printing limits travel stringing. Each float
piece has its own plate in [magnetic-float-aero.3mf](magnetic-float-aero.3mf).

The core process has three wall loops, five top/bottom layers and **100% infill**.
This produces a filled body of foamed extrusions. Bambu's one-wall/zero-infill
aircraft process describes a hollow aircraft skin, not a foam backing core.
Cooling and first-layer slowdowns remain active.

The [TDS](https://store.bblcdn.com/2bb7c6814cdc42d19ffc62570cfc1fb2.pdf)
specifies **80 °C drying for eight hours**, followed by storage below 20% RH.
Use the enclosed printer with room ventilation/extraction. The manufacturer
identifies ASA Aero as unsuitable for food-contact applications; it remains
fully enclosed by PETG in this bench article. The finished wetted surface has
no food-contact qualification recorded.

## Density and buoyancy

Bambu's [density table](https://bambulab-us.myshopify.com/products/asa-aero)
gives **0.46 g/cm³** at 270 °C and **0.45 flow**, on an 80 × 10 × 4 mm specimen
printed with a 0.4 mm nozzle at 80 mm/s. That is a minimum specimen density.
The standard preset uses **0.52 flow**.

At maintained external dimensions, nominal feed accounting gives
`0.99 × 0.52 = 0.515 g/cm³`. Scaling the specimen mass gives
`0.46 × 0.52 / 0.45 = 0.532 g/cm³`. The **0.55 g/cm³ working density** rounds
up from both estimates. It is an engineering assumption, not a measured density
or upper tolerance guarantee. Studio keeps the **0.99 g/cm³ unexpanded density**
so its mass accounting includes foaming only once, through the flow ratio.

The [CAD calculation](design.json) has:

| Component | Volume | Mass basis |
| --- | --- | --- |
| Displaced water, open bore excluded | 60.0468 cm³ | 60.0468 g at 1.000 g/cm³ |
| PETG Translucent Clear shell | 24.8690 cm³ | 31.0863 g at 1.25 g/cm³ |
| Aero core + insert | 34.3750 cm³ | Bulk foam density × volume |
| RC62 magnet | 0.6787 cm³ | 5.09 g from [K&J](https://www.kjmagnetics.com/rc62-neodymium-ring-magnet) |

```text
assembled mass = 36.1763 + 34.3750 × foam density       grams
reserve lift   = 60.0468 − assembled mass              grams equivalent
freeboard      = 60.06 × reserve lift / 60.0468         mm, upright
neutral density = 0.694415 g/cm³
```

| Foam density | Assembled mass | Reserve lift |
| --- | --- | --- |
| 0.46 g/cm³ | 51.99 g | 8.06 g |
| 0.53 g/cm³ | 54.40 g | 5.65 g |
| **0.55 g/cm³** | **55.08 g** | **4.96 g** |
| 0.60 g/cm³ | 56.80 g | 3.25 g |
| 0.65 g/cm³ | 58.52 g | 1.53 g |
| 0.70 g/cm³ | 60.24 g | −0.19 g |

The [native slice verification](verification.json) integrates object extrusion,
including the press-fit compensation and ironing, while excluding brims/purge.
It predicts 18.03 g Aero + 31.50 g PETG + 5.09 g magnet = **54.62 g**.
The modeled PETG thickness, printing provenance and pressure loads are in
[petg-shell.md](petg-shell.md).

## Pressure evidence

Bambu's ASA Aero TDS mechanical specimens were printed at 225 °C and annealed
at 80 °C for twelve hours. Those tensile/flexural results are not compressive
allowables for the 270 °C foamed core. The reported moisture figure is a
humidity-conditioned measurement, not a submerged pressure-leak limit.

[Gaugelhofer and Yavrucuk, 2026](https://doi.org/10.4050/F-0082-2026-0265)
report testing ASA Aero cores for composite-blade manufacture. The accessible
abstract supports the existence of compression testing; it provides no numeric
hydrostatic endurance value applicable to this float. Only that abstract was
available for this research.

The material identity, print recipe, mass and buoyancy are supported by the
manufacturer data and emitted paths. Sustained pressure, sealing and dimensional
stability remain physical results of the assembled float, with no pass claimed.
