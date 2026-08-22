# Faucet installation reference

`00-install.html` and `01-mount.html` are two single-sided landscape 11 x 17 in development sheets
for the faucet and its factory umbilical. They publish together as `quick-start.pdf` on `/drawings`
and print at actual size on the Epson for in-house review.

The before-you-start sheet has three visual acts:

1. Identify the complete factory assembly: one faucet, one braided sleeve, one blue `SODA` tube,
   two black `FLAVOR` tubes, and one flat factory-assembled SIG-6 ribbon.
2. Plan the cabinet envelope around the current appliance: 60 mm behind the stored unit, both side
   grilles unobstructed, 300 mm service depth to the cabinet face, and an umbilical-clearance volume.
3. Match physical labels without drawing a connection route: the blue `SODA` collar matches the
   rear `SODA` label, either black `FLAVOR` collar matches either rear `FLAVOR` label, and SIG-6 is
   already physically assembled and fitted.

The first sheet establishes product identity and space. The second carries the literal countertop
mount sequence in the same visual system.

## Confirmed installation facts

The complete faucet and umbilical remain one factory assembly. The retained donor washer and nut
fit the donor shank and its nominal deck range. They are factory-preloaded on the bare shank before
the blue supply-tube connection. Field installation lowers that complete assembly through the
prepared opening, slides the open keyhole under-counter plate laterally into the captive donor
stack, and tightens the same retained donor nut. The washer and nut are never loose field parts.

Current product geometry provides these visual inputs:

- prepared opening Ø34.93 mm;
- intended seated opening center 4.992 mm behind the shank axis;
- rigid upper plate 4.000 mm and TPU gasket 2.000 mm;
- open dual-channel stainless keyhole plate 1.524 mm thick and Ø54.45 mm;
- thread below the keyhole plate represented by `42.476 mm - countertop thickness`;
- one blue round tube, two black round tubes, and one flat factory-fitted SIG-6 ribbon in the
  braided umbilical.

The rear `SODA` and both `FLAVOR` stations use JG PP1208E fittings. The manufacturer's `H`
tube-insertion dimension is
[15.7 mm / 0.62 in](https://www.johnguest.com/sites/jg/files/2023-04/JG%20Drinks%20Polypropylene%20Bulkhead%20Connector%20Data%20Sheet.pdf),
measured with the collet in its release position. Either black tube can use either `FLAVOR` station.

## Mount visual sheet

The mount sequence uses one fixed below-counter 3/4 camera and four large beats:

1. `STAYS ON` — washer and nut already captive above the blue tube joint.
2. `LOWER` — the complete faucet, four tails, washer, and nut pass through the prepared opening as
   one assembly.
3. `SLIDE PLATE` — the exact dual-channel keyhole plate moves laterally above the captive washer.
4. `TIGHTEN SAME NUT` — the retained nut draws the washer and plate into the final clamped stack.

The image alone preserves this final order: faucet base, gasket, countertop, keyhole plate,
donor washer, donor nut, remaining threaded shank, blue tube joint, blue tube. Both black tubes and
the fitted SIG-6 ribbon remain individually traceable and unpinched.

## Picture contract

Each visual establishes the object and spatial relationship before its caption is read. The
before-you-start sheet uses:

- exact product-derived artwork for the appliance, faucet, umbilical tails, and rear labels;
- crosshatching for the braided sleeve, with one blue tube, two black tubes, and the flat ribbon
  separated at the tail end;
- detached matching badges with visible gaps between every factory tail and rear connector;
- a fitted-state check on the factory-assembled SIG-6 ribbon;
- no hand, tool, cut line, fictitious connector, or recreated interface state.

Cabinet and sink outlines are simplified spatial context. The broad hatched umbilical zone is a
clearance envelope rather than a prescribed route. The 60 mm and 300 mm values are current design
reservations.

The mount sheet keeps all four states on one registered camera, target, scale, and countertop
horizon. The upper image locates the full faucet; the lower image magnifies the same frame. The
washer and nut remain present in all four states, the plate alone moves laterally, and the final
hand touches the same nut without hiding the plate mouth or washer perimeter. Coral arrows and the
two simplified hand silhouettes are the only drawn action overlays. No loose donor hardware,
wrench, torque value, interface state, or wet-commissioning claim appears.

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

`out/00-install.png`, `out/01-mount.png`, and their page PDFs are the full-resolution sheet renders.
The bound PDF is two 17 x 11 in pages at 150 px/in. Inspect both pages at actual size and in
grayscale before publication.
