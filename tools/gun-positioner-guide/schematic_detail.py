"""Keep the divider's capacitor branch outside the Pico label box."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import art


def voltage_divider():
    s=art.SVG(2000,830)
    s.box(80,270,350,160,"Switched 24 V",fill=art.STEEL,size=40)
    s.box(560,290,250,120,"100 kΩ",fill=art.PALE,size=40)
    s.box(1260,270,600,160,"Pico GP27 / ADC1",fill=art.PALE,size=42)
    s.box(850,525,240,100,"10 kΩ",fill=art.PALE,size=40)
    s.box(1290,525,400,100,"100 nF",fill=art.PALE,size=40)
    s.line([(430,350),(560,350)],color=art.CORAL)
    s.line([(810,350),(1260,350)],color=art.BLUE)
    s.dot(970,350)
    s.dot(1160,350)
    s.line([(970,350),(970,525)],color=art.INK)
    s.line([(1160,350),(1160,470),(1490,470),(1490,525)],color=art.BLUE)
    s.line([(970,625),(970,690),(1490,690),(1490,625)],color=art.INK)
    s.text("GND",1110,750,size=40)
    s.text("24 V at the motor bus produces 2.18 V at GP27.",1000,140,
           anchor="middle",size=43,weight=700)
    s.text("Meter the divider before connecting GP27. Keep the ADC node below 3.3 V.",1000,210,
           anchor="middle",size=34,color=art.MUTED)
    s.save("voltage-divider")


if __name__=='__main__':
    path=art.ART/'schematic-receipt.json'
    receipt=json.loads(path.read_text())
    for p,h in receipt['input_sha256'].items():
        if hashlib.sha256((art.ROOT/p).read_bytes()).hexdigest()!=h:
            raise RuntimeError(f'Stale schematic source: {p}')
    voltage_divider()
    receipt['input_sha256'].update(art.hashes([Path(__file__).resolve()]))
    receipt['svg_sha256']['voltage-divider.svg']=hashlib.sha256((art.ART/'voltage-divider.svg').read_bytes()).hexdigest()
    path.write_text(json.dumps(receipt,indent=2)+'\n')
