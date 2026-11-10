//! Least-squares fits use the same singular-value rank threshold as the observation models.
use anyhow::{Context, Result};
use nalgebra::DMatrix;

pub fn rank_and_condition(matrix: &DMatrix<f64>) -> (usize, f64) {
    let values = matrix.clone().svd(false, false).singular_values;
    let largest = values.iter().copied().fold(0., f64::max);
    let smallest = values.iter().copied().fold(f64::INFINITY, f64::min);
    let tolerance = largest * matrix.nrows().max(matrix.ncols()) as f64 * f64::EPSILON;
    (
        values.iter().filter(|&&v| v > tolerance).count(),
        largest / smallest,
    )
}
pub fn solve(matrix: &DMatrix<f64>, values: &DMatrix<f64>) -> Result<DMatrix<f64>> {
    let decomposition = matrix.clone().svd(true, true);
    let largest = decomposition
        .singular_values
        .iter()
        .copied()
        .fold(0., f64::max);
    let tolerance = largest * matrix.nrows().max(matrix.ncols()) as f64 * f64::EPSILON;
    decomposition
        .solve(values, tolerance)
        .map_err(anyhow::Error::msg)
        .context("least-squares observation fit")
}
