# c5 — Ends as stock: the machine makes XH-ended ribbon, not looms

A process and scheduling change: the machine terminates ribbon straight off
the spool, in runs of one type, and the unit build cuts ends to length. It
hosts any termination arrangement that can run a spool unattended. Sketch:
[`../sketches/c5-ends-as-stock.svg`](../sketches/c5-ends-as-stock.svg)
(schematic). Numbers: [`../calc/ctq.out.txt`](../calc/ctq.out.txt) §1, §9;
[`../calc/wave2.out.txt`](../calc/wave2.out.txt) §7 [w2 §n];
[`../calc/wave3.out.txt`](../calc/wave3.out.txt) §6 [w3b §6].

## Picture it

**Where things start.** A 4P spool hangs on a rack behind the machine. Its
leading end is threaded through a belt feed into the web clamp. The 5P and
3P spools wait beside it for their runs.

**One cycle.**
1. The feed advances the leading end to the tip stop.
2. The machine terminates it: split, strip, place, crimp, insert. It can use
   any termination arrangement in this study that runs a whole spool
   unattended (hosts below):
   - [`c1c`](c1c-crimp-in-the-row.md)'s half-rows crimped in the row;
   - force-and-form's [f2c](../../force-and-form/ideas/f2c-applicator-station-makes-t4-ends.md),
     an applicator in a slow crank press delivering into 5.0 mm output pallets;
   - borrowed-machines' [b8](../../borrowed-machines/ideas/b8-spool-fed-borrowed-line.md),
     a spool-fed line whose feed retraction rips the webs;
   - into-the-housing's [k7](../../into-the-housing/ideas/k7-pre-formed-contacts-crimped-in-the-cavity.md)
     with strip pre-formed in line (its S1c branch), a T4 run's one visit;
   - hand-tool-as-press's [a3](../../hand-tool-as-press/ideas/a3-tool-travels-to-ribbon.md)
     (the tool travels to the ribbon) or [a2d](../../hand-tool-as-press/ideas/a2d-batch-then-gang-push.md)
     (batch, then gang push): with one ribbon, one housing size and no
     crossings, a3's on-edge fixture and a2d's squaring comb need no
     configurability, and the unspooled remainder on a slip ring is their
     far-end electrode array before any loom exists;
   - a sibling's single-conductor indexer.
3. The housing is pushed onto the **real-wafer tester**: order, opens,
   adjacent shorts. The far end is the rest of the spool; with its inner end
   on a slip ring (procedure-is-the-machine's
   [p3](../../procedure-is-the-machine/ideas/p3-terminate-at-the-spool-cut-last.md),
   Adafruit 736, $14.95), the test also names each conductor.
4. The clamp opens. The feed pushes out a **standard length**, measured by an
   encoder wheel on the ribbon, and a guillotine cuts.
   - The cut is also the next end's flush cut.
   - The ribbon-as-pallet explorer's spool-as-magazine
     ([`../../ribbon-as-pallet/ideas/a4-spool-as-magazine.md`](../../ribbon-as-pallet/ideas/a4-spool-as-magazine.md))
     is this same feed and cut, used per loom.
5. The finished end falls down a chute into a bin by its type. A label
   printer or a printed tag marks the housing with the type.

**What locates, drives and carries force** is the hosted arrangement's. What
this arrangement adds is one reference kept for a whole run: the spool's
leading end, squared by the previous cut, fed to the same tip stop, in the
same web clamp, with the same housing size.

**What the machine is asked to make** [calc §1]:

| Type | Ribbons into housing | Looms | Ends per unit | Crimps per unit | Program ends (60 units) |
|---|---|---|---:|---:|---:|
| **T4** | 4P into XHP-4 | J3, J5, J9, J11, J13 | 5 | 20 (38%) | 300 |
| T9 | 5P + 4P into XHP-9 | J1 | 1 | 9 | 60 |
| T7s | 4P + 3P into XHP-7 | J4 | 1 | 7 | 60 |
| T7r | 5P + 3P (one trimmed) into XHP-7 | J7 | 1 | 7 | 60 |
| T6 | 3P + 3P, cavity 3 empty, into XHP-6 | J2 | 1 | 5 | 60 |
| T5 | 5P into XHP-5 | J6 | 1 | 5 | 60 |

