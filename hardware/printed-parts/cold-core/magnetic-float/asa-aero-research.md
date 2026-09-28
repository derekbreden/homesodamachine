# ASA Aero and the magnetic float

Research checked 2026-09-28. [Calculation and preset evidence](asa-aero-research.json).

**The purchased material supports a buoyant float at Bambu's standard H2C
filament settings.** For the present 28 × 50 mm geometry, a 0.55 g/cm³ core
gives 25.28 g assembled mass, 4.09 g of reserve lift in water, and 6.96 mm
of height above the water when upright. This is an engineering prediction for
an intact, sealed envelope at the modeled dimensions.

## Material identity

The [purchase ledger](../../../ledger/purchases.md#15-3d-printing-equipment-and-filaments-bambu-lab-direct)
records two 1 kg spools of **Bambu ASA Aero, White 46100**, acquired in order
us718417332286169089. The saved float projects specify PLA Aero, filament
GFA11, at 250 °C and 0.38 flow. The installed ASA Aero preset identifies GFB02.
The saved projects are not ASA Aero print files.

## Bambu's recipe

The installed Studio 02.08.02.61 preset
`Bambu ASA-Aero @BBL H2C 0.4 nozzle` resolves to:

| Setting | Value |
| --- | --- |
| Nozzle | 0.4 mm, standard flow for this recommendation |
| Nozzle temperature, first and subsequent layers | 270 °C |
| Flow ratio | 0.52 |
| Filament density used for mass accounting | 0.99 g/cm³ |
| Maximum volumetric speed | 12 mm³/s |
| Engineering, smooth PEI or textured PEI bed | 90 °C |
| Chamber target | 60 °C |
| Part cooling | 30–50%; off for the first three layers |
| Auxiliary fan | Off |
| Retraction / wipe distance | 1.5 / 5 mm |

These are resolved manufacturer settings, including inherited values. Their
source hashes are in the evidence JSON. The public
[H2C preset](https://github.com/bambulab/BambuStudio/blob/master/resources/profiles/BBL/filament/Bambu%20ASA-Aero%20%40BBL%20H2C%200.4%20nozzle.json)
also specifies 270 °C, 0.52 flow and a 60 °C chamber. Bambu's
[downloadable example project](https://wiki.bambulab.com/filament-acc/filament/asa-aero-printing-guide/asa-aero.3mf)
uses the same temperature and flow.

Dry at **80 °C for eight hours**, then feed from dry storage below 20% RH.
The [ASA Aero TDS](https://store.bblcdn.com/2bb7c6814cdc42d19ffc62570cfc1fb2.pdf)
specifies these conditions.

For the Aero pieces, the process recommendation is:

- Engineering plate or smooth PEI with Bambu glue; an enclosed printer with
  room extraction or ventilation.
- 0.20 mm layers, 0.48 mm nominal lines, and 80 mm/s for ordinary walls and
  infill. Retain the manufacturer's first-layer and cooling slowdowns.
- Three wall loops, five top/bottom layers and **100% infill** for the core.
  Full infill here is a filled body of foamed extrusions; the material still
  contains its microscopic gas volume.
- Print each core piece individually or use sequential printing with verified
  head clearance. Trim travel strings before assembly.

Bambu's [ASA Aero printing guide](https://wiki.bambulab.com/en/filament-acc/filament/asa-aero-printing-guide)
supplies the line width, ordinary speeds and single-object guidance. Its
one-wall, zero-infill aircraft shell is a different structure from this
skin-supporting core; wall count and solid fill above are part-specific choices.
The guide prefers smooth/Engineering plates because removal from textured PEI
can tear the foam's bottom layers. The product page also lists textured PEI as
compatible. Smooth/Engineering is the recommendation for these pieces.

## Buoyancy calculation

The open 6 mm guide bore fills with water and contributes no displacement.
Independent annulus calculations reproduce the CAD volumes; all three STL
volumes agree within 0.015%.

| Component | Volume | Mass basis |
| --- | --- | --- |
| Complete envelope, excluding the guide bore | 29.3739 cm³ | 29.3739 g of water at 1.000 g/cm³ |
| PETG skin | 6.3020 cm³ | 7.8775 g at the installed preset's 1.25 g/cm³ |
| Aero core and insert | 22.3931 cm³ | Bulk foam density × volume |
| RC62 magnet | 0.6787 cm³ | 5.09 g from [K&J](https://www.kjmagnetics.com/rc62-neodymium-ring-magnet) |

With core density `rho` in g/cm³:

```text
assembled mass = 12.9675 + 22.3931 × rho           grams
reserve lift   = 29.3739 − assembled mass         grams equivalent
freeboard      = 50 × reserve lift / 29.3739      millimetres, upright
neutral rho    = (29.3739 − 12.9675) / 22.3931 = 0.73265 g/cm³
```

| Aero bulk density | Assembled mass | Reserve lift | Upright freeboard |
| --- | --- | --- | --- |
| 0.46 g/cm³ | 23.27 g | 6.11 g | 10.39 mm |
| 0.53 g/cm³ | 24.84 g | 4.54 g | 7.72 mm |
| **0.55 g/cm³** | **25.28 g** | **4.09 g** | **6.96 mm** |
| 0.60 g/cm³ | 26.40 g | 2.97 g | 5.06 mm |
| 0.65 g/cm³ | 27.52 g | 1.85 g | 3.15 mm |
| 0.70 g/cm³ | 28.64 g | 0.73 g | 1.24 mm |

Bambu's [ASA Aero density table](https://bambulab-us.myshopify.com/products/asa-aero)
gives 0.46 g/cm³ at 270 °C and 0.45 flow, measured with a 0.4 mm nozzle at
80 mm/s. That is a minimum specimen density, not the stock-preset prediction.

Two estimates locate the standard 0.52-flow recipe: nominal feed accounting
gives `0.99 × 0.52 = 0.515 g/cm³`; scaling Bambu's specimen mass to 0.52 flow
at unchanged dimensions gives `0.46 × 0.52 / 0.45 = 0.532 g/cm³`.
Both assume the foamed paths occupy their intended dimensions. The 0.55 g/cm³
working estimate rounds upward from them; it is not a measured value or an
upper tolerance guarantee. The sensitivity table shows that the core can be
about 33% denser than this working estimate before buoyancy disappears.

The unexpanded filament density of 0.99 g/cm³ belongs in Studio's mass
accounting. Replacing it with foam density would count the weight reduction
twice. A body with this geometry filled with unexpanded 0.99 g/cm³ material
would weigh 35.14 g including PETG and magnet and would sink.

The lift calculation assumes free vertical movement. Guide friction and magnet
attraction can consume its roughly 0.040 N reserve at the working density.

## Fabrication recommendation

Print the Aero body core and upper insert separately with the ASA preset.
Print the PETG envelope with its own H2C PETG Translucent preset: 250 °C first
layer, 245 °C afterward, 0.97 flow, a 70 °C bed and no active chamber heat.
Install the cooled core, magnet and upper insert before the PETG roof closes.
The present nominal geometry has an unobstructed axial insertion path through
the annular opening; printed fit still needs allowance appropriate to this
assembly. The full-height core and guide lining have nominally touching faces.

This fabrication route preserves each material's manufacturer temperature and
flow settings. ASA's 90 °C bed / 60 °C chamber and PETG's 70 °C bed / unheated
chamber cannot both be the environment of one simultaneous print.

The existing 3MF prints the core together with the skin and pauses only for the
magnet and upper insert. A separate-core project needs a core plate and a
PETG-only envelope plate, with the insertion pause before the first roof
layer at Z49.2 mm. No ASA project is generated by this research record.
The 0.2 mm project likewise uses PLA Aero. The recommended ASA route uses
0.4 mm, the nozzle used for Bambu's foaming data and supported H2C preset.

Bambu explicitly excludes ASA Aero from food contact in its printing guide.
The Aero therefore remains completely enclosed; its buoyancy says nothing
about the finished PETG envelope's beverage-contact suitability.

## Pressure evidence

The carbonator's 90 psi operating pressure is 0.621 MPa; its 180 psi hydrostatic
test pressure is 1.241 MPa. With an initially atmospheric interior, these
differentials apply approximately 365 N and 729 N, respectively, to an
annular end of this float. The internal foam and skin carry those loads.
Uniform external pressure itself does not cancel buoyancy: buoyancy remains
the displaced liquid's weight while external dimensions remain intact.

At the 0.55 g/cm³ working density, loss of 4.09 cm³ of displacement or gain of
4.09 g through flooding would consume the reserve. The former is 13.9% of
the initial displacement. Small elastic compression does not immediately make
the float sink; collapse or enough water ingress does.

The ASA Aero TDS gives tensile/bending results for 225 °C specimens annealed
at 80 °C. It supplies no crush curve, hydrostatic endurance or creep allowable
for this 270 °C foam. Its 0.80% water-absorption figure is labeled 25 °C / 55%
RH; it is not a bound on liquid filling accessible pores under pressure.

A [2026 rotor-core paper](https://doi.org/10.4050/F-0082-2026-0265) reports ASA
Aero compression and moisture characterization. The accessible abstract
supports its use under composite-curing loads but supplies neither numerical
compression data nor this float's sustained carbonated-water exposure.
Only that abstract was available in this research. It cannot establish a
90 psi rating for the float.

The material selection, buoyancy prediction and manufacturer print recipe
have a numerical basis. Sustained sealing and pressure endurance of the
finished assembly remain separate qualification results; none is claimed here.
