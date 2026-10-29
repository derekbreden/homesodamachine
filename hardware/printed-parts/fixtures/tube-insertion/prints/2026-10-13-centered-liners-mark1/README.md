# Centred plus-handle TPU inserts — Mark1 task 1336534713

Mark1 accepted both F inserts on October 13 at 1:59 pm CDT. Derek
authorized the launch with “Bed is clear and TPU is loaded on mark1 for
your new TPU inserts for that plus handle”. Fresh status reports RUNNING,
layer 0 of 155, without a printer error or HMS fault. The
[physical acceptance](../../physical-acceptance.json) records successful
insertion with these inserts and the centred plus handle. Derek reports
that the handle starts insertion well and the full tool makes the final
press very easy.

Each insert retains its Ø7.75 mm half-round channel and has 1 mm added to
its flat backing. Its 9 mm thickness stands 1 mm proud of the 8 mm jaw
pocket. The pair provides 2 mm total closing reserve in the centred plus
handle. Each prints upright with the tube axis vertical, using a solid
9×20 mm footprint and 28 mm height. The two models have a 2 mm gap.

- [Exact launched native slice](https://github.com/derekbreden/homesodamachine/blob/33d50d2ecd2a0fb6b518483a44c8031e3a0c1617/hardware/printed-parts/fixtures/tube-insertion/prints/2026-10-13-centered-liners-mark1/tube-insertion-centered-liners-tpu85a-right06-z018-mark1.gcode.3mf)
- [Exact G-code for Studio preview](https://github.com/derekbreden/homesodamachine/blob/33d50d2ecd2a0fb6b518483a44c8031e3a0c1617/hardware/printed-parts/fixtures/tube-insertion/prints/2026-10-13-centered-liners-mark1/tube-insertion-centered-liners-tpu85a-right06-z018-mark1.gcode)
- [Editable native project](tube-insertion-centered-liners-tpu85a-right06-z018-mark1.3mf)
- [Project settings and source meshes](tube-insertion-centered-liners-tpu85a-right06-z018-mark1.print.json)
- [Native slice review and checksums](tube-insertion-centered-liners-tpu85a-right06-z018-mark1.readiness.json)
- [Preflight printer observations](preflight.json)
- [Launch receipt and startup spacing](launch.json)
- [Fresh startup observation](startup.json)

The slice uses black TPU 85A through Mark1's right fixed 0.6 mm nozzle and
external spool 255, textured PEI, 225 °C nozzle, 35 °C bed, 2.2 mm³/s maximum
flow, two Arachne walls, 100% zig-zag infill, a 0.30 mm first layer and
0.18 mm normal layers. It generates no supports. Standard +0.18 mm user
Z trim emits `G29.1 Z0.16` after the reset to zero. The saved restart amount
is retained. The estimate is 1 hour 18 minutes and 10.7 g using the saved
material density. The complete emitted bead footprint has at least
142.22 mm of usable-bed edge clearance.

Timelapse and bed leveling are On; flow dynamic calibration and nozzle
offset calibration are Auto. Mark2 task 1335906696 was accepted at
10:19 am CDT, 3 hours 40 minutes 29 seconds before this acceptance.
The receipt records both UTC observations and the required 180-second
minimum startup separation.

The matching [PET-GF jaw job](../2026-10-13-centered-grip-mark1/README.md)
has a software completion report at 63/63 layers. The separate physical
acceptance supplies the functional grip and insertion result for both jobs.
