"""The complete enclosure electrical graph, independent of its physical routing.

J2/J13 share the IDs and pin labels of assembly/harnesses. Unused contacts and
the enclosure boundary are explicit, rather than wires invented to fill them.
"""
from .model import Connection


UNUSED = {
    "J2.OUT4": "Spare driver; no contact in XHP-6 cavity 3",
    "J4.IO23": "Reserved; no cable", "J4.IO27": "Reserved; no cable",
    "J8": "I2C expansion, unused", "J14": "USB programming, no permanent harness",
    "relay-1.NC": "Normally-closed contact unused", "relay-2.NC": "Normally-closed contact unused",
    "keystone.1": "Unused IDC", "keystone.6": "Unused IDC",
    "faucet-earth": "Bond requirement and plate landing unresolved; no completed connection claimed",
}
BOUNDARIES = {
    "faucet": "The inboard harness ends at the rear keystone. The umbilical and faucet have their own assembly.",
    "compressor": "Routes reach the retained donor interface region; exact Unit B hot/neutral/earth landings are unlocated.",
    "fan": "Routes reach the condenser crown; the donor lead exit and final connector are unlocated.",
}


def owner(part):
    if part.startswith('cold-core/') or part in (
            'pcba','psu','g-ganen-pump','valve-v-a','coil-v-a','valve-v-b','coil-v-b',
            'vk-solenoid','ground-stack','digiten-flow',
            'wago-v12','wago-gnd','wago-sensors','wago-reeds-b'):
        return 'cold-core'
    if part in ('pump-a-motor','pump-b-motor'):
        return 'pump-cartridge'
    if part in ('compressor','condenser+fan','thermal-fuse','mq6-sensor'):
        return 'front-bottom'
    if part in ('relay-1','relay-2'):
        return 'back-top'
    if part.startswith('coil-v-') or part in ('display','wago-mana','wago-manb'):
        return 'front-top'
    return 'back-top'


def interfaces(terminals,graph):
    used={t for c in graph for t in (c.start,c.end)}
    buses=[]
    for part in sorted({terminals[t].part for t in used if t.startswith(('wago-','ground.'))}):
        ports=sorted(t for t in used if terminals[t].part==part)
        buses.append({'id':part,'terminals':ports,'kind':'ring stack' if part=='ground-stack' else 'WAGO busbar'})
    return {'common_junctions':buses,
            'assembly_owners':{t:owner(terminals[t].part) for t in sorted(used)},
            'crossing_wires':[{'wire':c.id,'from':owner(terminals[c.start].part),
                               'to':owner(terminals[c.end].part)} for c in graph
                              if owner(terminals[c.start].part)!=owner(terminals[c.end].part)]}


