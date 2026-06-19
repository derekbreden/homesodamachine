# I've Never Desoldered Anything

In-flight production brief. The narration is captured (live DJI Mic during the
shoot); the GoPro footage is syncing from Quik cloud. This is the editorial
plan the [pipeline](workflow.md) fills in once the synced video lands. First
**electronics** video on the channel — the "I've Never X" lineage
([*I've Never Welded*](concepts.md), [*I've Never Tapped*](concepts.md)) crosses
off the welding bench for the first time.

The hero: a total beginner picks up a vacuum desoldering gun, touches it to a
through-hole joint, and the solder just vanishes — and the genuine disbelief
("absolutely zero skill level," "that is amazing") is the whole appeal. The
soda machine stays backdrop: the board is a part the build needs. Never the
pitch — see [`concepts.md`](concepts.md) (every Tier-2 piece keeps the machine
present, never selling).

## The narration

Live narration, ~3 min. Working draft at
`~/Developer/soda-edit/2026-06-19-desolder/transcript-draft.txt`; the
word-timestamp `medium.en` pass (for caption truncation, [workflow](workflow.md)
step 11) lives next to it as `narration.json`. The beats, in order:

- Brand-new desoldering gun, never used a thing like this — this is attempt #2,
  recorded to show how easy it is. *"freaking amazing… absolutely zero skill level."*
- Turn it on, touch the tip, the little vacuum noise — *"and that's it. It
  desoldered that entire joint just now, and sucked a little solder out of that hole."*
- *"You can just do a whole bunch of them in a row."*
- *"Okay, I missed two, but damn, that's good."*
- *"So much easier than the — what do you call this — solder wick stuff."*
- *"They might have actually been fine to begin with, just a friction fit… but
  look how clean. That is amazing."*

## Title

Lead with the channel's franchise hook; the broad **desoldering** node rides in
the hook verb *and* the specifics, brand stays out of the title per
[`distribution.md`](distribution.md) (the documented ~365× Browse-reach gap):

> **I've Never Desoldered Anything — through-hole desoldering with a vacuum gun**

The one contestable call is word order. The franchise hook ("I've Never X") wins
subscriber legibility and doubles as the on-screen title card, but it puts the
first-person phrase in the lead slot; a **verb-forward** title leads the Browse
node harder. Both honest, both name "desoldering." Decide at publish:

- *It just comes right out — desoldering through-hole joints for the first time*
- *Way easier than solder wick — desoldering through-hole joints with a vacuum gun*
- *Zero skill, clean joints — desoldering through-hole parts with a vacuum gun*

**Node choice (the title-rule work):** candidate nodes are soldering, electronics
repair, PCB repair, through-hole rework, desoldering, solder wick. Reject
*soldering* / *electronics repair* — nothing is soldered, diagnosed, or repaired
on screen; anchoring there mismatches the thumbnail and tanks retention. Reject
*solder wick* — it's the thing being beaten, not done. The footage literally
shows a vacuum gun clearing through-hole joints repeatedly, so the largest node
the footage honestly supports is **desoldering**, with *through-hole* as
specifics for adjacent rework searchers.

## Thumbnail

Top-of-frame text per [`/marketing/thumbnail/make.sh`](/marketing/thumbnail/make.sh).
Source frame: the clean cleared hole / a part lifted free.

- **A — "It just sucks it out"** (visceral, topic-evocative; watch the
  "this sucks = bad" misread — the clean-board image disambiguates)
- **B — "Right out of there"** (plainer, safer)

## Cold open — the payoff, before the title

Open mid-action on the tightest, best-lit POV shot of the gun tip touching a
single joint: the vacuum noise, then the solder disappearing from the hole.
Lay it under *"look at this, look at this thing, it just comes right out of
there"* and land on *"that is amazing."* **Withhold** every honesty beat (no
"I missed two," no setup) so the open reads as a promise, not a fumble. Hold the
last frame on the cleared board and author it as a `type:"freeze"` cut
([`cut.py`](cut.py) freeze format); the **"I've Never Desoldered Anything"**
title card lands on that freeze, then hard-cut to the setup line. That
freeze-into-title seam is the pre/post-title boundary.

