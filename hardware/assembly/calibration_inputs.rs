//! Calibration inputs share acceptance targets and pressure-vessel equations with the prototype pour model.
pub const GLASS_CAPACITY_OZ: f64 = 12.0;
pub const DISPENSE_TEMP_MAX_C: f64 = 6.0;
pub const SYRUP_RATIO_WATER: f64 = 20.0;
pub const METERED_WATER_ML: f64 = 250.0;
pub const METERED_FLAVOR_ML: f64 = METERED_WATER_ML / SYRUP_RATIO_WATER;
pub const METERED_TOTAL_ML: f64 = METERED_WATER_ML + METERED_FLAVOR_ML;
pub const RATIO_VOLUME_TOL_PCT: f64 = 5.0;
pub const PSI_PER_BAR: f64 = 14.5038;
pub const PSI_PER_ATM: f64 = 14.6959;
pub const SECONDARY_REGULATOR_BAR: f64 = 3.0;
pub fn secondary_regulator_pressure_psi() -> f64 {
    (SECONDARY_REGULATOR_BAR * PSI_PER_BAR * 10.0).round() / 10.0
}
// Fresh-water Bunsen and CO2 coefficients follow the Weiss relations used in pressure-vessel.md.
pub fn vapor_atm(t_c: f64) -> f64 {
    0.61121 * ((18.678 - t_c / 234.5) * (t_c / (257.14 + t_c))).exp() / 101.325
}
pub fn bunsen(a1: f64, a2: f64, a3: f64, t_c: f64) -> f64 {
    let t = t_c + 273.15;
    (a1 + a2 * (100.0 / t) + a3 * (t / 100.0).ln()).exp()
}
pub fn headspace_air_atm(t_c: f64) -> f64 {
    let dry = 1.0 - vapor_atm(15.0);
    [
        (0.78084, -59.6274, 85.7661, 24.3696),
        (0.20946, -58.3877, 85.8079, 23.8439),
        (0.00934, -55.6578, 82.0262, 22.5929),
    ]
    .into_iter()
    .map(|(x, a1, a2, a3)| x * dry * bunsen(a1, a2, a3, 15.0) / bunsen(a1, a2, a3, t_c))
    .sum()
}
pub fn co2_k0(t_k: f64) -> f64 {
    (-58.0931 + 90.5069 * (100.0 / t_k) + 22.2940 * (t_k / 100.0).ln()).exp()
}
pub fn co2_fugacity(p_co2: f64, p_total: f64, t_k: f64) -> f64 {
    let b = -1636.75 + 12.0408 * t_k - 3.27957e-2 * t_k.powi(2) + 3.16528e-5 * t_k.powi(3);
    p_co2 * (b * p_total / (82.0578 * t_k)).exp()
}
pub fn carbonation_volumes(t_c: f64, air: bool, secondary_psi: f64) -> f64 {
    let t = t_c + 273.15;
    let total = secondary_psi / PSI_PER_ATM + 1.0;
    let co2 = total - vapor_atm(t_c) - if air { headspace_air_atm(t_c) } else { 0.0 };
    co2_k0(t) * co2_fugacity(co2, total, t) * 22.26
}
