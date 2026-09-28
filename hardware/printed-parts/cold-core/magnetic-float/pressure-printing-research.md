# Pressure printing: evidence and first-article choices

Research checked **2026-09-28**, including publications through 2026. The task is
an uncoated PETG Basic envelope around an ASA Aero core, under **external** water
pressure: 90 psi operating reference, 125 psi relief reference, and a 180 psi,
30-minute first-article hydrostatic proof target.

**FDM PETG can retain substantial pressure without a coating.** Published
positive results include printing parameters and downloadable projects. They
establish feasibility of sealing the material; their geometry, loading and
exposure duration determine which conclusions transfer to this float.

## First article

Use the [specified shell and recipe](petg-shell.md): **3 mm outer wall, 1.8 mm
bore lining, 3 mm floor, 3.06 mm roof**; Bambu PETG Basic on the 0.6 mm nozzle,
255/260 °C, 0.30/0.18 mm layers, 0.60 mm lines, flow **1.02**, six requested
walls, 100% solid fill and 10–20% part cooling. Use the float's slow wall speeds,
zero seam gap, unconditional scarf seams and fully backed roof. ASA Aero keeps
the [manufacturer-based printing recipe](asa-aero-research.md).

This selection combines the repository's actual water-holding result with the
process variables supported by the studies below. Its pressure endurance is
unknown. The incomplete sphere record establishes no limit for an unpierced
wall; the recovered event concerns a printed threaded port.

Prepare the cooled core, insert, magnet and tools before the shell reaches its
pause. Keep the bed at its prescribed temperature, complete insertion promptly,
close the enclosure and resume. Record pause duration. A cold, prolonged pause
introduces a bond condition absent from the successful reservoir. Supplemental
reheating and salt remelting require their own process development, including
protection of foam geometry and the magnet's temperature limit.

## Strongest PETG successes

### Uncoated fittings, 2025: substantial pressure with ordinary FDM

