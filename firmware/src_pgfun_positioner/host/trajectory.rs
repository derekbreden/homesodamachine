//! Dry rotations fit bounded periodic corrections whose replay keeps independent optical evidence.
use crate::{
    digest,
    kinematics::{Geometry, MAX_ACCELERATION, MAX_RATE},
    linear,
    policy::{HOLDOUT_MAX_MM, HOLDOUT_P95_MM, MAX_SIGMA_MM},
    servo::{Model, inverse},
};
use anyhow::{Context, Result, ensure};
use hsm_pgfun_observation::quantile;
use nalgebra::DMatrix;
use serde::{Deserialize, Serialize};
use std::{
    collections::{BTreeMap, BTreeSet},
    f64::consts::PI,
};

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct Profile {
    pub geometry_sha256: String,
    pub period_us: u64,
    pub knots: Vec<[i32; 2]>,
    #[serde(default)]
    pub qualified: bool,
    #[serde(default)]
    pub physical: bool,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub model_sha256: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub target_sha256: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub target_values_mm: Option<[f64; 4]>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub training_capture_sha256: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub optics_config_sha256: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub training_sample_ids: Option<Vec<u64>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub speed_mm_s: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub direction: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub index_label: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub harmonics: Option<usize>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub training_fit_p95_mm: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub holdout_sha256: Option<Vec<String>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub holdout_p95_mm: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub holdout_max_mm: Option<f64>,
}
impl Profile {
    pub fn centered(geometry: &Geometry, period_us: u64) -> Self {
        Self {
            geometry_sha256: geometry.sha256.clone(),
            period_us,
            knots: vec![[0, 0]; 256],
            qualified: false,
            physical: false,
            model_sha256: None,
            target_sha256: None,
            target_values_mm: None,
            training_capture_sha256: None,
            optics_config_sha256: None,
            training_sample_ids: None,
            speed_mm_s: None,
            direction: None,
            index_label: None,
            harmonics: None,
            training_fit_p95_mm: None,
            holdout_sha256: None,
            holdout_p95_mm: None,
            holdout_max_mm: None,
        }
    }
}
#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct Target {
    #[serde(default)]
    pub physical: bool,
    pub values_mm: [f64; 4],
    pub optics_config_sha256: Option<String>,
    #[serde(flatten)]
    pub fields: BTreeMap<String, serde_json::Value>,
}
#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct DryRow {
    #[serde(default)]
    pub physical: bool,
    pub valid: bool,
    pub phase: f64,
    pub elapsed_s: f64,
    pub sigma_mm: [f64; 4],
    pub clock_uncertainty_ms: f64,
    pub values_mm: [f64; 4],
    pub sample_ns: u64,
    pub optics_config_sha256: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub command_counts: Option<[f64; 2]>,
    #[serde(flatten)]
    pub fields: BTreeMap<String, serde_json::Value>,
}
#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct DryCapture {
    pub physical: bool,
    pub profile: Profile,
    pub rows: Vec<DryRow>,
    pub optics_config_sha256: Option<String>,
    pub speed_mm_s: f64,
    pub direction: String,
    pub index_label: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub geometry_sha256: Option<String>,
}

