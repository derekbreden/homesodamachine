use super::*;
use model::{V, add, mul, sub, v};
const RING_BORE: f64 = 3.2;
fn cylinder(radius: f64, height: f64, base: V, axis: V) -> Value {
    json!({"radius_mm":radius,"height_mm":height,"base_mm":base,"axis":axis})
}
fn ring(src: &sources::Sources) -> Result<(Value, sources::Bond)> {
    let d = terminals::bond(src)?;
    let t = d.ring_tongue_thickness_mm;
    let eye = d.ring_eye_diameter_mm;
    let barrel = d.ring_barrel_diameter_mm;
    let reach = d.ring_barrel_length_mm;
    Ok((
        json!({"kind":"ring","eye":cylinder(eye/2.,t,[0.;3],[0.,0.,1.]),"bore":cylinder(RING_BORE/2.,t+2.,[0.,0.,-1.],[0.,0.,1.]),"barrel":cylinder(barrel/2.,reach,[eye/2.-1.,0.,barrel/2.],[1.,0.,0.]),"origin_mm":d.contact_point_mm,"x_dir":d.wire_outward,"normal":d.contact_outward}),
        d,
    ))
}
pub fn inputs(
    src: &sources::Sources,
    at: &terminals::State,
    connections: &[graph::Connection],
) -> Result<Value> {
    let mut records = json!({});
    let mut bodies = Vec::new();
    let terminals = &at.terminals;
    let rotation = json!(sources::PORTS_FORE);
    let references = src.wago_references()?;
    let color = src.ac_hub_colour()?;
    for (id, point) in terminals::FINAL_JOINS {
        let name = format!("wiring-junction-{id}");
        bodies.push(json!([name,{"kind":"import","step":references["413"],"pose":{"rotation":rotation,"translation_mm":point}},color]));
        let mut used = BTreeSet::new();
        for connection in connections {
            for terminal in [&connection.start, &connection.end] {
                if terminal.starts_with(&format!("join-{id}.")) {
                    used.insert(terminal.to_owned());
                }
            }
        }
        let unused = (1..=3)
            .filter(|i| !used.contains(&format!("join-{id}.{i}")))
            .collect::<Vec<_>>();
        records[&name] = json!({"kind":"WAGO 221-413 final connection","size":"413","parent":"final-connections","translation_mm":point,"rotation":rotation,"terminal_ids":used,"unused_ports":unused,"mount":"Free connector retained by its dressed leads","assembly":"Connect through the open funnel after closing the quadrants; fit the frame afterward."});
    }
    let name = "terminal-carbonator-pe";
    let (ring, bond) = ring(src)?;
    bodies.push(json!([name, ring, [0.32, 0.55, 0.30]]));
    records[name] = json!({"kind":"M3 closed-ring earth terminal","terminal_ids":["carbonator.PE"],"attachment":"cold-core/carbonator-tube","status":"Nominal owned M3 / 22–16 AWG ring envelope; metal clamp defined by shared rim datums","tongue_thickness_mm":bond.ring_tongue_thickness_mm,"barrel_diameter_mm":bond.ring_barrel_diameter_mm,"barrel_length_mm":bond.ring_barrel_length_mm});
    for header in ["J1", "J2", "J3", "J4", "J5", "J6", "J7", "J9", "J11", "J13"] {
        let mut pins = terminals
            .iter()
            .filter(|(id, _)| id.starts_with(&format!("{header}.")))
            .map(|(_, v)| v)
            .collect::<Vec<_>>();
        pins.sort_by_key(|p| p.pin.parse::<i64>().unwrap());
        let first = pins.first().context("connector pins")?;
        let last = pins.last().unwrap();
        let a = first.point;
        let b = last.point;
        let centre = mul(add(a, b), 0.5);
        let row = sub(b, a);
        let axis = first.outward;
        let floor = sub(centre, mul(axis, 7.5));
        let width = (pins.len() as f64 - 1.) * 2.5 + 4.8;
        let name = format!("terminal-{header}");
        let bores = pins
            .iter()
            .map(|p| cylinder(0.98, 7.7, sub(p.point, mul(axis, 7.6)), axis))
            .collect::<Vec<_>>();
        bodies.push(json!([name,{"kind":"housing","origin_mm":floor,"x_dir":row,"normal":axis,"dimensions_mm":[width,5.7,7.5],"bores":bores},[0.86,0.85,0.79]]));
        let mating=pins.iter().map(|p|(p.id.as_str(),json!({"part":p.part,"point":p.point,"outward":p.outward,"pin":p.pin}))).collect::<BTreeMap<_,_>>();
        records[&name] = json!({"kind":"JST-XH housing envelope","housing":format!("XHP-{}",pins.len()),"dimensions_mm":[width,5.7,7.5],"assembled_height_above_board_mm":9.8,"source":"https://www.jst-mfg.com/product/pdf/eng/eXH.pdf","status":"nominal envelope; latch detail and on-hand clone fit unqualified","terminal_ids":pins.iter().map(|p|p.id.clone()).collect::<Vec<_>>(),"mating_terminals":mating});
    }
    for (label, lead) in &at.fuse_leads {
        let segments = model::rounded(&json!(lead.points_mm), lead.bend_radius_mm, true, 0.44)?;
        let name = format!("terminal-fuse-{label}-lead");
        bodies.push(json!([name,{"kind":"sweep","connection_id":format!("fuse-{label}"),"points_mm":lead.points_mm,"segments":segments,"diameter_mm":lead.lead_diameter_mm},[0.62,0.63,0.65]]));
        let mut record = serde_json::to_value(lead)?;
        record["kind"] = json!("Dressed thermal-fuse lead");
        record["segments"] = segments.clone();
        record["retained_lead_length_mm"] = json!(
            lead.native_straight_mm
                + rows(&segments)?
                    .iter()
                    .map(|s| number(&s["length_mm"]))
                    .collect::<Result<Vec<_>>>()?
                    .into_iter()
                    .sum::<f64>()
                - 1.5
        );
        record["reference_stub_overlap_mm"] = json!(1.5);
        record["terminal_ids"] = json!([format!("fuse.{label}")]);
        records[name] = record;
        let t = at.terminal(&format!("fuse.{label}"))?;
        let p = t.point;
        let axis = t.outward;
        let name = format!("terminal-fuse-{label}-splice");
        bodies.push(json!([name,{"kind":"sleeve","outer":cylinder(1.6,6.,p,axis),"inner":cylinder(1.3,6.02,sub(p,mul(axis,0.01)),axis)},[0.04,0.04,0.045]]));
        records[name] = json!({"kind":"Insulated fuse-splice envelope","outer_diameter_mm":3.2,"length_mm":6.,"status":"proposed joint and recovered sleeve profile","terminal_ids":[format!("fuse.{label}")]});
    }
    Ok(json!([bodies, records]))
}
