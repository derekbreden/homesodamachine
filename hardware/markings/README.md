# Household refrigerant markings

The design basis for the U.S. residential Home Soda Machine is **household
refrigeration with R-600a**, using EPA SNAP Rule 22 and UL 60335-2-24, second edition,
April 28, 2017. This is the best-supported classification of the described product,
not an individual agency determination. It supplies a usable marking specification
without making an outside inquiry a dependency.

The required warning content occupies **two permanent locations**: integral raised
disposal lettering low on the exterior +Y wall of enclosure back-bottom, and one
service panel near the compressor and exposed tubing. The
brand/serial/QR plate and ordinary appliance ratings can occupy separate surfaces.
The preferred nameplate study is [L](../../future/nameplate-qr-studies/l-big-faucet.svg),
for its balanced interlocking composition. No visible short domain is specified.

## Why household refrigeration

[EPA's definition][definitions] includes small household beverage centers and
stand-alone household ice makers. This machine is a residential kitchen appliance:
it chills carbonated drinking water and flavor reservoirs for household consumption.
Its complete refrigerant circuit stays inside the enclosure; the separate faucet
carries water and flavor. The retail-food category concerns goods for commercial
sale, which is a weaker match to this product. A water cooler describes a simpler
chilled-water appliance and is also a weaker match to this refrigerated beverage
system. Carbonation alone does not establish commercial intended use.

[R-600a is acceptable with conditions in household refrigeration][household]. The
household donor and the finished machine share that intended use. Replacing the
ice-maker evaporator with a coil around the carbonator changes the design that must
meet the safety requirements; it does not itself change the end-use to commercial.
The refrigeration design stays R-600a. R-290 is not a drop-in substitute.

The [2018 final rule][household-rule], 83 FR 38969-38976, incorporates the **April 28,
2017 edition** of UL 60335-2-24. The [codified household entry][appendix-r] retains
that reference. EPA's [current rules index][rules], reviewed September 18, 2026,
lists Rule 27 as proposed; its household addition concerns HCR 4141, a different
refrigerant. The marking basis here is the incorporated 2017 edition.

## Applicable warning content and placement

UL 60335-2-24 (2017), 7.1DV.4.1, gives five warning messages or their equivalent.
The [standard text, pages 26-30][ul2017], specifies their locations. The same warning
sentences are published in the [2011 EPA rule][rule17], 76 FR 78855-78856; the current
legal incorporation and dimensions are established by the 2018 rule.

| Clause | Content | Application to this machine |
| --- | --- | --- |
| (a) | No mechanical defrosting; do not puncture refrigerant tubing | Not included. It is required near evaporators a user can contact. The coil is embedded in the closed cold core, with no user defrosting surface. |
| (b) | Flammable refrigerant; trained service personnel; do not puncture tubing | Include near the compressor compartment. |
| (c) | Consult repair manual/owner's guide; follow all safety precautions | Include near the compressor compartment. |
| (d) | Proper disposal under applicable federal or local regulations | Include on the exterior of the enclosure. A rear or side face is suitable. |
| (e) | Fire/explosion from punctured tubing; follow handling instructions | Include beside tubing exposed when the compressor compartment is opened. One panel serves the clustered compressor, process tube and coil connections; another location would need a copy if exposed tubing were separated from this panel. |

The service panel combines (b), (c) and (e). It keeps all substantive instructions,
uses DANGER, and states the tubing-puncture fire/explosion hazard. Combining equivalent
wording is an implementation judgment based on the clause's express permission for
equivalent markings. Three separate stickers and repeated introductory sentences
are not the design target. The exterior panel reproduces (d) with CAUTION.

The service panel belongs near the compressor compartment, visible as it is opened,
and near the exposed tubing. The disposal panel must remain outside. The interior
placement of the service messages is an interpretation of their specified location
near the machine compartment; only the disposal clause explicitly says exterior.
A fixed carrier is preferable to a loose removable cover that could be set aside
while the technician works.

## Lettering, symbol and service-tube color

**6.4 mm is the U.S. minimum warning-letter height in the incorporated edition.**
Clause 7.1DV.4.2 and the [2018 final rule][household-rule], 83 FR 38973, explicitly
retain it. The proof uses 6.5 mm H capitals; the shortest actual letter outline is
6.491 mm. This requirement applies to the specified warning messages, not every
letter on the brand plate or ordinary rating label.

The [2020 UL revision notice][ul2020] allows 3.2 mm body letters with 5.0 mm uppercase
signal words and removes the separate consult-manual message. That explains smaller
warnings on newer products, but does not replace the edition incorporated into the
current R-600a listing. This specification uses 6.4 mm because it is the applicable
published dimension, not an added safety margin.

The household symbol is **ISO 7010 W021**, the flame in a warning triangle, at least
15 mm high, visible when gaining access to the compressor (7.1DV.6, 7.14, 7.15).
The proof has an 18 mm triangle and R-600a identification in the service-panel header.
The red GHS diamond and an adjacent A3 designation from the commercial rule are not
required by this household marking provision. The source [W021 artwork][w021] is
public domain; the supplied file retains the source geometry. Production color and
contrast must reproduce the safety sign, not just an unframed white flame.

Clause 7.1DV.4.4 requires **PMS 185 red** at expected refrigerant service-opening
locations. The compressor process-tube marking extends at least **25 mm from the
compressor**. Color the BPV31/process-tube service area without obstructing its seal,
threads or inspection surfaces. The commercial wording requiring 25 mm in both
directions is not the household wording. The [2017 Intertek notice][ul2017-sun]
independently reproduces the household color and size provisions.

## Dimensioned artwork

Print the [two-page proof](../../output/pdf/refrigerant-warning-proof.pdf) at
**100% / actual size** and check its 50 mm scale bars.

| Panel | Artwork | Size | Position |
| --- | --- | --- | --- |
| Exterior disposal wording proof | [SVG](artwork/household-exterior-disposal.svg) | 190 x 71 mm | Integral raised lettering on enclosure back-bottom; the CAD defines its centered layout |
| Combined service | [SVG](artwork/household-service.svg) | 190 x 163 mm | At compressor access, near the exposed tubing; includes W021 and R-600a |

These are artwork dimensions, not mandated label dimensions. Width, line breaks and
panel shape can change while preserving the warning content, letter height and
location. The 215 x 462 x 361 mm enclosure provides substantially more marking area
than the 104.53 x 66.07 mm brand plate.

The exterior implementation is owned by the [enclosure CAD](../printed-parts/enclosure/enclosure/README.md#exterior-disposal-warning).
The full disposal wording is centered low on back-bottom, raised in the enclosure's
own material. Fluting is omitted beneath the letters and their surrounding margin;
the flat field has no border or separate carrier. The CAD measures actual warning
letter heights against the minimum, and the relief supplies the visible edges of
the same-color text. The paper proof establishes the wording and a full-size type
reference; its panel dimensions and left alignment are not the enclosure layout.
The service panel's physical carrier is not modeled in this proof.

## Ordinary appliance information

Reserve a separate, legible rating block on or near the nameplate. UL Part 1's
identification/electrical fields and Part 2-24 clause 7.1 call for:

- Manufacturer or identifying trademark and model/type designation.
- Rated voltage, AC identification/frequency, and **rated input current in amperes**.
  For this compression appliance, clause 7.1 specifies current rather than ordinary
  input watts. The proposed format is `120 V~ 60 Hz` plus the established current.
- Actual refrigerant charge in grams and `R-600a`.
- Manufacturing date or a date code identifying a consecutive three-month period;
  the code must not repeat within ten years and belongs on or near the nameplate.
- The principal insulation blowing-gas identity, from the foam formulation actually
  used in this machine.

Serial 0001 and its QR are product identity features. They can remain prominent while
the ratings live on an adjacent label. The 6.4 mm warning rule does not set the
ordinary rating letters' size; use legible, durable letters and the demonstrated
printing capability to choose it. Neither `120V 60Hz ONLY` nor `NOT FOR 240V` has an
additional wording requirement in this household marking review. A clear appliance
input rating identifies the supply despite the C14 component's own 250 V rating.

`5A 600W` is unverified study copy. A 5 A fuse does not establish a 5 A appliance input.
The build record must supply the established rated current and actual weighed charge;
these cannot be inferred from a layout drawing. No invented values appear in the
warning artwork.

The cold core uses Fiberglass Supply Depot 2 lb pour foam, not the donor cabinet's
insulation. Its [published SDS][foam-sds], pages 10-12, lists no flammable volatile
blowing component and does not disclose a blowing-agent identity. **The best estimate
is that the separate 40 mm flammable-blowing-gas identity marking is not needed**;
that is an inference from the formulation information, not a claim that the gas has
been positively identified. Do not copy the donor's C5H10 marking onto this machine.
Record the actual foam formulation/lot and its gas identity when the product data
supplies it. The ordinary identity field is retained in the rating specification.

## Commercial comparison

[EPA Rule 26][rule26], Appendix Y listing 2, is the source of the commercial R-290 dispensing
warning set. Those provisions describe simultaneous markings in different places,
with some conditions; they are not alternative layouts or six warnings all required
on a nameplate. This is the crosswalk for the commercial set's IDs:

| Commercial ID | Commercial position/purpose | Household specification |
| --- | --- | --- |
| A | Exterior service / puncture warning | Retain the household service message near the compressor; put it in the combined service panel. |
| B | Exterior disposal warning | Retain the household disposal message on the exterior. |
| C | Inside, near compressor; consult manual | Retain the household message in the combined service panel. |
| D | Packaging / handling paragraph | No corresponding household paragraph in the reviewed marking clauses. |
| F | Exterior storage paragraph for non-fixed equipment | No corresponding household paragraph in the reviewed marking clauses. |
| Service ID | Red GHS flame, A3 and refrigerant identification | Use household W021 and R-600a at compressor access; no separate A3 tag. |

The household exposed-tubing message is also included in the combined service panel.
The commercial minimum-room-area/installation-height label is not part of this
household specification. No such calculation-based marking appears in the reviewed
2017 household marking clauses; this does not remove the need for clear ventilation
and installation instructions.

For the expected sub-40 g charge, the refrigerant itself also fits the **100 g or
less** U.S. transport exception in 49 CFR 173.307(a)(4)(v).
[PHMSA's interpretation][transport] confirms this exception for refrigerating
machines containing flammable, non-toxic liquefied gas. Thus a DOT refrigerant-hazmat
carton label is not expected for this charge. This conclusion concerns the enclosed
refrigerant, not a separate CO2 cylinder or other shipment contents.

## Other household requirements relevant to the markings

The household conditions allow **up to 150 g per refrigerant circuit**, and require
equipment designed and identified for the refrigerant. The donor charges of 15 g and
23 g plus the development allowance of 5-15 g are comfortably below that limit;
actual charge is recorded after assembly. The limit is specific to this household
route, not a universal natural-refrigerant exemption.

The finished enclosure, coil, electrical components and installation must meet the
incorporated safety provisions, including relevant leakage/ignition, mechanical,
electrical and abnormal-operation tests. Donor qualification does not cover those
changes. The label proof establishes dimensions and content; it does not report
hardware tests that have not been performed or authorize a UL/ETL certification mark.

The delivered instructions need the household installation, handling, service and
disposal information and applicable clause 7.12 warnings, including keeping
ventilation openings clear. State indoor household use, installation clearances,
potable-water connection, service precautions and refrigerant identity/charge.
Do not substitute a QR destination for the permanent warnings.

For the same household end-use, [40 CFR 82.154(a)(1)(ix)][venting] includes R-600a in
the Section 608 venting exception. This is end-use-specific; R-600a flammability still
controls the handling method in the assembly procedure.

## Build and verification

```sh
tools/cad-venv/bin/python hardware/markings/build.py
```

The generator checks warning-letter outline heights, line widths, label bounds and
element overlaps, and writes outlined SVGs, [measured bounds](artwork-dimensions.json)
and the PDF. Both final PDF pages have been rendered and visually inspected. Physical
production checks cover actual printed size, carrier fit, permanent retention and
legibility under the expected heat, moisture and cleaning conditions.

[definitions]: https://www.epa.gov/snap/substitutes-refrigeration-and-air-conditioning
[household]: https://www.epa.gov/snap/substitutes-household-refrigerators-and-freezers
[household-rule]: https://www.epa.gov/sites/default/files/2018-08/documents/epa_frdoc_0001-22694.pdf
[appendix-r]: https://www.govinfo.gov/content/pkg/CFR-2025-title40-vol21/pdf/CFR-2025-title40-vol21-part82-subpartG-appR.pdf
[rules]: https://www.epa.gov/snap/regulations-proposed-rules-and-final-rules-determined-epa
[ul2017]: https://www.normsplash.com/Samples/CSA/179615323/CAN-CSA-C22.2-NO.-60335-2-24-17-en-2.pdf
[ul2017-sun]: https://cdn.intertek.com/www-intertek-com/dms-legacy/UL-60335-2-24-CSA-C22-2-No-60335-2-24-Rev-4-28-2017-ED-3-31-2019.pdf
[ul2020]: https://cdn.intertek.com/www-intertek-com/dms-legacy/UL-60335-2-24-CSA-C22-2-No-60335-2-24-SUN-Rev-2-27-2020-ED-2-28-2024.pdf
[rule17]: https://www.govinfo.gov/content/pkg/FR-2011-12-20/pdf/2011-32175.pdf
[rule26]: https://www.govinfo.gov/content/pkg/FR-2024-06-13/pdf/2024-11690.pdf
[w021]: https://commons.wikimedia.org/wiki/File:ISO_7010_W021.svg
[foam-sds]: https://fiberglasssupplydepot.com/2-lb-pour-foam-sds
[transport]: https://www.phmsa.dot.gov/regulations/title49/interp/24-0028
[venting]: https://www.govinfo.gov/content/pkg/CFR-2025-title40-vol21/pdf/CFR-2025-title40-vol21-sec82-154.pdf