**T4 is half the housings and 38% of the crimps**, and it is the simplest
end:
- one ribbon, four conductors;
- no pair;
- no skipped cavity;
- no crossing.

**Standard lengths for T4.** Two lengths, 400 and 700 mm, including a 50 mm
service loop [assumption]:
- J5 and J13 come from the 400;
- J3, J9 and J11 from the 700;
- J3's length is unmeasured in the repo and taken as 450 mm [assumption].

The offcut is ~$1.21 of 4P ribbon per unit [calc §9; ribbon price repo
bom.md §11]. One 15.2 m spool makes 21 long or 38 short T4 ends in a single
unattended run.

**Supplying a whole run.** An unattended run needs every contact and
housing for the run loaded with the spool, or the run is attended at every end
[terminal-supply exchange, c5]. For T4 [w2 §7]:

| Run | Ends | Contacts | XHP-4 housings | Housing stick |
|---|---:|---:|---:|---|
| Long (700 mm ends) | 21 | 84 | 21 | 120 mm stacked by depth, 163 mm by height |
| Short (400 mm ends) | 38 | 152 | 38 | 217–294 mm |

- **Contacts from strip.** A long run's 84 contacts fit one 100-piece strip
  with 16 spare, so **the spool change and the strip change fall on the same
  visit**. A short run needs 1.5 strips: a 500-piece strip, a reel, or two
  strips spliced. A strip-fed pallet loader (terminal-supply's C1: pin the
  strip, shear the tab 0.2–0.3 mm behind the contact, push the contact down a
  window into its pocket) feeds the pallets at 10–15 s a contact, overlapped
  with crimping.
- **Contacts loose.** Kit contacts reach a run only through something that
  orients 84–152 of them: terminal-supply's hanging rail or post, a pocket
  plate, or [c6](c6-pre-form-the-contact.md)'s pre-former filling
  four-contact sticks (21 sticks for a long run, 0.49–0.57 m of contacts
  nose to tail).
- **Housings** from a spring-fed stick with an escapement into the housing
  nest. The CQRobot kits come mixed by size; a run's 21–38 XHP-4 is likely
  more than one kit's 4-ways [assumption]. XHP-4 is $0.049–0.058 from LCSC or
  Digi-Key in quantity [xh-facts §6].
- With both, one visit per T4 spool: load a 4P spool, a 100-piece strip and a
  stick of 21 housings; come back to 21 tested ends in a bin, ~3–4 h later
  at 8–12 min an end [terminal-supply exchange calc §9, estimate].

**How it knows it worked.** Every end is tested on the wafer, and can be
pull-tested, **before any loom exists**. A bad end is scrapped: at most a
700 mm offcut of 4P (~$1.13) and a kit housing with its contacts (~$0.17)
[repo bom.md]. The repo treats a loom with one failed termination as
"suspect end-to-end" [repo cable-assemblies.md]. Stock ends move that
judgement to before the far end has been made.

**What the person does.**
- Changes spools between runs, with the strip (or sticks) and the housing
  stick for that run.
- Empties the bins.
- At build time, picks the type, cuts to length, peels branches, makes the
  far end.
- For T7s and T7r, reads the tag. They share the XHP-7 housing and a swap is
  a wiring fault [repo cable-assemblies.md], so the tag is applied when the
  end is made.

**Steps covered:** the whole XH end, through the hosted arrangement; the test
before the loom exists; cut to length. **Hands back:** spool, strip (or
sticks) and housing-stick changes per run; emptying bins; at build, cutting to
length, peeling branches and the far end; the pair types if they stay by
hand.

## What this changes for any machine

