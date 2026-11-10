//! Directional response fits retain their lost-motion intervals and independent observation evidence.
use crate::{
    digest,
    kinematics::Geometry,
    linear,
    policy::{
        HOLDOUT_MAX_MM, HOLDOUT_P95_MM, MAX_RESPONSE_CONDITION, MAX_REVERSAL_DEADBAND, MAX_SIGMA_MM,
    },
};
use anyhow::{Context, Result, ensure};
use hsm_pgfun_observation::quantile;
use nalgebra::DMatrix;
use serde::{Deserialize, Serialize};
use std::collections::{BTreeMap, BTreeSet};

pub const DIRECTIONS: [[i32; 2]; 4] = [[1, 1], [1, -1], [-1, 1], [-1, -1]];
#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct ResponseRow {
    pub delta: [i32; 2],
    pub change_mm: [f64; 4],
    pub direction: [i32; 2],
    #[serde(default)]
    pub physical: bool,
    pub sigma_mm: Option<[f64; 4]>,
    pub optics_config_sha256: Option<String>,
    pub before_ns: Option<u64>,
    pub after_ns: Option<u64>,
}
#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct Branch {
    pub jacobian: [[f64; 2]; 4],
    pub reversal_deadband_counts: [i32; 2],
    pub fit_rms_mm: f64,
    pub sample_count: usize,
    pub counts_tested: Vec<i32>,
}
#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct Model {
    pub geometry_sha256: String,
    pub branches: BTreeMap<String, Branch>,
    pub qualified: bool,
    pub optics_config_sha256: String,
    pub source_sha256: String,
    pub physical: bool,
    #[serde(default)]
    pub training_sample_ids: Vec<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub holdout_sha256: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub holdout_p95_mm: Option<f64>,
}
pub fn branch_key(direction: [i32; 2]) -> String {
    format!("{},{}", direction[0], direction[1])
}
impl Model {
    pub fn branch(&self, direction: [i32; 2]) -> Result<&Branch> {
        self.branches
            .get(&branch_key(direction))
            .context("the response approach-direction branch")
    }
}
pub fn apply(jacobian: &[[f64; 2]; 4], delta: [f64; 2]) -> [f64; 4] {
    std::array::from_fn(|i| jacobian[i][0] * delta[0] + jacobian[i][1] * delta[1])
}
pub fn inverse(jacobian: &[[f64; 2]; 4], error: [f64; 4]) -> Result<[f64; 2]> {
    let matrix = DMatrix::from_row_slice(
        4,
        2,
        &jacobian.iter().flatten().copied().collect::<Vec<_>>(),
    );
    let values = DMatrix::from_column_slice(4, 1, &error);
    let delta = linear::solve(&matrix, &values)?;
    Ok([delta[(0, 0)], delta[(1, 0)]])
}

