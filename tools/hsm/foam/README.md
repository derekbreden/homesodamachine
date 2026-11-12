# hsm-foam

`hsm-foam` predicts where a pour of expanding foam ends up in a cavity, and how it got there.
[homesodamachine.com/foam](https://homesodamachine.com/foam) draws its predictions.

It takes solids, the spots the liquid is poured at with their grams and timing, and what it
believes about the foam. It gives back, for every cell of the cavity, the time foam arrived
there, or that it never did.

## What it does

The cavity is cut into cubic cells. Each cell is empty, part full or full.

- **Liquid.** The pour lands on the floor under its spot and spreads under its own weight
  until the foam's clock says it starts to rise.
- **Rise.** Every bit of foam grows on one curve, from the liquid's volume to its free-rise
  volume. Foam near a wall grows less: the wall takes its heat, and it stays denser.
- **Flow.** Growing foam has to go somewhere, and it goes where the cavity resists least.
  A cell lets foam through as the square of its distance to the nearest wall, over the
  foam's viscosity, which rises as the foam cures and as it fills with gas. That one rule
  gives a slot, a film on a floor and a duct their textbook flow rates, so a narrow gap
  holds foam back the way it does in lubrication theory.
- **Fronts.** A front moves on when the cell behind it is full. Once the liquid has become
  foam a front does not retreat.
- **Air.** Air leaves through any way out that is still mostly air. Air that foam has closed
  in on every side is a sealed pocket: it obeys Boyle's law, so the foam compresses it a
  little and no more. A scrap of air that an open front has just closed around is taken to
  have gone ahead of the front.

Each step solves one set of equations for the head in every cell that holds foam or is about
to: full cells pass on what they take in, part-full cells store it, and each sealed pocket is
one more unknown.

## What it leaves out

- Heat. The foam's own warming, the room's temperature and the batch's size change how far
  and how fast it rises; here that is one curve.
- The pour's path. Liquid arrives on the floor; a stream that wets a wall on the way down
  leaves foam there that the model does not know about.
- Surface tension and the foam's yield stress. A thin gap wicks liquid; a stiff foam stops
  in a gap under a pressure the model would let it creep through.
- Inertia, apart from a cap on how fast liquid moves.
- The cavity's walls giving way.

## What it believes, and what corrects it

The numbers it starts from are in [`foam_fill.rs`](../../../hardware/print-tests/foam-fill/foam_fill.rs),
and the page shows them. They come from the maker's page and the usual run of two-pound
pour foams. The [foam-fill test](../../../hardware/print-tests/foam-fill/README.md) is built
so that each reading corrects one of them:

| Belief | Corrected by |
| --- | --- |
| How much the foam grows, and when it starts and stops | The column's height over time |
| How much growth a wall costs | The foam's volume in the comb's narrow cells against the column's, and each cell's weight once sawn apart |
| How fast the foam thickens | How long the comb's cells keep level with the well before they fall behind |
| How strongly a narrow gap holds foam back | The cells' final heights against their gaps |
| How fast the liquid spreads before it rises | The liquid's run along the comb's floor duct and across the tray's floor |
| What seals a pocket of air, and what a vent does | The comb's rooms |
| Whether foam fills a deep cell from above | The comb's blind cells |
| How far foam runs sideways under a ceiling instead of leaving by a port | The tray |

## Running it

`foam-fill predict` runs it on the test pieces and writes the page's files. A new cavity
needs its solids, an up axis, its pours and the boxes foam can be in, as a `Setup` for
[`sim::run`](src/sim.rs); [`read`](src/read.rs) turns the result into heights, reaches and
fills in a box, and packs it for the page.

The cells are cubes of a size the caller picks. Walls that lie on the cells' faces are
exact; the test pieces are drawn that way.
