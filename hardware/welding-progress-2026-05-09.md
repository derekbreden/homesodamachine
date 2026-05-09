# Welding progress — Snapshot 2026-05-09

**Point-in-time snapshot, follow-up to [welding-progress-2026-05-01.md](welding-progress-2026-05-01.md). Supersedes the 05-01 Fall-Down recipe.** The wire-stick problem the 05-01 recipe targeted turned out to be a different parameter. Captured here while the understanding is fresh.

## TL;DR — the actual fix

**Bushing delay 2000 ms.** Default 400 ms is calibrated for thin sheet — too short for 0.065" 304L SS. With 400 ms, the Patch (forward push that follows the Pullback retract) fires into a still-molten puddle and re-fuses the wire. With 2000 ms, the puddle has solidified before Patch fires; wire pushes against solid metal and doesn't re-fuse.

Revert the 05-01 Fall-Down change. Fall-Down (= Fall time, possibly + Off delay) keeps the laser hot longer after trigger release, which compounds the re-fuse problem rather than fixing it. **The Pullback / Patch / Bushing-delay parameter trio on the X1 Pro IS the wire-retract feature** — the 05-01 conversation's claim that "the X1 Pro does not have a wire-retract parameter — Fall-Down is the substitute" was wrong. The parameters were sitting at factory defaults the whole time, doing exactly what they were designed to do, just sized wrong for this material.

## The translation problem in the English manual

The English X1 Pro Operator's Manual (52-page version, Figure 17 in §4.1) describes the wire feeding configuration parameters this way:

> Pullback length: the length of the wire back after releasing the trigger during welding.
> Patch length: length the wire retracts after releasing the trigger.
> Bushing delay: set the delay time for forward patching.

Pullback and Patch are both described as "wire retracts after releasing the trigger." That's a contradiction in the manual itself, not just a sloppy summary. The Chinese terms (the manual was translated from Chinese — the file's PDF metadata title is `X1 Pro产品手册及说明书.cdr`) resolve it:

| English (broken) | Chinese | Correct meaning |
|---|---|---|
| Pullback length | 回抽长度 (huí chōu) | Wire moves **backward** on trigger release, by this distance. |
| Patch length | 补丝长度 (bǔ sī) | Wire moves **forward** by this distance, *after* the Pullback retract — restores wire stickout so the next weld starts with consistent geometry. |
| Bushing delay | 补丝延迟 (bǔ sī yán chí) | Wait time **between** the retract and the forward push. "Bushing" is a mistranslation of 补丝 ("patch wire" / "compensating feed"). |

Chinese welding industry guidance (general, not X1 Pro specific): bushing delay typically 0 ms, "increased to prevent the wire from sticking a *second* time when the forward push happens too soon." That last clause was the missed insight. The default 400 ms is sized for sheet metal that solidifies fast; the realistic test fixture's 0.065" wall holds heat much longer.

## Sequence on trigger release, with corrected understanding

Settings on the welder (mostly factory defaults — only Bushing delay was changed):

- Wire feed speed: 10 mm/s
- Pullback length: 17 mm
- Patch length: 14 mm
- Manual pullback speed: 20 mm/s
- Wire feed delay: 0 ms
- **Bushing delay: 2000 ms** (was 400 ms default)
- Smoothness: 40 %
- Wire feed mode: Continuous
- Off delay: 200 ms (from Figure 18 "More parameter settings")
- Fall time: 50 ms (from Figure 18)

On trigger release:

1. t=0: trigger released. Wire stops feeding. Laser holds at full power.
2. t=0 to t≈850 ms: Pullback retracts wire 17 mm at 20 mm/s. Laser still firing during the first 200 ms (Off delay), then ramps down over 50 ms (Fall time). Laser fully off at t=250 ms.
3. t≈850 ms to t≈2850 ms: 2 s wait (Bushing delay). Puddle solidifies.
4. t≈2850 ms to t≈3550 ms: Patch pushes wire 14 mm forward at 20 mm/s. Wire pushes against now-solid metal — no re-fuse.

