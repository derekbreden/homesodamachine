# The brief a direction is drawn against

Every direction in this study draws the same five screens of the enclosure display, with the
same facts on them, so the comparison is of the design and nothing else.

## The surface

800 × 480, a 4.3" IPS panel in the enclosure's front face, tilted back on a 45° facet off the
top-front arris — a cabinet under a kitchen counter, so the panel is read from above at roughly
arm's length, standing. Capacitive touch, one finger, no hover and no cursor. RGB565, so a
gradient over a wide field bands; flat fills and dithered art do not. The backlight is on or
off with nothing between, and the machine is a kitchen appliance that lives in a lit room.

A target a standing adult hits with a thumb is 64 px on a side at the smallest, and the
committing targets on this panel are much larger than that.

## The five screens

Each direction writes these five files. Same facts, same state, every direction:

| File | The screen |
|---|---|
| `choose.html` | Choose — the machine's home, both flavors, one of them selected |
| `flavor.html` | One flavor's own page — its ratio, and the row of faces it can wear |
| `pick.html` | Fill a flavor — the two-up pick that opens a service action |
| `lock.html` | The operation lock, mid clean cycle |
| `settings.html` | Settings — system status and the areas beside it |

### `choose.html`

The appliance's default page, and what it returns to. It carries:

- The page's own name in the top band.
- **Flavor A — selected.** Its face. `1:20`. Reservoir level 3 of 4. A way into its own page.
- **Flavor B — not selected.** Its face. `1:14`. Reservoir level 1 of 4, which is the low
  reading and says so. A way into its own page.
- The four rail destinations — **CHOOSE · PRIME · FILL · CLEAN** — reachable from here.
- A way into Settings, which is not a customer destination.

Whether the selection is a badge, a fill, an outline, a position or something else is the
direction's call. That one of the two is selected and the other is not has to be unmistakable
from two metres away.

### `flavor.html`

Flavor A's own page, reached from its card on Choose, with a way back to Choose.

- Which flavor this is about, said in the picture rather than in a word for it.
- **Ratio `1:20`**, with a `−` and a `+` that step it. The range is 1:10 to 1:30.
- **The row of faces this flavor can wear** — eight of them, the third one chosen. The row is
  wider than the space it has, so it is dragged sideways; it must say so in something that can
  be pressed, and say where in the row you are.

### `pick.html`

**FILL A FLAVOR** — the first step of the fill: which channel this is about.

- Two cards, one per flavor, each carrying the mark for what is about to happen (a funnel) over
  that channel's face.
- A way back.

### `lock.html`

The full-screen operation lock, with the clean cycle running. Nothing else on the panel is
reachable while it is up.

- The machine is deliberately busy, and says so without words as well as with them.
- **Cleaning**, on channel A — that channel's face is on it.
- A progress bar across the whole cycle, about 40% through.
- **1 of 3 · water in**
- **11 MIN LEFT**
- **STOP** — the one way out.

The current design runs a 16-frame glass-and-bubbles loop at 10 fps on this screen. A direction
may keep a moving element, replace it, or do without one; draw whatever stands in for it as one
still frame.

### `settings.html`

- **System status**: the machine's own side profile with every reed on it — the enclosure seen
  along X, 462 mm deep and 361 mm tall, the display's 45° facet off the top-front arris, the
  front on the left. The cold core lies at the back of the floor: the carbonator's tube in the
  middle of it and a reservoir pocket at either end. Ten reeds: a column of four on each
  pocket's outer wall at 57.5, 102.5, 147.5 and 192.5 mm up the shell (empty at the bottom,
  full at the top), and the carbonator's low and high on its tube's aft wall at 99.1 and
  127.3 mm. Show the two bottom reeds of each column and the carbonator's low reed closed, the
  rest open. Closed and open have to be separable at a glance.
- **PUMP SERVICE** — the one area a person can go into from here, as its own target. Room for
  more of them later.
- A way back to where you were.

## What every screen carries

- **Settings is not a customer destination.** It gets no equal footing with the four rail
  destinations, wherever a direction puts it.
- **A channel is named by the logo it wears, never by a number.** No "Channel 1", no "A" and
  "B" on the glass. The face is the name. (`Flavor A` in this brief is the writer's shorthand,
  not a string that appears on a screen.)
- **Nothing on a panel is there for the person building it.** No link health, no frame rate,
  no transport counters, no firmware version.
- **The face is a glass.** A logo is 43:80 — tall, because it is a preview of what the faucet's
  own 1.47" display will wear while that flavor pours. Three scales are in use today: 172×320,
  129×240, 86×160. A direction may choose its own scales, but the aspect is the faucet's and
  does not change; a square crop of a face answers a question nobody asked.

## Facts and strings

Use these, so the screens compare:

| | |
|---|---|
| Flavor A | face `assets/flavor_1.png`, ratio `1:20`, level 3 of 4 |
| Flavor B | face `assets/flavor_2.png`, ratio `1:14`, level 1 of 4 (low) |
| Other faces for the row | `assets/flavor_3.png`, `assets/flavor_4.png`, and repeats of all four |

A face is drawn from a square source. `object-fit: cover` on a 43:80 box is the same
centre-crop the firmware's converter makes, so it is the right way to place one.

Flavors carry no brand names in this study. A face is the name.

## How a page is written

- One self-contained `.html` file per screen, plus one `style.css` per direction that all five
  share. The shared sheet is what makes a direction a direction.
- `html, body { margin: 0; width: 800px; height: 480px; overflow: hidden; }` — the page is
  exactly the panel and nothing scrolls. The renderer fails a page whose content spills past it.
- Faces load from `../../assets/`. Everything else is written in the page: inline SVG for
  icons, marks, the side profile and any illustration. No image files a direction invents, and
  nothing fetched at render time except a webfont.
- Webfonts come from `https://fonts.googleapis.com`. Any family there is available.
- No `:hover` state — there is no cursor on this panel. A pressed state may be drawn on one
  element per screen to show what a press looks like, and the page should say which.

## Rendering

```sh
node render.mjs --dpr 2 --out renders pages/<key>/*.html
```

Writes `renders/<key>-<screen>.png`. `--dpr 1` is the panel's own pixel grid.
