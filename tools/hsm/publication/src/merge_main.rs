//! Git's pointer merge driver combines member hashes with matching provenance.
fn main() {
    hsm_publication::maintenance_main("hsm-merge-pointers", hsm_publication::merge::run);
}