Total post-release cycle ≈ 3.5 s. Long but tolerable; eliminates the wire-stick.

## Why this was hard to see

At Bushing delay = 0 ms, retract and forward push happen back-to-back so fast the wire appears not to move at all. At the default 400 ms, the retract motion is briefly visible but obscured by the laser goggles plus residual sparks/glow. Only at ≥1500 ms does the retract become clearly visible and the timing distinct enough to interpret. Easy to conclude "auto-pullback isn't working" when in fact it's working perfectly — just in a 400 ms observation window the operator cannot reliably see through goggles.

## What's still valid from the 05-01 recipe

- Power 60% (down from 75%) — for warp reduction, independent of wire-stick.
- Wire feed 12 mm/s — compensates for the power drop.
- Wobble 80 Hz, 2 mm — unchanged.
- Argon 2 s pre / 2 s post — unchanged.
- Plate prep 30 s with 80–120 grit on cut edges — unchanged.
- Tack pattern (8 tacks, opposite-side bisecting) — unchanged.
- Trail-off motion — unchanged. Compounds with the auto-retract.
- Internal copper plug — still untested, still worth trying.

## What to drop from the 05-01 recipe

- **"Rise-up: 50 ms / Fall-Down: 100 ms"** — drop. These were targeting wire-stick and were the wrong lever. Revert to defaults (Off delay 200 ms, Fall time 50 ms). The wire-stick problem is owned by Bushing delay, not by the laser ramp.

## Open questions

1. **Lower Bushing delay sufficient?** 2000 ms works. Could probably tune to 1200–1500 ms for a faster end-of-bead cycle. Untested.
2. **Does wire feed actually stop at trigger release, or only after laser fully off?** Not explicitly confirmed. If wire continues feeding during the 250 ms laser-on-after-release window (Off delay + Fall time), that's extra wire deposited into the puddle before Pullback fires. Test: lower Wire feed speed to 1 mm/s, trigger briefly, watch whether wire continues to emerge from the contact tip during the 250 ms window.
3. **Wire feed mode = Pulse** — untested. Cycles wire in/out at the Cycle period (200 ms default). Could be useful for problematic geometries.
4. **Bushing delay vs material thickness** — 2000 ms is for 0.065" 304L SS. Production-side 0.065" 316L SS should behave similarly. Thicker plate will hold heat longer (longer delay); thinner sheet should need less.

## Sources

- X1 Pro Operator's Manual (52 pp, English long version), Figures 17 and 18: <https://cdn.shopify.com/s/files/1/0564/7581/1898/files/xlaserlab_X1_Pro_laser_welder_user_Manual_compressed.pdf?v=1760577559>
- X1 Pro multi-language manual download index: <https://www.xlaserlab.com/pages/xlaserlab-x1-pro-instruction-manual>
- Chinese welding parameter reference (Baidu TaShuo, hand-held laser welder operating instructions): <https://wapbaike.baidu.com/tashuo/browse/content?id=f008437b2cc3dab1932d2641>
- QL welding system Chinese manual — canonical 回抽长度, 补丝长度, 补丝延迟 definitions: <https://www.cf388.com/wp-content/uploads/2023/04/QL%E7%84%8A%E6%8E%A5%E7%B3%BB%E7%BB%9F%E6%93%8D%E4%BD%9C%E8%AF%B4%E6%98%8E%E4%B9%A6%E5%9F%BA%E7%A1%80%E7%89%88.pdf>

## What this snapshot is NOT

- Not a living document — re-snapshot at the next inflection point.
- Not a full recipe re-validation — only the wire-stick fix is confirmed. The 60% / 12 mm/s / plate-prep recipe from 05-01 still hasn't been run end-to-end as one integrated weld test.
- Not a substitute for hands-on observation — Bushing delay timing depends on puddle thermal mass (power, wall thickness, chill-block coverage). The 2000 ms value is for the realistic test fixture geometry; production stock may need tuning.