def connections():
    out = []
    def wire(id, harness, net, start, end, stock="ribbon22", schedule="", service="fixed", note=""):
        out.append(Connection(id, harness, net, start, end, stock, schedule, service, note))
    for net, port, stock in (("L", "h", "power16"), ("N", "n", "neutral16"), ("PE", "g", "earth16")):
        wire("AC1-"+net, "AC inlet", net, "c14."+net, f"wago-{port}.1", stock, "AC-1")
    wire("AC2-L", "PSU primary", "L", "wago-h.2", "psu.L", "power16", "AC-2")
    wire("AC2-N", "PSU primary", "N", "wago-n.2", "psu.N", "neutral16", "AC-2")
    wire("AC3-L", "Compressor", "L", "wago-h.3", "relay-1.COM", "power16", "AC-3")
    wire("AC4-H", "Compressor", "H_switched", "relay-1.NO", "fuse.in", "cord18", "AC-4")
    wire("AC4-fuse", "Compressor", "H_switched", "fuse.out", "compressor.H", "cord18", "AC-4")
    wire("AC5-N", "Compressor", "N", "wago-n.3", "compressor.N", "neutral18", "AC-5")
    wire("AC6-PE", "Compressor", "PE", "ground.compressor", "compressor.PE", "earth18", "AC-6")
    wire("PE-bus", "Earth bonds", "PE", "wago-g.2", "ground.inlet", "earth16", "AC-1")
    wire("PE-carbonator", "Earth bonds", "PE", "ground.carbonator", "carbonator.PE", "earth16", "earth bonds",
         note="Carbonator metal landing is unresolved; a plastic cap screw is not an electrical bond.")
    for net, pole in (("V12", "v12"), ("GND", "gnd")):
        wire("DC1-"+net, "12V power", net, "psu."+net, f"wago-{pole}.1", "power16", "DC-1")
        wire("DC4-"+net, "12V power", net, f"wago-{pole}.3", "J10."+net, "power16", "DC-4")
    wire("DC2-V12", "Diaphragm pump", "V12", "wago-v12.2", "relay-2.COM", "power16", "DC-2")
    wire("DC3-positive", "Diaphragm pump", "pump-switched", "relay-2.NO", "diaphragm.positive", "power16", "DC-3")
    wire("DC3-negative", "Diaphragm pump", "GND", "wago-gnd.2", "diaphragm.negative", "power16", "DC-3")
    for j, coils, common in (("J1", "ABCDEFGH", "mana"), ("J2", "IJ", "manb")):
        wire(j+"-COM", j, "V12", j+".COM", f"wago-{common}.1", schedule="DC-6" if j=="J1" else "DC-7")
        for i, coil in enumerate(coils, 1):
            wire(f"{j}-OUT{i}", j, f"{j}.OUT{i}", f"{j}.OUT{i}", f"V-{coil}.negative", schedule="DC-6" if j=="J1" else "DC-7")
            wire(f"{j}-positive-{coil}", j, "V12", f"wago-{common}.{i+1}", f"V-{coil}.positive", "bulk22", "DC-6" if j=="J1" else "DC-7")
    for id, net, start, end, schedule in (
        ("J2-FAN", "J2.FAN", "J2.FAN", "fan.negative", "DC-8"),
        ("J2-positive-fan", "V12", "wago-manb.4", "fan.positive", "DC-8"),
        ("J2-OUT3", "J2.OUT3", "J2.OUT3", "V-K.negative", "DC-9"),
        ("J2-positive-K", "V12", "wago-manb.5", "V-K.positive", "DC-9")):
        wire(id, "J2", net, start, end, schedule=schedule)
    for label, motor in (("AM2", "pump-a.2"), ("AM1", "pump-a.1"),
                         ("BM2", "pump-b.2"), ("BM1", "pump-b.1")):
        wire("J13-"+label, "J13", label, "J13."+label, motor, schedule="DC-5")
    for label, pin in (("V5", 2), ("GND", 3), ("IO35", 4), ("IO33", 5)):
        wire("J3-"+label, "J3", label, "J3."+label, f"keystone.{pin}", schedule="SIG-6")
    for label, target in (("3V3", "temp-carbonator.V"), ("IO26", "temp-carbonator.DATA"),
                           ("V5", "flow.V"), ("IO25", "flow.PULSE"), ("GND", "wago-sensors.1")):
        wire("J4-"+label, "J4", label, "J4."+label, target, schedule="SIG-1 / SIG-4")
    wire("temp-GND", "J4", "GND", "wago-sensors.2", "temp-carbonator.GND", schedule="SIG-1")
    wire("flow-GND", "J4", "GND", "wago-sensors.3", "flow.GND", schedule="SIG-4")
    for label in ("V", "DATA", "GND"):
        wire("temp-bus-"+label, "J4", {"V":"3V3","DATA":"IO26","GND":"GND"}[label],
             "temp-carbonator."+label, "temp-coil."+label, schedule="SIG-1",
             note="Parallel 1-wire bus; insulated branch joint layout is proposed.")
    for label in ("V5", "GND"):
        wire("J5-"+label, "J5", label, "J5."+label, "relay-1."+label, schedule="LV-3")
        wire("relay-bus-"+label, "J5", label, "relay-1."+label, "relay-2."+label, schedule="LV-3",
             note="Shared relay-end rail; termination accommodating both leads remains to be specified.")
    for label, relay in (("IO19", 1), ("IO2", 2)):
        wire("J5-"+label, "J5", label, "J5."+label, f"relay-{relay}.IN", schedule=f"LV-{1 if relay==1 else 2}")
    for j, bank in (("J6", "a"), ("J7", "b")):
        wire(j+"-GND", j, "GND", j+".GND", "reed-a-4.GND" if bank=="a" else "wago-reeds-b.1", schedule="SIG-10" if bank=="a" else "SIG-11")
        for i in range(1, 5):
            signal=f"R{bank.upper()}{i}"
            wire(j+"-"+signal, j, signal, j+"."+signal, f"reed-{bank}-{i}.signal", schedule="SIG-10" if bank=="a" else "SIG-11")
            if bank=="a" and i==4:
                continue
            ground_start=f'wago-reeds-{bank}.2' if i==4 else f'reed-{bank}-{i+1}.GND'
            wire(f"{j}-earth-{i}", j, "GND", ground_start, f"reed-{bank}-{i}.GND", schedule="SIG-10" if bank=="a" else "SIG-11",
                 note="Continuous common down the reed column; short soldered taps, individually insulated.")
    for i, label in ((1, "CLO"), (2, "CHI")):
        wire("J7-"+label, "J7", label, "J7."+label, f"reed-carb-{i}.signal", schedule=f"SIG-{i+1}")
        ground_start='wago-reeds-b.3' if i==2 else 'reed-carb-2.GND'
        wire(f"J7-carb-earth-{i}", "J7", "GND", ground_start, f"reed-carb-{i}.GND", schedule=f"SIG-{i+1}",
             note="Common carbonator-reed conductor with insulated local taps.")
    for label in ("B", "A", "GND", "V12"):
        wire("J9-"+label, "J9", label, "J9."+label, "display."+label, schedule="SIG-7")
    for label, pin in (("V5", 1), ("GND", 2), ("DOUT", 3), ("AOUT", 4)):
        wire("J11-"+label, "J11", label, "J11."+label, f"mq6.{pin}", schedule="SIG-12")
    return out
