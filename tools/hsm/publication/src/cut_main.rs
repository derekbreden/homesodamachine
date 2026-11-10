//! An explicitly requested comparison reads current Bazel and published output bytes.
fn main() {
    hsm_publication::maintenance_main("hsm-cut-vs-pointers", hsm_publication::cut::run);
}
