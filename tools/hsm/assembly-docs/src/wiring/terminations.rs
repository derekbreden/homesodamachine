use super::*;
use model::{V, add, mul, sub, v};
const RING_BORE: f64 = 3.2;
fn cylinder(radius: f64, height: f64, base: V, axis: V) -> Value {
    json!({"radius_mm":radius,"height_mm":height,"base_mm":base,"axis":axis})
}
fn ring() -> Result<(Value, Value)> {
    let d = terminals::bond()?;
    let t = number(&d["ring_tongue_thickness_mm"])?;
    let eye = number(&d["ring_eye_diameter_mm"])?;
    let barrel = number(&d["ring_barrel_diameter_mm"])?;
    let reach = number(&d["ring_barrel_length_mm"])?;
    Ok((
        json!({"kind":"ring","eye":cylinder(eye/2.,t,[0.;3],[0.,0.,1.]),"bore":cylinder(RING_BORE/2.,t+2.,[0.,0.,-1.],[0.,0.,1.]),"barrel":cylinder(barrel/2.,reach,[eye/2.-1.,0.,barrel/2.],[1.,0.,0.]),"origin_mm":d["contact_point_mm"],"x_dir":d["wire_outward"],"normal":d["contact_outward"]}),
        d,
    ))
}
pub fn inputs(at: &Value, connections: &Value) -> Result<Value> {
    let mut records = json!({});
    let mut bodies = Vec::new();
    let terminals = &at["terminals"];
    let rotation = get("above_core_wiring", "PORTS_FORE")?;
    let references = get("above_core_wiring", "REFERENCES")?;
    let color = get("above_core_wiring", "C_AC_HUB")?;
    for (id, point) in terminals::final_joins().as_object().unwrap() {
        let name = format!("wiring-junction-{id}");
        bodies.push(json!([name,{"kind":"import","step":references["413"],"pose":{"rotation":rotation,"translation_mm":point}},color]));
        let mut used = BTreeSet::new();
        for connection in rows(connections)? {
            for terminal in [&connection["start"], &connection["end"]] {
                let terminal = string(terminal)?;
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
    let (ring, bond) = ring()?;
    bodies.push(json!([name, ring, [0.32, 0.55, 0.30]]));
    records[name] = json!({"kind":"M3 closed-ring earth terminal","terminal_ids":["carbonator.PE"],"attachment":"cold-core/carbonator-tube","status":"Nominal owned M3 / 22–16 AWG ring envelope; metal clamp defined by shared rim datums","tongue_thickness_mm":bond["ring_tongue_thickness_mm"],"barrel_diameter_mm":bond["ring_barrel_diameter_mm"],"barrel_length_mm":bond["ring_barrel_length_mm"]});
    for header in ["J1", "J2", "J3", "J4", "J5", "J6", "J7", "J9", "J11", "J13"] {
        let mut pins = terminals
            .as_object()
            .context("wiring terminals")?
            .iter()
            .filter(|(id, _)| id.starts_with(&format!("{header}.")))
            .map(|(_, v)| v)
            .collect::<Vec<_>>();
        pins.sort_by_key(|p| p["pin"].as_str().unwrap().parse::<i64>().unwrap());
        let first = pins.first().context("connector pins")?;
        let last = pins.last().unwrap();
        let a = v(&first["point"])?;
        let b = v(&last["point"])?;
        let centre = mul(add(a, b), 0.5);
        let row = sub(b, a);
        let axis = v(&first["outward"])?;
        let floor = sub(centre, mul(axis, 7.5));
        let width = (pins.len() as f64 - 1.) * 2.5 + 4.8;
        let name = format!("terminal-{header}");
        let bores = pins
            .iter()
            .map(|p| {
                Ok(cylinder(
                    0.98,
                    7.7,
                    sub(v(&p["point"])?, mul(axis, 7.6)),
                    axis,
                ))
            })
            .collect::<Result<Vec<_>>>()?;
        bodies.push(json!([name,{"kind":"housing","origin_mm":floor,"x_dir":row,"normal":axis,"dimensions_mm":[width,5.7,7.5],"bores":bores},[0.86,0.85,0.79]]));
        let mating=pins.iter().map(|p|(p["id"].as_str().unwrap(),json!({"part":p["part"],"point":p["point"],"outward":p["outward"],"pin":p["pin"]}))).collect::<BTreeMap<_,_>>();
        records[&name] = json!({"kind":"JST-XH housing envelope","housing":format!("XHP-{}",pins.len()),"dimensions_mm":[width,5.7,7.5],"assembled_height_above_board_mm":9.8,"source":"https://www.jst-mfg.com/product/pdf/eng/eXH.pdf","status":"nominal envelope; latch detail and on-hand clone fit unqualified","terminal_ids":pins.iter().map(|p|p["id"].clone()).collect::<Vec<_>>(),"mating_terminals":mating});
    }
    for (label, lead) in at["fuse_leads"].as_object().context("fuse leads")? {
        let segments = model::rounded(
            &lead["points_mm"],
            number(&lead["bend_radius_mm"])?,
            true,
            0.44,
        )?;
        let name = format!("terminal-fuse-{label}-lead");
        bodies.push(json!([name,{"kind":"sweep","connection_id":format!("fuse-{label}"),"points_mm":lead["points_mm"],"segments":segments,"diameter_mm":lead["lead_diameter_mm"]},[0.62,0.63,0.65]]));
        let mut record = lead.clone();
        record["kind"] = json!("Dressed thermal-fuse lead");
        record["segments"] = segments.clone();
        record["retained_lead_length_mm"] = json!(
            number(&lead["native_straight_mm"])?
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
        let t = &terminals[format!("fuse.{label}")];
        let p = v(&t["point"])?;
        let axis = v(&t["outward"])?;
        let name = format!("terminal-fuse-{label}-splice");
        bodies.push(json!([name,{"kind":"sleeve","outer":cylinder(1.6,6.,p,axis),"inner":cylinder(1.3,6.02,sub(p,mul(axis,0.01)),axis)},[0.04,0.04,0.045]]));
        records[name] = json!({"kind":"Insulated fuse-splice envelope","outer_diameter_mm":3.2,"length_mm":6.,"status":"proposed joint and recovered sleeve profile","terminal_ids":[format!("fuse.{label}")]});
    }
    Ok(json!([bodies, records]))
}
