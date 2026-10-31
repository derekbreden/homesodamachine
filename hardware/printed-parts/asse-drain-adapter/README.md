# ASSE 1022 vent elbow · TPU 85A

One printed elbow joins the downward-facing Multiplex 19-0897 vent barb to
white 4 mm OD / 2.5 mm ID LLDPE. Its tube socket points aft toward OVER on
the rear face. The short turn is inside the printed elbow; the LLDPE exits
straight and does not make that turn.

| Feature | Relaxed print dimension |
|---|---|
| Barb socket | Ø[6.10](BARB_BORE) mm × [8.8](BARB_DEPTH) mm |
| Tube socket | Ø[3.80](TUBE_BORE) mm × [14](TUBE_DEPTH) mm insertion |
| Socket reach from vent axis | 25.4 mm |
| Tube axis below vent tip | 4.55 mm |
| Printed drain turn | R4.05 mm, Ø3.8 mm passage |
| Tie lands | Two, 2.8 mm wide with 0.5 mm recesses |
| Solid CAD volume | [3.684](VOLUME) cm³ |

The installed barb mouth stops below the vent hex. The ASSE snap cap has a
clearance slot around this elbow and leaves both tie lands accessible.
The installed representation opens the sockets around the reference barb
and 4 mm tube, conserving nominal annular area. It is a routing envelope;
fit and sealing require a printed part.

## Print and assemble

The STL stands on a small exterior flat with both sockets rising at 45°.
Print in Siraya Tech Flex TPU 85A Clear using the
[accepted Siraya recipe](/future/pump-elbow-exploration/prints/2026-10-14-compact-single-siraya85a-overhang10-engineering-z000-mark1/README.md):
Mark1's right 0.6 mm nozzle, glued Engineering Plate, zero user Z trim,
225°C first layer, 215°C normal layers and 100% infill. Keep supports out of
the sealing bores. Keep hole and contour compensation at zero for the first fit.

1. Put loose four-inch, 2.54 mm wide nylon ties around the two recessed lands.
2. Seat the large socket over the vent barb, stopping below the vent hex.
3. Square-cut the white 4 mm tube, mark 14 mm and insert to the mark.
4. Snug each tie without flattening the tube or distorting the fitting;
   flush-cut the tails and leave the passage open.
5. Insert the other end into OVER to its receiving mark. The short rear
   link follows the socket's aft direction with a gentle lateral correction.

The Ø6.10 mm relaxed barb socket and Ø3.80 mm tube socket are explicit fit
parameters. The reference barb is an occupied envelope, not a measured fit
coupon. Socket seating, retention, water tightness and complete rising vent
capacity have no physical acceptance record. The
[faucet fault-drip record](../faucet/vent-qualification/README.md) defines the
unsealed outlet over the bowl.

Regenerate from the repository root:

```sh
tools/cad-venv/bin/python hardware/printed-parts/asse-drain-adapter/asse_drain_adapter.py
```

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/asse-drain-adapter/asse_drain_adapter.py`
