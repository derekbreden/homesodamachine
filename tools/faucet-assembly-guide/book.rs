//! The faucet shop book reads its changing cuts from their native assembly provider.
use anyhow::{Result, ensure};
use hsm_fabrication_guides::cuts;
use std::path::Path;

fn current(root: &Path) -> Result<String> {
    let mut source =
        std::fs::read_to_string(root.join("hardware/faucet-assembly-guide/pages.json"))?;
    let cuts = cuts::faucet()?;
    let above = hsm_faucet_assembly_numbers::SLEEVE_Z_TOP
        - hsm_faucet_assembly_numbers::umbilical_z_bottom();
    for (key, value, spec) in [
        ("BLUE_CUT", cuts.blue_cut, ".0f"),
        ("SODA_FAUCET_CUT", cuts.soda_faucet_cut, "g"),
        ("DRAIN_CUT", cuts.drain_cut, ".0f"),
        ("FLAVOR_CUT", cuts.flavor_cut, ".0f"),
        ("FOAM_LENGTH", cuts.foam_length, ".0f"),
        ("FOAM_BARE_TOP", cuts.foam_bare_top, ".0f"),
        ("SLEEVE_ABOVE_FOAM", above, ".0f"),
    ] {
        source = source.replace(
            &format!("{{{{cut_{key}}}}}"),
            &hsm_documents::format_number(value, spec)?,
        );
    }
    ensure!(
        !source.contains("{{"),
        "unresolved native faucet-guide figure"
    );
    Ok(source)
}

pub fn build(root: &Path, output: Option<&Path>) -> Result<()> {
    crate::fixed_book::build(root, "faucet-assembly-guide", &current(root)?, output)
}
