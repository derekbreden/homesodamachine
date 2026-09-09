# John Guest PP0208E — 1/4" union tee, black polypropylene

The tee in the install kit — the **black tee** the customer pushes into an existing 1/4" line
under the sink (`hardware/ledger/bom.md` §3, install-kit tee, scenario A). The same SKU is the
water split on the ASSE 1022's outlet (`../water-split/`) and the six manifold junctions the
topology calls Tees.

Three identical ports: a straight **run** of two in line and a **branch** off the middle at a
right angle. Every one takes 1/4" OD LLDPE by push — no ferrule, no nut, no tool. Black PP body
and collet, EPDM O-ring, 301 stainless collet teeth, NSF 51 + 61, 10 bar at 20 °C.

The other tee in the kit is the John Guest ASVPP1LF angle stop adapter valve — white body, brass
run threads, a blue lever, and one 1/4" push port. Beside it this one is small, all black, and
identical on all three ends.

## Geometry

John Guest's own figures, off the **Polypropylene Equal Tee data sheet Pp4608_01/23**, 1/4" row
— the row `PP0208W`, `PP0208W-B` and `PP0208E` share.

| | | |
|---|---|---|
| A | 6.35 mm (+0.03 / −0.10) | tube OD |
| B | 39.0 mm | collet face to collet face along the run |
| C | 19.5 mm | body centre to any one of the three collet faces |
| D | 15.7 mm | collet face to the internal tube stop |
| E | Ø16.3 mm | the collar on each arm — the fitting's widest section |
| F | Ø4.3 mm | through bore |
| G | 27.7 mm | branch collet face to the far side of the run body |

**B, C and G are dimensioned with the collets in the release position**, pressed home against
the collar, and that is the state the solid here is cut in. At rest each collet stands 1.65 mm
further out and the run measures 42.5 mm across — calipered on the fitting in hand, with the
rest of the bench reading, at [`../tee-connector/README.md`](../tee-connector/README.md).

Not on the data sheet: the steps along each arm. Outward from the hub every arm carries a
Ø10.6 barrel to 8.2, then the Ø16.3 collar to 16.3, then the release collet — Ø9.7 outside,
Ø6.70 bore — standing the last 3.2 mm out to the port face. Those are the tree's one drawing of
a John Guest 1/4" push-fit port, shared with the Quick Start's plumbing scenes
([`../../quickstart/plumbing/`](../../quickstart/plumbing/)), so the collet the customer pushes
a tube into is the same collet wherever this repository draws one.

Frame: the **run on Z**, its two collet faces at ±19.5; the **branch on +Y**, its face at the
same 19.5. Origin at the body centre. The same frame [`../tee-connector/`](../tee-connector/)
states, so a turn written for one tee turns the other.

Ports: `run(+1)`, `run(-1)` and `branch()`, each `(position, outward axis)`, the position being
the collet's own outer face.

## Not the tee-connector

[`../tee-connector/`](../tee-connector/) is McMaster 51175K143, a **stand-in** its own README
says is close but not this part, kept because the manifold's layout and the pump cartridge's
carrier are built on its solid and on the PP0208E bench measurements filed beside it. This
directory is the PP0208E itself, drawn from the manufacturer's data sheet, and it is what a
picture of the customer's own fitting is drawn from.

Where the two disagree: the stand-in's run spans 40.14 mm against this tee's published 39.0 in
the release position, and its tube-bottom station is the bench's 10.0 mm against the data
sheet's 15.7 mm insertion depth. The bench figure is what the cartridge's tube lengths are cut
to.

## Regenerate

```
tools/cad-venv/bin/python hardware/reference/jg-pp0208e-tee/jg_pp0208e_tee.py
```
