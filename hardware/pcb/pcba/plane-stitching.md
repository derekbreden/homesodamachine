# SMD pads on plane nets need an explicit via

A through-hole pin pierces every layer, so it commons to a plane (GND / 3V3 / 5V / V12)
at its barrel for free — the carrier's whole power scheme. An SMD pad sits on one layer.
A pad whose net is a plane on a *different* layer is not connected by the pour; it needs a
via.

tscircuit's DRC treats a pad on `net.GND` and the `net.GND` copperpour as connected by net
identity, so a missing stitch via **passes DRC with 0 errors** while the physical pad
floats. It does not flag this. Verify by hand: every SMD pad on a plane net has a via to
that plane's layer.

Pattern (see `pcba.tsx`, the C1/C2/R2/R4 GND legs) — a via-in-pad pcbtrace at the pad
centre:

    <pcbtrace route={[{ route_type: "via", x: PADX, y: PADY, from_layer: "top", to_layer: "bottom" }]} />

A pad already on its plane's layer (e.g. a top pad sitting on the top V12 island) connects
directly and needs none.
