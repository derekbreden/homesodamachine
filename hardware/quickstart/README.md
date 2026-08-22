# Installation reference

`00-install.html` is one single-sided landscape 11 x 17 in sheet for the faucet and its factory
umbilical. It publishes as `quick-start.pdf` on `/drawings` and prints at actual size on the Epson.

The sheet has three visual acts:

1. Drop the complete faucet through a 1 3/8 in / 35 mm opening, push it rearward until both black
   flavor tubes touch the opening wall, then install the keyhole plate, washer, and nut from below.
2. Before any field cut, plan the appliance route with 60 mm behind its stored position, both side
   grilles open, room to tip a 440 mL bottle above the hopper, and a 300 mm pull-forward service
   loop to the cabinet face.
3. With the machine pulled forward, route each factory tail to its port, mark the port face, add the
   PP1208E's 15.7 mm / 0.62 in tube insertion depth, and cut only the excess below the collar. Then
   push and tug-check `SODA`, `FLAVOR`, and `FLAVOR` on the exact rear face. Either black tube can
   land on either `FLAVOR` port.

The field-trim allowance is the manufacturer's `H` tube-insertion dimension for the 1/4 in
PP1208E: [15.7 mm / 0.62 in](https://www.johnguest.com/sites/jg/files/2023-04/JG%20Drinks%20Polypropylene%20Bulkhead%20Connector%20Data%20Sheet.pdf).

## Procedure boundary

This is a development installation reference, not a commissioning procedure. It stops after the
three factory round tubes are seated and tug-checked. It does not authorize or depict:

- `TAP` water connection;
- CO2 connection, regulation, restraint, or leak testing;
- faucet signal termination;
- AC power;
- filling, priming, refrigeration, carbonation, or dispensing.

Those operations require their own released and validated procedures. The current integrated
appliance firmware does not provide a complete customer first-pour sequence, so this document makes
no owner-interface or ready-to-pour claims.

## Picture contract

Each visual must communicate the object, location, motion, and result before its caption is read.
The recurring grammar is:

- exact CAD for the appliance, faucet, countertop hardware, umbilical tails, and rear ports;
- coral only for a person's motion;
- green only for a verified result;
- product colors and molded words for physical identity;
- crosshatching for the braided sleeve, with one blue and two black tubes visible at both ends;
- ghosting only for the pulled-forward service position in the top-view planning inset;
- stop marks attached directly to connections outside this sheet's scope.

Cabinet, sink, hand, cutter, connector cutaway, dimensions, and motion arrows are simplified
instructional context. The washer and nut are conservative stand-ins because the donor hardware has
no source CAD.

## Build

From the repository root:

```sh
# Rebuild product-derived PNGs after CAD or rear-port changes.
tools/cad-venv/bin/python hardware/quickstart/quickstart_art.py

# Rebuild the PDF after an HTML or CSS edit.
tools/cad-venv/bin/python hardware/quickstart/_build.py
```

The two steps are separate build targets. A layout iteration consumes the checked-in artwork and
does not regenerate CAD.

The pinned Linux CAD image is the byte authority for generated artwork and the bound PDF. Local
macOS runs are visual previews because native OCCT tessellation differs by host. The derive workflow
regenerates and commits the canonical Linux result.

`out/00-install.png` and `out/00-install.pdf` are the full-resolution sheet render. The bound PDF is
one 17 x 11 in page at 150 px/in. Inspect the page at actual size and in grayscale before publication.
