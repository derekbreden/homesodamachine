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

Three interfaces remain explicit layout proxies in `UNQUALIFIED_DATUMS`:

- The fully extended branch face is provisionally **20.07 mm** from the axis.
- The fixed-body/moving-sleeve split is provisionally **16.95 mm**.
- The release nose radius is provisionally **5.715 mm**.

The requested branch caliper width and identification of the actual moving rim
must qualify those interfaces before print release. Sleeve depression moves
only the terminal proxy sleeve and preserves the entire measured fixed collar.
CAD consistency tests do not convert a proxy into a bench measurement.

The bores show Ø6.35 mm tube clearance. They do not claim teeth, O-rings, the
hydraulic bore or an inferred internal stop. The stop is the measured insertion
station below.

```sh
tools/cad-venv/bin/python hardware/reference/tee-connector/tee_connector.py
tools/cad-venv/bin/python hardware/reference/tee-connector/tee_connector.py selftest
```

## Measured on the PP0208E in hand

Calipered on the production tee itself. The generated clearance reference carries the run
span and the operating branch travel, and `stations_hold` reads those back. Both spans are collet face to collet face along the run. The three depths are
how far a 1/4" tube stands inside one collet from the sleeve's face with the sleeve pressed
home, which is where the tube was marked.

| | |
|---|---|
| run span, sleeves extended | 42.5 mm (`RUN_SPAN`) |
| run span, both sleeves pressed | 39.2 mm (`RUN_SPAN_PRESSED`) |
| one sleeve's stroke | 1.65 mm (`COLLET_TRAVEL`) |
| first resistance to the tube | 7.0 mm (`FIRST_RESISTANCE`) |
| the teeth hold | 8.5 mm (`GRIP_DEPTH`); at 8.4 mm the tube still draws out |
| the tube bottoms | 10.0 mm (`INSERTION`) |

The collet and its gripping teeth move during locking; the internal tube stop stays in the
body. The measured sleeve stroke sets the carrier's fore-to-aft movement. The 7 and 8.5 mm
insertion observations describe how the tube enters the fitting.

At the fore stop the plate holds each sleeve fully depressed and a bottomed tube projects
10 mm beyond that face. The return stroke is 2.15 mm: 1.65 mm of sleeve extension while its
nose stays at the plate, followed by a 0.5 mm plate-to-nose gap. Tube length places each tip at the internal stop with the carrier aft and the cartridge
fully seated: 11.65 mm beyond the extended sleeve. At the fore stop, the cartridge is
2.15 mm short of seating when its tubes bottom. Relax the squeeze and advance it through
that final 2.15 mm. Both the connected carrier and the empty carrier rest at the aft stop.
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
