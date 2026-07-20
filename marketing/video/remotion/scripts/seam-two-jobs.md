# Narration script — "The Seam Does Two Jobs" (Episode 02 · The Faucet)

Composition: `SeamTwoJobs` (marketing/video/remotion). ~95 s @ 30 fps.
Record VO to these beats; the on-screen text is already timed. First-person,
builder's POV — honest, unhurried. Every figure below is verified against the
repo + git history (fact-check pass); sources noted in `SeamTwoJobs.tsx` (`F`).

Alternate titles considered: *Print It Face Up* · *No Screws*.

---

**B1 · Cold open (0–10 s)** — the assembled faucet glowing in the void
> "This faucet is printed in three pieces. Not for strength. Not to make it
> easier to build. For one surface you'll never see — and one you will."

**B2 · The job (10–24 s)** — the harvested valve
> "Underneath is a real self-closing valve, harvested for about thirty dollars.
> The printed shell around it has one job: make the machine look finished — not
> garage-built. Which means the plastic has to be clean."

**B3 · The surface fight (24–46 s)** — 21 attempts, the quote
> "It started as a single piece. Then — start over. When a good print finally
> came off the bed, the verdict was: *beautiful everywhere except where the
> supports were.* On a 3D print, the down-facing surfaces are where the supports
> scar the plastic. So the fix wasn't a setting. It was geometry — split the
> part so every surface you'll actually see prints facing up."

**B4 · The split (46–58 s)** — one part → three
> "One piece became a few. It settled on three — split along the gooseneck, each
> joint a slip fit tuned by hand until it held."

**B5 · Button → screen (58–72 s)**
> "Meanwhile, choosing a flavor was going to be a button on the front. That got
> cut — and about two weeks later, a small touchscreen went on the spout
> instead."

**B6 · The payoff (72–86 s)** — the seam clamps the screen
> "And here's the part I didn't plan. The seam that existed only to hide the
> supports is exactly the clamp that holds the screen. Close the joint, and it
> captures the display. One seam. Two problems. No screws."

**B7 · Honest closer (86–95 s)**
> "It's not finished. There's a surface defect on the last print I haven't
> beaten, and nothing's printed since June. But the idea is right — make the
> seam do two jobs."

---

## Fact notes (for anyone editing on-screen text)
- Valve: Westbrass A2031-NL-62, self-closing spring-piston lever valve, ~$32
  (`hardware/ledger/bom.md`). Brand kept off-screen by choice; "harvested
  self-closing valve" is the on-screen phrasing.
- 21 PET-CF print attempts (`print-log.md`). The "beautiful everywhere…" line is
  Derek's, verbatim, at end of attempt 9 (`print-log.md:208`).
- Three-piece split; the two slip-fit joints along the gooseneck are the
  `split_*_socket_overlap_len` constants in `touch_flo_shell.py` (currently
  20 mm each). On-screen value reads from the same figure — reconfirm against
  the source if the geometry changes. (There was never a true 4-piece shell —
  don't say "four.")
- Display: Waveshare **ESP32-S3-Touch-LCD-1.47**, "no separate physical button"
  (`bom.md:18`). Button (KRAUS air switch) cut 2026-05-24; touchscreen mocked on
  the spout 2026-06-08 (~2 weeks later).
- Not finished: attempt-21 socket-mouth defect unresolved; last print activity
  2026-06-14. "Nothing printed since mid-June" holds as of writing.
