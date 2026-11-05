//! `_bom`: every cold-core row of the bill, against the body that realizes it.

use super::cold_scorecard;
use super::*;

pub const NAME: &str = "_bom";

pub const UNBILLED_PREFIXES: [&str; 2] = ["line-", "tube-"];

/// The bodies one bill row claims.
enum Bodies {
    Named(&'static [&'static str]),
    /// `tuple(f'cap-clamp-{side}-{i}' for side in ('top', 'bottom') for i in range(1, 11))`.
    CapClamps,
}
use Bodies::{CapClamps, Named};

/// `PARTS`: (label, the text its bom.md row carries, the bodies it is).
const TABLE: [(&str, &str, Bodies); 38] = [
    ("316 tube", "OnlineMetals #12498", Named(&["carbonator-tube"])),
    ("endcap plates", "SendCutSend 1/4\"-thick 316 SS circular endcap plate", Named(&["endcap-bottom", "endcap-top"])),
    ("earth clamp screw", "Carbonator earth-clamp screw", Named(&["carbonator-earth-screw"])),
    ("earth clamp lockwasher", "DIN 6797", Named(&["carbonator-earth-lockwasher"])),
    ("top-plate elbows", "TAISHER 2PCS 316L SS 90° Barstock Street Elbow", Named(&["carbonator-elbow-water-in", "carbonator-elbow-prv"])),
    ("bottom-plate elbows", "neoFit AME4-N2-E", Named(&["carbonator-elbow-co2-in", "carbonator-elbow-carb-water-out"])),
    ("water inlet jet", "Water-inlet jet cap", Named(&["water-inlet-jet-cap-nominal"])),
    ("upper float stop", "Carbonator upper float stop", Named(&["float-stop-carb-top"])),
    ("PRV", "Control Devices SV-125", Named(&["prv-sv125"])),
    ("PTFE thread tape", "Millrose 70894 Nickel Guard", Named(&[])),
    ("water PTC collet", "John Guest PP010822E", Named(&["collet-water-in"])),
    ("evaporator coil", "GOORY 1/4\" OD × 50 ft ACR copper coil", Named(&["evap-coil", "evap-tail-inlet", "evap-tail-outlet"])),
    ("carbonator probe", "TIEXYE DS18B20", Named(&["probe-carbonator-ds18b20"])),
    ("coil probe", "DS18S20+ TO-92", Named(&["probe-coil-ds18s20"])),
    ("pour-in-place foam", "closed-cell pour-in-place PU foam", Named(&[])),
    ("foil tape", "3M 425 aluminum foil tape", Named(&[])),
    ("foam shell", "Cold-core inner shell (foam-shell)", Named(&["foam-shell"])),
    ("foam cap lid top", "Cold-core foam cap lid — top", Named(&["foam-cap-lid-top"])),
    ("foam cap bottom", "Cold-core foam cap — bottom", Named(&["foam-cap-bottom"])),
    ("B-fill bend holder", "Reservoir B fill bend holder", Named(&["reservoir-b-fill-guide"])),
    ("PRV shroud", "PRV shroud", Named(&["prv-shroud"])),
    ("reservoir body L", "Flavor reservoir body — left", Named(&["reservoir-b"])),
    ("reservoir body R", "Flavor reservoir body — right", Named(&["reservoir-a"])),
    ("reservoir cap L", "Flavor reservoir cap — left", Named(&["reservoir-b-cap"])),
    ("reservoir cap R", "Flavor reservoir cap — right", Named(&["reservoir-a-cap"])),
    ("reservoir gaskets", "2× reservoir gasket", Named(&["reservoir-a-gasket", "reservoir-b-gasket"])),
    ("reed bridge", "Carbonator reed bridge", Named(&["reed-bridge"])),
    ("floats", "ASA Aero magnetic float", Named(&["float-carb", "float-a", "float-b"])),
    ("float magnets", "K&J Magnetics RC62 N42 ring magnet", Named(&["float-carb", "float-a", "float-b"])),
    ("reed columns", "Pre-soldered reed-and-wire column", Named(&[])),
    ("float rods", "Tandefio 1/8\" × 12\" 316 SS round rod", Named(&["float-rod-carb", "float-rod-a", "float-rod-b"])),
    ("reeds", "Littelfuse MDSR-7-10-15 reed switches", Named(&["reed-carb-1", "reed-carb-2", "reed-a-1", "reed-a-2", "reed-a-3", "reed-a-4", "reed-b-1", "reed-b-2", "reed-b-3", "reed-b-4"])),
    ("M3 heat-set inserts", "ruthex RX-M3 × 5.7 full-length heat-set inserts", Named(&[])),
    ("M5 closure inserts", "ruthex M5 Threaded Inserts", Named(&[])),
    ("cap clamp screws", "SVLING M5 × 0.8 × 100 mm", CapClamps),
    ("reservoir cap screws", "BNUOK M3 × 12 mm socket head cap, 304 stainless", Named(&[])),
    ("reservoir tube grips", "4× reservoir tube grip", Named(&["reservoir-grip-a-fill", "reservoir-grip-a-draw", "reservoir-grip-b-fill", "reservoir-grip-b-draw"])),
    ("reservoir air grips", "2× reservoir air grip", Named(&["reservoir-grip-a-air", "reservoir-grip-b-air"])),
];

pub struct Part {
    pub label: &'static str,
    pub bills: &'static str,
    pub bodies: Vec<String>,
}

pub struct State {
    pub sys: Val,
    pub here: PathBuf,
    pub hw: PathBuf,
    pub check: Val,
    pub verdict: Val,
    pub bom: PathBuf,
    pub parts: Vec<Part>,
}

