//! The shared fits, from the scalars catalog every program reads.
use serde::Deserialize;
use std::sync::OnceLock;

#[derive(Deserialize)]
struct Fits {
    slip: f64,
    sliding_extra: f64,
    supported_surface: f64,
}

#[derive(Deserialize)]
struct Scalars {
    fits: Fits,
}

fn fits() -> &'static Fits {
    static FITS: OnceLock<Fits> = OnceLock::new();
    FITS.get_or_init(|| {
        serde_json::from_str::<Scalars>(include_str!("../../../../../tools/hsm/shared-data/catalog/scalars.json"))
            .expect("the shared scalars catalog parses")
            .fits
    })
}

/// Head-on seats take the slip allowance.
pub fn slip() -> f64 {
    fits().slip
}

/// Faces that slide past their mates take the running allowance.
pub fn running() -> f64 {
    let f = fits();
    f.slip + f.sliding_extra
}

/// A face printed over support takes this allowance for its rougher finish.
pub fn supported() -> f64 {
    fits().supported_surface
}
