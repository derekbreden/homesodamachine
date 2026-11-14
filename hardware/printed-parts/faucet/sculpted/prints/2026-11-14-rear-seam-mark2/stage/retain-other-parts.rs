// Composes the seam trial using continuous base courses and the accepted plate's other courses.
use hsm_print_prep::plate_sequence::{BASE, Band, Metadata, Tape, emit, leveling, read_reference};
use std::path::Path;

fn replace_base(band: &Band<'_>) -> bool {
    band.obj == BASE && matches!(band.phase.as_str(), "native tilted base" | "graded shaft transition")
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args = std::env::args_os().skip(1).collect::<Vec<_>>();
    let [reference, revised, destination] = args.as_slice() else {
        return Err("usage: retain-other-parts REFERENCE.gcode REVISED.gcode OUT.gcode".into());
    };
    let reference = Tape::read(Path::new(reference))?;
    let revised = Tape::read(Path::new(revised))?;
    let reference_lines = reference.lines();
    let revised_lines = revised.lines();
    let mut metadata = Metadata::new();
    let (start, original, end) = read_reference(&reference_lines, &mut metadata)?;
    let (_, modified, _) = read_reference(&revised_lines, &mut metadata)?;

    let mut replacements = modified.iter().filter(|band| replace_base(band));
    let mut groups = Vec::with_capacity(original.len());
    for band in &original {
        if replace_base(band) {
            let candidate = replacements.next().ok_or("missing revised base course")?;
            if (band.label.as_str(), band.phase.as_str()) != (candidate.label.as_str(), candidate.phase.as_str()) {
                return Err(format!("revised base course {} differs from {}", candidate.label, band.label).into());
            }
            groups.push(candidate);
        } else {
            groups.push(band);
        }
    }
    if replacements.next().is_some() {
        return Err("unexpected extra base course".into());
    }

    let destination = Path::new(destination);
    let (start, _) = leveling(start, &reference_lines, &groups)?;
    let report = emit(destination, &start, &groups, &end, &metadata)?;
    std::fs::write(destination.with_extension("json"), format!("{}\n", report.dumps_indented()))?;
    Ok(())
}
