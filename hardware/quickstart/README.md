# Faucet + umbilical installation quick start

`00-mount.html` and `01-connect.html` are two single-sided landscape 11 x 17 in owner-installation
sheets. They publish together as `quick-start.pdf` on `/drawings` and print at actual size on the
Epson for in-house review.

The two sheets form one physical story:

1. Mount the complete factory faucet assembly through the prepared countertop opening.
2. Connect its three tubes and RJ11 signal lead, plus the tap-water and CO2 supply tubes, to the
   appliance rear panel.

Four registered model states tell the mounting story. Two registered model states show the rear
connections before and after installation. Words identify only the action and endpoint; modeled
product geometry carries the instruction.

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

- red `CO2` supply to the red `CO2` inlet;
- white tap-water supply to the white `TAP` inlet;
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
frame the plate stands clear of the retained washer before it moves. The exact same 220 x 72 mm
countertop solid and opening appear in all four frames, so the lower views read as the underside of
the upper views. That window is long on the plate's slide axis and narrow across it, preserving the
full support behind the retracted plate while showing the constrained under-sink working direction.

The connection sheet carries exactly two physical scenes from the same tight rear-panel camera:

1. the appliance with the red CO2 tube, white tap-water tube, blue soda tube, two black flavor
   tubes, and RJ11 signal lead modeled entirely clear of the enclosure silhouette;
2. the same appliance with all six leads fully seated.

The enclosure, camera, scale, lighting, and crop remain registered between the two states. An
oblique rear camera foreshortens the appliance's +Y face, so the large physical +Y withdrawal
projects into a compact white gap while every free lead still clears the enclosure silhouette.
The page preserves that common render scale but lays out each scene by its visible content bounds:
equal outer margins and a transition arrow centered in the actual white gap, without allowing the
connected render's unused frame area to push its appliance toward the gutter. The lower enclosure
is outside the viewport so the ports and lead ends dominate each column; a clean white field
carries no floor, contact shadow, gradient, or distance fog. The five tube collars are production
solids with their modeled lettering. The RJ11 body, boot,
latch, contacts, and ribbon are CAD solids. Tube end faces, routing bends, port labels, and signal
jack remain physical model geometry. No connector, tube, cord, leader, or callout is drawn over a
render; the small transition arrow in the page gutter is the only overlay.

## Build

From the repository root:

```sh
# Rebuild product-derived PNGs after faucet, rear-port, or artwork-generator changes.
tools/cad-venv/bin/python hardware/quickstart/quickstart_art.py

# Rebuild the PDF after an HTML or CSS edit.
tools/cad-venv/bin/python hardware/quickstart/_build.py
```

The two steps are separate build targets. A layout-only iteration consumes generated artwork
without rebuilding CAD. `connect-rear-open.png` and `connect-rear-connected.png` use fixed frame
anchors and one camera definition so every rear-panel feature remains in the same printed
position. The publisher's pinned CAD environment is the byte authority for generated artwork and
the bound PDF; local runs remain visual previews because native OCCT tessellation differs by host.

`out/00-mount.png`, `out/01-connect.png`, and their page PDFs are the full-resolution 150 px/in
sheet renders. Inspect both pages at actual size, in grayscale, at quarter scale, and with the
captions covered before publication.
