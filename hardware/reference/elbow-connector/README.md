# Elbow connector — reference fitting (stand-in)

`elbow-connector.step` is **McMaster 51055K136**, a 1/4" push-to-connect
drinking-water elbow: a vendor STEP close to, but not the same as, the
**John Guest PP0308E** 1/4" union elbow, black PP. It is a reference only;
nothing in the machine places it.

The machine's PP0308E is the scanned
[PP0308E reference](/hardware/reference/jg-pp0308e-elbow/README.md).
[`manifold-layout/enclosure_assembly.py`](/hardware/manifold-layout/enclosure_assembly.py)
`build_drain_joint` places it under the funnel frame's drain hole as the drain's
disconnect. The funnel's drain stub takes its insertion, `UNION_INSERTION` =
15.7 mm, from John Guest's data sheet for the 1/4" PP range
([`funnel_drain_stub.py`](/hardware/reference/funnel-drain-stub/funnel_drain_stub.py)).

## Geometry (measured from the STEP)

The McMaster part's figures, not the PP0308E's.

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
bottoms on the socket's own stop.
