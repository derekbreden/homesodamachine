# Where the current design strains

A close read of the enclosure display as it stands, made before the directions were drawn.
Every direction in this study answers some part of it.

## Who the panel is for

This is a $7,500 hand-built kitchen appliance (units 001–050, numbered and signed; $5,500 thereafter) sold to homeowners with $150K–250K household incomes who drink two to four diet sodas a day and hate hauling cans. They are not enthusiasts of the machine — they are people who want a Diet Mountain Dew to appear, cold and fully carbonated, when they pull the faucet handle at the counter. The 4.3" 800×480 panel sits on a 45° facet on the front of a cabinet under that counter, read from above at arm's length, standing, in a lit room, by someone who is not reading a manual and who will touch this glass perhaps once a week: to switch which of two flavors is armed. Everything else it does — prime, fill, clean, pump service — is maintenance a person performs a handful of times a year, and the panel should not be shaped as though those are equals. The backlight is on or off, so the panel is either fully present or completely gone; it must look like an appliance in the dark kitchen as much as in the lit one. RGB565 bands any wide gradient, so the design must live on flat fills, real hierarchy of size and weight, and photographic faces — not on soft light. The faces are the product identity: a channel is named by the logo it wears, in the faucet's own 43:80 aspect, never by a number or a word. The panel's job is to look like it belongs next to a Sub-Zero and a Wolf, not next to an oscilloscope.

## What it already gets right

- **The face is the name, at the faucet's own aspect.** `FLAVOR_ANCHOR_W/H` 172×320, `FLAVOR_CARD_W/H` 129×240, `FLAVOR_TILE_W/H` 86×160 — three scales, one 43:80 aspect, everywhere a channel is offered. No numbers, no letters, no square crops. This is the single strongest idea on the panel and every direction must keep it.
- **The anchor column is one unchanging west edge across four pages.** `BACK_W` is defined as `FLAVOR_ANCHOR_W` (main.cpp:266), so the back button and the face are one 172 px column, and moving between a flavor's page, prime, fill and clean moves only the east half. This is real interaction design, not decoration.
- **Flat fills, zero gradients, zero shadows.** `mkCard()` (main.cpp:2172) explicitly strips LVGL's default border and shadow. Correct for RGB565, and correct for a panel whose repaint cost is literally the dirty rectangle over a contended PSRAM bus. Any direction that reaches for soft light will band and will cost frames.
- **The pane is transparent, not filled** (`buildPane`, main.cpp:4170): a second opaque fill would make every small change dirty all 586 KB. The design is already shaped by the hardware in a way that is invisible and correct.
- **Nothing on any page is for the builder.** No firmware version, no link health, no frame counter. Everything a bring-up needs is `GET_DIAG` over USB. That discipline is hard-won and must survive.
- **Layout does not move when state does.** `refreshHomeSelection` (main.cpp:2409) holds `border_width` at 1 px whether selected or not and puts the emphasis in an *outline* outside the box, so the artwork and badge never jump. Keep that principle whatever replaces the outline.
- **The per-flavor gear is a sibling of the card, not a child** (`buildHome`, main.cpp:4203) — no press on the settings target can reach the selection target under it. The right call.
- **The rail is ordered by consequence:** CHOOSE · PRIME · FILL · CLEAN, least destructive to most, so reading order is a risk gradient.
- **Settings is denied a rail slot** and lives as one 64 px corner square on the screen root, over every page — the hierarchy claim from the brief is structural, not just stated.
- **The picker's arrows are as tall as the thing they move** (`TILE_ARROW_W` 48 × `TILE_BTN_H` 170) and disappear entirely when the row fits. "An arrow the size of a scrollbar is a scrollbar with a shape" is the right instinct, and the vanish-when-unneeded rule is right.
- **Every committing target is enormous.** Rail items 178×110, Choose cards 281×300, pick cards 281×372, START 390×120. The panel never asks a standing adult to hit something small — with the single exception noted below.
- **Press-lock with two deliberate exceptions.** `mkBtn` sets `LV_OBJ_FLAG_PRESS_LOCK` so a wandering thumb still fires; START and STOP clear it so sliding off cancels a commit. That asymmetry is correct and subtle.
- **The accent is rationed.** ~20 uses of `COL_ACCENT` across 5,564 lines. Whatever replaces #e94560, the discipline of one scarce hue is worth keeping.

