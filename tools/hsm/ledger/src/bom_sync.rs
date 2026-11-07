//! bom.md's and labor.md's hardware: what one machine takes, counted from the machine and its
//! parts, priced from the packs it is bought in, and stated where the two ledgers name it.
use crate::{labor, shared::*};
use anyhow::{Context as _, Result, ensure};
use hsm_documents::Variables;
use num_bigint::BigInt;
use num_traits::{Signed, Zero};
use serde_json::{Value, json};
use std::collections::{BTreeMap, BTreeSet};

/// Decimal text as an exact rational; used for the paid pack allocations.
fn rational(text: &str) -> Result<(i128, i128)> {
    let (lower, exponent) = text
        .split_once(['e', 'E'])
        .map(|(a, b)| (a, b.parse::<i32>()))
        .unwrap_or((text, Ok(0)));
    let exponent = exponent?;
    let places = lower
        .split_once('.')
        .map(|(_, s)| s.len() as i32)
        .unwrap_or(0)
        - exponent;
    let digits = lower
        .replace('.', "")
        .parse::<i128>()
        .context("decimal allocation amount")?;
    Ok(if places >= 0 {
        (digits, 10i128.pow(places as u32))
    } else {
        (digits * 10i128.pow((-places) as u32), 1)
    })
}
fn exact_decimal(text: &str) -> Result<(BigInt, BigInt)> {
    let (lower, exponent) = text
        .split_once(['e', 'E'])
        .map(|(a, b)| (a, b.parse::<i32>()))
        .unwrap_or((text, Ok(0)));
    let places = lower
        .split_once('.')
        .map(|(_, s)| s.len() as i32)
        .unwrap_or(0)
        - exponent?;
    let digits: BigInt = lower
        .replace('.', "")
        .parse()
        .context("decimal allocation amount")?;
    let power = BigInt::from(10).pow(places.unsigned_abs());
    Ok(if places >= 0 {
        (digits, power)
    } else {
        (digits * power, BigInt::from(1))
    })
}
fn rounded_cost(numerator: BigInt, denominator: BigInt) -> Result<String> {
    ensure!(!denominator.is_zero(), "zero pack quantity");
    let sign = if numerator.is_negative() != denominator.is_negative() {
        "-"
    } else {
        ""
    };
    let (n, d) = (numerator.abs() * 100, denominator.abs());
    let half_up = if (&n % &d) * 2 >= d { 1 } else { 0 };
    let cents: BigInt = n / d + half_up;
    Ok(format!("${sign}{}.{:02}", &cents / 100, &cents % 100))
}
fn pack_cost(quantity: f64, price: &str, count: &str) -> Result<String> {
    pack_cost_text(&quantity.to_string(), price, count)
}
fn pack_cost_text(quantity: &str, price: &str, count: &str) -> Result<String> {
    let (qn, qd) = exact_decimal(quantity)?;
    let (pn, pd) = exact_decimal(price)?;
    let (cn, cd) = exact_decimal(count)?;
    rounded_cost(qn * pn * cd, qd * pd * cn)
}
fn stem_cost(quantity: f64) -> Result<String> {
    let (qn, qd) = exact_decimal(&quantity.to_string())?;
    rounded_cost(qn * 3618 * 17354, qd * 100 * 30 * 14722)
}
fn decimal_divide_1000(value: f64) -> String {
    let text = value.to_string();
    if let Ok((n, d)) = rational(&text) {
        let d = d * 1000;
        let mut places = 0;
        let mut divisor = d;
        while divisor > 1 && divisor % 10 == 0 {
            places += 1;
            divisor /= 10;
        }
        if divisor == 1 {
            let sign = if n < 0 { "-" } else { "" };
            let n = n.abs();
            let whole = n / d;
            let fraction = format!("{:0width$}", n % d, width = places);
            let fraction = fraction.trim_end_matches('0');
            return if fraction.is_empty() {
                format!("{sign}{whole}")
            } else {
                format!("{sign}{whole}.{fraction}")
            };
        }
    }
    (value / 1000.).to_string()
}


