//! The raised disposal warning on the rear face, set in its artwork's glyph outlines.
use crate::plan::{Bounds, Graph, Letters, Op, Shape};
use crate::shell::*;
use serde_json::Value;
use hsm_enclosure_solid::text::Artwork;
use std::rc::Rc;
use std::sync::OnceLock;

fn artwork() -> Rc<Artwork> {
    static SOURCE: OnceLock<Value> = OnceLock::new();
    let source = SOURCE.get_or_init(|| {
        let v: Value = hsm_enclosure_numbers::input::json("hardware/printed-parts/enclosure/enclosure/disposal-warning-artwork.json")
            .expect("the disposal warning's artwork parses");
        assert!(
            v["family"] == DISPOSAL_FONT && v["kind"] == "bold",
            "the disposal warning needs artwork for its selected face"
        );
        v
    });
    Rc::new(Artwork { source: source.clone() })
}

/// The warning's raised letters on the rear face, embedded a little into the wall.
pub fn disposal_letters(g: &mut Graph, outer: &Bounds) -> Shape {
    let letters = Letters {
        outer: *outer,
        lines: DISPOSAL_LINES.iter().map(|s| s.to_string()).collect(),
        family: DISPOSAL_FONT.to_string(),
        artwork: artwork(),
        cap_height: DISPOSAL_CAP_HEIGHT,
        depth: DISPOSAL_RAISE + DISPOSAL_EMBED,
        embed: DISPOSAL_EMBED,
        line_gap: DISPOSAL_LINE_GAP,
        bottom: DISPOSAL_BOTTOM,
    };
    g.add(Op::DisposalLetters(Rc::new(letters)), vec![], None)
}