## Where it strains

### Selection — the one thing a customer comes here to change — is carried by a 1.26:1 fill shift

On Choose, "this is the flavor the machine is on" is drawn three ways: the card fill moves from `COL_CARD` #242440 to `COL_CARD_ON` #33335c, a 3 px `COL_ACCENT` outline appears, and a 44 px circle with LVGL's built-in checkmark glyph shows up at the head of the side column. Two of those three are nearly invisible at two metres, which leaves the whole selection resting on a small generic tick. The brief demands the selected/unselected distinction be unmistakable from two metres; the panel's primary weekly act is the weakest signal on the screen.

**In the code.** `refreshHomeSelection` (main.cpp:2409-2436). #242440 has relative luminance 0.0199, #33335c 0.0383 — a contrast ratio of **1.26:1** between selected and unselected card. The outline is 3 px on a 281×300 card (`cw = (610 - 32 - 16)/2 = 281`, `HOME_CARD_H = 448 - 76 - 56 - 16 = 300`). The badge is `HOME_BADGE_H` 44 carrying `LV_SYMBOL_OK` at Montserrat 20 — the smallest font built.

**What a direction can do with it.** Make selection a change of *state class*, not a change of shade: the unselected flavor could recede (desaturated, dimmed, smaller, pushed back) while the selected one is fully present, or the selection could be a physical device — a lit bar, a filled field, a position — that reads as a different kind of object rather than a slightly lighter rectangle. Whatever it is, it must survive being photographed from two metres and thresholded.

### Four buttons have literally no press feedback, because their resting fill is the pressed fill

`mkBtn` sets the pressed background to `COL_CARD_ON` #33335c for every button it makes (main.cpp:2234). Four controls are then *created* with #33335c as their resting fill: the ratio `−` and `+`, and both picker arrows. The lock's STOP is a fifth. Pressing any of them changes nothing on the glass — the only confirmation a person gets is the main board's sound, over J9. On a capacitive panel with no travel, that is the whole feedback loop delegated to a speaker in another enclosure.

**In the code.** main.cpp:2234 `lv_obj_set_style_bg_color(b, lv_color_hex(COL_CARD_ON), LV_PART_MAIN | LV_STATE_PRESSED)` against main.cpp:4273 `flvRatioMinus = mkBtn(row, 84, 72, COL_CARD_ON)`, :4278 `flvRatioPlus`, :4320 `flvTileLeft`, :4326 `flvTileRight`, :3414 `lockStop`. Identical hex, main and pressed.

**What a direction can do with it.** A direction needs a press device that is a different *dimension* from the resting palette — a scale, an inversion, a rim, a wash — rather than one more step on a four-stop ladder of near-identical dark blue-purples. The current palette has run out of shades before it has run out of states.

### The one way out of a running clean cycle is a tenth the size of the button that starts it

START CLEAN CYCLE is 390×120 in full accent. STOP, on the lock that is up while tap water is running through the machine into a pitcher at the faucet, is 110×44 in the dimmest button fill on the panel, bottom-right of a modal. 44 px is below the brief's own 64 px minimum for a standing adult's thumb. The commit is loud and enormous; the abort is quiet and small — backwards for the only screen where something is physically happening in the kitchen.

**In the code.** `CONFIRM_ACT_H` 120 × `DETAIL_W` 390 = 46,800 px² (main.cpp:4415). `LOCK_STOP_W` 110 × `LOCK_STOP_H` 44 = 4,840 px² in `COL_CARD_ON` (main.cpp:415-416, 3414). Ratio **9.7:1** in favour of the commit.

**What a direction can do with it.** The lock is the one screen where the machine has taken something away from the person. Its design should acknowledge that: the escape wants to be the most findable object on it, and the lock overall wants to read as *deliberately withheld*, not as a dialog box.

### The lock screen's hierarchy is inverted — a 360×360 square glass outranks the flavor by 9×

