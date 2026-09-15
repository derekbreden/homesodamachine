# The enclosure display as it stands

The baseline the variations are compared against, drawn from
[`firmware/src_front/main.cpp`](/firmware/src_front/main.cpp) at the commit this study was made
on. Every number here is the firmware's own.

## Palette

| Role | Hex | `main.cpp` |
|---|---|---|
| Screen | `#1a1a2e` | `THEME_BG` |
| Card | `#242440` | `COL_CARD` |
| Card, pressed or selected | `#33335c` | `COL_CARD_ON` |
| Accent | `#e94560` | `COL_ACCENT` |
| Text | `#e8e8f2` | `COL_TEXT` |
| Dim text | `#8888aa` | `COL_DIM` |
| Good | `#37c98b` | `COL_GOOD` |
| Warn | `#f0a83c` | `COL_WARN` |
| A control at the end of its travel | `#3a3a55` | `COL_OFF` |

Montserrat at 20, 28 and 40 px. 20 is the smallest font built into the image.
Every card and every button has a 14 px corner radius and no shadow.

## Shell

- Screen 800 × 480. Rail 190 wide on the left; pane 610 wide from x 190.
- Rail targets: four, each 178 × 110 at x 6, starting y 8, 8 px apart — so y 8, 126, 244, 362.
  An icon over a word: the word (Montserrat 20, `COL_TEXT`) sits on the target's floor inside
  6 px padding, the 48 px icon centres in what is left. Background `COL_CARD`, and `COL_ACCENT`
  for the one you are on.
- Pane padding 16, so the pane's content runs x 206…784, y 16…464 — 578 × 448.
- Every pane keeps its top 64 px clear and starts its body at y 76 of the pane's content
  (screen y 92), because the Settings square floats over that band.
- Settings: one 64 × 64 square at screen (720, 16), `COL_CARD`, `COL_ACCENT` when you are on it,
  a gear glyph centred in Montserrat 28.

## Choose

Title **CHOOSE A FLAVOR**, Montserrat 28, `COL_DIM`, at pane content (0, 17).

Two cards, each 281 × 300, at pane content y 76, x 0 and x 297. Card padding 12, so a card's
content box is 257 × 276. Under each card, its own 281 × 56 settings target on the pane's
floor (pane content y 392), reading `⚙  SETTINGS` in Montserrat 20 `COL_DIM`.

Inside a card, measured from its content box:

- The face, 129 × 240, left, vertically centred — content (0, 18).
- A second column starts at x 145.
- **RATIO**, Montserrat 20 `COL_DIM`, centred on content y 112.
- The ratio itself, Montserrat 40 `COL_TEXT`, centred on content y 152.
- **LEVEL**, Montserrat 20 `COL_DIM`, centred on content y 192.
- Four 24 × 14 segments, 4 px radius, 28 px apart, centred on content y 218: lit ones
  `COL_GOOD`, or `COL_WARN` when only one is lit; the rest `COL_OFF`. The caption reads
  **EMPTY** instead of **LEVEL** when the float sits on the bottom reed.
- The selection badge, a 44 px `COL_ACCENT` disc with a white check, at content (179, 0), on
  the selected card only.

The selected card is `COL_CARD_ON` with a 1 px `COL_ACCENT` border and a 3 px `COL_ACCENT`
outline outside it. The other is `COL_CARD` with a 1 px `COL_OFF` border and no outline. The
border is 1 px on both so the artwork never moves when the selection does.

## A flavor's own page

- **Back** — 172 × 58, `COL_CARD`, at pane content (0, 3), reading `‹  BACK` in Montserrat 20.
- **The anchor** — that flavor's face at 172 × 320, at pane content (0, 106): it hangs from the
  line both columns end on, pane content y 426.
- The east column starts at x 188 and is 390 wide.
- **The ratio card** — 390 × 130, `COL_CARD`, at (188, 76), 14 px padding. Inside it, `−` and
  `+` as two 84 × 72 `COL_CARD_ON` buttons and the ratio between them. The range is 1:10…1:30,
  and a stepper at the end of its travel goes `COL_OFF`.
