//! Printed pages and their pictures. A page is drawn once, as shapes, text set in an embedded
//! TrueType font and raster pictures, and written from that one drawing as a PDF page or as
//! pixels.
pub mod font;
pub mod lines;
pub mod page;
pub mod pdf;
pub mod picture;
pub mod raster;
pub mod reads;
pub mod text;

pub use font::Font;
pub use page::{Cap, Join, Link, Op, Page, Path, Pen, Run, Seg, Target};
pub use picture::{Outlined, RgbImage, RgbaImage};

/// A colour in the RGB device space, each channel from 0 to 1.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Rgb {
    pub r: f64,
    pub g: f64,
    pub b: f64,
}

impl Rgb {
    /// `#RRGGBB`.
    pub const fn hex(s: &str) -> Rgb {
        let b = s.as_bytes();
        assert!(b.len() == 7 && b[0] == b'#', "a colour is #RRGGBB");
        Rgb {
            r: (nibble(b[1]) * 16 + nibble(b[2])) as f64 / 255.0,
            g: (nibble(b[3]) * 16 + nibble(b[4])) as f64 / 255.0,
            b: (nibble(b[5]) * 16 + nibble(b[6])) as f64 / 255.0,
        }
    }

    pub const WHITE: Rgb = Rgb { r: 1.0, g: 1.0, b: 1.0 };

    /// The channels as bytes, rounded.
    pub fn bytes(self) -> [u8; 3] {
        [self.r, self.g, self.b].map(|v| (v.clamp(0.0, 1.0) * 255.0).round() as u8)
    }
}

const fn nibble(c: u8) -> u8 {
    match c {
        b'0'..=b'9' => c - b'0',
        b'a'..=b'f' => c - b'a' + 10,
        b'A'..=b'F' => c - b'A' + 10,
        _ => panic!("a hex digit"),
    }
}