The lock gives 360×360 to a generic glass-and-bubbles loop and 86×160 — the smallest of the three face scales — to the channel the machine is actually cleaning. The brief's own rule is that a square crop of a face answers a question nobody asked; the biggest picture on this screen is a square illustration of a drink that is not being poured. Meanwhile **11 MIN LEFT** — the single fact a person standing there wants — is the kicker: Montserrat 20, the smallest built size, top-left of the modal in accent. And the progress bar across an eleven-minute cycle is 10 px tall, which is the exact height of `TILE_TRACK_H`, the picture-strip scroll indicator. "How far through the clean cycle" and "where you are in a row of thumbnails" are drawn at identical weight.

**In the code.** `LOGO_SIZE` 360 (main.cpp:56) aligned LEFT_MID at x=18; `lockFace` uses `flavorTile` = 86×160 (main.cpp:3395, 68-69). `lockBar` height 10, `LOCK_COL_W` = 396−24−28−102 = 242 (main.cpp:3401, 411). `TILE_TRACK_H` 10 (main.cpp:310). Kicker at `lv_font_montserrat_20` (main.cpp:3383).

**What a direction can do with it.** Decide what the lock is *for* and size accordingly. If it is "the machine is busy and here is when you get it back," the time remaining and the progress are the screen, and the animation is at most an accent. If it is a moment of theatre, the theatre should be about this flavor, at 43:80, not about a generic glass.

### The page's own name is the dimmest text on the screen; the ratio is the brightest

Every pane titles itself in `COL_DIM` #8888aa at Montserrat 28 — "CHOOSE A FLAVOR", "PRIME A FLAVOR", "SETTINGS". On Choose, the loudest element is `1:20` in `COL_TEXT` #e8e8f2 at Montserrat 40: the concentrate ratio, a number a customer sets once and then never touches, is the brightest, largest thing on the machine's home screen, beside two flavor faces at 129×240 and a page title in grey. The hierarchy is exactly upside down relative to how often each thing is used.

**In the code.** `buildHome` main.cpp:4194 (title, 28/COL_DIM) and :4222 (`homeFlavorRatio[i]` at `lv_font_montserrat_40`, COL_TEXT). #8888aa on #242440 computes to **4.4:1** — under 4.5 — and it is carrying "RATIO", "LEVEL", "IMAGE", every body paragraph, and the lock's body line.

**What a direction can do with it.** Rank by frequency of use, not by ease of drawing. What a person does weekly (pick a flavor) should dominate; what they set once (ratio) can be small, or behind the flavor's own page entirely. And the dim tier needs to be a *real* tier — right now it is a single grey doing caption, label, body prose and page title, four jobs at one weight and one colour.

### 24% of the glass is permanently spent on three maintenance operations

The rail is 190 px of an 800 px screen, full-bleed top to bottom — 91,200 px², 23.75% of the panel — and it is allocated equally across CHOOSE (the only customer act) and PRIME, FILL, CLEAN (maintenance a person performs a handful of times a year). All four items are the same 178×110 card in the same #242440 as every card in the pane, so the rail is not even a distinct *region* visually — it is four more cards that happen to be stacked on the left. Only the accent fill on the current item separates it from the pane, and the rail's top item starts at y=8 while the pane's title text starts at y=33 and the settings square at y=16: three different top edges on one band, no shared datum.

**In the code.** `RAIL_W` 190, `RAIL_ITEM_H` 110, `RAIL_INSET_Y` 8 (main.cpp:208-211); `buildRail` creates `mkBtn(scr, RAIL_W - 12, RAIL_ITEM_H, COL_CARD)` at x=6 (main.cpp:4118-4119). `PANE_PAD` 16, title at `(PANE_HEAD_H - TEXT_H_28)/2` = 17 inside a 16 px pad. `SETTINGS_BTN` 64 at y = `PANE_PAD` = 16.

**What a direction can do with it.** The owner is fine with the layout, but a direction is allowed to argue the rail should be *materially* different from the pane — a different ground, a different depth, a different family of shapes — so that the eye reads "place-switcher" instead of "four more cards". A direction that keeps the rail should give it a hierarchy of its own: CHOOSE is not a peer of CLEAN. And the three top edges want to land on one line.

