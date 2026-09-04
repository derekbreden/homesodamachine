# Home Soda Machine installation quick start

One single-sided, borderless 19 x 13 inch sheet publishes as `quick-start.pdf` on `/drawings`.
Thirteen registered scenes carry the installation without headings, captions, step numbers or a
separate legend:

1. mount the complete factory faucet assembly;
2. close the under-sink cold-water valve;
3. release the existing 1/4-inch plastic tube from its push fitting;
4. insert the supplied tube-and-tee assembly, then reconnect the released line;
5. connect the five tubes and RJ11 signal lead to the appliance rear panel.

The sheet reads as a strip of photographs of the customer's own sink. Each physical action uses
registered before and after states from one camera: the before state carries the cue on the part
that moves, and the result stays clean. The changed pose remains legible with the cue covered, and
the before state plus cue predicts the result. Cue anchors and directions follow the model's
projected travel, while line weight, head construction and halo remain fixed page dimensions at
every scene scale. Cameras close in until the moving part and its travel survive arm's-length
reading; the release closeup exaggerates the collet's short physical stroke for that reason.

Every pictured object has the form in which the customer receives it, and the sequence contains
only work the customer performs. The white run arrives with its filter and `TAP` collar installed;
the red tether arrives with its flare connector and `CO2` collar installed; the faucet tails carry
their collars from the umbilical bench. Nothing on this sheet is cut, trimmed, insulated or
threaded through a collar. The cutter and loose foam belong to the separately bagged cold kit and
its own guide.

The sheet is a four-row sequence on a full-bleed pale blue-grey field (`#dce7e9`). Motion arrows
are the only marks added to the scenes. Straight arrows use one bold flat glyph aligned to the
projected travel axis. Its head overlaps and extends beyond the shaft endpoint, eliminating any
visible cap or seam. Rotation paths scale to the indicated object and continue around a
camera-projected ellipse before reaching a broad head foreshortened in that same plane. Every cue
keeps the same coral fill and field-colored halo. The field separates the white household tubing
from the page and leaves the blue handle, black fittings and coral cues distinct.

This edition follows the modern-home installation path: an existing 1/4-inch plastic cold-water
line and push fitting under the sink. The installer releases one tube, inserts the supplied
stub/tee/appliance-tube assembly into the existing coupler, and reconnects the original line to
the tee's open port. The assembly's long white tube continues through the supplied filter before
it reaches the appliance `TAP` inlet. No threaded fitting is opened during this path.

## Faucet mount

The first row shows one physical story: lower the complete factory assembly through the prepared
opening, seat it, slide the open under-counter plate around the attached tubes, and hand-tighten
the retained nut. The exact same 220 x 72 mm countertop window appears in every state. It is long
on the plate's slide axis and narrow across the real under-sink working space. The retracted plate
stays visibly clear of the washer and nut before it moves.

## Cold-water connection

`plumbing/modern/render_modern_tee.py` models the complete push-fit sequence in one continuous
under-sink coordinate frame. The shutoff pair is cropped to the valve and its handle, with the
rotation cue on the open state and the closed state left unobstructed. The macro
pair first shows the highlighted collet proud with opposing press and pull cues, then holds the
collet visibly recessed while the original tube begins to move out, with the result unobstructed.
The next row holds the supplied subassembly in normal T orientation in all three scenes: short stub
to the left, original-line port to the right, and the long appliance tube downward. It first shows
the complete subassembly approaching the existing coupler, then the installed subassembly with the
original line approaching its open port, then both connections fully seated.

The existing fitting uses the repository's measured John Guest PP0408W union geometry. Its source
declares 1.335 mm physical collet travel and 16 mm tube insertion; the macro illustration uses a
2.4 mm depressed position so the wordless state change remains visible at print size. The
customer-facing PP0208E tee is built from John Guest's published 1/4-inch dimensions: 39.0 mm run
span, 19.5 mm port reach, 15.7 mm insertion depth, 16.3 mm maximum body diameter, and 4.3 mm bore.
Long tubes continue through the crop; no arbitrary remote tube end is shown. Every connector and
tube is a CAD solid.

`plumbing/plumbing_scenes.py` retains the separate older-home braided-hose study assets. They are
not scenes or dependencies of this modern push-fit guide.

## Appliance rear connections

The final row contains exactly two registered states: all six customer leads clear of the rear
face, and all six fully seated. In the open state the six terminated ends are already grouped and
aimed along their common insertion direction; that pose carries the motion without a separate
overlay. The five tube collars are production solids. The faucet-display SIG-6 cable is black in
both the faucet and rear-panel scenes. Each 30 mm collar
starts 47.5 mm behind its insertion tip and ends 77.5 mm behind it. The routed ends of every tube
and the RJ11 ribbon continue out of the common crop, so the connected state contains no visible
loose distal ends.

The physical endpoint rule is:

- red `CO2` supply to `CO2`;
- filtered white tap-water supply to `TAP`;
- blue faucet tail to `SODA`;
- both black faucet tails to the two `FLAVOR` ports;
- RJ11 plug to the signal jack.

## Build

From the repository root:

```sh
# Faucet and appliance-rear CAD artwork.
tools/cad-venv/bin/python hardware/quickstart/quickstart_art.py

# Modern under-sink shutoff, release, and tee sequence.
tools/cad-venv/bin/python hardware/quickstart/plumbing/modern/render_modern_tee.py

# The rendered sheet and public PDF.
tools/cad-venv/bin/python hardware/quickstart/_build.py
```

The page is authored at 5700 x 3900 px and rendered at 360 dpi. Print it on an Epson ET-8550 from
the rear feed, landscape, page size **13x19 borderless**, media type premium semigloss, photo
quality, and 100 %. Stock: A-SUB satin RC photo paper, 260 gsm (72 lb), 13 x 19 in, warm white,
waterproof, single-sided - [B0DSJ9X4CR](https://www.amazon.com/dp/B0DSJ9X4CR), 50 sheets. The outer
0.5 inch holds nothing essential so the printer's borderless expansion cannot cut an action.