impl Module for State {
    const NAME: &'static str = NAME;
    fn init(rt: &Runtime) -> Result<Self> {
        let sys = rt.py("sys")?;
        let here = resolve(&rt.file(NAME));
        let hw = ancestor(&here, "hardware")?;
        let directory = here.parent().map(PathBuf::from).unwrap_or_default();
        if !sys.a("path")?.contains(&Val::Str(ps(&directory)))? {
            rt.sys_path_insert(0, &directory)?;
        }
        let card = cold_scorecard::state(rt)?;
        let bom = hw.join("ledger").join("bom.md");
        let parts = TABLE
            .iter()
            .map(|(label, bills, bodies)| Part {
                label: *label,
                bills: *bills,
                bodies: match bodies {
                    Named(names) => names.iter().map(|n| (*n).to_owned()).collect(),
                    CapClamps => ["top", "bottom"]
                        .iter()
                        .flat_map(|side| (1..11).map(move |i| format!("cap-clamp-{side}-{i}")))
                        .collect(),
                },
            })
            .collect();
        Ok(Self {
            sys,
            here,
            hw,
            check: card.check.clone(),
            verdict: card.verdict.clone(),
            bom,
            parts,
        })
    }
}

pub fn state(rt: &Runtime) -> Result<Rc<State>> {
    rt.state::<State>()
}

/// `_bill_text()`: the bill as it stands.
pub fn bill_text(rt: &Runtime) -> Result<String> {
    read_text(&state(rt)?.bom)
}

/// `check(placed)`: the `bom-covered` row, a `_card.Check`. `placed` holds the body names.
pub fn check(rt: &Runtime, placed: &[String]) -> Result<Val> {
    let s = state(rt)?;
    let bill = bill_text(rt)?;
    let has = |name: &str| placed.iter().any(|n| n == name);
    let mut claimed: Vec<&str> = vec![];
    let (mut missing_row, mut no_body, mut absent) = (vec![], vec![], vec![]);
    for part in &s.parts {
        if !bill.contains(part.bills) {
            missing_row.push(format!(
                "{}: no row in bom.md matching \"{}\"",
                part.label, part.bills
            ));
        }
        if part.bodies.is_empty() {
            no_body.push(format!(
                "{} — billed, no solid here (\"{}\")",
                part.label, part.bills
            ));
            continue;
        }
        let gone: Vec<&str> = part
            .bodies
            .iter()
            .map(String::as_str)
            .filter(|b| !has(*b))
            .collect();
        for body in &part.bodies {
            if !claimed.contains(&body.as_str()) {
                claimed.push(body.as_str());
            }
        }
        if !gone.is_empty() {
            absent.push(format!("{}: {} not placed", part.label, gone.join(", ")));
        }
    }
    let mut unclaimed: Vec<&str> = placed
        .iter()
        .map(String::as_str)
        .filter(|n| !claimed.contains(n) && !UNBILLED_PREFIXES.iter().any(|p| n.starts_with(p)))
        .collect();
    unclaimed.sort();
    let covered = s
        .parts
        .iter()
        .filter(|part| !part.bodies.is_empty() && part.bodies.iter().all(|b| has(b.as_str())))
        .count();
    let mut detail = missing_row;
    detail.extend(absent);
    detail.extend(no_body);
    detail.extend(unclaimed.iter().map(|n| format!("placed, unbilled: {n}")));
    let verdict = s.verdict.c(args![detail.is_empty()])?;
    s.check.c(args![
        "bom-covered",
        "Every billed cold-core part has a body here",
        "goal",
        verdict,
        format!("{covered}/{}", s.parts.len()),
        "a body per billed part",
        detail
    ])
}

/// `report(placed)`: the coverage line and what it misses.
pub fn report(rt: &Runtime, placed: &[String]) -> Result<()> {
    let c = check(rt, placed)?;
    rt.print(format!(
        "  bom coverage    {} billed parts carry a body",
        fv(&c.a("value")?, "")?
    ))?;
    for line in c.a("detail")?.iter()? {
        rt.print(format!("    {}", fv(&line, "")?))?;
    }
    Ok(())
}

/// The body names a `placed` mapping holds, in its order.
fn names(placed: &Val) -> Result<Vec<String>> {
    placed.iter()?.iter().map(String::from_val).collect()
}

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    let s = state(rt)?;
    ns.value("sys", s.sys.clone());
    ns.value("Path", rt.import_module("pathlib")?.a("Path")?);
    ns.value("_here", Val::Path(s.here.clone()));
    ns.value("_hw", Val::Path(s.hw.clone()));
    ns.value("Check", s.check.clone());
    ns.value("verdict", s.verdict.clone());
    ns.value("BOM", Val::Path(s.bom.clone()));
    ns.value(
        "PARTS",
        Val::Tuple(
            s.parts
                .iter()
                .map(|p| (p.label, p.bills, Tuple(p.bodies.clone())).to_val())
                .collect(),
        ),
    );
    ns.value("UNBILLED_PREFIXES", UNBILLED_PREFIXES);
    ns.func(rt, "_bill_text", |rt, _| Ok(Val::Str(bill_text(rt)?)));
    ns.func(rt, "check", |rt, c| {
        check(rt, &names(&c.req::<Val>(0, "placed")?)?)
    });
    ns.func(rt, "report", |rt, c| {
        report(rt, &names(&c.req::<Val>(0, "placed")?)?)?;
        Ok(Val::None)
    });
    Ok(())
}

#[allow(dead_code)]
pub fn main(_rt: &Runtime) -> Result<()> {
    Ok(())
}