### The entire icon vocabulary is LVGL's default symbol font — this is the loudest dev-tool tell

`LV_SYMBOL_SETTINGS`, `LV_SYMBOL_OK`, `LV_SYMBOL_LEFT`/`RIGHT`, `LV_SYMBOL_MINUS`/`PLUS`, plus four raw FontAwesome codepoints in `front_icons_48`. Every mark on a $7,500 appliance's face is a stock glyph from the toolkit's built-in subset, at whatever weight FontAwesome drew it, sitting next to photographic product faces. Nothing on the panel was drawn for this machine. A person who has seen an Arduino project recognises the gear immediately.

**In the code.** main.cpp:2243-2256 (`\xEF\x89\x9A`, `\xEF\x81\x83`, `\xEF\x82\xB0`, `\xEE\x81\xAD` in `front_icons_48`), :4178 (`LV_SYMBOL_SETTINGS`), :4257 (`LV_SYMBOL_OK`), :4323/:4329 (`LV_SYMBOL_LEFT`/`RIGHT`), :4276/:4281 (`LV_SYMBOL_MINUS`/`PLUS`), :2265 (`LV_SYMBOL_LEFT "  BACK"`).

**What a direction can do with it.** Every direction owes this panel a drawn mark system — inline SVG in the study, a custom icon font on the device — with its own weight, its own corner treatment and its own relationship to the type. The funnel, the drop, the clean cycle and back are four marks; getting them right is most of the difference between an appliance and a demo.

### Settings lands on an engineering elevation of the machine with ten unlabelled dots

The settings landing is a 3 px hairline CAD side profile of the enclosure — 462 mm × 361 mm, the 45° facet, the cold core, the carbonator tube, two reservoir pockets — with ten 14 px state dots on it and no labels anywhere. Open/closed is a filled #37c98b disc versus a #242440 disc with a 2 px #8888aa ring, at 14 px, on a 340 px-wide line drawing, at arm's length. The brief asks that closed and open be separable at a glance; a 10 px green core inside a ring is not. And the same landing puts a second 190 px column of #242440 buttons on the right, mirroring the rail on the left — the settings page reads as two rails with a schematic between them.

**In the code.** `buildStatusDiagram` main.cpp:4526-4592. `cardW = 610 − 32 − 190 − 16 = 372`, diagram width 344, scale `s = (344−4)/462 = 0.736`, so a 14 px dot is 19 mm of machine. `STATUS_MM_REED_DOT` 14, `STATUS_MARGIN` 2 (main.cpp:4522-4523). `STATUS_MENU_W` 190 — identical to `RAIL_W` (main.cpp:227, 208).

**What a direction can do with it.** This is the place the panel most looks like a dev tool, and it is the place with the most room to be beautiful. A direction can decide what "is my machine OK" should look like to a homeowner: a single verdict with detail underneath, a warm cutaway with the two reservoirs as legible vessels rather than rectangles, states carried by fill and level rather than by dot diameter. If the profile stays, its states need to read as *things being full or empty*, not as dots being on or off.

### A 43:80 face inside a near-square card — the pick screens waste half their width

The panel is 800×480 (1.67:1) and its primary content unit is 43:80 (0.54:1). Every container the face lives in except the anchor column is roughly square or landscape, so the answer everywhere is to pad a tall picture inside a wide box. The pick cards are the extreme: a 281×372 card holding a 129×240 face and a 48 px glyph — 54% of the card's width is empty. On Choose the face is centred vertically in its card while the column beside it is top-anchored and runs out 44 px early, so the two halves of the card share neither baseline nor centreline.

**In the code.** `buildFlavorPicker` main.cpp:4370-4400: `cw = 281`, `ch = PANE_H − PANE_BODY_Y = 372`, `top = (372 − (48+16+240))/2 = 34`, face `FLAVOR_CARD_W` 129. On Choose: card inner 257×276, face 129×240 at `LV_ALIGN_LEFT_MID`, column at `colX = 145` width 112; the level segments end at inner-y 232 of 276 (main.cpp:4230-4240).