/// What bom.md's and labor.md's hardware is counted and priced from: the installed machine, its
/// manifold and harness, and the parts' own numbers.
pub struct Inputs {
    /// The bodies the installed machine places, and every body it stands.
    pub placed: BTreeSet<String>,
    pub bodies: BTreeSet<String>,
    /// Each drawn run's length, mm, by its id.
    pub run_lengths: BTreeMap<String, f64>,
    /// The compressor's floor bosses, the condenser's mount screws and the collet plate's tees,
    /// as the box seats them.
    pub floor_bosses: usize,
    pub condenser_screws: usize,
    pub dock_tees: usize,
    /// How far the compressor's grommets squeeze onto their bosses, mm.
    pub floor_grommet_squeeze: f64,
    pub manifold: Manifold,
    pub wire: Wire,
    pub coil: Coil,
    /// The PRV vent's tube along its centreline, mm.
    pub prv_vent: f64,
    pub faucet: Faucet,
    /// Reservoir A's tied stations, and the cap's six-inch tie paths.
    pub reservoir_a_ties: usize,
    pub cap_tie_paths: usize,
    /// The inserts on each of the foam cap's clamp faces and on each reservoir cap, and the reeds
    /// each reservoir carries.
    pub foam_cap_face_inserts: usize,
    pub reservoir_cap_inserts: usize,
    pub reeds_per_reservoir: usize,
    pub deck: Deck,
    /// The TouchFlo base's insert pods.
    pub touchflo_inserts: usize,
    /// The above-core union elbows and stem elbows.
    pub union_elbows: usize,
    pub stem_elbows: usize,
    /// The relays the machine places, and the supply's ceiling screws.
    pub relays: usize,
    pub psu_screws: usize,
    pub relay: Relay,
    pub c14: C14,
    /// The rods one flank's Y stack takes, and the funnel frame's screws.
    pub seam_rods: usize,
    pub funnel_screws: usize,
    pub compressor: Compressor,
}

/// The manifold's solenoids, purchased tees and lower returns, and a pump tube's cut, mm.
pub struct Manifold {
    pub solenoids: usize,
    pub purchased_tees: usize,
    pub lower_returns: usize,
    pub pump_tube_cut: f64,
}

/// The AC harness's 16 AWG cut lengths, mm.
pub struct Wire {
    pub mid: f64,
    pub short_2: f64,
    pub short: f64,
    pub dc1: f64,
    pub dc2: f64,
    pub opening_join: f64,
}

/// The evaporator coil: its pitch, the copper in its laid wrap and in one carbonator's cut, mm,
/// what a roll has left, ft, the inlet's and outlet's stub allowances, mm, and the carbonators
/// one roll winds.
pub struct Coil {
    pub pitch: f64,
    pub wrap: f64,
    pub cut: f64,
    pub spare_ft: f64,
    pub stubs: [f64; 2],
    pub per_roll: u32,
}

/// The faucet's flavor and soda tube cuts, mm.
pub struct Faucet {
    pub flavor_cut: f64,
    pub soda_cut: f64,
}

/// The main board's deck screws: how many, the board they cross, how far each reaches into its
/// column and the pilot the column is bored to, mm.
pub struct Deck {
    pub screws: usize,
    pub board: f64,
    pub reach: f64,
    pub bore: f64,
}

/// A relay board's wall screws: how many, the board they cross, the setback to the insert's face,
/// the insert, how far a screw reaches into it, the pilot, and the least wall behind a pilot,
/// plain and under the flutes, mm.
pub struct Relay {
    pub screws: usize,
    pub board: f64,
    pub setback: f64,
    pub insert: f64,
    pub reach: f64,
    pub bore: f64,
    pub backing: f64,
    pub fluted_backing: f64,
}

/// The C14 inlet's flange screws: how many, the flange they cross, the pilot and how far each
/// screw reaches past the flange and its washer, mm.
pub struct C14 {
    pub screws: usize,
    pub flange: f64,
    pub bore: f64,
    pub reach: f64,
}

