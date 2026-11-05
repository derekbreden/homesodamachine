# Nameplate attachment options

Full-size attachment proposals for the 88 × 100 mm nameplate. These models are
for selecting the attachment. They do not change the installed enclosure or
release a print package. Printing is held for Derek's attachment review.

[Compare all three in 3D](https://homesodamachine.com/3d#glb:assembly%2Fscenes%2Fglb%2Fnameplate-attachment-options.glb).
The upper row shows receivers, the middle row plate backs, and the lower row
assembled faces. Orange marks the flexible wall, green its continuous root into
the body, and blue a rigid catch. Those inspection colours are not print colours.

## A — Plate wings

[Inspect A in 3D](https://homesodamachine.com/3d#glb:assembly%2Fscenes%2Fglb%2Fnameplate-attachment-option-a.glb).

Each short side wall joins the face continuously along a 34 mm root, with an
R0.8 transition. The wall is 1 mm thick and projects 5 mm behind the plate.
A pointed lead-in gives 0.25 mm capture; the receiver provides 0.35 mm inward
release travel and a centred 6 mm tool opening on each side. The spring belongs
to the replaceable nameplate.

The proposed plate print direction is CAD +Z, upright with a brim. This places
the bending in XY within each layer. A 45° lower end grows the wall out from the
face. The colour printing and insertion force need physical verification in this
orientation. The receiver remains part of the roof-down back-top.

## B — Receiver wings

[Inspect B in 3D](https://homesodamachine.com/3d#glb:assembly%2Fscenes%2Fglb%2Fnameplate-attachment-option-b.glb).

Each receiver side wall has a continuous 40 mm root into its backing. The wall
is 1 mm thick with an R0.8 transition. The rigid plate catches engage it by
0.25 mm, with 0.35 mm outward release travel. The centred tool openings expose
the retaining shoulders.

The plate prints flat, face up. The receiver prints roof down, putting its
bending in XY within each layer. This option recesses the face 1.5 mm behind
the bezel and lowers the assembly 2 mm to maintain the DATA-jack gap. Its
flexible feature belongs to the enclosure back-top.

Both wall ends and retaining-head starts have 45° grow-outs in their proposed
print direction.

## C — Two M3 screws

[Inspect C in 3D](https://homesodamachine.com/3d#glb:assembly%2Fscenes%2Fglb%2Fnameplate-attachment-option-c.glb).

The rigid plate uses two acquired black M3 × 6 socket screws and two acquired
ruthex RX-M3S × 4 inserts. The plate prints flat, face up. The 6.2 mm counterbores
leave the screw heads 1.8 mm proud. The inserts are drawn as installed envelopes;
the cold printed insert pilot is 4.0 mm. The thread envelopes are illustrative.

## Shared geometry and generation

The artwork and QR are imported from the fine nameplate model. The face size,
94.3 mm receiver width and horizontal frame placement are retained. The frame
leaves 2.95 mm to the enclosure corner tangent and 2.90 mm to the colour-chip
frame. The proposals put the plate face at world Y477.3; A and C centre it at
Z220, B at Z218. The receiver pocket backing is at least 3 mm nominally.

`review.rs` cuts these proposals with the installed Rust kernel. Its manual
review checks solid validity, connected plate/receiver bodies, seated overlap
and separation from the white artwork. A 9 mm insertion sweep at 0.5 mm intervals
uses an idealized wall displacement with 0.35 mm head travel to check passage.
These checks do not establish insertion force or printed spring life.

```sh
python3 tools/run.py -- tools/cad-venv/bin/python \
  hardware/printed-parts/enclosure/nameplate/attachment-options/generate.py
```

The GLBs are written to `hardware/assembly/scenes/glb/` for the website's existing
3D viewer. `review.numbers.json` identifies the approved face model used as the
input. [The review report](review.json) records the dimensions, measured checks,
source and artifact hashes, and desktop/mobile browser results.
