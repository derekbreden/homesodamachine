# Elbow connector — reference fitting (stand-in)

The production fitting is the **John Guest PP0308E** 1/4" union elbow, black PP.

**Where one stands in the machine:** under the funnel's spout, as the
drain's disconnect. Its **+Z** leg takes the 1/4" LLDPE stub the funnel carries
(`hardware/reference/funnel-drain-stub/`) with the spout's exit face on its
collet, and its **+Y** leg hands `fluid-4` aft to V-B. Turning the fall inside
its own envelope is what the fitting is there for: it stands one leg under the
spout where a straight union hangs its whole length, which keeps the joint out of
the folded deck's own storey. `elbow_connector.py` beside this file states the
figures the machine spaces it by and holds them to the STEP;
[`manifold-layout/enclosure_assembly.py`](/hardware/manifold-layout/enclosure_assembly.py)
`build_drain_joint` places it, and `drain-over-deck` on the machine's scorecard
is what reads its foot against the pack beneath it.

`elbow-connector.step` is **McMaster 51055K136**, a 1/4" push-to-connect
drinking-water elbow — simply a STEP that happened to be available, used as a
close-but-not-exact geometric stand-in for layout, exactly as
[`../tee-connector/`](/hardware/reference/tee-connector/README.md) stands in for
the PP0208E tee. The design iterates toward the **installed characteristics of
the PP0308E**, not this file; swap in measured PP0308E geometry as parts come in
hand.

## Geometry (measured from the STEP)

The McMaster stand-in's figures — close to the PP0308E, not identical; reconcile
against a measured production elbow once one is in hand.

Two 1/4" ports whose axes meet at 90°. In the file's own frame the two leg axes
cross at the **origin** (the bend corner): one leg runs along **+Y**, the other
along **+Z**.

| Port | Opens | Collet face | Axis |
|---|---|---|---|
| Leg 1 | +Y | Y ≈ +19.56 | along Y (x = 0, z = 0) |
| Leg 2 | +Z | Z ≈ +19.56 | along Z (x = 0, y = 0) |

Both legs reach **19.56 mm** from the bend corner to the collet face. The outer
corner (the back of the bend) sits at **Y = Z = −7.37**, and the body is
**14.73 mm wide** across X (±7.37). Overall envelope **14.73 × 26.92 × 26.92 mm**.

Accepts 1/4" (6.35 mm) OD tube; the 1/4" bore radius is 3.175 mm, the collet
outer radius 7.366 mm. A tube pushed into either leg runs **15.75 mm** before it
bottoms on the socket's own stop, which is what the funnel's drain stub is cut to.