/// The compressor plate's bolt bore and the plate it leaves outboard of each hole, mm.
pub struct Compressor {
    pub bore: f64,
    pub ligament: f64,
}

/// What one machine takes that no input counts: the carbonator's end-cap plates, ports and
/// reeds; the flavor reservoirs; the panel's umbilical bulkhead; the foam cap's clamp faces, top
/// and bottom; the flanks a seam rod pair stands in; the four-inch ties the cable runs and the
/// vent adapter's lands take beside reservoir A's; the ASSE split's tee beside the manifold's
/// own; the funnel drain's stem elbow; and the screws, each in a short insert, that hold the
/// nameplate, the display cover and the status plate.
const END_CAPS: f64 = 2.;
const CARBONATOR_PORTS: f64 = 4.;
const CARBONATOR_REEDS: f64 = 2.;
const RESERVOIRS: f64 = 2.;
const UMBILICAL_BULKHEADS: f64 = 1.;
const FOAM_CAP_FACES: f64 = 2.;
const FLANKS: f64 = 2.;
const CABLE_TIES: f64 = 15.;
const VENT_LAND_TIES: f64 = 2.;
const WATER_SPLIT_TEES: f64 = 1.;
const FUNNEL_DRAIN_ELBOWS: f64 = 1.;
const NAMEPLATE_SCREWS: f64 = 4.;
const DISPLAY_COVER_SCREWS: f64 = 4.;
const STATUS_PLATE_SCREWS: f64 = 4.;

/// The machine's runs in the faucet's 4 mm flavor tube.
const FLAVOR_TUBE_RUNS: [&str; 2] = ["fluid-18", "fluid-28"];

/// A pack the ledger buys in: what it cost and how many it holds, as its purchase states them.
struct Pack(&'static str, &'static str);
const RC62: Pack = Pack("88.28", "30");
const TEES: Pack = Pack("42.68", "20");
const FOUR_INCH_TIES: Pack = Pack("4.28", "200");
const SIX_INCH_TIES: Pack = Pack("6.42", "100");
const SOLID16_SPOOL: Pack = Pack("12.86", "7.62");
const SMALL_WASHERS: Pack = Pack("7.82", "200");
const M3X6: Pack = Pack("7.64", "120");
const M3X8: Pack = Pack("7.71", "120");
const M3X10: Pack = Pack("8.57", "120");
const M3X12: Pack = Pack("8.57", "120");
const RESERVOIR_SCREWS: Pack = Pack("8.66", "120");
const M5X100: Pack = Pack("7.70", "20");
const PP0308E: Pack = Pack("68.49", "30");
const M3_INSERTS: Pack = Pack("10.71", "100");
const M5_INSERTS: Pack = Pack("10.71", "50");

/// The funnel's silicone kit: what it mixes, g, and what it cost; the flavor tube's price per
/// foot; and a foot, mm.
const FUNNEL_KIT_G: f64 = 1098.0;
const FUNNEL_KIT_PRICE: f64 = 35.16;
const FLAVOR_TUBE_PER_FT: f64 = 0.13;
const FOOT: f64 = 304.8;

fn cost(quantity: f64, pack: Pack) -> Result<String> {
    pack_cost(quantity, pack.0, pack.1)
}
fn count(value: f64) -> String {
    fmt(value, ".4g")
}
fn mm(value: f64, spec: &str) -> String {
    format!("{} mm", fmt(value, spec))
}
fn ft(value: f64) -> String {
    format!("{} ft", fmt(value, ".4g"))
}