pub fn fit(geometry: &Geometry, rows: &[ResponseRow]) -> Result<Model> {
    ensure!(rows.len() >= 12, "insufficient measured response pairs");
    let optics: BTreeSet<_> = rows
        .iter()
        .map(|r| r.optics_config_sha256.clone())
        .collect();
    ensure!(
        optics.len() == 1 && !optics.contains(&None),
        "one fixed optical configuration is required"
    );
    let mut models = BTreeMap::new();
    for direction in DIRECTIONS {
        let batch: Vec<_> = rows.iter().filter(|r| r.direction == direction).collect();
        ensure!(
            batch.len() >= 3,
            "insufficient responses for {}",
            branch_key(direction)
        );
        let x = DMatrix::from_row_slice(
            batch.len(),
            2,
            &batch
                .iter()
                .flat_map(|r| r.delta.map(f64::from))
                .collect::<Vec<_>>(),
        );
        let y = DMatrix::from_row_slice(
            batch.len(),
            4,
            &batch.iter().flat_map(|r| r.change_mm).collect::<Vec<_>>(),
        );
        ensure!(
            y.iter().all(|v| v.is_finite()),
            "finite response coordinates required"
        );
        let mut best: Option<(f64, [[f64; 2]; 4], [i32; 2])> = None;
        for yaw in 0..=MAX_REVERSAL_DEADBAND {
            for pitch in 0..=MAX_REVERSAL_DEADBAND {
                let deadband = [yaw, pitch];
                let effective = DMatrix::from_fn(x.nrows(), 2, |row, axis| {
                    x[(row, axis)].signum() * (x[(row, axis)].abs() - deadband[axis] as f64).max(0.)
                });
                if linear::rank_and_condition(&effective).0 < 2 {
                    continue;
                }
                let coefficients = linear::solve(&effective, &y)?;
                let residual = &y - &effective * &coefficients;
                let score = residual.iter().map(|v| v * v).sum::<f64>() / residual.len() as f64;
                if best.as_ref().is_none_or(|(old, _, _)| score < *old - 1e-18) {
                    best = Some((
                        score,
                        std::array::from_fn(|coordinate| {
                            std::array::from_fn(|axis| coefficients[(axis, coordinate)])
                        }),
                        deadband,
                    ));
                }
            }
        }
        let (score, jacobian, deadband) =
            best.context("response probes do not span both joints")?;
        ensure!(
            !deadband.contains(&MAX_REVERSAL_DEADBAND),
            "reversal deadband reaches the search boundary; inspect preload and routing"
        );
        let j = DMatrix::from_row_slice(
            4,
            2,
            &jacobian.iter().flatten().copied().collect::<Vec<_>>(),
        );
        let (rank, condition) = linear::rank_and_condition(&j);
        ensure!(
            linear::rank_and_condition(&x).0 == 2
                && rank == 2
                && condition <= MAX_RESPONSE_CONDITION,
            "the view cannot separate the joints"
        );
        let counts: BTreeSet<_> = batch
            .iter()
            .flat_map(|r| r.delta)
            .filter(|&v| v != 0)
            .map(i32::abs)
            .collect();
        models.insert(
            branch_key(direction),
            Branch {
                jacobian,
                reversal_deadband_counts: deadband,
                fit_rms_mm: score.sqrt(),
                sample_count: batch.len(),
                counts_tested: counts.into_iter().collect(),
            },
        );
    }
    Ok(Model {
        geometry_sha256: geometry.sha256.clone(),
        branches: models,
        qualified: false,
        optics_config_sha256: optics.into_iter().next().flatten().unwrap(),
        source_sha256: digest(&rows)?,
        physical: rows.iter().all(|r| r.physical),
        training_sample_ids: rows
            .iter()
            .map(|r| r.after_ns.map_or_else(|| "None".into(), |v| v.to_string()))
            .collect::<BTreeSet<_>>()
            .into_iter()
            .collect(),
        holdout_sha256: None,
        holdout_p95_mm: None,
    })
}

