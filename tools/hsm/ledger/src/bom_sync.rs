//! Hardware counts and cost allocations from the current scalar provider records.
use crate::{labor, shared::*};
use anyhow::{Context as _, Result, bail, ensure};
use hsm_documents::Variables;
use num_bigint::BigInt;
use num_traits::{Signed, Zero};
use serde_json::{Value, json};
use std::collections::BTreeSet;

fn length(value: &Value) -> f64 {
    value
        .as_array()
        .map(Vec::len)
        .or_else(|| value.as_object().map(|v| v.len()))
        .unwrap_or(0) as f64
}
fn values(value: &Value) -> Vec<&Value> {
    if let Some(a) = value.as_array() {
        a.iter().collect()
    } else {
        value
            .as_object()
            .map(|v| v.values().collect())
            .unwrap_or_default()
    }
}
fn minimum(value: &Value) -> Result<f64> {
    values(value)
        .into_iter()
        .map(num)
        .collect::<Result<Vec<_>>>()?
        .into_iter()
        .reduce(f64::min)
        .context("empty receiving range")
}
fn maximum(value: &Value) -> Result<f64> {
    values(value)
        .into_iter()
        .map(num)
        .collect::<Result<Vec<_>>>()?
        .into_iter()
        .reduce(f64::max)
        .context("empty receiving range")
}

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
fn number_text(value: &Value) -> String {
    value
        .as_str()
        .map(str::to_owned)
        .unwrap_or_else(|| value.to_string())
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
fn stem_unit_text() -> String {
    let numerator: BigInt = BigInt::from(3618) * 17354;
    let denominator: BigInt = BigInt::from(100) * 30 * 14722;
    let digits = (&numerator / &denominator).to_string().len();
    let places = 28 - digits;
    let power = BigInt::from(10).pow(places as u32);
    let scaled = numerator * &power;
    let mut quotient = &scaled / &denominator;
    let twice = (&scaled % &denominator) * 2;
    if twice > denominator || (twice == denominator && (&quotient % 2) != BigInt::zero()) {
        quotient += 1;
    }
    format!(
        "{}.{:0width$}",
        &quotient / &power,
        &quotient % power,
        width = places
    )
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

fn counts(input: &Value) -> Result<Value> {
    let mut n = json!({});
    n["reeds_per_reservoir"] = input["reeds_per_reservoir"].clone();
    n["deck_mount_bore_depth"] = input["pcba_bore"].clone();
    macro_rules! put {
        ($name:ident,$value:expr) => {
            let $name: f64 = $value;
            n[stringify!($name)] = json!($name);
        };
    }
    let placed: BTreeSet<_> = strings(&input["placed"])?.into_iter().collect();
    let trays: Vec<_> = placed
        .iter()
        .filter(|s| s.contains("tray") || s.starts_with("valve-panel"))
        .collect();
    ensure!(
        trays.is_empty(),
        "the machine places {} body(ies) under its valves and pumps ({trays:?}) — a seat is printed into the piece that carries it, and bom.md §7 bills no part standing under one",
        trays.len()
    );
    ensure!(
        !placed.contains("compressor-shroud"),
        "the machine places `compressor-shroud` and bom.md §5 bills no added sheet-metal cover over the compressor — add the cut-part row, its cable gland and its bond back with it"
    );
    let body_names: BTreeSet<_> = strings(&input["bodies"])?.into_iter().collect();
    let missing: Vec<_> = ["display-cover", "display-gasket"]
        .into_iter()
        .filter(|s| !body_names.contains(*s))
        .collect();
    ensure!(
        missing.is_empty(),
        "the machine no longer stands {missing:?} — bom.md §7 bills the display's snap-retained cover and its gasket"
    );
    let w = &input["wire"];
    let wire_mm = 5. * num(&w["len_mid_mm"])?
        + 2. * num(&w["len_short_2_mm"])?
        + num(&w["len_short_mm"])?
        + 2. * num(&w["len_dc1_mm"])?
        + num(&w["len_dc2_mm"])?
        + 2. * num(&w["len_opening_join_mm"])?;
    n["solid16_cut_m"] = json!(decimal_divide_1000(wire_mm));
    // Exact Decimal(str(mm))/1000, then a ceiling at a tenth of a metre.
    let (wn, wd) = rational(&wire_mm.to_string())?;
    let tenth = (wn + wd * 100 - 1) / (wd * 100);
    let solid16_allocation_m = tenth as f64 / 10.;
    n["solid16_allocation_m"] = json!(solid16_allocation_m.to_string());
    put!(_wrap_mm, num(&input["coil"]["wrap"])?);
    put!(_cut_mm, num(&input["coil"]["cut"])?);
    put!(_roll_spare_ft, num(&input["coil"]["spare_ft"])?);
    put!(
        _prv_vent_mm,
        values(&input["prv_segments"])
            .iter()
            .map(|v| num(&v["length_mm"]))
            .collect::<Result<Vec<_>>>()?
            .iter()
            .sum()
    );
    put!(
        _flavor_4mm_mm,
        2. * num(&input["faucet"]["flavor_cut"])?
            + values(&input["fluid_runs"])
                .iter()
                .filter(|v| [Some("fluid-18"), Some("fluid-28")].contains(&v["id"].as_str()))
                .map(|v| num(&v["length"]))
                .collect::<Result<Vec<_>>>()?
                .iter()
                .sum::<f64>()
    );
    put!(end_cap_plates_per_carbonator, 2.);
    put!(carbonator_ports, 4.);
    put!(reservoirs_per_build, 2.);
    put!(floats_per_build, 1. + reservoirs_per_build);
    put!(rc62_per_build, floats_per_build);
    put!(reeds_per_carbonator, 2.);
    put!(
        solenoid_count,
        strings(&input["manifold"]["positions"])?
            .iter()
            .filter(|s| s.starts_with("V-"))
            .count() as f64
    );
    put!(tee_count, length(&input["manifold"]["purchased_tees"]) + 1.);
    put!(
        reservoir_a_ties_per_build,
        values(&input["reservoir_a_anchors"])
            .iter()
            .filter(|v| v["closure"].as_str().unwrap_or("tie") == "tie")
            .count() as f64
    );
    put!(
        reservoir_a_snap_caps_per_build,
        values(&input["reservoir_a_anchors"])
            .iter()
            .filter(|v| v["closure"].as_str() == Some("snap"))
            .count() as f64
    );
    put!(
        four_inch_ties_per_build,
        15. + 2. + reservoir_a_ties_per_build
    );
    let mut cap_paths: BTreeSet<String> = input["meter_tie_routes"]
        .as_object()
        .context("meter tie routes")?
        .keys()
        .cloned()
        .collect();
    for name in input["union_tie_routes"]
        .as_object()
        .context("union tie routes")?
        .keys()
    {
        if input["union_support_datums"][name]["support_implemented"]
            .as_bool()
            .unwrap_or(false)
        {
            cap_paths.insert(name.clone());
        }
    }
    put!(six_inch_ties_per_build, cap_paths.len() as f64);
    put!(panel_umbilical_bulkheads, 1.);
    put!(panel_water_inlet_bulkheads, 0.);
    put!(foam_cap_faces, 2.);
    put!(inserts_per_foam_cap_face, length(&input["attachments"]));
    put!(
        inserts_per_reservoir_cap,
        length(&input["reservoir_positions"])
    );
    put!(
        reservoir_reeds_total,
        num(&input["reeds_per_reservoir"])? * reservoirs_per_build
    );
    put!(
        total_reeds_per_build,
        reeds_per_carbonator + reservoir_reeds_total
    );
    put!(
        pp1208e_per_build,
        panel_umbilical_bulkheads + panel_water_inlet_bulkheads
    );
    put!(
        pp0308e_per_build,
        length(&input["union_elbows"]) + length(&input["core_union_elbows"])
    );
    put!(
        stem_elbows_per_build,
        1. + 2. * length(&input["manifold"]["lower_connections"])
            + length(&input["stem_elbows"])
            + length(&input["core_stem_elbows"])
    );
    n["stem_elbow_delivered_unit_cost"] = json!(stem_unit_text());
    put!(b_fill_clamp_fasteners_per_build, 0.);
    put!(
        foam_cap_deck_inserts_per_build,
        values(&input["deck_mount_xy"])
            .iter()
            .map(|v| length(v))
            .sum()
    );
    put!(pump_mount_screws_per_build, 0.);
    put!(
        foam_cap_clamp_inserts_per_build,
        inserts_per_foam_cap_face * foam_cap_faces
    );
    put!(foam_cap_inserts_per_build, foam_cap_deck_inserts_per_build);
    put!(foam_cap_screws_per_build, foam_cap_clamp_inserts_per_build);
    put!(
        reservoir_cap_inserts_per_build,
        inserts_per_reservoir_cap * reservoirs_per_build
    );
    put!(
        reservoir_cap_screws_per_build,
        reservoir_cap_inserts_per_build
    );
    put!(
        touchflo_inserts_per_build,
        length(&input["base_pod_centers"])
    );
    put!(touchflo_screws_per_build, touchflo_inserts_per_build);
    put!(faucet_display_cover_inserts_per_build, 0.);
    put!(
        faucet_display_cover_screws_per_build,
        faucet_display_cover_inserts_per_build
    );
    let psu_fasteners = &input["psu_fasteners"];
    let relay_fasteners = &input["relay_fasteners"];
    let c14_fasteners = &input["c14_fasteners"];
    put!(shelf_psu_screws_per_build, num(&psu_fasteners["count"])?);
    put!(
        shelf_pcba_screws_per_build,
        length(&input["deck_mount_xy"]["pcba"])
    );
    put!(
        shelf_relay_screws_per_build,
        strings(&input["above_core_parts"])?
            .iter()
            .filter(|s| s.starts_with("relay-") && placed.contains(*s))
            .count() as f64
            * num(&relay_fasteners["count"])?
    );
    put!(shelf_inserts_per_build, shelf_psu_screws_per_build);
    put!(
        shelf_screws_per_build,
        shelf_pcba_screws_per_build + shelf_psu_screws_per_build + shelf_relay_screws_per_build
    );
    put!(flat_washers_9_per_build, pump_mount_screws_per_build);
    put!(floor_inserts_per_build, length(&input["floor_bosses"]));
    put!(floor_screws_per_build, floor_inserts_per_build);
    put!(floor_washers_per_build, floor_screws_per_build);
    put!(cond_inserts_per_build, length(&input["cond_mount"][3]));
    put!(cond_screws_per_build, cond_inserts_per_build);
    put!(nameplate_inserts_per_build, 4.);
    put!(nameplate_wings_per_build, 0.);
    put!(nameplate_screws_per_build, 4.);
    put!(display_cover_inserts_per_build, 4.);
    put!(display_cover_screws_per_build, 4.);
    put!(display_cover_wings_per_build, 0.);
    put!(
        pump_retainer_inserts_per_build,
        length(&input["pump_fasteners"])
    );
    put!(
        pump_retainer_screws_per_build,
        pump_retainer_inserts_per_build
    );
    put!(dock_tees_per_build, length(&input["collet_holes"]));
    put!(dock_fixture_locks_per_build, 0.);
    put!(c14_inserts_per_build, length(&input["c14_panel_screws"]));
    put!(c14_screws_per_build, c14_inserts_per_build);
    put!(c14_washers_per_build, c14_screws_per_build);
    put!(
        c14_washer_thickness,
        num(&c14_fasteners["washer_thickness_mm"])?
    );
    put!(c14_bore, num(&c14_fasteners["pilot_depth_mm"])?);
    put!(
        small_washers_per_build,
        dock_fixture_locks_per_build + c14_washers_per_build
    );
    put!(
        enclosure_seam_rods_per_build,
        2. * length(&input["seam_rods"])
    );
    put!(
        enclosure_seam_inserts_per_build,
        enclosure_seam_rods_per_build
    );
    put!(
        funnel_frame_screws_per_build,
        length(&input["funnel_fasteners"])
    );
    put!(roof_closure_screws_per_build, funnel_frame_screws_per_build);
    put!(
        roof_closure_inserts_per_build,
        roof_closure_screws_per_build
    );
    put!(
        m3x8_per_build,
        shelf_pcba_screws_per_build
            + cond_screws_per_build
            + shelf_relay_screws_per_build
            + faucet_display_cover_screws_per_build
            + touchflo_screws_per_build
    );
    put!(
        m3x10_per_build,
        c14_screws_per_build + b_fill_clamp_fasteners_per_build + num(&psu_fasteners["count"])?
    );
    put!(m3x20_per_build, pump_mount_screws_per_build);
    put!(psu_screw_len, num(&psu_fasteners["screw_length_mm"])?);
    put!(pcba_screw_len, num(&input["pcba_screw_len"])?);
    put!(relay_screw_len, num(&relay_fasteners["screw_length_mm"])?);
    put!(c14_screw_len, num(&c14_fasteners["screw_length_mm"])?);
    put!(pcba_insert_recess, 0.);
    put!(pcba_bore, num(&input["pcba_bore"])?);
    put!(psu_bore, num(&psu_fasteners["pilot_depth_mm"])?);
    put!(relay_bore, num(&relay_fasteners["pilot_depth_mm"])?);
    put!(
        psu_screw_reach,
        minimum(&psu_fasteners["receiving_range_mm"])?
    );
    put!(
        psu_screw_reach_max,
        maximum(&psu_fasteners["receiving_range_mm"])?
    );
    put!(pcba_screw_reach, num(&input["pcba_screw_reach"])?);
    put!(
        relay_screw_reach,
        minimum(&relay_fasteners["receiving_range_mm"])?
    );
    put!(
        c14_screw_reach,
        c14_screw_len - num(&input["c14_flange_t"])? - c14_washer_thickness
    );
    put!(m3x60_per_build, pump_retainer_screws_per_build);
    put!(
        m3x12_per_build,
        dock_fixture_locks_per_build + roof_closure_screws_per_build
    );
    put!(
        m3_long_inserts_per_build,
        foam_cap_inserts_per_build
            + reservoir_cap_inserts_per_build
            + cond_inserts_per_build
            + pump_retainer_inserts_per_build
            + roof_closure_inserts_per_build
    );
    put!(
        m3_short_inserts_per_build,
        nameplate_inserts_per_build + display_cover_inserts_per_build + touchflo_inserts_per_build
            + shelf_inserts_per_build
            + faucet_display_cover_inserts_per_build
            + c14_inserts_per_build
            + dock_fixture_locks_per_build
            + shelf_relay_screws_per_build
    );
    put!(
        total_m3_inserts_per_build,
        m3_long_inserts_per_build + m3_short_inserts_per_build
    );
    put!(
        total_m5_inserts_per_build,
        floor_inserts_per_build
            + enclosure_seam_inserts_per_build
            + foam_cap_clamp_inserts_per_build
    );
    put!(
        total_m3_screws_per_build,
        pump_mount_screws_per_build
            + reservoir_cap_screws_per_build
            + touchflo_screws_per_build
            + shelf_screws_per_build
            + cond_screws_per_build
            + nameplate_screws_per_build
            + display_cover_screws_per_build
            + faucet_display_cover_screws_per_build
            + pump_retainer_screws_per_build
            + c14_screws_per_build
            + b_fill_clamp_fasteners_per_build
            + dock_fixture_locks_per_build
            + roof_closure_screws_per_build
    );
    put!(
        total_m5_screws_per_build,
        floor_screws_per_build + enclosure_seam_rods_per_build + foam_cap_screws_per_build
    );
    Ok(n)
}

include!("bom_sync_figures.rs");

pub fn dispatch(op: &str, r: &Value, ctx: &mut Context) -> Result<Value> {
    if op == "pack_cost" {
        return Ok(json!(pack_cost_text(
            &number_text(&r["quantity"]),
            &number_text(&r["price"]),
            &number_text(&r["count"])
        )?));
    }
    let input = &r["inputs"];
    let counts = counts(input)?;
    if op == "counts" {
        return Ok(counts);
    }
    let casting = if r["casting"].is_object() {
        r["casting"].clone()
    } else {
        labor::casting_estimate(r, ctx)?
    };
    let (bom, labor) = figures(input, &counts, &casting)?;
    if op == "figures" {
        return Ok(json!({"bom":bom,"labor":labor}));
    }
    if op != "main" {
        bail!("unknown BOM sync operation: {op}")
    }
    let path = ctx.path(r, "bom", "hardware/ledger/bom.md");
    ctx.substitute(&path, &bom, "/hardware/scripts/_bom_sync.py")?;
    let mut out = "-> bom.md\n".to_owned();
    if !r["only_bom"].as_bool().unwrap_or(false) {
        let path = ctx.path(r, "labor", "hardware/ledger/labor.md");
        ctx.substitute(&path, &labor, "/hardware/scripts/_bom_sync.py")?;
        out += "-> labor.md\n";
    }
    Ok(main_result(0, out))
}
