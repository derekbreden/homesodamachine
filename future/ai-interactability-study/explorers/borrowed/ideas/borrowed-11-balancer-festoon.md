# borrowed-11-balancer-festoon: carry the weight from above and give the umbilical a guided path

Origin: swarm. Maturity: sketch (no scene). Software has nothing to move here: it is the carrying and the cable.

## Picture it

A spring tool balancer, the retractable reel that lets a heavy tool hang weightless at any height, hangs from a ceiling or a bench-top frame and holds the gun. The umbilical does not dangle: it rides on a curtain-track or crane-style festoon, or in a CNC cable chain, so it is carried and cannot twist.

## The proposal

Two donor products for the two loads the study keeps returning to. Spring balancers ($17 to $21 on Prime for 1 to 5 kg ranges, sourcing/borrowed.md) take the gun's weight at any height; a track festoon or a printed drag chain is a guided path with a guaranteed minimum bend radius and, in a chain, no twist. The fibre needs at least 240 mm stored and 350 mm emitting, and forbids twisting [manual p. 20]; a chain built for a radius of 350 mm or more is a large chain. Any of borrowed-01, -02, -03, -07 could hang from a balancer instead of standing on the bench.

## What carries loads, establishes position, is free, restrained, driven

- Load path: gun to balancer cable to ceiling frame; umbilical to festoon trolleys to the track. Position: none; a balancer provides height freedom, not position. Free: the gun in height; restrained: none.

## Software: command, observe, manual

- Nothing to command. Could observe: the balancer cable's extension (a rotary encoder on the reel is a free height signal, unchecked). Manual: everything.

## What was tried to break it

1. **Range mismatch.** The listed balancers are rated 1.1 to 3.3, 3.3 to 6.6 lb or 3 to 5 kg; the gun's mass is unknown, so which range fits is unknown. The balancer sells at thin volume (29 and 34 ratings, "50+ bought in past month").
2. **A balancer is a single vertical line.** A gun hanging from one cable swings in pendulum; it needs a rigid arm or a second point. Not solved.
3. **The festoon.** Curtain-track carriers are cheap and common; whether one supports a 5 m armoured fibre at a 350 mm radius without kinking was not checked.

## Branches and combinations

- Carries weight for borrowed-02 or borrowed-03 (a lighter gantry or a lighter arm); the umbilical route applies to every arrangement.

## Unresolved problems and questions that need Derek

- The gun's weight; the umbilical's weight per metre; how it lies today when he welds.

## Assumptions

- Fibre bend radii 240 mm stored and 350 mm emitting [manual p. 20]. Balancer ratings from listings.

## Sourcing pointers

sourcing/borrowed.md: QWORK spring balancer 2-pack (Prime, $18.97, 29 ratings) and two other balancer listings.

## Scene

None (sketch).

## Wave 2

- **The fibre's direction is a design input.** `borrowed-16-taut-cone` maps which directions of the fibre's pull keep freedom-03's six lines taut (the shipped layout: worst direction 0.13 N, 58 % of directions below 1 N); a route chosen with a gallows or festoon can be checked against that map, and a layout searched for a route's cone.
- A balancer is also a bought preload: a constant downward pull of 5 to 15 N (Tigon 0.5 to 1.5 kg, $39.00) widens the cone to 4.75 N worst-direction slack pull, for a layout made for it.
- The couple a clamped, bent fibre applies at the exit (freedom-15) is not removed by a balancer: anchor the cable on the gimbal pivot with a slack service loop (`borrowed-15-sled-keel`).