pub fn period_for_speed(speed: f64) -> Result<u64> {
    ensure!(
        (5.0..=15.).contains(&speed),
        "rotator speed outside the existing controller interval"
    );
    let half = (500000. * PI * 123.698 / (speed * 14400.) + 0.5).floor() as u64;
    Ok(2 * half * 14400)
}
pub fn controls(knots: &[[i32; 2]]) -> Vec<[[i64; 2]; 4]> {
    let n = knots.len();
    (0..n)
        .map(|i| {
            std::array::from_fn(|point| {
                std::array::from_fn(|axis| {
                    let p = i64::from(knots[i][axis]);
                    let next = i64::from(knots[(i + 1) % n][axis]);
                    match point {
                        0 => 6 * p,
                        1 => 6 * p + next - i64::from(knots[(i + n - 1) % n][axis]),
                        2 => 6 * next - i64::from(knots[(i + 2) % n][axis]) + p,
                        _ => 6 * next,
                    }
                })
            })
        })
        .collect()
}
pub fn check(geometry: &Geometry, profile: &Profile) -> Result<()> {
    ensure!(
        profile.geometry_sha256 == geometry.sha256,
        "trajectory geometry mismatch"
    );
    ensure!(
        (16..=256).contains(&profile.knots.len()),
        "integer two-axis periodic knots required"
    );
    ensure!(
        (8_000_000..=120_000_000).contains(&profile.period_us),
        "trajectory period outside the controller interval"
    );
    let n = profile.knots.len() as i128;
    let period = profile.period_us as i128;
    let dt = period / n;
    let limit = i64::from(geometry.soft_limit()?);
    for section in controls(&profile.knots) {
        ensure!(
            section
                .iter()
                .flatten()
                .all(|&value| value.abs() <= 6 * limit),
            "cubic control envelope exceeds joint travel"
        );
        for axis in 0..2 {
            for i in 0..3 {
                ensure!(
                    (section[i + 1][axis] as i128 - section[i][axis] as i128).abs() * n * 1_000_000
                        <= 2 * MAX_RATE as i128 * period,
                    "trajectory rate exceeds the controller limit"
                );
            }
            for i in 0..2 {
                ensure!(
                    (section[i + 2][axis] as i128 - 2 * section[i + 1][axis] as i128
                        + section[i][axis] as i128)
                        .abs()
                        * 1_000_000_000_000
                        <= MAX_ACCELERATION as i128 * dt * dt,
                    "trajectory acceleration exceeds the controller limit"
                );
            }
        }
    }
    Ok(())
}
pub fn evaluate(profile: &Profile, phase: f64) -> Result<[f64; 2]> {
    ensure!(
        !profile.knots.is_empty() && phase.is_finite(),
        "finite periodic evaluation requires knots"
    );
    let n = profile.knots.len();
    let f = phase.rem_euclid(1.) * n as f64;
    let i = f.floor() as usize % n;
    let u = f - f.floor();
    let h00 = 2. * u.powi(3) - 3. * u.powi(2) + 1.;
    let h10 = u.powi(3) - 2. * u.powi(2) + u;
    let h01 = -2. * u.powi(3) + 3. * u.powi(2);
    let h11 = u.powi(3) - u.powi(2);
    Ok(std::array::from_fn(|axis| {
        f64::from(profile.knots[i][axis]) * h00
            + f64::from(profile.knots[(i + 1) % n][axis] - profile.knots[(i + n - 1) % n][axis])
                * h10
                / 2.
            + f64::from(profile.knots[(i + 1) % n][axis]) * h01
            + f64::from(profile.knots[(i + 2) % n][axis] - profile.knots[i][axis]) * h11 / 2.
    }))
}
pub fn rows_for_fit(record: &DryCapture) -> Result<&[DryRow]> {
    ensure!(
        record.physical && record.rows.len() >= 512,
        "physical observations from complete dry revolutions required"
    );
    ensure!(
        record.rows.iter().map(|r| r.elapsed_s).fold(0., f64::max)
            >= 2. * record.profile.period_us as f64 / 1e6,
        "capture complete dry revolutions"
    );
    let mut bins = [0_usize; 64];
    for row in &record.rows {
        ensure!(
            row.valid
                && row.sigma_mm.iter().all(|&v| v <= MAX_SIGMA_MM)
                && row.clock_uncertainty_ms <= 5.,
            "invalid or uncertain dry-run observation"
        );
        ensure!(
            Some(&row.optics_config_sha256) == record.optics_config_sha256.as_ref(),
            "dry capture optical configuration changed"
        );
        ensure!(row.phase.is_finite(), "finite dry-run phase required");
        bins[((row.phase * 64.).trunc() as i64).rem_euclid(64) as usize] += 1;
    }
    ensure!(
        bins.iter().all(|&count| count >= 3),
        "every phase bin requires independent observations"
    );
    Ok(&record.rows)
}
fn basis(phases: &[f64], harmonics: usize) -> DMatrix<f64> {
    DMatrix::from_fn(phases.len(), 1 + 2 * harmonics, |row, column| {
        if column == 0 {
            1.
        } else {
            let angle = 2. * PI * ((column + 1) / 2) as f64 * phases[row];
            if column % 2 == 1 {
                angle.cos()
            } else {
                angle.sin()
            }
        }
    })
}
pub fn fit(
    geometry: &Geometry,
    record: &DryCapture,
    model: &Model,
    target: &Target,
    harmonics: usize,
) -> Result<Profile> {
    check(geometry, &record.profile)?;
    let rows = rows_for_fit(record)?;
    ensure!(
        model.qualified && model.physical && model.geometry_sha256 == geometry.sha256,
        "qualified physical response model required"
    );
    ensure!(target.physical, "a measured working target is required");
    ensure!(
        record.optics_config_sha256.as_ref() == Some(&model.optics_config_sha256)
            && target.optics_config_sha256.as_ref() == Some(&model.optics_config_sha256),
        "response, target and capture require fixed optics"
    );
    ensure!(
        (1..=6).contains(&harmonics),
        "spatial harmonic count outside its interval"
    );
    let phases: Vec<_> = rows.iter().map(|r| r.phase).collect();
    let observations = DMatrix::from_row_slice(
        rows.len(),
        4,
        &rows.iter().flat_map(|r| r.values_mm).collect::<Vec<_>>(),
    );
    let design = basis(&phases, harmonics);
    let coefficient = linear::solve(&design, &observations)?;
    let residual = &observations - &design * &coefficient;
    let residual: Vec<_> = residual.iter().map(|v| v.abs()).collect();
    let p95 = quantile(&residual, 0.95);
    ensure!(
        p95 <= HOLDOUT_P95_MM,
        "runout is not repeatable; inspect indexing, support and vision"
    );
    let phases: Vec<_> = (0..256).map(|i| i as f64 / 256.).collect();
    let values = basis(&phases, harmonics) * coefficient;
    let old: Vec<_> = phases
        .iter()
        .map(|&phase| evaluate(&record.profile, phase))
        .collect::<Result<_>>()?;
    let mut new = old.clone();
    let old_direction: Vec<[i32; 2]> = (0..256)
        .map(|i| {
            std::array::from_fn(|axis| {
                if old[(i + 1) % 256][axis] - old[(i + 255) % 256][axis] >= 0. {
                    1
                } else {
                    -1
                }
            })
        })
        .collect();
    for _ in 0..4 {
        let direction: Vec<[i32; 2]> = (0..256)
            .map(|i| {
                std::array::from_fn(|axis| {
                    if new[(i + 1) % 256][axis] - new[(i + 255) % 256][axis] >= 0. {
                        1
                    } else {
                        -1
                    }
                })
            })
            .collect();
        for i in 0..256 {
            let branch = model.branch(direction[i])?;
            let error = std::array::from_fn(|axis| target.values_mm[axis] - values[(i, axis)]);
            let delta = inverse(&branch.jacobian, error)?;
            let predicted = crate::servo::apply(&branch.jacobian, delta);
            ensure!(
                (0..4).all(|axis| (error[axis] - predicted[axis]).abs() <= HOLDOUT_MAX_MM),
                "observed error lies outside the motor span; change the static cradle pose"
            );
            ensure!(
                (delta[0].powi(2) + delta[1].powi(2)).sqrt() * geometry.nominal_mm_per_count()?
                    <= 0.250,
                "correction exceeds the learned local neighborhood"
            );
            let old_band = model.branch(old_direction[i])?.reversal_deadband_counts;
            new[i] = std::array::from_fn(|axis| {
                old[i][axis]
                    + delta[axis]
                    + f64::from(
                        direction[i][axis] * branch.reversal_deadband_counts[axis]
                            - old_direction[i][axis] * old_band[axis],
                    ) / 2.
            });
        }
    }
    let mut out = Profile::centered(geometry, record.profile.period_us);
    out.knots = new
        .iter()
        .map(|p| p.map(|v| v.round_ties_even() as i32))
        .collect();
    out.physical = true;
    out.model_sha256 = Some(digest(model)?);
    out.target_sha256 = Some(digest(target)?);
    out.target_values_mm = Some(target.values_mm);
    out.training_capture_sha256 = Some(digest(record)?);
    out.optics_config_sha256 = Some(model.optics_config_sha256.clone());
    out.training_sample_ids = Some(rows.iter().map(|r| r.sample_ns).collect());
    out.speed_mm_s = Some(record.speed_mm_s);
    out.direction = Some(record.direction.clone());
    out.index_label = Some(record.index_label.clone());
    out.harmonics = Some(harmonics);
    out.training_fit_p95_mm = Some(p95);
    check(geometry, &out)?;
    Ok(out)
}
pub fn qualify(geometry: &Geometry, profile: &Profile, captures: &[DryCapture]) -> Result<Profile> {
    check(geometry, profile)?;
    ensure!(
        captures.len() >= 2,
        "independent physical dry-run captures required"
    );
    let training: BTreeSet<_> = profile
        .training_sample_ids
        .as_ref()
        .context("training observation evidence")?
        .iter()
        .copied()
        .collect();
    let goal = profile
        .target_values_mm
        .context("measured trajectory target")?;
    let speed = profile.speed_mm_s.context("trajectory speed")?;
    let direction = profile
        .direction
        .as_deref()
        .context("trajectory direction")?;
    let index = profile.index_label.as_deref().context("trajectory index")?;
    let mut errors = vec![];
    let mut seen = BTreeSet::new();
    let expected = digest(profile)?;
    for capture in captures {
        let rows = rows_for_fit(capture)?;
        check(geometry, &capture.profile)?;
        ensure!(
            digest(&capture.profile)? == expected,
            "validation must replay the exact candidate profile"
        );
        ensure!(
            capture.index_label == index
                && capture.direction == direction
                && capture.speed_mm_s == speed,
            "index, direction or speed mismatch"
        );
        ensure!(
            capture.optics_config_sha256 == profile.optics_config_sha256,
            "validation optical configuration changed"
        );
        let ids: BTreeSet<_> = rows.iter().map(|r| r.sample_ns).collect();
        ensure!(
            ids.is_disjoint(&training) && ids.is_disjoint(&seen),
            "training and dry-run holdouts must be independent"
        );
        seen.extend(ids);
        for row in rows {
            errors.extend((0..4).map(|axis| (row.values_mm[axis] - goal[axis]).abs()));
        }
    }
    let p95 = quantile(&errors, 0.95);
    let maximum = errors.iter().copied().fold(0., f64::max);
    ensure!(
        p95 <= HOLDOUT_P95_MM && maximum <= HOLDOUT_MAX_MM,
        "dot and wire endpoints exceed dry-run tolerances"
    );
    let mut out = profile.clone();
    out.qualified = true;
    out.holdout_sha256 = Some(captures.iter().map(digest).collect::<Result<_>>()?);
    out.holdout_p95_mm = Some(p95);
    out.holdout_max_mm = Some(maximum);
    Ok(out)
}

