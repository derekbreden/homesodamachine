"""Controller PCB — code-defined netlist (SKiDL).

The circuit in Python — the electrical analog of the CadQuery mechanical scripts.
Define parts and nets here; generate a KiCad netlist for import into Pcbnew (board
layout). Connections follow netlist.md; parts + footprints follow bom-board.md.

Run with the project's PCB venv (KiCad must be installed for its symbol libraries):

    tools/pcb-venv/bin/python hardware/pcb/controller_board.py

Writes controller-board.net next to this file.

Symbol substitutions — stock KiCad libraries lack an exact symbol for a few parts;
each substitute carries the same signals and is a bom-board.md alternate. Swap the
exact part at layout:
  - Regulators: LM2596S-5 (12->5V buck) + AMS1117-3.3 (5->3.3V LDO) stand in for the
    MP2315 first-pick buck pair (both are bom-board.md alternates).
  - RTC: DS3231MZ (SOIC-8) stands in for the DS3231SN (SOIC-16); same I2C/VBAT signals.
  - Relays: generic Relay_SPDT stands in for the HF115F-class (K1) / SRD-class (K2).

Open decisions from netlist.md resolved concretely here:
  #1 pump enable: DRV8871 is 2-wire — IO33/IO19 are freed (not used as pump PWM).
  #2 backflow sensor: assigned to IO13.
  RS485 DE/~RE: driven from the freed IO33 (SP3485 is not auto-direction).
"""

import os
import sys

# Run from this file's directory so SKiDL's byproducts (.log/.erc/_sklib, created at
# import and generation time) stay in hardware/pcb/ rather than the repo root.
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from skidl import (
    Part, Net, generate_netlist, ERC, POWER,
    set_default_tool, lib_search_paths, KICAD9,
)

# ── KiCad symbol libraries ────────────────────────────────────────────────────
set_default_tool(KICAD9)
_MAC = "/Applications/KiCad.app/Contents/SharedSupport/symbols"
_sym = os.environ.get("KICAD9_SYMBOL_DIR") or (_MAC if os.path.isdir(_MAC) else None)
if not _sym:
    sys.exit("KiCad symbols not found — install KiCad or set KICAD9_SYMBOL_DIR")
lib_search_paths[KICAD9].append(_sym)


def pn(part, key):
    """Exact pin lookup by name OR number. SKiDL's default [] is unanchored regex,
    which mismatches IO2/IO21 and chokes on '+'/'{}' in pin names."""
    key = str(key)
    hits = [p for p in part.pins if p.name == key or str(p.num) == key]
    if not hits:
        have = [(str(p.num), p.name) for p in part.pins]
        raise KeyError(f"{part.ref}: no pin {key!r}. have={have}")
    return hits if len(hits) > 1 else hits[0]


def wire(*nodes):
    """Connect nodes (nets and/or pins) together. Local var on the left makes the
    augmented assignment legal even when a node is a pin expression."""
    a = nodes[0]
    for b in nodes[1:]:
        a += b
    return nodes[0]


# ── Power + global nets ───────────────────────────────────────────────────────
p12, p5, p3v3, gnd = Net("+12V"), Net("+5V"), Net("+3V3"), Net("GND")
vbus = Net("VBUS")        # USB-C 5V — flash-time supply for the bridge
earth = Net("EARTH")      # AC protective earth (separate from logic GND)


def R(value, fp="Resistor_SMD:R_0603_1608Metric", **kw):
    return Part("Device", "R", value=value, footprint=fp, **kw)


def C(value, fp="Capacitor_SMD:C_0603_1608Metric", **kw):
    return Part("Device", "C", value=value, footprint=fp, **kw)


def conn(ref, npins, value, fp):
    return Part("Connector_Generic", f"Conn_01x{npins:02d}", ref=ref,
                value=value, footprint=fp)


def jst(ref, npins, value):
    fp = f"Connector_JST:JST_XH_B{npins}B-XH-A_1x{npins:02d}_P2.50mm_Vertical"
    return conn(ref, npins, value, fp)


def bypass(node, n=1, value="100nF"):
    for _ in range(n):
        c = C(value)
        wire(node, pn(c, "1"))
        wire(gnd, pn(c, "2"))


def res(a, value, b):
    r = R(value)
    wire(a, pn(r, "1"))
    wire(b, pn(r, "2"))
    return r


