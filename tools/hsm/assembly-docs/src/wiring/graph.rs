use super::*;
fn wire(
    out: &mut Vec<Value>,
    id: impl Into<String>,
    harness: &str,
    net: impl Into<String>,
    start: impl Into<String>,
    end: impl Into<String>,
    stock: &str,
    schedule: &str,
    service: &str,
    note: &str,
) {
    out.push(json!({"id":id.into(),"harness":harness,"net":net.into(),"start":start.into(),"end":end.into(),"stock":stock,"schedule":schedule,"service":service,"note":note}));
}
pub fn connections() -> Value {
    let mut out = Vec::new();
    for (net, port, stock) in [
        ("L", "h", "power16"),
        ("N", "n", "neutral16"),
        ("PE", "g", "earth16"),
    ] {
        wire(
            &mut out,
            format!("AC1-{net}"),
            "AC inlet",
            net,
            format!("c14.{net}"),
            format!("wago-{port}.1"),
            stock,
            "AC-1",
            "fixed",
            "",
        );
    }
    for (id, h, net, a, b, stock, schedule, service) in [
        (
            "AC2-L",
            "PSU primary",
            "L",
            "wago-h.2",
            "psu.L",
            "power16",
            "AC-2",
            "fixed",
        ),
        (
            "AC2-N",
            "PSU primary",
            "N",
            "wago-n.2",
            "psu.N",
            "neutral16",
            "AC-2",
            "fixed",
        ),
        (
            "AC3-L",
            "Compressor",
            "L",
            "wago-h.3",
            "relay-1.COM",
            "power16",
            "AC-3",
            "fixed",
        ),
        (
            "AC4-pigtail",
            "Compressor",
            "H_switched",
            "relay-1.NO",
            "join-compressor-h.1",
            "power16",
            "AC-4",
            "final join",
        ),
        (
            "AC4-H",
            "Compressor",
            "H_switched",
            "join-compressor-h.2",
            "fuse.in",
            "cord18",
            "AC-4",
            "final join",
        ),
        (
            "AC4-fuse",
            "Compressor",
            "H_switched",
            "fuse.out",
            "compressor.H",
            "cord18",
            "AC-4",
            "fixed",
        ),
        (
            "AC5-pigtail",
            "Compressor",
            "N",
            "wago-n.3",
            "join-compressor-n.1",
            "neutral16",
            "AC-5",
            "final join",
        ),
        (
            "AC5-N",
            "Compressor",
            "N",
            "join-compressor-n.2",
            "compressor.N",
            "neutral18",
            "AC-5",
            "final join",
        ),
        (
            "AC6-PE",
            "Compressor",
            "PE",
            "wago-g.3",
            "compressor.PE",
            "earth18",
            "AC-6",
            "fixed",
        ),
    ] {
        wire(&mut out, id, h, net, a, b, stock, schedule, service, "");
    }
    wire(
        &mut out,
        "PE-carbonator",
        "Earth bonds",
        "PE",
        "wago-g.2",
        "carbonator.PE",
        "earth16",
        "earth bonds",
        "fixed",
        "Closed ring clamped directly to the drilled stainless vessel rim; fitted before the body foam pour.",
    );
    for (net, pole) in [("V12", "v12"), ("GND", "gnd")] {
        wire(
            &mut out,
            format!("DC1-{net}"),
            "12V power",
            net,
            format!("psu.{net}"),
            format!("wago-{pole}.1"),
            "power16",
            "DC-1",
            "fixed",
            "",
        );
        wire(
            &mut out,
            format!("DC4-{net}"),
            "12V power",
            net,
            format!("wago-{pole}.3"),
            format!("J10.{net}"),
            "power16",
            "DC-4",
            "fixed",
            "",
        );
    }
    for (id, net, a, b, schedule, service) in [
        (
            "DC2-V12",
            "V12",
            "wago-v12.2",
            "relay-2.COM",
            "DC-2",
            "fixed",
        ),
        (
            "DC3-pigtail",
            "pump-switched",
            "relay-2.NO",
            "join-pump-positive.3",
            "DC-3",
            "final join",
        ),
        (
            "DC3-positive",
            "pump-switched",
            "join-pump-positive.2",
            "diaphragm.positive",
            "DC-3",
            "final join",
        ),
        (
            "DC3-negative",
            "GND",
            "wago-gnd.2",
            "diaphragm.negative",
            "DC-3",
            "fixed",
        ),
    ] {
        wire(
            &mut out,
            id,
            "Diaphragm pump",
            net,
            a,
            b,
            "power16",
            schedule,
            service,
            "",
        );
    }
    for (j, coils, common, schedule) in [
        ("J1", "ABCDEFGH", "mana", "DC-6"),
        ("J2", "IJ", "manb", "DC-7"),
    ] {
        wire(
            &mut out,
            format!("{j}-COM"),
            j,
            "V12",
            format!("{j}.COM"),
            format!("wago-{common}.1"),
            "ribbon22",
            schedule,
            "fixed",
            "",
        );
        for (i, coil) in coils.chars().enumerate() {
            wire(
                &mut out,
                format!("{j}-OUT{}", i + 1),
                j,
                format!("{j}.OUT{}", i + 1),
                format!("{j}.OUT{}", i + 1),
                format!("V-{coil}.negative"),
                "ribbon22",
                schedule,
                "fixed",
                "",
            );
            wire(
                &mut out,
                format!("{j}-positive-{coil}"),
                j,
                "V12",
                format!("wago-{common}.{}", i + 2),
                format!("V-{coil}.positive"),
                "bulk22",
                schedule,
                "fixed",
                "",
            );
        }
    }
    for (id, net, a, b, schedule) in [
        ("J2-FAN", "J2.FAN", "J2.FAN", "fan.negative", "DC-8"),
        (
            "J2-positive-fan",
            "V12",
            "wago-manb.4",
            "fan.positive",
            "DC-8",
        ),
        ("J2-OUT3", "J2.OUT3", "J2.OUT3", "V-K.negative", "DC-9"),
        (
            "J2-positive-K",
            "V12",
            "wago-manb.5",
            "V-K.positive",
            "DC-9",
        ),
    ] {
        wire(
            &mut out, id, "J2", net, a, b, "ribbon22", schedule, "fixed", "",
        );
    }
    for (label, motor) in [
        ("AM2", "pump-a.2"),
        ("AM1", "pump-a.1"),
        ("BM2", "pump-b.2"),
        ("BM1", "pump-b.1"),
    ] {
        wire(
            &mut out,
            format!("J13-{label}"),
            "J13",
            label,
            format!("J13.{label}"),
            motor,
            "ribbon22",
            "DC-5",
            "fixed",
            "",
        );
    }
    for (label, pin) in [("V5", 2), ("GND", 3), ("IO35", 4), ("IO33", 5)] {
        wire(
            &mut out,
            format!("J3-{label}"),
            "J3",
            label,
            format!("J3.{label}"),
            format!("keystone.{pin}"),
            "ribbon22",
            "SIG-6",
            "fixed",
            "",
        );
    }
    for (label, target) in [
        ("3V3", "temp-coil.V"),
        ("IO26", "temp-coil.DATA"),
        ("V5", "flow.V"),
        ("IO25", "flow.PULSE"),
        ("GND", "wago-sensors.1"),
    ] {
        wire(
            &mut out,
            format!("J4-{label}"),
            "J4",
            label,
            format!("J4.{label}"),
            target,
            "ribbon22",
            "SIG-1 / SIG-4",
            "fixed",
            "",
        );
    }
    for (id, target, schedule) in [
        ("temp-GND", "temp-coil.GND", "SIG-1"),
        ("flow-GND", "flow.GND", "SIG-4"),
    ] {
        wire(
            &mut out,
            id,
            "J4",
            "GND",
            if id == "temp-GND" {
                "wago-sensors.2"
            } else {
                "wago-sensors.3"
            },
            target,
            "ribbon22",
            schedule,
            "fixed",
            "",
        );
    }
    for (label, net) in [("V", "3V3"), ("DATA", "IO26"), ("GND", "GND")] {
        wire(
            &mut out,
            format!("temp-bus-{label}"),
            "J4",
            net,
            format!("temp-coil.{label}"),
            format!("temp-carbonator.{label}"),
            "ribbon22",
            "SIG-1",
            "fixed",
            "Parallel 1-wire bus; insulated branch joint layout is proposed.",
        );
    }
    for label in ["V5", "GND"] {
        wire(
            &mut out,
            format!("J5-{label}"),
            "J5",
            label,
            format!("J5.{label}"),
            format!("relay-1.{label}"),
            "ribbon22",
            "LV-3",
            "fixed",
            "",
        );
        wire(
            &mut out,
            format!("relay-bus-{label}"),
            "J5",
            label,
            format!("relay-1.{label}"),
            format!("relay-2.{label}"),
            "ribbon22",
            "LV-3",
            "fixed",
            "Shared relay-end rail; termination accommodating both leads remains to be specified.",
        );
    }
    for (label, relay) in [("IO19", 1), ("IO2", 2)] {
        wire(
            &mut out,
            format!("J5-{label}"),
            "J5",
            label,
            format!("J5.{label}"),
            format!("relay-{relay}.IN"),
            "ribbon22",
            &format!("LV-{relay}"),
            "fixed",
            "",
        );
    }
    for (j, bank, schedule) in [("J6", "a", "SIG-10"), ("J7", "b", "SIG-11")] {
        wire(
            &mut out,
            format!("{j}-GND"),
            j,
            "GND",
            format!("{j}.GND"),
            if bank == "a" {
                "reed-a-4.GND"
            } else {
                "wago-reeds-b.1"
            },
            "ribbon22",
            schedule,
            "fixed",
            "",
        );
        for i in 1..=4 {
            let signal = format!("R{}{i}", bank.to_uppercase());
            wire(
                &mut out,
                format!("{j}-{signal}"),
                j,
                &signal,
                format!("{j}.{signal}"),
                format!("reed-{bank}-{i}.signal"),
                "ribbon22",
                schedule,
                "fixed",
                "",
            );
            if bank == "a" && i == 4 {
                continue;
            }
            let start = if i == 4 {
                format!("wago-reeds-{bank}.2")
            } else {
                format!("reed-{bank}-{}.GND", i + 1)
            };
            wire(
                &mut out,
                format!("{j}-earth-{i}"),
                j,
                "GND",
                start,
                format!("reed-{bank}-{i}.GND"),
                "ribbon22",
                schedule,
                "fixed",
                "Continuous common down the reed column; short soldered taps, individually insulated.",
            );
        }
    }
    for (i, label) in [(1, "CLO"), (2, "CHI")] {
        wire(
            &mut out,
            format!("J7-{label}"),
            "J7",
            label,
            format!("J7.{label}"),
            format!("reed-carb-{i}.signal"),
            "ribbon22",
            &format!("SIG-{}", i + 1),
            "fixed",
            "",
        );
        wire(
            &mut out,
            format!("J7-carb-earth-{i}"),
            "J7",
            "GND",
            if i == 2 {
                "wago-reeds-b.3"
            } else {
                "reed-carb-2.GND"
            },
            format!("reed-carb-{i}.GND"),
            "ribbon22",
            &format!("SIG-{}", i + 1),
            "fixed",
            "Common carbonator-reed conductor with insulated local taps.",
        );
    }
    for label in ["B", "A", "GND", "V12"] {
        wire(
            &mut out,
            format!("J9-{label}"),
            "J9",
            label,
            format!("J9.{label}"),
            format!("display.{label}"),
            "ribbon22",
            "SIG-7",
            "fixed",
            "",
        );
    }
    for (label, pin) in [("V5", 1), ("GND", 2), ("DOUT", 3), ("AOUT", 4)] {
        wire(
            &mut out,
            format!("J11-{label}"),
            "J11",
            label,
            format!("J11.{label}"),
            format!("mq6.{pin}"),
            "ribbon22",
            "SIG-12",
            "fixed",
            "",
        );
    }
    json!(out)
}
pub fn owner(part: &str) -> &str {
    if part.starts_with("wiring-junction-") {
        return "final-connections";
    }
    if part.starts_with("cold-core/")
        || [
            "pcba",
            "g-ganen-pump",
            "valve-v-b",
            "coil-v-b",
            "wago-v12",
            "wago-gnd",
            "wago-sensors",
            "wago-reeds-b",
        ]
        .contains(&part)
    {
        return "cold-core";
    }
    if ["pump-a-motor", "pump-b-motor"].contains(&part) {
        return "front-top";
    }
    if ["compressor", "condenser+fan", "thermal-fuse", "mq6-sensor"].contains(&part) {
        return "front-bottom";
    }
    if (part.starts_with("coil-v-") && part != "coil-v-a")
        || ["display", "wago-mana", "wago-manb"].contains(&part)
    {
        return "front-top";
    }
    "back-top"
}
pub fn interfaces(terminals: &Value, graph: &Value) -> Result<Value> {
    let used = rows(graph)?
        .iter()
        .flat_map(|c| [c["start"].as_str().unwrap(), c["end"].as_str().unwrap()])
        .collect::<BTreeSet<_>>();
    let mut buses = Vec::new();
    let parts = used
        .iter()
        .filter(|t| t.starts_with("wago-") || t.starts_with("join-"))
        .map(|t| terminals[*t]["part"].as_str().unwrap())
        .collect::<BTreeSet<_>>();
    for part in parts {
        let ports = used
            .iter()
            .filter(|t| terminals[**t]["part"] == part)
            .collect::<Vec<_>>();
        buses.push(json!({"id":part,"terminals":ports,"kind":"WAGO busbar"}));
    }
    let owners = used
        .iter()
        .map(|t| Ok(((*t).to_owned(), owner(string(&terminals[*t]["part"])?))))
        .collect::<Result<BTreeMap<_, _>>>()?;
    let mut crossing = Vec::new();
    for c in rows(graph)? {
        let from = owner(string(&terminals[string(&c["start"])?]["part"])?);
        let to = owner(string(&terminals[string(&c["end"])?]["part"])?);
        if from != to {
            crossing.push(json!({"wire":c["id"],"from":from,"to":to}));
        }
    }
    Ok(json!({"common_junctions":buses,"assembly_owners":owners,"crossing_wires":crossing}))
}
/// The terminals the wiring leaves unused and the interfaces it ends at, as the review lists them.
pub fn constants() -> Result<Value> {
    Ok(json!({"UNUSED":hsm_kernel::reads::json("tools/hsm/assembly-docs/src/wiring/unused.json")?,"BOUNDARIES":hsm_kernel::reads::json("tools/hsm/assembly-docs/src/wiring/boundaries.json")?}))
}
