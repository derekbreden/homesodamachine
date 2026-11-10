//! An explicitly requested comparison reads native producer receipts and published bytes.
fn main() {
    hsm_publication::maintenance_main("hsm-cut-vs-pointers", hsm_publication::cut::run);
}