pub fn correction(
    geometry: &Geometry,
    model: &Model,
    error: [f64; 4],
    direction: [i32; 2],
    trust_mm: f64,
) -> Result<([i32; 2], [f64; 4])> {
    ensure!(
        model.geometry_sha256 == geometry.sha256,
        "geometry or response model mismatch"
    );
    ensure!(
        trust_mm > 0. && trust_mm <= HOLDOUT_MAX_MM,
        "correction trust is outside its interval"
    );
    ensure!(
        error.iter().all(|v| v.is_finite()),
        "four finite errors required"
    );
    let j = &model.branch(direction)?.jacobian;
    ensure!(
        j.iter().flatten().all(|v| v.is_finite()),
        "finite response required"
    );
    let matrix = DMatrix::from_row_slice(4, 2, &j.iter().flatten().copied().collect::<Vec<_>>());
    let (rank, condition) = linear::rank_and_condition(&matrix);
    ensure!(
        rank == 2 && condition <= MAX_RESPONSE_CONDITION,
        "unobservable response"
    );
    let delta = inverse(j, error)?;
    let predicted = apply(j, delta);
    let residual = std::array::from_fn(|i| error[i] - predicted[i]);
    ensure!(
        residual.iter().all(|v| v.abs() <= HOLDOUT_MAX_MM),
        "error outside the motor span; revise the cradle pose"
    );
    let nominal = geometry.nominal_mm_per_count()?;
    let norm = (delta[0] * delta[0] + delta[1] * delta[1]).sqrt();
    let magnitude = predicted.iter().map(|v| v.abs()).fold(0., f64::max);
    let factor = 1_f64
        .min(trust_mm / magnitude.max(1e-15))
        .min(trust_mm / (norm * nominal).max(1e-15));
    let mut counts = delta.map(|v| (v * factor).round_ties_even() as i32);
    loop {
        let predicted = apply(j, counts.map(f64::from));
        let norm = (f64::from(counts[0]).powi(2) + f64::from(counts[1]).powi(2)).sqrt();
        if predicted.iter().all(|v| v.abs() <= trust_mm) && norm * nominal <= trust_mm {
            break;
        }
        let axis = if counts[0].abs() >= counts[1].abs() {
            0
        } else {
            1
        };
        counts[axis] -= counts[axis].signum();
    }
    Ok((counts, residual))
}

pub fn qualify(model: &Model, holdout: &[ResponseRow]) -> Result<Model> {
    ensure!(
        model.physical && holdout.len() >= 20 && holdout.iter().all(|r| r.physical),
        "independent physical response holdouts required"
    );
    ensure!(
        !holdout.iter().any(|r| model
            .training_sample_ids
            .contains(&r.after_ns.map_or_else(|| "None".into(), |v| v.to_string()))),
        "training and holdout observations overlap"
    );
    for branch in DIRECTIONS {
        ensure!(
            holdout.iter().filter(|r| r.direction == branch).count() >= 5,
            "physical holdouts required for every direction branch"
        );
    }
    let hash = digest(&holdout)?;
    ensure!(
        hash != model.source_sha256,
        "training samples are not independent validation"
    );
    let mut errors = vec![];
    for row in holdout {
        ensure!(
            row.optics_config_sha256.as_ref() == Some(&model.optics_config_sha256),
            "holdout optical configuration changed"
        );
        ensure!(
            row.sigma_mm
                .context("response observation uncertainty")?
                .iter()
                .all(|&v| v <= MAX_SIGMA_MM),
            "observation noise exceeds the qualification limit"
        );
        let branch = model.branch(row.direction)?;
        let effective = std::array::from_fn(|i| {
            f64::from(row.delta[i].signum())
                * (f64::from(row.delta[i]).abs() - branch.reversal_deadband_counts[i] as f64)
                    .max(0.)
        });
        let predicted = apply(&branch.jacobian, effective);
        errors.extend((0..4).map(|i| (row.change_mm[i] - predicted[i]).abs()));
    }
    let p95 = quantile(&errors, 0.95);
    ensure!(
        p95 <= HOLDOUT_P95_MM && errors.iter().all(|&v| v <= HOLDOUT_MAX_MM),
        "loaded response error exceeds tolerance"
    );
    let mut out = model.clone();
    out.qualified = true;
    out.holdout_sha256 = Some(hash);
    out.holdout_p95_mm = Some(p95);
    Ok(out)
}

