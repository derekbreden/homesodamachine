# Faucet + umbilical installation quick start

`00-mount.html` and `01-connect.html` are two single-sided landscape 11 x 17 in owner-installation
sheets. They publish together as `quick-start.pdf` on `/drawings` and print at actual size on the
Epson for in-house review.

The two sheets form one physical story:

1. Mount the complete factory faucet assembly through the prepared countertop opening.
2. Follow its braided umbilical to the appliance, trim the three tube tails to the real cabinet,
   push and tug-test each tube, then click its RJ11 plug into the signal jack.

Words identify the action and result. Exact product artwork, the supplied cutter, motion, and the
changed physical state carry the instructions.

## Confirmed installation facts

The faucet, three tubes, braided sleeve, and fitted SIG-6 ribbon remain one factory assembly. The
retained donor washer and nut fit the donor shank and are factory-preloaded before the blue soda
umbilical tube is connected. Field installation lowers that complete assembly through the prepared opening,
slides the open under-counter plate laterally into the captive donor stack, and
hand-tightens the same retained nut.

The registered mount pictures preserve this order:

1. faucet base and gasket;
2. countertop;
3. open stainless under-counter plate;
4. retained donor washer;
5. retained donor nut;
6. threaded shank and the three tube tails.

At the appliance, the user pulls the machine forward until its rear face is accessible at the
cabinet face. The three factory tubes carry 350 mm of installer-trim allowance. Each tail is laid
to its physical port and cut square below its retained collar with the supplied Mudder cutter.
The square end pushes directly into the PP1208E fitting to the internal hard stop, then receives a
pull-back tug that sets the collet.

The physical endpoint rule is:

- blue `SODA` tail to the blue `SODA` port;
- either black `FLAVOR` tail to either black `FLAVOR` port;
- flat SIG-6 ribbon's RJ11 plug to the square signal jack.

SIG-6 remains part of the same routed assembly and arrives with its RJ11 plug factory-fitted. It is
not one of the three tubes being trimmed or pushed into the round rear ports.

## Picture contract

The mount sheet uses one below-counter three-quarter camera for all four states. The upper image
locates the complete recognizable faucet in the kitchen-scale event. The lower image magnifies the
same registered frame at the countertop stack. Only the complete assembly moves down, only the
under-counter plate moves sideways, and the final cue turns the same retained nut. In the approach
frame the plate stands clear of the retained washer before it moves. The countertop window is long
on the plate's slide axis and narrow across it, preserving the full support behind the retracted
plate while showing the constrained under-sink working direction.

The connection sheet carries four physical scenes in order:

1. one cabinet-scale view keeps the mounted faucet, relaxed braided service loop, and appliance in
   the same route while the appliance moves forward to the cabinet opening;
2. the supplied cutter crosses one tail at a square cut beside the exact machine rear, with all
   three tubes laid toward their physical ports and the action marked `3x`;
3. one registered rear-port view leaves all three tubes visibly seated while the opposed arrows
   show push-in and pull-back tug test;
4. a tighter crop of the same rear camera keeps the three tubes seated while the ribbon's RJ11 plug
   enters the square signal jack, latch up, in one motion and with no tool.

The braided sleeve is crosshatched so it cannot read as another tube. Tube collars stay on the
physical lines, port labels stay on the exact rear face, and the final state shows the connected
hardware rather than detached identity cards. No interface screen or commissioning state is
invented.

## Build

From the repository root:

```sh
# Rebuild product-derived PNGs after faucet, rear-port, or artwork-generator changes.
tools/cad-venv/bin/python hardware/quickstart/quickstart_art.py

# Rebuild the PDF after an HTML or CSS edit.
tools/cad-venv/bin/python hardware/quickstart/_build.py
```

The two steps are separate build targets. A layout-only iteration consumes the generated artwork
without rebuilding CAD. `machine-ports-iso.png`, `machine-ports-action.png`, and
`machine-signal-iso.png` are fixed crops of `machine-back-iso.png`; every connection beat therefore
preserves the same camera and physical port locations.

The pinned Linux CAD image is the byte authority for generated artwork and the bound PDF. Local
macOS runs are visual previews because native OCCT tessellation differs by host. The scoped derive
workflow regenerates and publishes the canonical Linux PDF, cover, and metadata.

`out/00-mount.png`, `out/01-connect.png`, and their page PDFs are the full-resolution 150 px/in
sheet renders. Inspect both pages at actual size, in grayscale, at quarter scale, and with the
captions covered before publication.