This is the channel's first **cold-open-on-the-payoff + freeze-into-title**
seam — the format advance over the last video, per
[`principles.md`](principles.md#the-pipeline-is-the-floor).

> **Hook depends entirely on this shot reading.** Solder vanishing into a hole is
> small and fast; if the cold-open frame isn't macro-tight and well-lit, the
> "that is amazing" reaction lands flat. If the take isn't tight enough,
> substitute the cleanest single-joint clear in the footage — and frame it
> *differently* from the closing "that is amazing" shot so the bookend reads
> intentional, not like repeated footage.

## Cut-list section skeleton

Ordered sections to fill with timestamps after the visual-analysis pass
([workflow](workflow.md) step 10). `section` / `tool` are
[`cut.py`](cut.py) overlay fields. Skeleton JSON staged at
`~/Developer/soda-edit/2026-06-19-desolder/cutlist-skeleton.json`.

1. **Cold open (payoff)** — clean solder-suck + freeze on cleared board → title
   card. No `section` overlay, no captions over the card. ~4–6 s.
2. **I've never done this** — `section`: *"I've never desoldered anything."* The
   honest premise up front. Novice voice, **not** instructional.
3. **Why the board's on the bench** — exactly one line: rework for the soda
   machine build. No specific PCB/component named (see open questions). One light
   touch; past a line it becomes a pitch.
4. **The move, shown slow** — `section`: *"Touch, suck, done."* `tool`
   (upper-right, ~3.5 s): *"Hakko FR-301D desoldering gun"* — brand lives **here**,
   never the title. POV hands.
5. **The run** — a row of joints, beginner pace. Keep the *"zero skill level"*
   line — it is the credibility. Sparse narration, music bed.
6. **Okay, I missed two** — *do not cut.* The miss is the credibility play. No
   overlay; let it stand.
7. **Beats solder wick** — one in-narration line. Names the node out loud without
   drifting into the well-worn wick-vs-vacuum meme. Optional `section`:
   *"vs. solder wick."*
8. **Cleanup + last reveal** — clean the last two, *"might've been fine to begin
   with, just a friction fit… but look how clean"* → *"that is amazing."* Close on
   the part freed from the board. Quiet button, no hard CTA; one optional line
   that the part goes back toward the build.

## Description (draft)

> First time I've ever picked up a desoldering gun, and the solder just vanishes
> out of the hole on the first real try — total beginner, absolutely zero skill
> level, and it works. Touch the tip, the little vacuum noise, the joint clears;
> run a whole row of through-hole joints, miss two, clean those up too. The board
> is a part for a home soda machine I'm building — this video is about the
> desoldering, not the machine.
>
> Desoldering gun: Hakko FR-301D
> Camera: GoPro HERO13 (cap mount, POV)
> Mic: DJI Mic Mini

## Where it fits

The "I've Never X" lineage ([`series.md`](series.md)), now in electronics — but
**Tier-2-spirit**, not Tier-1-trust. The welding/tapping videos build buyer
trust in the founder doing real fabrication; this one is audience-building,
anchored to the desoldering Browse node (a large maker/electronics-repair pool,
deliberately **low** buyer overlap — acceptable for Tier 2; don't expect product
conversion from this audience). It closes none of the six capability arcs — it's
connective bench work that keeps the "object accretes" spine visible.

## Open questions — confirm against the footage before final cut

- **What board/part is being desoldered, and why.** The transcript never says.
  Keep the soda-machine tie at *"rework for the build" / "a part the machine
  needs"* — do **not** name a specific PCB or component on screen or in narration
  until confirmed (over-specifying invents a fact).
- **Cold-open shot is macro-tight and legible** — the whole hook depends on it.
  Identify the cleanest single-joint clear as the cut-#1 candidate.
- **A clean frame of the cleared board** (or part lifted free) exists to author
  the `type:"freeze"` title-card cut.
- **Exact Hakko tip** (bore size, chisel vs. conical) before burning it into a
  `tool` overlay — currently an assumption, leave it off if unconfirmed.
- **Closing "that is amazing" framing differs** from the cold-open shot so the
  bookend reads intentional.
- **Vacuum "pop" foley** — usable GoPro ambient audio of the suck, or pull an SFX
  from [`sfx/`](sfx/) for the cold open.

## Related

- [`workflow.md`](workflow.md) — the capture-to-publish pipeline this feeds.
- [`distribution.md`](distribution.md) — the broad-topic title rule the title
  section applies.
- [`principles.md`](principles.md), [`concepts.md`](concepts.md),
  [`series.md`](series.md) — voice, tier placement, narrative spine.