# ── U1  ESP32-WROOM-32E (main MCU) ────────────────────────────────────────────
esp = Part("RF_Module", "ESP32-WROOM-32E", ref="U1",
           footprint="RF_Module:ESP32-WROOM-32")
wire(p3v3, pn(esp, "VDD"))
wire(gnd, pn(esp, "GND"))
bypass(p3v3, n=2)
bypass(p3v3, n=1, value="10uF")

en  = Net("EN");       wire(en, pn(esp, "EN"))
io0 = Net("IO0_BOOT"); wire(io0, pn(esp, "IO0"))
res(p3v3, "10k", en)
bypass(en, n=1, value="100nF")
res(p3v3, "10k", io0)
sw_en = Part("Switch", "SW_Push", ref="SW2", value="EN",
             footprint="Button_Switch_THT:SW_PUSH_6mm")
wire(en, pn(sw_en, "1")); wire(gnd, pn(sw_en, "2"))
sw_bt = Part("Switch", "SW_Push", ref="SW1", value="BOOT",
             footprint="Button_Switch_THT:SW_PUSH_6mm")
wire(io0, pn(sw_bt, "1")); wire(gnd, pn(sw_bt, "2"))


def espnet(name, gpio):
    n = Net(name); wire(n, pn(esp, gpio)); return n

i2c_sda = espnet("I2C_SDA", "IO21")
i2c_scl = espnet("I2C_SCL", "IO22")
onewire = espnet("ONEWIRE", "IO16")
carb_lo = espnet("CARB_REED_LOW", "IO17")
carb_hi = espnet("CARB_REED_HIGH", "IO27")
flow    = espnet("FLOW_PULSE", "IO23")
rly1    = espnet("RELAY1_DRIVE", "IO14")
rly2    = espnet("RELAY2_DRIVE", "IO4")
pA_in1  = espnet("PUMP_A_IN1", "IO25")
pA_in2  = espnet("PUMP_A_IN2", "IO26")
pB_in1  = espnet("PUMP_B_IN1", "IO18")
pB_in2  = espnet("PUMP_B_IN2", "IO5")
u1tx    = espnet("UART1_TX", "IO15")
u1rx    = espnet("UART1_RX", "IO34")
u2tx    = espnet("UART2_TX", "IO32")
u2rx    = espnet("UART2_RX", "IO35")
rs485_de = espnet("RS485_DE", "IO33")          # freed pin -> SP3485 DE/~RE
backflow = espnet("BACKFLOW_MOIST", "IO13")    # decision #2
txd0    = espnet("TXD0", "TXD0/IO1")
rxd0    = espnet("RXD0", "RXD0/IO3")
status  = espnet("STATUS_LED", "IO2")
# IO19 left free — DRV8871 is 2-wire (decision #1).

res(p3v3, "4.7k", i2c_sda)
res(p3v3, "4.7k", i2c_scl)
res(p3v3, "4.7k", onewire)
res(p3v3, "10k", carb_lo)
res(p3v3, "10k", carb_hi)
res(p5, "10k", flow)                            # 5V open-collector sensor

led_st = Part("Device", "LED", ref="LED2", value="STATUS",
              footprint="LED_SMD:LED_0805_2012Metric")
res(status, "1k", pn(led_st, "A")); wire(gnd, pn(led_st, "K"))
led_pwr = Part("Device", "LED", ref="LED1", value="PWR",
               footprint="LED_SMD:LED_0805_2012Metric")
res(p3v3, "1k", pn(led_pwr, "A")); wire(gnd, pn(led_pwr, "K"))

# ── U2  CH340X USB-UART bridge + 2-transistor auto-reset ──────────────────────
ch = Part("Interface_USB", "CH340X", ref="U2",
          footprint="Package_SO:MSOP-10_3x3mm_P0.5mm")
wire(vbus, pn(ch, "VCC")); wire(gnd, pn(ch, "GND"))
bypass(vbus, n=1)
bypass(pn(ch, "V3"), n=1)
usb_dp = Net("USB_D+"); usb_dm = Net("USB_D-")
wire(usb_dp, pn(ch, "UD+")); wire(usb_dm, pn(ch, "UD-"))
wire(rxd0, pn(ch, "TXD")); wire(txd0, pn(ch, "RXD"))
dtr = Net("DTR"); rts = Net("RTS")
wire(dtr, pn(ch, "TNOW/~{DTR}")); wire(rts, pn(ch, "~{RTS}"))
q_en = Part("Transistor_BJT", "MMBT3904", ref="Q3",
            footprint="Package_TO_SOT_SMD:SOT-23")
