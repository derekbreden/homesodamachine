# Quick start

The customer quick start is two single-sided landscape 11 x 17 in sheets:

1. `00-install.html` — an installer map for mounting the faucet, preserving service reach and
   matching every customer connection to the exact rear face.
2. `01-first-glass.html` — a six-frame owner sequence that follows one 440 mL bottle through
   Reservoir 1 and Flavor 1 to the first glass.

`quick-start.pdf` binds them in packing order. The sidecar publishes the document on `/drawings`,
and each sheet prints independently on the Epson at actual size.

This is a recognition document, not a substitute for the validated water, gas, electrical and
regulatory procedures supplied to the installer. The installer sheet shows where the finished
connections belong. It deliberately shows only cold supply → filter → `TAP`, rather than implying
a specific sink branch or tee arrangement.

## Picture contract

Every frame must communicate the object, action, direction and finished condition before its
caption is read. The recurring visual grammar is:

- exact CAD for the appliance, faucet, countertop hardware, hopper and rear ports;
- coral for a person's action;
- blue for carbonated water and deep berry for flavor concentrate;
- the same Reservoir 1 / Flavor 1 marker through the whole first-pour sequence;
- a check or prohibition mark attached directly to the condition it judges;
- words beside a physical connection only when they repeat the word molded into the rear face.

Cabinet, hand, bottle, glass, receptacle, filter and cylinder drawings are simplified context. They
must not add an unverified fitting, valve, restraint or operating claim.

## Physical facts shown

The installer map carries only the facts a person can recognize in the product:

- the faucet passes through a 1 3/8 in / 35 mm countertop opening;
- both flavor tubes seat against the rear edge of the opening before the keyhole plate, washer and
  nut are tightened from below;
- the appliance can pull forward 300 mm / 12 in while remaining connected;
- the rear needs 60 mm of connection space and both side grilles remain open;
- the five customer-side round tubes — three from the faucet, filtered water and regulated CO2 —
  are fitted and square-cut one at a time at their ports, below their collars;
- blue matches `SODA`, either black tube matches either `FLAVOR`, filtered cold water matches
  `TAP`, regulated CO2 matches `CO2`, and power comes last from a 120 V GFCI-protected receptacle;
- every push connection is taken to its hard stop and tug-checked;
- the CO2 cylinder is upright and restrained before connection, and a qualified installer
  leak-tests the completed water and gas system.

No pressure, torque, insertion depth, tee topology, regulator procedure or restraint hardware is
invented in the pictures.

## Product acceptance contract

The owner sheet depicts the intended end-to-end product behavior. Its interface enlargements are
an acceptance contract, not evidence that the current firmware or sensing already implements the
states. Publication with a product requires validation of all of the following:

- the field water connection, filter direction and isolation procedure;
- the regulator and adapter for CO2 service, regulator attachment, cylinder restraint, outlet
  valve sequence and leak-test points;
- packing of every fitting, washer, tether and restraint required by those procedures;
- a single signal-cable architecture, connector and countertop strain relief; the customer-facing
  product requires this work to be completed by the validated installer procedure rather than
  guessed from the fluid-tube pictures;
- selecting the reservoir before filling, routing the whole bottle to that reservoir and detecting
  both an empty hopper and a completed fill;
- opening the correct manifold path while the owner holds Prime 1, and stopping it on release;
- reporting real filled, cold and carbonated readiness;
- making the faucet display's Flavor 1 selection authoritative at the appliance controller;
- one complete installation and one complete first-pour test performed from the printed sheets.

Until those gates close, the PDF is a design and build artifact rather than a ship-ready customer
procedure.

## Build

From the repository root:

```sh
tools/cad-venv/bin/python hardware/quickstart/_build.py
```

`out/` contains the full-resolution PNG and PDF render for each sheet. The bound PDF is two
17 x 11 in pages at 150 px/in; the cover and `.pdf.json` sidecar beside this README are committed
website outputs. Inspect the rendered PDF pages at actual size and in grayscale before publication.
