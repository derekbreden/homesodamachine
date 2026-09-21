# Tee connector — PP0208E measured clearance reference

The production fitting is the **John Guest PP0208E** 1/4 inch union tee, black
polypropylene. The manifold and water split share the generated
`tee-connector.step` from `tee_connector.py`.

The reference uses the unscaled five-view scan registered in
[`../jg-pp0208e-tee/scan-registration.json`](../jg-pp0208e-tee/scan-registration.json).
Its fixed root envelope is **Ø14.0 mm**. Its collar envelope is **Ø16.5 mm**,
covering the draft beyond the **Ø16.3 mm nominal** collar. This is a rounded
sample envelope, not a manufacturing tolerance limit. Printed journals provide
**Ø17.0 mm**, including 0.25 mm radial running air.

The run is on ±Z with extended sleeve faces at **±21.25 mm**, from Derek's
42.5 mm run-span reading. The branch is on +Y. Fitted root and collar patches
have distinct run and branch stations; they are interior surface patches, not
shoulder edges. The connecting shoulders and central union are conservative
clearance envelopes. They deliberately do not claim every molded fillet.

The measured branch widths are **30.5 mm extended** and **29.0 mm pressed**, from
the back of the widest fixed run collar to the outermost terminal face. Subtracting
the **8.15 mm nominal back-collar radius** places those faces at **22.35 mm** and
**20.85 mm** from the run axis. The **1.50 mm branch stroke** is distinct from the
**1.65 mm run-sleeve stroke**. The conservative Ø16.5 clearance envelope is not the
caliper back datum. The raw measurements are retained in
[`branch-operating-measurements.json`](../jg-pp0208e-tee/branch-operating-measurements.json).

The scan distinguishes a reduced fixed barrel behind the small moving terminal
ring. Conservative fixed-barrel bounds are **R7.75 mm**, ending at **18.50 mm** on
the run and **20.25 mm** on the branch. These flat envelope ends are not exact
molded seams. The terminal clearance radius remains **5.715 mm** in
`UNQUALIFIED_DATUMS`; the exact terminal OD and seam remain unqualified.

[`terminal-ring-scan.json`](../jg-pp0208e-tee/terminal-ring-scan.json) reads an
approximate **Ø10.62 mm** terminal surface, with **0.235 mm held-out radial p95**.
Its observed face near **21.36 mm** lies between the measured operating endpoints.
The merged scan therefore cannot establish an absolute terminal seam or minimum
ring size. Release moves only the terminal proxy and preserves both the fixed
collar and reduced barrel. The printed **Ø8.5 mm circular tube opening** retains
a full flat annular bearing; actual release performance still requires the part.

The bores show Ø6.35 mm tube clearance. They do not claim teeth, O-rings, the
hydraulic bore or an inferred internal stop. The stop is the measured insertion
station below.

```sh
tools/cad-venv/bin/python hardware/reference/tee-connector/tee_connector.py
tools/cad-venv/bin/python hardware/reference/tee-connector/tee_connector.py selftest
```

## Measured on the PP0208E in hand

Calipered on the production tee itself. The generated clearance reference carries the run
span and the distinct branch travel, and `stations_hold` reads those back. Both run spans are collet face to collet face. The three depths are
how far a 1/4" tube stands inside one collet from the sleeve's face with the sleeve pressed
home, which is where the tube was marked.

| | |
|---|---|
| run span, sleeves extended | 42.5 mm (`RUN_SPAN`) |
| run span, both sleeves pressed | 39.2 mm (`RUN_SPAN_PRESSED`) |
| one run sleeve's stroke | 1.65 mm (`RUN_COLLET_TRAVEL`) |
| branch width, sleeve extended / pressed | 30.5 / 29.0 mm |
| branch sleeve's stroke | 1.50 mm (`BRANCH_COLLET_TRAVEL`) |
| first resistance to the tube | 7.0 mm (`FIRST_RESISTANCE`) |
| the teeth hold | 8.5 mm (`GRIP_DEPTH`); at 8.4 mm the tube still draws out |
| the tube bottoms | 10.0 mm (`INSERTION`) |

The collet and its gripping teeth move during locking; the internal tube stop stays in the
body. The measured sleeve stroke sets the carrier's fore-to-aft movement. The 7 and 8.5 mm
insertion observations describe how the tube enters the fitting.

At the fore stop the plate holds each sleeve fully depressed and a bottomed tube projects
10 mm beyond that face. The return stroke is 2.00 mm: 1.50 mm of branch-sleeve extension while its
nose stays at the plate, followed by a 0.5 mm plate-to-nose gap. Tube length places each tip at the internal stop with the carrier aft and the cartridge
fully seated: 11.50 mm beyond the extended branch sleeve. At the fore stop, the cartridge is
2.00 mm short of seating when its tubes bottom. Relax the squeeze and advance it through
that final 2.00 mm. Both the connected carrier and the empty carrier rest at the nominal aft station.
The springs remain preloaded there; final cartridge seating may require a push.

## Observed push-connect action

Derek's physical checks use a tube-tight collar to hold the collet while the tube moves:

- With the collar continuously holding the collet in, the tube withdraws easily with a
  small pull. Derek considers four times that single-connection effort comfortable for
  cartridge removal.
- A collet that is free to move follows an extracting tube outward and locks again, even
  if it was pressed inward immediately beforehand. Release requires continued restraint
  throughout withdrawal.
- A very small separating tug on either the tube or the fitting draws the collet into its
  locked position. The required movement is the collet's short travel; Derek judges the
  effort compatible with spring return.
- During insertion, the tube pushes an extended collet inward, including against a small
  spring-level outward force.

The fixed enclosure plate supplies the continuous collet restraint during cartridge removal.
For insertion, the opposed cartridge/carrier grasp bottoms the tubes; relaxing the grasp
allows the carrier springs to supply the short separating movement that engages the collets.
These observations establish the connection action. They contain no instrumented force
reading for the complete printed carrier or its spring pair.