q_io0 = Part("Transistor_BJT", "MMBT3904", ref="Q4",
             footprint="Package_TO_SOT_SMD:SOT-23")
res(rts, "12k", pn(q_en, "B"))                  # cross-coupled auto-reset
wire(en, pn(q_en, "C")); wire(dtr, pn(q_en, "E"))
res(dtr, "12k", pn(q_io0, "B"))
wire(io0, pn(q_io0, "C")); wire(rts, pn(q_io0, "E"))

usbc = Part("Connector", "USB_C_Receptacle_USB2.0_16P", ref="J1",
            footprint="Connector_USB:USB_C_Receptacle_GCT_USB4085")
wire(vbus, pn(usbc, "VBUS")); wire(gnd, pn(usbc, "GND")); wire(earth, pn(usbc, "SHIELD"))
wire(usb_dp, pn(usbc, "D+")); wire(usb_dm, pn(usbc, "D-"))
res(pn(usbc, "CC1"), "5.1k", gnd)
res(pn(usbc, "CC2"), "5.1k", gnd)

# ── U9  DS3231MZ RTC (0x68) + CR2032 ──────────────────────────────────────────
rtc = Part("Timer_RTC", "DS3231MZ", ref="U9",
           footprint="Package_SO:SOIC-8_3.9x4.9mm_P1.27mm")
wire(p3v3, pn(rtc, "VCC")); wire(gnd, pn(rtc, "GND"))
wire(i2c_sda, pn(rtc, "SDA")); wire(i2c_scl, pn(rtc, "SCL"))
bypass(p3v3, n=1)
bt = Part("Device", "Battery_Cell", ref="BT1", value="CR2032",
          footprint="Battery:BatteryHolder_Keystone_3002_1x2032")
vbat = Net("VBAT"); wire(vbat, pn(rtc, "VBAT"), pn(bt, "+")); wire(gnd, pn(bt, "-"))

# ── U3/U4  MCP23017 expanders (clock pin is named 'SCK') ──────────────────────
def mcp(ref, addr):
    m = Part("Interface_Expansion", "MCP23017x-x-SO", ref=ref,
             footprint="Package_SO:SOIC-28W_7.5x17.9mm_P1.27mm")
    wire(p3v3, pn(m, "V_{DD}")); wire(gnd, pn(m, "V_{SS}"))
    wire(i2c_sda, pn(m, "SDA")); wire(i2c_scl, pn(m, "SCK"))
    wire(p3v3, pn(m, "~{RESET}"))
    for bit, ap in zip(addr, ("A0", "A1", "A2")):
        wire(p3v3 if bit else gnd, pn(m, ap))
    bypass(p3v3, n=1)
    return m

u3 = mcp("U3", (0, 0, 0))   # 0x20
u4 = mcp("U4", (1, 0, 0))   # 0x21

# ── U5/U6  ULN2803A sink drivers (COM -> +12V flyback) ────────────────────────
def uln(ref):
    u = Part("Transistor_Array", "ULN2803A", ref=ref,
             footprint="Package_SO:SOIC-18W_7.5x11.6mm_P1.27mm")
    wire(gnd, pn(u, "GND")); wire(p12, pn(u, "COM"))
    return u

u5 = uln("U5")   # valves V-A..V-H
u6 = uln("U6")   # valves V-I..V-K-B + condenser fan
for i in range(8):
    wire(pn(u3, f"GPA{i}"), pn(u5, f"I{i+1}"))
for i in range(4):
    wire(pn(u3, f"GPB{i}"), pn(u6, f"I{i+1}"))
rsvr_a = [Net(f"RSVR_A_REED{i+1}") for i in range(4)]
for i in range(4):
    wire(rsvr_a[i], pn(u3, f"GPB{i+4}"))
rsvr_b = [Net(f"RSVR_B_REED{i+1}") for i in range(4)]
for i in range(4):
    wire(rsvr_b[i], pn(u4, f"GPA{i}"))
wire(pn(u4, "GPA4"), pn(u6, "I5"))              # condenser fan drive

valve_a = jst("J8", 9, "VALVES V-A..V-H + 12V")
for i in range(8):
    wire(pn(u5, f"O{i+1}"), pn(valve_a, f"Pin_{i+1}"))