- A caption at (188, 218), then the strip of faces at (188, 248): 86 × 160 tiles in a 96 × 170
  button, 12 px apart, the chosen one ringed. Flanking it, two 48 px arrows the height of the
  tiles at x 188 and x 734; between them the strip is 294 wide. Under it at y 426 a 10 px track
  saying where in the row you are. All three appear only when the row runs off the column,
  which with eight faces it does.

## Fill a flavor

Title **FILL A FLAVOR**, Montserrat 28 `COL_DIM`. Two cards 281 × 372 at pane content y 76,
x 0 and x 297. Each carries a 48 px funnel mark in `COL_ACCENT` over that channel's 129 × 240
face, the pair centred as a block in the card.

Prime and Clean are the same page with their own word and their own mark.

## The operation lock

Full screen, `THEME_BG`, nothing else reachable.

- The animation, 360 × 360, at (18, 60) — 16 frames of a glass filling with bubbles, at 10 fps.
- The modal, 396 × 238, at (378, 121), `COL_CARD`, 14 px radius. Padding: 24 left, 28 right,
  30 top, 28 bottom, so its content box is 344 × 180 at (402, 151).
- The channel's face, 86 × 160, left, vertically centred — (402, 161).
- A column at content x 102, 242 wide:
  - the kicker, Montserrat 20 `COL_ACCENT`, at (504, 151) — **11 MIN LEFT**;
  - the title, Montserrat 40 `COL_TEXT`, at (504, 181) — **Cleaning**;
  - a 242 × 10 bar at (504, 239), track `COL_OFF`, indicator `COL_GOOD`, 5 px radius;
  - the note, Montserrat 20 `COL_DIM`, at (504, 257) — **1 of 3 • water in**.
- **STOP**, 110 × 44, `COL_CARD_ON`, Montserrat 20, at the content box's bottom right — (636, 287).

The boot lock is the same object at 360 wide, with a 6 × 178 `COL_ACCENT` bar where the face
stands and no bar, note or STOP: **HOME SODA MACHINE** / **Powering on** / **Getting everything
ready.**

## Settings

Title **SETTINGS**, Montserrat 28 `COL_DIM`.

- The status card, 372 wide at pane content (0, 76), `COL_CARD`, 14 px padding, its height
  whatever the drawing needs — 328, so it ends at pane content y 404.
  - **SYSTEM STATUS**, Montserrat 20 `COL_DIM`, at its top left.
  - The drawing, 344 wide, 30 px below that caption. It is the enclosure seen along X: 462 mm
    deep by 361 mm tall, 2 px margin, scale `(344 − 4) / 462`, depth running left to right with
    the front on the left and height running bottom to top.
    - The profile, a 3 px `COL_DIM` polyline, rounded: (0, 0) → (0, 361 − 61.87) → (61.87, 361)
      → (462, 361) → (462, 0) → close. The chamfer is the display's own 45° facet.
    - The cold core, a 4 px-radius `COL_DIM` outline from depth 173 to 456, height 6 to 259.4.
    - The carbonator's tube, a 10 px-radius outline, 127 mm wide centred on depth 314.5, from
      height 38 to 190.4.
    - Two reservoir pockets, 6 px-radius outlines, depth 393…446 and 183…236, height 8 to 219.4.
  - Ten reeds, 14 px discs: four on each pocket's outer wall — depth 449 and 180, at heights
    63.5, 108.5, 153.5 and 198.5 — and two on the tube's aft wall at depth 379.25, heights
    105.1 and 133.3. A reed the main board reads closed is a filled `COL_GOOD` disc; every other
    one is a `COL_CARD` disc with a 2 px `COL_DIM` ring.
  - Under the card, and only when the main board is not answering: **not reading the reeds**,
    Montserrat 20 `COL_WARN`.
- East of it, a 190-wide column of areas, one 64-high `COL_CARD` target each, 12 px apart.
  One so far: **PUMP SERVICE**.
