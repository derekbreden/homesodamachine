//! The colours the core's tube stock is drawn in: each spool the routing catalog lists, in its
//! port's colour from the machine's palette or in its own, turned linear as the viewer's files
//! carry it.
use hsm_cold_core_catalog::Colour;
use serde::Deserialize;
use std::collections::BTreeMap;
use std::sync::OnceLock;

#[derive(Deserialize)]
struct SpoolColour {
    palette: Option<String>,
    bytes: Option<[f64; 3]>,
}

#[derive(Deserialize)]
struct Spool {
    color: SpoolColour,
    alpha: f64,
}

#[derive(Deserialize)]
struct Routing {
    spools: BTreeMap<String, Spool>,
}

fn routing() -> &'static Routing {
    static ROUTING: OnceLock<Routing> = OnceLock::new();
    ROUTING.get_or_init(|| {
        serde_json::from_str(include_str!("../../../tools/hsm/shared-data/catalog/routing.json"))
            .expect("the shared routing catalog parses")
    })
}

/// The spool `name`'s colour.
pub fn colour(name: &str) -> Colour {
    static PALETTE: OnceLock<BTreeMap<String, [f64; 3]>> = OnceLock::new();
    let palette = PALETTE.get_or_init(|| {
        let chips = hsm_shared_data::color::chips().expect("the machine's port colours");
        serde_json::from_value(chips["port_colors"].clone()).expect("the port colours are bytes")
    });
    let spool =
        routing().spools.get(name).unwrap_or_else(|| panic!("the routing catalog lists no spool {name}"));
    let bytes = match (&spool.color.palette, spool.color.bytes) {
        (Some(port), _) => palette[port],
        (None, Some(bytes)) => bytes,
        (None, None) => panic!("spool {name} has no colour"),
    };
    let linear =
        hsm_shared_data::color::rgb8_linear(&serde_json::json!(bytes), false).expect("a spool's colour");
    Colour { linear, alpha: spool.alpha }
}