wire(p12, pn(valve_a, "Pin_9"))
valve_b = jst("J9", 6, "VALVES V-I..V-K-B + FAN + 12V")
for i in range(4):
    wire(pn(u6, f"O{i+1}"), pn(valve_b, f"Pin_{i+1}"))
wire(pn(u6, "O5"), pn(valve_b, "Pin_5"))        # fan sink
wire(p12, pn(valve_b, "Pin_6"))

# ── U7/U8  DRV8871 peristaltic pump drivers ───────────────────────────────────
def drv(ref, in1, in2, jref):
    d = Part("Driver_Motor", "DRV8871DDA", ref=ref,
             footprint="Package_SO:Texas_HSOP-8-1EP_3.9x4.9mm_P1.27mm_ThermalVias")
    wire(p12, pn(d, "VM")); wire(gnd, pn(d, "GND"))
    wire(in1, pn(d, "IN1")); wire(in2, pn(d, "IN2"))
    res(pn(d, "ILIM"), "47k", gnd)
    cb = C("100uF", "Capacitor_SMD:C_1210_3225Metric")
    wire(p12, pn(cb, "1")); wire(gnd, pn(cb, "2"))
    j = jst(jref, 2, f"PUMP {ref}")
    wire(pn(d, "OUT1"), pn(j, "Pin_1")); wire(pn(d, "OUT2"), pn(j, "Pin_2"))
    return d

u7 = drv("U7", pA_in1, pA_in2, "J6")
u8 = drv("U8", pB_in1, pB_in2, "J7")

# ── Relays K1/K2 + opto + low-side FET drive ──────────────────────────────────
def relay_drive(ref_k, ref_q, ref_ok, drive_net, vcoil, com_net, no_net):
    k = Part("Relay", "Relay_SPDT", ref=ref_k,
             footprint="Relay_THT:Relay_SPDT_SANYOU_SRD_Series_Form_C")
    q = Part("Transistor_FET", "2N7002", ref=ref_q,
             footprint="Package_TO_SOT_SMD:SOT-23")
    ok = Part("Isolator", "PC817", ref=ref_ok, footprint="Package_DIP:DIP-4_W7.62mm")
    gate = Net(f"{ref_k}_GATE")
    res(drive_net, "1k", pn(ok, "1"))           # GPIO -> opto LED anode
    wire(gnd, pn(ok, "2"))                       # LED cathode
    wire(p5, pn(ok, "4"))                        # phototransistor collector
    wire(gate, pn(ok, "3"))                      # emitter -> gate
    res(gate, "10k", gnd)                        # gate pulldown
    wire(gate, pn(q, "G")); wire(gnd, pn(q, "S")); wire(pn(q, "D"), pn(k, "A2"))
    wire(vcoil, pn(k, "A1"))
    d = Part("Diode", "SS14", ref=f"D_{ref_k}", footprint="Diode_SMD:D_SMA")
    wire(vcoil, pn(d, "K")); wire(pn(d, "A"), pn(k, "A2"))   # coil flyback
    wire(com_net, pn(k, "11")); wire(no_net, pn(k, "14"))    # COM / NO
    return k

ac_hot = Net("AC_HOT_IN"); ac_sw = Net("COMPRESSOR_AC_HOT"); ac_n = Net("AC_N")
k1 = relay_drive("K1", "Q1", "OK1", rly1, p5, ac_hot, ac_sw)     # 5V coil
j_ac_in = conn("J3", 2, "AC IN H/N (fenced)",
               "TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal")
wire(ac_hot, pn(j_ac_in, "Pin_1")); wire(ac_n, pn(j_ac_in, "Pin_2"))
j_ac_comp = conn("J4", 3, "COMPRESSOR H_sw/N/G",
                 "TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-3-5.08_1x03_P5.08mm_Horizontal")
wire(ac_sw, pn(j_ac_comp, "Pin_1")); wire(ac_n, pn(j_ac_comp, "Pin_2"))
wire(earth, pn(j_ac_comp, "Pin_3"))

dia_sw = Net("DIAPHRAGM_12V_SW")
k2 = relay_drive("K2", "Q2", "OK2", rly2, p12, p12, dia_sw)      # 12V coil
j_dia = jst("J5", 2, "DIAPHRAGM PUMP 12V")
wire(dia_sw, pn(j_dia, "Pin_1")); wire(gnd, pn(j_dia, "Pin_2"))