pub fn collect<T: crate::client::Transport + 'static>(
    client: &crate::client::Client<T>,
    latest: &std::path::Path,
    levels: &[i32],
) -> Result<Vec<ResponseRow>> {
    let baseline = client.status()?;
    ensure!(
        baseline.state == crate::client::State::Armed && baseline.referenced,
        "reference and arm before collecting responses"
    );
    let origin = baseline.count;
    let clock = client.clock()?;
    let mut rows = vec![];
    for [yaw, pitch] in DIRECTIONS {
        for &level in levels {
            for delta in [
                [yaw * level, pitch * 2 * level],
                [yaw * 2 * level, pitch * level],
            ] {
                client.move_to_counts(origin, 1_000_000)?;
                let before = crate::observe::latest(
                    latest,
                    clock.now_ns() + 200_000_000,
                    std::time::Duration::from_secs(2),
                    &*clock,
                )?;
                client.move_counts(delta, 500_000)?;
                let after = crate::observe::latest(
                    latest,
                    clock.now_ns() + 200_000_000,
                    std::time::Duration::from_secs(2),
                    &*clock,
                )?;
                ensure!(
                    before.optics_config_sha256 == after.optics_config_sha256,
                    "optics changed during a response probe"
                );
                let (a, b, sa, sb) = (
                    after.values()?,
                    before.values()?,
                    after.sigma()?,
                    before.sigma()?,
                );
                rows.push(ResponseRow {
                    delta,
                    change_mm: std::array::from_fn(|i| a[i] - b[i]),
                    direction: [yaw, pitch],
                    physical: true,
                    sigma_mm: Some(std::array::from_fn(|i| sa[i].max(sb[i]))),
                    optics_config_sha256: after.optics_config_sha256.clone(),
                    before_ns: Some(before.stamp()?),
                    after_ns: Some(after.stamp()?),
                });
            }
        }
    }
    client.move_to_counts(origin, 1_000_000)?;
    Ok(rows)
}

pub fn follow<T: crate::client::Transport + 'static>(
    geometry: &Geometry,
    client: &crate::client::Client<T>,
    latest: &std::path::Path,
    model: &Model,
    target: [f64; 4],
    direction: [i32; 2],
    seconds: f64,
) -> Result<()> {
    ensure!(
        model.qualified,
        "independent loaded response qualification required"
    );
    ensure!(
        model
            .branches
            .values()
            .all(|branch| branch.reversal_deadband_counts == [0, 0]),
        "measured reversal deadband requires independently validated periodic replay"
    );
    let clock = client.clock()?;
    let deadline = clock.now_ns() + (seconds * 1e9) as u64;
    let mut history = direction;
    let mut stalled = 0;
    while clock.now_ns() < deadline {
        let observation =
            crate::observe::latest(latest, 0, std::time::Duration::from_secs(2), &*clock)?;
        let values = observation.values()?;
        let error = std::array::from_fn(|i| target[i] - values[i]);
        let magnitude = error.iter().map(|v| v.abs()).fold(0., f64::max);
        if magnitude <= HOLDOUT_P95_MM {
            clock.sleep(std::time::Duration::from_millis(50));
            continue;
        }
        let (mut delta, _) = correction(geometry, model, error, history, HOLDOUT_MAX_MM)?;
        let desired = std::array::from_fn(|i| {
            if delta[i] != 0 {
                delta[i].signum()
            } else {
                history[i]
            }
        });
        if desired != history {
            delta = correction(geometry, model, error, desired, HOLDOUT_MAX_MM)?.0;
        }
        ensure!(
            delta != [0, 0],
            "error persists below the learned useful step"
        );
        client.move_counts(delta, 150_000)?;
        let settled = crate::observe::latest(
            latest,
            clock.now_ns() + 200_000_000,
            std::time::Duration::from_secs(2),
            &*clock,
        )?;
        let values = settled.values()?;
        let next = (0..4)
            .map(|i| (target[i] - values[i]).abs())
            .fold(0., f64::max);
        stalled = if next >= magnitude - 0.001 {
            stalled + 1
        } else {
            0
        };
        ensure!(
            stalled < 5,
            "corrections failed to improve observed alignment"
        );
        history = std::array::from_fn(|i| {
            if delta[i] != 0 {
                delta[i].signum()
            } else {
                history[i]
            }
        });
    }
    Ok(())
}