/// The machine's checks on what the hardware rows bill: no tray or panel stands under the
/// valves and pumps, no added cover over the compressor, and the display's cover and gasket
/// still stand.
fn check(input: &Inputs) -> Result<()> {
    let trays: Vec<_> = input
        .placed
        .iter()
        .filter(|s| s.contains("tray") || s.starts_with("valve-panel"))
        .collect();
    ensure!(
        trays.is_empty(),
        "the machine places {} body(ies) under its valves and pumps ({trays:?}) — a seat is printed into the piece that carries it, and bom.md §7 bills no part standing under one",
        trays.len()
    );
    ensure!(
        !input.placed.contains("compressor-shroud"),
        "the machine places `compressor-shroud` and bom.md §5 bills no added sheet-metal cover over the compressor — add the cut-part row, its cable gland and its bond back with it"
    );
    let missing: Vec<_> = ["display-cover", "display-gasket"]
        .into_iter()
        .filter(|s| !input.bodies.contains(*s))
        .collect();
    ensure!(
        missing.is_empty(),
        "the machine no longer stands {missing:?} — bom.md §7 bills the display's snap-retained cover and its gasket"
    );
    Ok(())
}

/// bom.md's and labor.md's hardware figures, counted from `input` and priced from their packs.
fn figures(input: &Inputs, casting: &Value) -> Result<(Variables, Variables)> {
    check(input)?;
    let n = |value: usize| value as f64;
    let mut bom = labor::casting_figures(casting)?;
    let mut put = |name: &str, value: String| {
        bom.insert(name.into(), value);
    };
    let mixed = num(&casting["mixed_g"])?;
    put("FUNNEL_KIT_YIELD", fmt(FUNNEL_KIT_G / mixed, ".2f"));
    put("FUNNEL_BATCH_COST", format!("${}", fmt((FUNNEL_KIT_PRICE * mixed) / FUNNEL_KIT_G, ".2f")));

    // The carbonator, the reservoirs and the floats over them, and the reeds they carry.
    let floats = 1. + RESERVOIRS;
    let reservoir_reeds = n(input.reeds_per_reservoir) * RESERVOIRS;
    put("END_CAPS", count(END_CAPS));
    put("CARBONATOR_PORTS", count(CARBONATOR_PORTS));
    put("RESERVOIRS", count(RESERVOIRS));
    put("AERO_FLOATS", count(floats));
    put("RC62_TOTAL", count(floats));
    put("RC62_COST", cost(floats, RC62)?);
    put("REEDS_PER_RES", count(n(input.reeds_per_reservoir)));
    put("CARB_REEDS", count(CARBONATOR_REEDS));
    put("RES_REEDS_TOTAL", count(reservoir_reeds));
    put("REEDS_TOTAL", count(CARBONATOR_REEDS + reservoir_reeds));

    // The manifold, the ties and the harness.
    let tees = n(input.manifold.purchased_tees) + WATER_SPLIT_TEES;
    let four_inch_ties = CABLE_TIES + VENT_LAND_TIES + n(input.reservoir_a_ties);
    let six_inch_ties = n(input.cap_tie_paths);
    put("SOLENOIDS", count(n(input.manifold.solenoids)));
    put("TEES", count(tees));
    put("TEES_COST", cost(tees, TEES)?);
    put("FOUR_INCH_TIES", count(four_inch_ties));
    put("FOUR_INCH_TIES_COST", cost(four_inch_ties, FOUR_INCH_TIES)?);
    put("RESERVOIR_A_TIES", fmt(n(input.reservoir_a_ties), ""));
    put("SIX_INCH_TIES", count(six_inch_ties));
    put("SIX_INCH_TIES_COST", cost(six_inch_ties, SIX_INCH_TIES)?);
    let w = &input.wire;
    let wire = 5. * w.mid + 2. * w.short_2 + w.short + 2. * w.dc1 + w.dc2 + 2. * w.opening_join;
    // The allocation is the cut, an exact decimal in metres, rounded up to a tenth of a metre.
    let (wn, wd) = rational(&wire.to_string())?;
    let allocation = ((wn + wd * 100 - 1) / (wd * 100)) as f64 / 10.;
    put("SOLID16_CUT_LENGTH", format!("{} m", decimal_divide_1000(wire)));
    put("SOLID16_ALLOCATION", format!("{allocation} m"));
    put("SOLID16_COST", cost(allocation, SOLID16_SPOOL)?);
    put("PP1208E_PANEL", count(UMBILICAL_BULKHEADS));

    // The cold core's casing, the deck, the reservoir caps and the faucet's base.
    let deck_inserts = n(input.deck.screws);
    let clamp_inserts = n(input.foam_cap_face_inserts) * FOAM_CAP_FACES;
    let reservoir_inserts = n(input.reservoir_cap_inserts) * RESERVOIRS;
    let touchflo = n(input.touchflo_inserts);
    put("FOAM_INSERTS", count(deck_inserts));
    put("FOAM_CLAMP_INSERTS", count(clamp_inserts));
    put("FOAM_SCREWS", count(clamp_inserts));
    put("RES_INSERTS_PER_CAP", count(n(input.reservoir_cap_inserts)));
    put("RES_INSERTS", count(reservoir_inserts));
    put("RES_SCREWS", count(reservoir_inserts));
    put("RES_SCREWS_COST", cost(reservoir_inserts, RESERVOIR_SCREWS)?);
    put("TOUCHFLO_INSERTS", count(touchflo));
    put("TOUCHFLO_SCREWS", count(touchflo));

    // The electronics: the supply on the ceiling, the main board on the deck, the relays on the
    // west flank; the condenser's fingers.
    let (deck, relay, c14) = (&input.deck, &input.relay, &input.c14);
    let psu = n(input.psu_screws);
    let pcba = n(deck.screws);
    let relays = n(input.relays) * n(relay.screws);
    let shelf = pcba + psu + relays;
    let condenser = n(input.condenser_screws);
    put("SHELF_INSERTS", count(psu));
    put("SHELF_SCREWS", count(shelf));
    put("SHELF_SCREWS_PSU", count(psu));
    put("SHELF_SCREWS_PCBA", count(pcba));
    put("SHELF_SCREWS_RELAY", count(relays));
    put("COND_INSERTS", count(condenser));
    put("COND_SCREWS", count(condenser));
    put("PCBA_BOARD_T", fmt(deck.board, "g"));
    put("PCBA_SCREW_REACH", fmt(deck.reach, ".3g"));
    put("PCBA_SCREW_TIP", fmt(deck.bore - deck.reach, ".3g"));
    put("RELAY_BOARD_T", fmt(relay.board, "g"));
    put("RELAY_INSERT_LEN", fmt(relay.insert, "g"));
    put("RELAY_INSERT_SETBACK", fmt(relay.setback, "g"));
    put("RELAY_BACKING", fmt(relay.backing, ".3g"));
    put("RELAY_FLUTED_BACKING", fmt(relay.fluted_backing, ".3g"));
    put("RELAY_BORE", fmt(relay.bore, ".3g"));
    put("RELAY_SCREW_REACH", fmt(relay.reach, ".3g"));
    put("RELAY_SCREW_TIP", fmt(relay.bore - relay.reach, ".3g"));

    // The C14 inlet, each flange screw on a washer over the moulding's countersink.
    let c14_screws = n(c14.screws);
    put("C14_FLANGE_T", fmt(c14.flange, "g"));
    put("C14_BORE", fmt(c14.bore, "g"));
    put("C14_SCREW_REACH", fmt(c14.reach, ".3g"));
    put("C14_INSERTS", count(c14_screws));
    put("C14_SCREWS", count(c14_screws));
    put("SMALL_WASHERS", fmt(c14_screws, "g"));
    put("SMALL_WASHERS_COST", cost(c14_screws, SMALL_WASHERS)?);

    // The screws by length.
    let m3x6 = NAMEPLATE_SCREWS + DISPLAY_COVER_SCREWS + STATUS_PLATE_SCREWS;
    let m3x8 = pcba + condenser + relays + touchflo;
    let m3x10 = c14_screws + psu;
    let funnel = n(input.funnel_screws);
    put("M3X6_TOTAL", count(m3x6));
    put("M3X6_COST", cost(m3x6, M3X6)?);
    put("M3X8_TOTAL", count(m3x8));
    put("M3X8_COST", cost(m3x8, M3X8)?);
    put("M3X10_TOTAL", count(m3x10));
    put("M3X10_COST", cost(m3x10, M3X10)?);
    put("M3X12_TOTAL", count(funnel));
    put("M3X12_COST", cost(funnel, M3X12)?);
    put("NAMEPLATE_SCREWS", count(NAMEPLATE_SCREWS));
    put(
        "NAMEPLATE_MOUNT",
        format!(
            "retained in `enclosure-back-top` by {} black M3 × 6 socket-head screws and {} short RX-M3S × 4 inserts in a solid receiver.",
            fmt(NAMEPLATE_SCREWS, ""),
            fmt(NAMEPLATE_SCREWS, "")
        ),
    );
    put("DISPLAY_COVER_SCREWS", count(DISPLAY_COVER_SCREWS));
    put(
        "DISPLAY_COVER_MOUNT",
        format!(
            "retained flush with `enclosure-front-top`'s display plane by {} black M3 socket-head screws in {} short inserts, arranged along the side borders. The flat TPU ring bears between the cover's lap and the glass.",
            fmt(DISPLAY_COVER_SCREWS, ""),
            fmt(DISPLAY_COVER_SCREWS, "")
        ),
    );
    put("FUNNEL_FRAME_SCREWS", count(funnel));
    put("ROOF_CLOSURE_INSERTS", count(funnel));
    put("ROOF_CLOSURE_SCREWS", count(funnel));
    let seam_rods = FLANKS * n(input.seam_rods);
    put("SEAM_RODS", count(seam_rods));
    put("SEAM_INSERTS", count(seam_rods));
    put("M5X100_TOTAL", count(seam_rods + clamp_inserts));
    put("M5X100_COST", cost(seam_rods + clamp_inserts, M5X100)?);
    put("SEAM_SCREW_UNIT_COST", cost(1.0, M5X100)?);

    // The pump dock and the stem and union elbows.
    let returns = n(input.manifold.lower_returns);
    let stem_elbows = FUNNEL_DRAIN_ELBOWS + 2. * returns + n(input.stem_elbows);
    put("DOCK_PUMP_TUBES", fmt(n(input.dock_tees), ""));
    put("PUMP_TUBE_CUT", mm(input.manifold.pump_tube_cut, ".3g"));
    put("DOCK_TEES", count(n(input.dock_tees)));
    put("DOCK_ELBOWS", fmt(2.0 * returns, ""));
    put("STEM_ELBOWS", count(stem_elbows));
    put("STEM_ELBOWS_COST", stem_cost(stem_elbows)?);
    put("PP0308E_TOTAL", fmt(n(input.union_elbows), ""));
    put("PP0308E_COST", cost(n(input.union_elbows), PP0308E)?);

    // The compressor's floor posts.
    let floor = n(input.floor_bosses);
    let compressor = &input.compressor;
    put("FLOOR_INSERTS", count(floor));
    put("FLOOR_SCREWS", count(floor));
    put("FLOOR_WASHERS", count(floor));
    put("COMPRESSOR_LIGAMENT", fmt(compressor.ligament, ".4g"));
    put("COMPRESSOR_BORE", fmt(compressor.bore, ".4g"));
    put("WASHER_MAX_OD", fmt(compressor.bore + (2.0 * compressor.ligament), ".4g"));
    put("GROMMET_SQUEEZE", fmt(input.floor_grommet_squeeze, ".4g"));

    // The inserts by body.
    let m3_long = deck_inserts + reservoir_inserts + condenser + funnel;
    let m3_short = NAMEPLATE_SCREWS + DISPLAY_COVER_SCREWS + STATUS_PLATE_SCREWS + touchflo + psu + c14_screws + relays;
    let m3_inserts = m3_long + m3_short;
    let m5_inserts = floor + seam_rods + clamp_inserts;
    put("TOTAL_M3_INSERTS", count(m3_inserts));
    put("M3_LONG_INSERTS", count(m3_long));
    put("M3_LONG_INSERTS_COST", cost(m3_long, M3_INSERTS)?);
    put("M3_SHORT_INSERTS", count(m3_short));
    put("M3_SHORT_INSERTS_COST", cost(m3_short, M3_INSERTS)?);
    put("TOTAL_M5_INSERTS", count(m5_inserts));
    put("M5_INSERTS_COST", cost(m5_inserts, M5_INSERTS)?);

    // The copper coil, the PRV's vent and the faucet's tubes.
    let coil = &input.coil;
    let flavor_tube = 2. * input.faucet.flavor_cut
        + FLAVOR_TUBE_RUNS.iter().filter_map(|id| input.run_lengths.get(*id)).sum::<f64>();
    put("PITCH", mm(coil.pitch, ".4g"));
    put("LAID_FT", ft(coil.wrap / FOOT));
    put("STUB_INLET", mm(coil.stubs[0], ".4g"));
    put("STUB_OUTLET", mm(coil.stubs[1], ".4g"));
    put("ROLL_SHARE", format!("1/{}", fmt(f64::from(coil.per_roll), "")));
    put("CUT_FT", ft(coil.cut / FOOT));
    put("ROLL_SPARE", format!("{} ft", fmt(coil.spare_ft, "+.2f")));
    put("PRV_VENT_MM", mm(input.prv_vent, ".0f"));
    put("FLAVOR_CUT", fmt(input.faucet.flavor_cut, "g"));
    put("FLAVOR_4MM_FT", fmt(flavor_tube / FOOT, ".2f"));
    put("FLAVOR_4MM_COST", format!("${}", fmt((flavor_tube / FOOT) * FLAVOR_TUBE_PER_FT, ".2f")));
    put("SODA_FAUCET_CUT", fmt(input.faucet.soda_cut, "g"));
    put("SODA_FAUCET_FT", fmt(input.faucet.soda_cut / FOOT, ".2f"));

    // labor.md's assembly: every insert pressed and every screw driven.
    let m3_screws = reservoir_inserts + touchflo + shelf + condenser + NAMEPLATE_SCREWS + DISPLAY_COVER_SCREWS + c14_screws + funnel;
    let m5_screws = floor + seam_rods + clamp_inserts;
    let mut labor = Variables::new();
    for (name, value) in [
        ("TOTAL_INSERTS", m3_inserts + m5_inserts),
        ("TOTAL_SCREWS", m3_screws + m5_screws),
        ("TOTAL_M3_INSERTS", m3_inserts),
        ("TOTAL_M5_INSERTS", m5_inserts),
        ("SEAM_INSERTS", seam_rods),
        ("SEAM_RODS", seam_rods),
        ("FOAM_CLAMP_INSERTS", clamp_inserts),
        ("FOAM_SCREWS", clamp_inserts),
        ("RES_SCREWS", reservoir_inserts),
        ("TOUCHFLO_SCREWS", touchflo),
        ("SHELF_INSERTS", psu),
        ("SHELF_SCREWS", shelf),
        ("COND_SCREWS", condenser),
        ("DISPLAY_COVER_SCREWS", DISPLAY_COVER_SCREWS),
        ("C14_SCREWS", c14_screws),
        ("ROOF_CLOSURE_SCREWS", funnel),
        ("NAMEPLATE_SCREWS", NAMEPLATE_SCREWS),
        ("FLOOR_SCREWS", floor),
        ("SOLENOIDS", n(input.manifold.solenoids)),
    ] {
        labor.insert(name.into(), count(value));
    }
    Ok((bom, labor))
}

/// Writes bom.md's and labor.md's hardware figures, counted and priced from `input`.
pub fn sync(input: &Inputs, ctx: &mut Context) -> Result<Value> {
    let casting = labor::casting_estimate(&json!({}), ctx)?;
    let (bom, labor) = figures(input, &casting)?;
    for (document, figures) in [("hardware/ledger/bom.md", &bom), ("hardware/ledger/labor.md", &labor)] {
        let path = ctx.root.join(document);
        ctx.substitute(&path, figures, BOM_PROGRAM)?;
    }
    Ok(main_result(0, "-> bom.md\n-> labor.md\n".into()))
}