# ── U12  SP3485 RS485 transceiver (config display link) ───────────────────────
rs = Part("Interface_UART", "SP3485EN", ref="U12",
          footprint="Package_SO:SOIC-8_3.9x4.9mm_P1.27mm")
wire(p3v3, pn(rs, "VCC")); wire(gnd, pn(rs, "GND"))
wire(u1tx, pn(rs, "DI")); wire(u1rx, pn(rs, "RO"))
wire(rs485_de, pn(rs, "DE")); wire(rs485_de, pn(rs, "~{RE}"))
bypass(p3v3, n=1)
rs485_a = Net("RS485_A"); rs485_b = Net("RS485_B")
wire(rs485_a, pn(rs, "A")); wire(rs485_b, pn(rs, "B"))
res(rs485_a, "120", rs485_b)                    # bus-end termination

# ── Power regulation ──────────────────────────────────────────────────────────
u10 = Part("Regulator_Switching", "LM2596S-5", ref="U10",
           footprint="Package_TO_SOT_SMD:TO-263-5_TabPin3")
sw5 = Net("SW_5V")
wire(p12, pn(u10, "VIN")); wire(gnd, pn(u10, "GND")); wire(gnd, pn(u10, "~{ON}/OFF"))
wire(sw5, pn(u10, "OUT")); wire(p5, pn(u10, "FB"))
l1 = Part("Device", "L", ref="L1", value="33uH", footprint="Inductor_SMD:L_12x12mm_H8mm")
wire(sw5, pn(l1, "1")); wire(p5, pn(l1, "2"))
d5 = Part("Diode", "SS14", ref="D2", footprint="Diode_SMD:D_SMA")
wire(sw5, pn(d5, "K")); wire(gnd, pn(d5, "A"))
ci5 = C("220uF", "Capacitor_SMD:C_1210_3225Metric"); wire(p12, pn(ci5, "1")); wire(gnd, pn(ci5, "2"))
co5 = C("220uF", "Capacitor_SMD:C_1210_3225Metric"); wire(p5, pn(co5, "1")); wire(gnd, pn(co5, "2"))

u11 = Part("Regulator_Linear", "AMS1117-3.3", ref="U11",
           footprint="Package_TO_SOT_SMD:SOT-223-3_TabPin2")
wire(p5, pn(u11, "VI")); wire(p3v3, pn(u11, "VO")); wire(gnd, pn(u11, "GND"))
ci3 = C("10uF", "Capacitor_SMD:C_0805_2012Metric"); wire(p5, pn(ci3, "1")); wire(gnd, pn(ci3, "2"))
co3 = C("10uF", "Capacitor_SMD:C_0805_2012Metric"); wire(p3v3, pn(co3, "1")); wire(gnd, pn(co3, "2"))

# ── Power input + bulk + protection ───────────────────────────────────────────
j_12v = jst("J2", 2, "+12V IN (PSU)")
wire(p12, pn(j_12v, "Pin_1")); wire(gnd, pn(j_12v, "Pin_2"))
c_bulk = C("470uF", "Capacitor_SMD:CP_Elec_10x10.5"); wire(p12, pn(c_bulk, "1")); wire(gnd, pn(c_bulk, "2"))
d_tvs = Part("Device", "D_TVS", ref="D1", value="SMAJ15A", footprint="Diode_SMD:D_SMA")
wire(p12, pn(d_tvs, "A1")); wire(gnd, pn(d_tvs, "A2"))

# ── Field connectors (sensor / signal islands) ────────────────────────────────
j_reed_a = jst("J10", 5, "RSVR A reeds")
for i in range(4):
    wire(rsvr_a[i], pn(j_reed_a, f"Pin_{i+1}"))
wire(gnd, pn(j_reed_a, "Pin_5"))
j_reed_b = jst("J11", 5, "RSVR B reeds")
for i in range(4):
    wire(rsvr_b[i], pn(j_reed_b, f"Pin_{i+1}"))
