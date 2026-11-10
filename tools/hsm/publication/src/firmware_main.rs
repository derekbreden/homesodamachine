//! Requested firmware images reach the website through a content-addressed release bundle.
use hsm_publication::{ContextData, Work, empty, read_json};
mod firmware;
fn main() {
    hsm_publication::maintenance_main("hsm-publish-firmware", firmware::run);
}
