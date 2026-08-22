# Unboxing and Quick-Start

The customer-documentation packet lies face-up at the top of the carton. Its working
instructions are the two landscape 11 x 17 in sheets built in
[`/hardware/quickstart/`](/hardware/quickstart/README.md). The faucet and its install-kit bag
sit together inside the carton. Safety, electrical and refrigerant notices are a separate
regulatory insert; the quick start stays on the actions a person must see and copy.

## The two sheets

**Sheet 1 - START HERE / INSTALL**

1. Mount the faucet through the 1 3/8 in countertop opening. The exact slide-on keyhole plate,
   washer and nut are pictured in their installed order.
2. Tee the cold-water line with whichever of the two supplied tee arrangements matches the
   cabinet. Run the result through the filter to the white `TAP` station.
3. Put the appliance and a secured upright CO2 cylinder beside the disposal. Leave 60 mm behind
   the appliance and keep both side grilles clear.
4. Leave a 300 mm service loop, square-cut the three faucet tubes below their collars, match blue
   to `SODA` and either black tube to either `FLAVOR` station, then push and tug-check each one.
5. Fit the cylinder regulator, connect its red tube to `CO2`, open it slowly and leak-test it.
6. Open water, open CO2 and connect 120 V GFCI power. The screen's real `READY` state is the handoff
   to the second sheet.

**Sheet 2 - FIRST GLASS / FILL TO POUR**

1. Choose Flavor 1 or Flavor 2 on the front display, then pour one 440 mL concentrate bottle into
   the single shared hopper. Repeat for the other reservoir when filling both.
2. On the front display choose `SERVICE` -> `PRIME` -> a flavor and hold `HOLD TO PRIME`, with a cup
   below the nozzle, until concentrate reaches it. Repeat for the other flavor.
3. Tap the faucet head to switch between the two flavor pictures on its display.
4. Wait for `READY`, put a glass under the nozzle and lift the lever.

## Picture sources

The pictures stay tied to the objects the customer holds or sees:

- faucet, counter stack and umbilical from
  [`faucet-assembly.step`](/hardware/faucet-layout/faucet-assembly.step);
- under-counter keyhole plate from its production
  [`DXF`](/hardware/cut-parts/faucet/touch-flo-under-counter-plate/touch-flo-under-counter-plate.dxf);
- appliance faces from the enclosure's generated
  [`line art`](/hardware/printed-parts/enclosure/drawings/line-art/);
- tube collars and rear stations from the packed appliance renders;
- Flavor 1 and Flavor 2 pictures from the RGB565 arrays compiled into the faucet firmware;
- front-screen layouts and wording from the 800 x 480 front-display interface;
- physical wayfinding colors from
  [`_back_panel_dimensions.port_colors`](/hardware/printed-parts/enclosure/back-panel/_back_panel_dimensions.py).

Hands, arrows, a sink cabinet, a cylinder and a glass are simple silhouettes. Product interfaces,
connection geometry, words and colors are not approximated.

## Color system

Connection color always means the fluid, never the motion:

| Color | Meaning |
|---|---|
| blue | carbonated water, `SODA` |
| black | either flavor line, `FLAVOR` |
| white with a black outline | tap water, `TAP` |
| red | regulated CO2, `CO2` |
| coral | a finger action or direction arrow on the page and display |

The rear face, the tube collars, the exact enclosure drawing and the quick-start stylesheet all
read the same port-color table. A word and its color travel together in every connection picture.

## Print and packing

`quick-start.pdf` contains the two sheets in packing order. Print landscape, 11 x 17 in, color,
actual size. The sheets are single-sided so either can be revised and printed independently on the
Epson; they can also be printed duplex as one physical leaf. Put Sheet 1 face-up on top of Sheet 2
in the customer-documentation packet.

The quick start does not carry specifications, product positioning, maintenance schedules,
warranty text or regulatory copy. Ongoing care, support and unit-specific information live at the
serialized URL on the rear nameplate.
