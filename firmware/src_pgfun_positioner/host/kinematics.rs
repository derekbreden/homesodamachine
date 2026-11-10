//! Counts describe commanded motion; camera observations establish the fixture's position.
use anyhow::{Context, Result, ensure};
use serde::{Deserialize, Serialize};
use std::{f64::consts::PI, path::Path};

pub const MAX_JOG_COUNTS: i32 = 256;
pub const MIN_DURATION_US: u64 = 100_000;
pub const MAX_DURATION_US: u64 = 2_000_000;
pub const MAX_RATE: u64 = 1_000;
pub const MAX_ACCELERATION: u64 = 4_000;

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct Motion {
    pub reduction: u64,
    pub motor_full_steps: u64,
    pub external_microsteps: u64,
    pub working_lever_mm: f64,
    pub soft_limit_deg: f64,
    pub aim: [f64; 3],
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct Geometry {
    pub motion: Motion,
    pub sha256: String,
}

impl Geometry {
    pub fn read(path: impl AsRef<Path>) -> Result<Self> {
        crate::read(path)
    }
    pub fn counts_per_rev(&self) -> Result<u64> {
        self.motion
            .reduction
            .checked_mul(self.motion.motor_full_steps)
            .and_then(|n| n.checked_mul(self.motion.external_microsteps))
            .filter(|&n| n > 0)
            .context("the motion record's counts per revolution")
    }
    pub fn soft_limit(&self) -> Result<i32> {
        Ok((self.counts_per_rev()? as f64 * self.motion.soft_limit_deg / 360.) as i32)
    }
    pub fn degrees_to_count(&self, degrees: f64) -> Result<i32> {
        ensure!(degrees.is_finite(), "finite angle required");
        Ok((degrees * self.counts_per_rev()? as f64 / 360.).round_ties_even() as i32)
    }
    pub fn nominal_mm_per_count(&self) -> Result<f64> {
        Ok(self.motion.working_lever_mm * 2. * PI / self.counts_per_rev()? as f64)
    }
    pub fn aim_point(&self, counts: [i32; 2]) -> Result<[f64; 3]> {
        let unit = 2. * PI / self.counts_per_rev()? as f64;
        let yaw = counts[0] as f64 * unit;
        let pitch = counts[1] as f64 * unit;
        let lever = self.motion.working_lever_mm;
        Ok([
            self.motion.aim[0] - lever * pitch.cos() * yaw.sin(),
            self.motion.aim[1] + lever * pitch.cos() * yaw.cos() - lever,
            self.motion.aim[2] + lever * pitch.sin(),
        ])
    }
    pub fn split_target(&self, current: [i32; 2], target: [i32; 2]) -> Result<Vec<[i32; 2]>> {
        let limit = self.soft_limit()?;
        ensure!(
            target
                .iter()
                .all(|n| i64::from(*n).abs() <= i64::from(limit)),
            "target outside mechanical count envelope"
        );
        let delta = [
            target[0] as i64 - current[0] as i64,
            target[1] as i64 - current[1] as i64,
        ];
        let segments = ((delta.iter().map(|n| n.abs()).max().unwrap_or(0) + MAX_JOG_COUNTS as i64
            - 1)
            / MAX_JOG_COUNTS as i64)
            .max(1);
        let mut previous = [0_i64; 2];
        let mut out = vec![];
        for index in 1..=segments {
            let cumulative =
                delta.map(|n| (n as f64 * index as f64 / segments as f64).round_ties_even() as i64);
            let step = [
                (cumulative[0] - previous[0]) as i32,
                (cumulative[1] - previous[1]) as i32,
            ];
            previous = cumulative;
            if step != [0, 0] {
                out.push(step);
            }
        }
        Ok(out)
    }
}