pub fn capture<T: crate::client::Transport + 'static>(
    geometry: &Geometry,
    client: &crate::client::Client<T>,
    latest: &std::path::Path,
    profile: &Profile,
    seconds: f64,
    speed: f64,
    direction: &str,
    index: &str,
) -> Result<DryCapture> {
    check(geometry, profile)?;
    client.load_trajectory(profile)?;
    let clock = client.clock()?;
    let deadline = clock.now_ns() + ((seconds + 60.) * 1e9) as u64;
    let mut started = false;
    let mut last_stamp = 0;
    let mut rows = vec![];
    println!(
        "Ready. Match the indexed rotator setup, release the pedal, then hold it for the dry capture."
    );
    while clock.now_ns() < deadline {
        let sent = clock.now_ns();
        let status = client.status()?;
        let received = clock.now_ns();
        ensure!(
            status.state != crate::client::State::Fault,
            "controller fault: {}",
            status.fault
        );
        if status.playback_active {
            started = true;
            let host_start = (sent as i128 + received as i128) / 2
                + (status.playback_started_us as i128 - status.time_us as i128) * 1000;
            let observation = crate::observe::latest(
                latest,
                last_stamp,
                std::time::Duration::from_millis(500),
                &*clock,
            )?;
            last_stamp = observation.stamp()?;
            let elapsed = (last_stamp as i128 - host_start) as f64 / 1e9;
            if elapsed < 0. {
                continue;
            }
            let phase = (elapsed / (profile.period_us as f64 / 1e6)).rem_euclid(1.);
            let mut fields = observation.fields.clone();
            for key in [
                "phase",
                "elapsed_s",
                "clock_uncertainty_ms",
                "command_counts",
            ] {
                fields.remove(key);
            }
            fields.insert(
                "noise_qualified".into(),
                serde_json::json!(observation.noise_qualified),
            );
            if let Some(value) = observation.receive_ns {
                fields.insert("receive_ns".into(), serde_json::json!(value));
            }
            if let Some(value) = observation.frame_seq {
                fields.insert("frame_seq".into(), serde_json::json!(value));
            }
            if let Some(value) = &observation.camera_id {
                fields.insert("camera_id".into(), serde_json::json!(value));
            }
            rows.push(DryRow {
                physical: observation.physical,
                valid: observation.valid,
                phase,
                elapsed_s: elapsed,
                sigma_mm: observation.sigma()?,
                clock_uncertainty_ms: (received - sent) as f64 / 2e6,
                values_mm: observation.values()?,
                sample_ns: last_stamp,
                optics_config_sha256: observation
                    .optics_config_sha256
                    .context("dry capture optical configuration")?,
                command_counts: Some(evaluate(profile, phase)?),
                fields,
            });
            if elapsed >= seconds {
                break;
            }
        } else if started {
            break;
        } else {
            clock.sleep(std::time::Duration::from_millis(30));
        }
    }
    client.stop()?;
    let optics = rows.first().map(|r| r.optics_config_sha256.clone());
    Ok(DryCapture {
        physical: true,
        profile: profile.clone(),
        rows,
        optics_config_sha256: optics,
        speed_mm_s: speed,
        direction: direction.into(),
        index_label: index.into(),
        geometry_sha256: Some(geometry.sha256.clone()),
    })
}
pub fn replay<T: crate::client::Transport + 'static>(
    geometry: &Geometry,
    client: &crate::client::Client<T>,
    profile: &Profile,
    seconds: f64,
) -> Result<()> {
    check(geometry, profile)?;
    ensure!(
        profile.qualified && profile.physical,
        "independently qualified physical dry trajectory required"
    );
    client.load_trajectory(profile)?;
    let clock = client.clock()?;
    let deadline = clock.now_ns() + ((seconds + 60.) * 1e9) as u64;
    let mut started = None;
    println!(
        "Ready. Match the indexed dry-run setup and rotator direction and speed before pressing the pedal."
    );
    while clock.now_ns() < deadline {
        let status = client.status()?;
        ensure!(
            status.state != crate::client::State::Fault,
            "controller fault: {}",
            status.fault
        );
        if status.playback_active {
            let start = *started.get_or_insert_with(|| clock.now_ns());
            if clock.now_ns() - start > (seconds * 1e9) as u64 {
                break;
            }
        } else if started.is_some() {
            break;
        }
        clock.sleep(std::time::Duration::from_millis(30));
    }
    client.stop()?;
    Ok(())
}