wire(gnd, pn(j_reed_b, "Pin_5"))
j_carb = jst("J12", 3, "CARB reeds lo/hi")
wire(carb_lo, pn(j_carb, "Pin_1")); wire(carb_hi, pn(j_carb, "Pin_2")); wire(gnd, pn(j_carb, "Pin_3"))
j_ow = jst("J13", 3, "DS18B20 1-wire")
wire(onewire, pn(j_ow, "Pin_1")); wire(p3v3, pn(j_ow, "Pin_2")); wire(gnd, pn(j_ow, "Pin_3"))
j_flow = jst("J14", 3, "FLOW meter")
wire(flow, pn(j_flow, "Pin_1")); wire(p5, pn(j_flow, "Pin_2")); wire(gnd, pn(j_flow, "Pin_3"))
j_back = jst("J15", 2, "BACKFLOW moisture")
wire(backflow, pn(j_back, "Pin_1")); wire(gnd, pn(j_back, "Pin_2"))
j_cfg = jst("J16", 4, "CONFIG display RS485")
wire(rs485_a, pn(j_cfg, "Pin_1")); wire(rs485_b, pn(j_cfg, "Pin_2"))
wire(p12, pn(j_cfg, "Pin_3")); wire(gnd, pn(j_cfg, "Pin_4"))
j_fau = jst("J17", 4, "FAUCET display UART")
wire(u2tx, pn(j_fau, "Pin_1")); wire(u2rx, pn(j_fau, "Pin_2"))
wire(p5, pn(j_fau, "Pin_3")); wire(gnd, pn(j_fau, "Pin_4"))

for net, ref in ((onewire, "D3"), (flow, "D4"), (u2tx, "D5"), (u2rx, "D6")):
    d = Part("Device", "D_TVS", ref=ref, value="ESD", footprint="Diode_SMD:D_SOD-323")
    wire(net, pn(d, "A1")); wire(gnd, pn(d, "A2"))

# ── ERC hygiene: source-pin drive + intentional no-connects ───────────────────
# Mark where each supply net is driven. The logic rails enter via connectors / the
# battery (PASSIVE pins), not an on-board POWER-OUT pin, so flag one source pin per
# rail as POWER to stop ERC reading the supply-input pins as undriven. +3V3 needs
# nothing — it is driven by the AMS1117 VO output pin.
import builtins
NC = builtins.NC
pn(j_12v, "Pin_1").drive = POWER       # +12V
pn(j_12v, "Pin_2").drive = POWER       # GND
pn(l1, "2").drive = POWER              # +5V (buck inductor output)
pn(usbc, "VBUS")[0].drive = POWER      # VBUS
pn(bt, "+").drive = POWER              # VBAT
pn(j_ac_comp, "Pin_3").drive = POWER   # EARTH


def noconn(part, *keys):
    """Mark intentionally-unused pins so ERC stays meaningful."""
    for k in keys:
        hit = pn(part, k)
        for p in (hit if isinstance(hit, list) else [hit]):
            wire(NC, p)

noconn(esp, "NC", "IO12", "IO19", "SENSOR_VP", "SENSOR_VN")   # spare + freed IOs
noconn(u3, "INTA", "INTB")
noconn(u4, "INTA", "INTB", "GPA5", "GPA6", "GPA7",
       "GPB0", "GPB1", "GPB2", "GPB3", "GPB4", "GPB5", "GPB6", "GPB7")  # 0x21 spares
noconn(u6, "I6", "I7", "I8", "O6", "O7", "O8")        # unused ULN #2 channels
noconn(rtc, "32KHZ", "~{INT}/SQW", "~{RST}")
noconn(ch, "~{CTS}")
noconn(usbc, "SBU1", "SBU2")
noconn(k1, "12"); noconn(k2, "12")                    # unused NC relay contact

# ── Generate ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import builtins
    circuit = builtins.default_circuit   # SKiDL injects this into builtins on import
    here = os.path.dirname(os.path.abspath(__file__))
    # Pin each part's tag to its (creation-ordered, stable) refdes so the netlist —
    # and the tstamp UUIDs derived from the tag — regenerate identically.
    for part in circuit.parts:
        part.tag = part.ref
    ERC()
    out = os.path.join(here, "controller-board.net")
    generate_netlist(file_=out)
    # Normalize the wall-clock timestamp so the checked-in netlist is byte-stable
    # across regenerations (git records the revision; the date adds only churn).
    with open(out) as f:
        text = f.read()
    import re
    text = re.sub(r'\(date "[^"]*"\)', '(date "generated by controller_board.py")', text, count=1)
    with open(out, "w") as f:
        f.write(text)