[Taherzadeh Fini et al., *Parametric Design of Easy-Connect Pipe Fitting
Components Using Open-Source CAD and Fabrication Using 3D Printing*](https://www.mdpi.com/2504-4494/9/2/65),
Table 3, §2.3, §3.1–3.2 and Figures 6–7:

- Polymaker PETG bodies/nuts with TPE gaskets; **no post-processing**.
- The 10 mm-pipe assembly reached **4.551 ± 0.138 MPa (660 ± 20 psi)**;
  the 20 mm assembly reached **2.392 ± 0.138 MPa (347 ± 20 psi)**.
- Internal water pressure increased in 0.345 MPa/50 psi steps, with **180 s
  between increments**. At least three assemblies per combination were tested.
  Maximum pressure depended on nut torque; excessive tightening cracked parts.

This establishes uncoated PETG sealing at substantial pressure. Short steps in
small fittings do not establish sustained endurance or external-collapse
resistance. The nominal 2 mm wall parameter excludes nut and shoulder geometry.

### What the downloadable print files actually contain

The [authors' OSF archive](https://osf.io/fqjxe/) supplies projects and G-code;
their [publication CAD branch](https://github.com/uwo-fast/pipe-fitting-SCAD/tree/jmmp)
supplies geometry. The inspected PETG projects contain:

| Setting | 10 mm fitting | 20 mm fitting | 10 mm nut |
| --- | --- | --- | --- |
| Flow multiplier | 1.15 | 1.10 | 1.05 |
| Nozzle / layer / line width | 0.4 / 0.15 / 0.50 mm | Same | Same |
| Temperature, first / subsequent | 230 / 240 °C | Same | Same |
| Bed | 80 °C | Same | Same |
| Outer / other perimeter speed | 40 / 65 mm/s | Same | Same |
| Requested perimeters / generator | 6 / Arachne | Same | Same |
| Infill / overlap | 100% concentric / 20% | Same | Same |
| Seam / fan range | Aligned / 30–50% | Same | Same |

The downloadable 10 mm fitting G-code confirms these settings. Its `M221 S100`
resets runtime flow scaling; the slicer's multiplier is already included in
extrusion moves. Object metadata adds no flow/infill overrides. **The archive
and paper differ on fill pattern and 10 mm nut flow.** Neither is silently
substituted for the other. URLs, extracted settings and file hashes are in
[pressure-printing-sources.json](pressure-printing-sources.json).

### Heat-treated PETG, 2025: a meaningful duration result

[*A Low-Cost Pressure-Driven Filtration System for Nanofiltration Membrane
Evaluation*](https://www.mdpi.com/2813-6640/3/4/14), §3.1 and §5:
printed PETG pressure components operated at **7.6 bar (110 psi) for 24 hours**
at 23 °C. The method uses 100% infill, **fine-salt packing and 180 °C for
40 minutes**, followed by wet-polishing sealing surfaces. The reservoir bottle
is a purchased carbonation bottle; the whole apparatus is not a printed tank.

This supports a defined post-processing route. It does not demonstrate the same
endurance for untreated PETG or our assembled PETG/Aero/magnet float. Heating the
assembled float to 180 °C is incompatible with its current material/fit basis.

## Which printing variables have experimental support?

| Primary experiment | Relevant observation | Transfer to this float |
| --- | --- | --- |
| [Gordeev et al., PLOS ONE, 2018](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0198370), Figures 3–5 and methods | Increasing extrusion multiplier closed connected pores; a 4 bar air-flow series fell from 24 mL/s to zero measured flow. Separate visual bubble screening used about 0.5 bar and included PETG. A different printer required a different multiplier. Solid diagonal fill between wall contours improved sealing in their setup. | Flow is a principal sealing variable. “Zero measured flow” has a measurement limit and no established lifetime. The 4 bar series is not a documented PETG float qualification. An all-perimeter wall is not universally superior to a filled wall. |
| [Al-Hasni & Santori, *Vacuum*, 2020](https://doi.org/10.1016/j.vacuum.2019.109017), Table 3; [author manuscript](https://www.pure.ed.ac.uk/ws/portalfiles/portal/115875507/3D_printing_of_vacuum_and_pressure_tight_polymer_vessels_for_thermally_driven_chillers_and_heat_pumps.pdf) | FDM study using ABS/PLA, 6 mm tube walls. At 0.09 mm layers and reported initial pressure 470 kPa, 100→110% flow reduced leakage from 4.87×10⁻³ to 1.51×10⁻⁵ Pa·m³/s, about 323-fold; leakage remained measurable. | Thick walls and nominal 100% fill alone do not assure sealing. This is process evidence, not a PETG rating. The pressure's gauge/absolute convention is not clearly specified. |
| [Szczęch & Sikora, 2024](https://www.astrj.com/The-Influence-of-Printing-Parameters-on-Leakage-and-Strength-of-Fused-Deposition%2C178330%2C0%2C2.html), Figures 4–5 | Thin PLA cylinders, 0.4 mm nozzle, 200 kPa air tests. With a 0.8 mm wall, 0.20 mm layers leaked substantially faster than 0.10/0.15 mm layers. Apparatus background leakage was measured. Text and plot labels differ on absolute leakage units. | The direction of the layer-height effect supports low layers; absolute leakage numbers are not transferred here. This does not prescribe PETG temperatures or shell thickness. |
| [Prusa, open vessels, 2021](https://blog.prusa3d.com/watertight-3d-printing-pt1-vases-cups-and-other-open-models_48949/) | Systematic water-holding trials favor adequate walls, lower layers, careful floor/seam paths and added flow; dimensions can grow with added flow. | Supports the successful reservoir recipe. Our 0.18 mm layer on a 0.6 mm nozzle has a low 0.30 height/nozzle ratio. |
| [McCauley et al., 2026](https://link.springer.com/article/10.1007/s40964-026-01693-w), §2–3 | PLA specimens paused 30 s at each layer had 7.44 MPa interlayer tensile strength versus 17.17 MPa controls; supplemental heating partly restored strength. Printer, material and repeated-pause protocol differ from ours. | Minimize the insertion pause and preserve normal bed heat. These data supply neither a PETG strength knockdown nor a validated reheating recipe for our magnet/foam assembly. |

Line width, infill overlap and flow serve different purposes. A slicer changes
path spacing as line width changes; that is not a controlled increase in
material delivered to a fixed volume. Infill overlap acts at the infill/wall
junction. Flow changes the extrusion amount. A wider nominal line or a glossy
surface does not by itself establish a sealed pressure boundary.

## Failure evidence and limits on headline claims

- [Prusa's closed-vessel study](https://blog.prusa3d.com/watertight-3d-printing-part-2_53638/)
  reports leakage through untreated PETG seams/infill junctions and success
  with epoxy-coated PETG. Selected other materials survived 20 m; its
  flashlight reached 30 m. Those examples establish neither a universal FDM
  pressure ceiling nor an untreated PETG success at our target pressure.
- [*Feasibility Study of Manufacturing Hydraulic Fittings*, 2026](https://www.mdpi.com/1996-1944/19/4/799)
  reports PETG leakage above 0.5 bar and interlayer failure during further
  tightening at 1 bar. Its 1.2 mm wall, 95% fill, 100% flow, 235 °C and
  50% fan differ from the successful fitting process. A failing threaded
  assembly does not isolate the pressure strength of an unpierced wall.
- [Firsthand Prusa forum pressure trials](https://forum.prusa3d.com/forum/english-forum-general-discussion-announcements-and-releases/watertight-prints-for-high-pressure-environments/)
  report an uncoated PETG cylinder filling approximately 75% with water during
  two hours at 5 bar external pressure despite 1.1 flow. A later **epoxy-coated
  PLA** article reportedly stayed dry for five days at 8 bar. Different material,
  coating and informal protocol: useful observations, not an uncoated PETG pass.
- [Formlabs/URI's enclosure tests](https://formlabs.com/eu/white-papers/3d-printing-watertight-enclosures-and-pressure-testing-results/)
  provide high external-pressure results for SLA/SLS. Their FDM comparison was
  a Craftbot PLA print that absorbed water and was excluded from pressure tests.
  That sample cannot establish that all FDM PETG is unsuitable.

## Recent developments and access limits

[Bond et al., July 2025 preprint](https://www.researchsquare.com/article/rs-6674568/v1)
([author-hosted full text](https://www.researchgate.net/publication/394062418_A_new_method_to_hermetically_seal_FDM_prints_applied_to_pressure_vessels_and_clean_room-grade_wafer_holders))
uses a Bambu X1 Carbon for two-stage deposition: print a containing wall, then
fill it slowly/hotly while cooling its exterior. Small pressure components
reached 3,000 psi; pressure decay was substantially better than conventional
deposition, but pressure loss remained. The published temperature/speed table
is for PVDF; it does not clearly identify a complete pressure-vessel
material/recipe. **This is not a 3,000 psi PETG result or an ordinary Bambu
preset.** It is a promising process-development direction, with preprint status,
rather than a setting to transplant into this first float.

Two unusually relevant leads have accessible abstracts but no recovered full
numerical results:

- [Krohmann et al., OMAE 2022, subsea enclosures](https://doi.org/10.1115/OMAE2022-79026):
  PETG/PC, water conditioning, external-pressure collapse and post-processing.
- [Gaugelhofer & Yavrucuk, VFS Forum 2026, rotor cores](https://doi.org/10.4050/F-0082-2026-0265):
  explicitly tests Bambu ASA Aero in compression, including elevated temperature.

Neither abstract supplies a usable collapse pressure or a foam compressive
allowable for this design. The retrieved sources provide no directly matching
uncoated PETG/270 °C-printed ASA Aero float result at 180 psi external pressure.

## Flow, thickness and buoyancy together

The local **1.02** flow is the successful PETG Basic recipe. Against its **0.97**
stock baseline it is already **5.15% more extrusion**. Multiplier values depend
on the slicer, material and printer; a published 1.15 is not a portable target.
Keeping the proven local value is the strongest available starting point.

The [native slice](verification.json) predicts 31.50 g of PETG and 5.37 g of
spare lift. With identical paths and external dimensions, an extrusion-only
estimate gives:

| PETG flow scenario | Added PETG mass | Remaining spare lift |
| --- | --- | --- |
| 1.02, specified | 0.00 g | 5.37 g |
| 1.05 | 0.93 g | 4.44 g |
| 1.08 | 1.85 g | 3.52 g |
| 1.15 | 4.01 g | 1.36 g |

These are mass sensitivities, not freshly sliced alternatives or predictions
that extra extrusion remains dimensionally contained. Flow changes can also
affect the bore, foam insertion fit and seams.

For the CAD mass model at **0.55 g/cm³ Aero**, changing only the outer wall,
keeping OD 36 mm, height 60.06 mm, caps and bore unchanged, gives:

| Outer wall scenario | Reserve lift |
| --- | --- |
| 3.0 mm, specified | 4.90 g |
| 3.6 mm | 2.80 g |
| 4.0 mm | 1.45 g |

The thicker wall replaces foam with PETG over the 54 mm interior height.
Added mass is `π × [15² − (18 − t)²] × 54 / 1000 × (1.25 − 0.55)` grams.
These CAD/density estimates and the native-extrusion estimates above are
separate mass models. [Source data and calculations](pressure-printing-sources.json)
preserve their inputs.

The 3 mm choice provides meaningful wall depth and better ovalization resistance
than a thin float skin while preserving buoyancy. The
[pressure calculation](pressure-analysis.json) explicitly screens cylinder
stresses and stiffness sensitivity; it does not qualify flat-end bending,
pause bonding, creep, foam crushing or connected porosity. The evidence supports
this first article, with an actual external-pressure result still to be measured.

The [assembled-float protocol](README.md#pressure-test) distinguishes water
ingress from structural deformation: gauge pressure alone cannot reveal water
entering a submerged float. Dry mass, post-hold mass, shape, lift and guide motion
are the relevant observations. A short proof hold and sustained service
endurance are different results and receive separate records.
