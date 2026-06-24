"""Reference solid for the DS3231 RTC module (bom: B09LLMYBM1 = the DORHEA
DS3231 + AT24C32 board), 1x on the controller tray — the I2C real-time clock at
0x68 (the onboard AT24C32 EEPROM sits at 0x57 on the same bus).

Geometry calipered from the physical board. Frame follows the module_tray
convention: X = length = the 38.5 mm long axis, Y = width = the 21.3 mm short
axis, Z up from the PCB underside; origin at the footprint centre, Z = 0 the
standoff plane. (length = X, width = Y is what controller_tray / module_tray
consume — keep it that way so the floor outline and bosses align.)

  Footprint     38.5 (X, length) x 21.3 (Y, width)
  Mount holes   3x dia 2.4 (M2): (-10.75, +/-8.65) flanking the 6-pin end and
                (15.05, 8.65) at the 4-pin end -- the 4th corner is left open
                for the coin-cell holder
  6-pin header  2.54mm along Y at X = -17.25 (one short end), span 12.7:
                32K SQW SCL SDA VCC GND  (Y = +6.35 down to -6.35)
  4-pin header  2.54mm along Y at X = +17.25 (other short end), span 7.62:
                SCL SDA VCC GND  (Y = +3.81 down to -3.81) -- the clean I2C tap

The two headers are the same I2C bus (the 4-pin is the VCC/GND/SDA/SCL subset);
the carrier taps one of them. SQW/32K (square-wave / 32 kHz outputs) are unused.
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
from _cadq_export import export_step

name = "ds3231"
length = 38.5          # X (long axis)
width = 21.3           # Y (short axis)
pcb_t = 1.6
envelope_z = 13.0      # 2.54 mm pin headers (tallest); coin-cell holder shorter
pin_drop = 3.0
hole_dia = 2.4         # M2 clearance
holes = [(-10.75, -8.65), (-10.75, 8.65), (15.05, 8.65)]   # 4th corner open for the cell
headers = [(-17.25, 12.7), (17.25, 7.62)]   # (X, Y-span): 6-pin end, 4-pin end


def build():
    pcb = cq.Workplane("XY").box(length, width, pcb_t, centered=(True, True, False))
    # DS3231 + AT24C32 + CR2032 holder envelope — the coin-cell holder dominates
    # the top face; modelled as one block over the centre (not individually
    # calipered), clear of the two end headers.
    body = (
        cq.Workplane("XY").box(24.0, 18.0, 5.0, centered=(True, True, False))
        .translate((0.0, 0.0, pcb_t))
    )
    # Two 2.54 mm headers, one at each short end, running along the short (Y) axis.
    hdr = pins = None
    for hx, span in headers:
        strip = (
            cq.Workplane("XY").box(3.0, span, envelope_z - pcb_t, centered=(True, True, False))
            .translate((hx, 0.0, pcb_t))
        )
        drop = (
            cq.Workplane("XY").box(3.0, span, pin_drop, centered=(True, True, False))
            .translate((hx, 0.0, -pin_drop))
        )
        hdr = strip if hdr is None else hdr.union(strip)
        pins = drop if pins is None else pins.union(drop)
    part = pcb.union(body).union(hdr).union(pins)
    for hx, hy in holes:
        part = part.cut(
            cq.Workplane("XY").workplane(offset=-pin_drop).center(hx, hy)
            .circle(hole_dia / 2.0).extrude(pin_drop + pcb_t)
        )
    return part


def main():
    export_step(build(), str(_here.parent / "ds3231-rtc.step"))
    print("-> ds3231-rtc.step")


if __name__ == "__main__":
    main()
