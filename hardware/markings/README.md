# Refrigerant markings

Provisional warning artwork for the integrated R-600a soda machine. The artwork uses
the current EPA A3 beverage-dispenser warning set as a conservative design target.
**The machine's SNAP category and R-600a acceptability are not established. Applying
these warnings does not establish either, or complete appliance compliance.**

The brand/serial nameplate remains a separate part. The preferred study composition is
[L](../../future/nameplate-qr-studies/l-big-faucet.svg): the logo, name, code and serial
fit together with balanced spacing. The long refrigerant warnings occupy separate
surfaces. None of the warning rules reviewed requires putting all this text on that
104.53 × 66.07 mm plate.

## Classification reading

Reviewed against EPA's current tables on September 18, 2026.

| Candidate end-use | Match to this machine | R-600a listing |
| --- | --- | --- |
| Refrigerated food processing and dispensing equipment | Closest functional match: chilled carbonated beverage held in a refrigerated vessel and dispensed through a faucet. EPA explicitly includes carbonated beverages; mixing ingredients is not required. | Pure R-600a has no entry in the current category table. R-290 has a conditional entry. The R-125/R-290/R-134a/R-600a blend entry does not list pure R-600a. |
| Household refrigerators/freezers | Residential purpose matches. EPA's examples include household beverage centers and household ice makers, but its definition centers on refrigerated storage. Whether this plumbed dispenser qualifies needs EPA confirmation. | R-600a is acceptable with use conditions, including the incorporated edition of UL 60335-2-24. |
| Retail food stand-alone refrigerators/freezers | A self-contained circuit alone does not establish this category. EPA separates beverage processing/dispensing from ordinary refrigerators, freezers and reach-in coolers. | R-600a is acceptable with use conditions in this category, which cannot simply be transferred to a dispenser. |

The circuit is entirely inside the under-counter enclosure. The remote faucet carries
water and flavor, not refrigerant. The machine dispenses no ice and has no payment
mechanism. Reusing an ice maker's compressor and condenser does not establish the
finished soda machine's category or qualification.

Sources: [EPA end-use definitions][definitions], [retail food categories][categories],
[dispensing refrigerant table][dispensing], [household refrigerant table][household],
[stand-alone refrigerant table][standalone]. A precise [classification inquiry](epa-inquiry.md)
is prepared but has not been sent. The inquiry asks about the residential boundary and
the applicable R-600a listing; it does not assume a refrigerant change. R-290 is not a
drop-in replacement for the R-600a donor circuit.

## Current rule used for the proof

[SNAP Rule 26][rule26], 89 FR 50482–50484, Appendix Y, listing 2, supplies the A3
**R-290** food-processing/dispensing warning set below. Its wording is a voluntary
hazard-communication target for this **R-600a** proof while classification is open.
The separate current R-600a stand-alone entry is Appendix R, listing 4, at 89 FR
50465–50467. It also requires substantial permanent warnings with 6.4 mm letters,
but has differences, including the packaging wording. A confirmed end-use controls
the final set.

The 2015 household entry is not the current household specification. The
[2018 household rule][household-rule] replaced its enumerated conditions with
compliance with UL 60335-2-24, second edition dated April 28, 2017, plus the
new-equipment/refrigerant-identification condition. A household determination requires
reviewing that incorporated standard; the commercial proof is not a substitute.

## Artwork and dimensions

The [three-page US Letter proof](../../output/pdf/refrigerant-warning-proof.pdf)
prints at **100% / actual size**. Its 50 mm scale bar checks printer scaling.
Each SVG is also dimensioned in millimetres and contains outlined type.

| ID | Artwork | Size | Target location |
| --- | --- | --- | --- |
| A | [Service / puncture](artwork/a-exterior-service.svg) | 190 × 91 mm | Outside the machine; includes GHS flame and A3 |
| B | [Disposal](artwork/b-exterior-disposal.svg) | 190 × 71 mm | Outside the machine |
| C | [Service instructions](artwork/c-compressor-service.svg) | 190 × 89 mm | Inside the machine near the compressor |
| D | [Handling](artwork/d-package-handling.svg) | 190 × 82 mm | Outer packaging of the factory-charged machine; includes GHS flame and A3 |
| F | [Storage](artwork/f-exterior-storage.svg) | 190 × 71 mm | Outside the machine, treating it as non-fixed equipment |
| Service ID | [GHS flame / A3 / R-600a](artwork/service-port-id.svg) | 82 × 33 mm | Visible at the service port / process tube |

All warning words are uppercase Helvetica Bold at a **6.5 mm H cap height**. The
smallest actual letter outline in the warning copy is 6.491 mm high, above the
6.4 mm target. Font em size is 9.031208 mm; em size is not letter height.
The collar's recorded 4.951 mm overall cap height is smaller. This is dimensioned
artwork, not evidence of a successful physical print.