- **A first machine can be built for T4 alone.**
  - It needs no configurability: four conductors, two half-rows of two in
    c1's terms, a 0.8 mm spread, one housing size.
  - It covers 1,200 of the program's ~3,180 crimps (20 per unit × 60) and
    half of every unit's housings.
  - The pairs (T9, T7s, T7r, T6) stay by hand until the machine grows. Their
    crossings and skips are the hardest configurations, and J4's crossing is
    the worst [calc §2].
- **One visit per spool.** A long T4 run's contacts fit one 100-piece strip,
  so spool, strip and housing stick are loaded together.
- **The machine runs when the printers run, not when a unit is being
  built.** Days of print time per unit [Derek] give it all the time it
  wants. A bin of ten units' ends decouples the two completely.
- **One configuration per run.** A spool of 4P becomes ~21–38 T4 ends with
  no changeover. The machine can be tuned for one thing at a time.
- **With [c7](c7-straight-across.md)'s one ribbon, one housing, every end is
  a single ribbon straight into its own housing:** 4P into XHP-4 becomes 7 ends
  and 28 crimps per unit (53 %), and the rest are 5P into XHP-5, 3P into XHP-3
  and 3P into XHP-2 with one conductor trimmed [w3b §6]. Every type is then a
  spool run of its own, and no run needs two spools fed edge to edge.
- **The floppy long tail never enters the machine as a free end.** The spool
  holds it until the cut, and after the cut it drops away down a chute.
  Moving a floppy cable is where the Sogang ribbon inserter lost most of its
  failures [prior-art, Start here].

## Problems worked through

1. **Offcuts waste ribbon.** About $1.21 per unit for T4 [calc §9], small
   beside a unit's wiring. Three standard lengths instead of two would cut it
   further.
2. **The far end is still by hand, and it is most of a loom's labour.** The far ends are Fastons, ferrules, 110 IDC and screw terminals,
   varied and loom-specific [repo cable-assemblies.md]. This arrangement
   automates only the XH end. The far end stays with the person. It is also
   where branches peel, which needs the loom's own length anyway.
3. **Pairs need two spools at once.**
   - T9, T7s, T7r and T6 need two ribbons fed edge to edge. Two spools and a
     wider belt feed do that.
   - Or keep pairs off the machine: four ends per unit (28 crimps) by hand.
   - Or remove pairs from the board ([c7](c7-straight-across.md) (b)).
4. **Stock ends need storing.** A bin of 50 T4 ends is a coil of ribbon,
   not a problem [assumption].

## Contribution

- It makes the machine's scope a choice. Automate T4 first: 1,200 program
  crimps, the simplest configuration, half the housings.
- It moves termination off the unit build's critical path, which suits a
  machine that is slow.
- Test-before-loom makes scrap cheap and rework unnecessary.
- Covers **the XH end completely** (through whatever termination arrangement
  it hosts) plus **cut to length**. It hands back the far end, branch
  peeling and the pair types if they stay manual.

## Major unresolved problems

- It relies on some termination arrangement working unattended for a whole
  spool. The hosts named above (c1c, force-and-form f2c, borrowed-machines b8)
  are each unbuilt, with their own open problems.
- **Supply for a run**: a strip-fed pallet loader and a housing stick with an
  escapement, or oriented loose contacts. Neither is built.
- **J3's length** is unmeasured in the repo [repo _run_lengths.py: J3 not
  measured]. It may need its own stock length.
- **Pair ends from two spools** need a feed that keeps two ribbons edge to
  edge through the clamp. Not designed here; procedure-is-the-machine's p3b
  merges lanes AMS-style for it. c7 (b) removes pairs from the board.

## What rests on assumptions

- Service-loop allowance and J3 length [assumption].
- That silicone ribbon feeds reliably through a belt feed and encoder wheel
  without slip [assumption; the ribbon-as-pallet explorer cites belt feed from
  the ribbon-machine makers, prior-art §1].