**What a direction can do with it.** Either make the container the face's own shape — let the 43:80 be the card, edge to edge, and hang everything else off it — or commit to a wide card and give the face a deliberate reason to sit where it does (bleeding off an edge, overlapping a band, held by a frame). The current answer, centring a portrait in a landscape box and filling the rest with grey captions, is the one that reads as unresolved.

### The accent does five unrelated jobs and the semantic hues barely appear

#e94560 means all of: you are here (rail selection fill), you are pressing (rail and corner press state), this flavor is selected (card outline and badge), press this to commit (START, DRY THE LINES), and where you are in a row (the picker's scroll thumb). One hue answering "location", "feedback", "state" and "action" teaches nothing. Meanwhile #37c98b and #f0a83c each appear on one or two screens — green is simultaneously "reservoir has syrup", "reed closed", "progress" and "prime running" — so neither has become a vocabulary the user knows. On four of the five screens the palette is doing almost nothing at all: near-black ground, one card grey, one text white, one text grey.

**In the code.** 20 `COL_ACCENT` uses spanning `setRailSelection` (:4165), `buildRail` pressed (:4123), `refreshHomeSelection` (:4432-4437), `buildConfirm`'s go button (:4415), `flvTileThumb` (:4351), `lockAccent` (:3379), `lockKicker` (:3383). `COL_GOOD` at main.cpp:3301 (level segments), reed dots, `lockBar` indicator, and the prime pad at :2604.

**What a direction can do with it.** Split the jobs. A direction can afford separate devices for *where you are*, *what you touched*, *what is armed* and *what commits* — and can also afford far more colour than this panel currently uses. A kitchen appliance in a lit room does not have to be a dark dashboard; that is a choice the current design made silently and never revisited.

### The flavor page's two columns do not end on the line the code insists they do

The detail-page geometry is built around one floor that both columns land on — the comment at main.cpp:263 is explicit and there are static_asserts for it. On the flavor page that rule breaks: the anchor's bottom lands at y=414 as designed, but the picker strip ends at 418 and its track at 436, twenty-two pixels below. The asserts only check that the floor is inside the pane, so the one page where the rule is violated is the one page the asserts do not cover. Visually it reads as a near-miss rather than a decision.

**In the code.** `DETAIL_FLOOR = 448 − 22 − 12 = 414`; `ANCHOR_Y = 414 − 320 = 94`. `IMAGE_LABEL_Y = 76 + 130 + 12 = 218`, `TILE_STRIP_Y = 218 + 22 + 8 = 248`, `TILE_BTN_H = 170` → strip bottom 418; `TILE_TRACK_Y = 248 + 170 + 8 = 426` + `TILE_TRACK_H` 10 → 436, against `PANE_H` 448 (main.cpp:277-315).

**What a direction can do with it.** Whatever a direction does with the picker, the east and west columns should visibly share a baseline. The discipline the rest of the detail pages already have is worth extending to this one.

### "SETTINGS" names two different destinations on the same screen

On Choose, each flavor card has a `⚙ SETTINGS` button under it that opens that flavor's ratio-and-face page, while the corner square — also a gear — opens the machine's Settings, whose title is also SETTINGS. Same word, same glyph, three meanings, two of them on one screen. NAMES.md's rule is one thing, one name; the panel breaks it in the most visible place it has.

**In the code.** `buildHome` main.cpp:4210-4212 (`mkText(gear, LV_SYMBOL_SETTINGS "  SETTINGS", ...)` → `homeSettingsCb` → `PAGE_FLAVOR`) against `buildSettingsButton` main.cpp:4177-4179 (`LV_SYMBOL_SETTINGS` → `PAGE_SETUP`) and `buildSettings` main.cpp:4600 (title "SETTINGS").

**What a direction can do with it.** The per-flavor target is about a *drink* — its strength and its face. Name it and mark it for that. It is also a chance to stop making the doorway to the flavor's own page a 281×56 grey strip of secondary text under the card, when it is the second-most-used control on the panel.