The flame diamond measures 21 mm vertically, above the 15 mm minimum in the selected
rule. The adjacent A3 has a 7.2 mm cap height, above one-third of that diamond height.
Red border, white ground, black flame; a bare white flame on the black nameplate does
not reproduce this symbol. The SVG source is the public-domain
[GHS02 artwork](https://commons.wikimedia.org/wiki/File:GHS-pictogram-flamme.svg),
derived there from UNECE's pictogram. `ghs02.svg` retains the downloaded source.

The warning text is fully present in the artwork and in
[artwork-dimensions.json](artwork-dimensions.json). Paragraph breaks and capitalization
are typographic; none of the warning sentences is shortened.

## Proposed attachment locations

The enclosure is [215 × 462 × 361 mm](../printed-parts/enclosure/enclosure/README.md).
These are fit proposals, not attached labels or released enclosure geometry:

- **A + B:** two labels with a 5 mm gap, occupying 190 × 167 mm on the upper rear
  portion of a side wall. Both stay outside the enclosure. A flat carrier needs its
  own border and retention allowance beyond that footprint.
- **F:** 190 × 71 mm on the lower rear exterior. Keep the brand/serial plate, plumbing
  connections, inlet and fasteners unobstructed.
- **C:** a fixed face inside the compressor compartment, visible on first opening.
  Reserve 190 × 89 mm near the compressor. A clear attachment face has not yet been
  verified in the assembly; do not put it over the condenser vents, wiring, terminal
  cover, thermal-fuse contact or a hot component.
- **Service ID:** at the BPV31/process-tube access, visible before opening the circuit.
  A retained tag or adjacent rigid face needs clearance from heat and moving parts.
- **D:** the outside of the shipping carton. For an unpackaged delivery the selected
  entry places it outside the machine near the nameplate/control panel. This is an
  EPA handling warning, not a determination of DOT shipping marks or exemptions.

The standing enclosure walls are fluted. Adhesion across the ridges is not established.
Use the paper proof to check fit, then qualify a flat carrier and permanent marking
process against the actual PET-GF surface, heat, moisture and expected cleaners.
Ordinary paper is only a fit template. A label or carrier must not bridge a removable
seam, cover a vent, or introduce a fastener into tubing or wiring. Physical fit,
retention, contrast and durability remain unverified.

## Service-port color

The selected current rule specifies **PMS 185 or RAL 3020** red at every service port
and other expected circuit-opening location, including process tubes, extending at
least **25 mm in both directions** from the location. Marking must be replaced if
removed. A screen red or a generically red filament is not a verified color match.

Apply the same target to the BPV31/process tube using compatible permanent paint,
sleeve or marking material. Record the actual accessible lengths. If the tube cannot
accommodate the specified extent, resolve the marking arrangement before claiming it
meets the rule. Do not cover a seal, service thread, brazing surface or necessary
inspection point.

## Remaining product information

| Item | Current state |
| --- | --- |
| Refrigerant | R-600a, safety class A3; the service ID states this accurately. |
| Charge mass | Actual finished-unit mass is not supplied for this proof. Record the measured charge in grams on the unit and in its service/install record. Donor charge and an estimated “under 40 g” do not establish the finished charge. No invented charge value is printed. |
| Minimum room area / installation height | Appendix Y listing 2(e) calls for a calculated room-area marking near the nameplate; height is conditional on the standard. The exact applicability and values require the applicable standard and actual charge. No zero area or blanket small-charge exemption is assumed. These marks are absent from this proof. |
| Fixed, ducted equipment warning | The current machine has condenser vents and a beverage umbilical, with no external air ductwork; the fixed/ducted warning is not included. Revisit for a ducted installation. |
| Manual | Permanent labels refer to a repair manual/owner's guide. The delivered documentation must contain the actual refrigerant, charge, applicable installation limits, handling, service and disposal precautions. A QR-only warning is not used. |
| Standard conformance | No complete UL 60335-2-24 / UL 60335-2-89 / ASHRAE 15 evaluation is established. Small charge and warning labels alone do not establish conformance. The applicable standard, edition and relevant listing obligations need resolution with classification. |

The 120 V electrical rating, model identification and verified input current/power are
separate appliance markings. The nameplate study's `5A 600W` remains unverified layout
copy; this warning proof does not qualify it.

## Refrigerant handling scope

[40 CFR 82.154(a)(1)(ix)][venting] exempts R-600a from the venting prohibition only in
specified end-uses: household refrigerators/freezers, retail food stand-alone
refrigerators/freezers, and vending machines. It is not a blanket natural-refrigerant
exemption. EPA includes stand-alone household ice makers in its household definition;
that supports the donor's category, not automatically the rebuilt soda machine's.
The integrated machine's handling route depends on its resolved end-use. Technician
certification does not itself authorize intentional venting of a non-exempt refrigerant.

## Build and verification

```sh
tools/cad-venv/bin/python hardware/markings/build.py
```

The generator checks label bounds, overlaps, actual warning-letter outline heights,
line widths and symbol/class proportions. It writes SVGs, measured bounds and the
full-size PDF. The current three-page proof has been rendered and visually inspected;
the complete warning copy matches the transcribed Appendix Y listing 2 wording.
Physical production verification requires a
100% print, measured letters and scale bar, enclosure fit, permanent attachment and
legibility after exposure to the intended service environment.

[definitions]: https://www.epa.gov/snap/substitutes-refrigeration-and-air-conditioning
[categories]: https://www.epa.gov/snap/retail-food-refrigeration
[dispensing]: https://www.epa.gov/snap/substitutes-refrigerated-food-processing-and-dispensing-equipment
[household]: https://www.epa.gov/snap/substitutes-household-refrigerators-and-freezers
[standalone]: https://www.epa.gov/snap/substitutes-stand-alone-equipment
[rule26]: https://www.govinfo.gov/content/pkg/FR-2024-06-13/pdf/2024-11690.pdf
[household-rule]: https://www.epa.gov/sites/default/files/2018-08/documents/epa_frdoc_0001-22694.pdf
[venting]: https://www.govinfo.gov/content/pkg/CFR-2025-title40-vol21/pdf/CFR-2025-title40-vol21-sec82-154.pdf
