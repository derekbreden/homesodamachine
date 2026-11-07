//! One page as it is drawn: shapes, text runs and pictures in drawing order, and the areas that
//! link elsewhere. Coordinates are points with the origin at the page's lower left and y up,
//! as in PDF.
use crate::font::Font;
use crate::picture::RgbImage;
use crate::Rgb;
use std::sync::Arc;

#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Cap {
    Butt,
    Round,
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Join {
    Miter,
    Round,
}

#[derive(Clone, Copy, Debug)]
pub enum Seg {
    Move([f64; 2]),
    Line([f64; 2]),
    Cubic([f64; 2], [f64; 2], [f64; 2]),
    Close,
}

#[derive(Clone, Debug, Default)]
pub struct Path {
    pub segs: Vec<Seg>,
}

/// The circle's control-point ratio for a quarter turn, 4/3·tan(π/8).
const KAPPA: f64 = 0.552_284_749_830_793_4;
/// The rounded rectangle's corner control-point ratio, as ReportLab draws its corners.
const CORNER: f64 = 0.4472;

impl Path {
    pub fn new() -> Path {
        Path::default()
    }
    pub fn move_to(&mut self, x: f64, y: f64) -> &mut Path {
        self.segs.push(Seg::Move([x, y]));
        self
    }
    pub fn line_to(&mut self, x: f64, y: f64) -> &mut Path {
        self.segs.push(Seg::Line([x, y]));
        self
    }
    pub fn curve_to(&mut self, a: [f64; 2], b: [f64; 2], to: [f64; 2]) -> &mut Path {
        self.segs.push(Seg::Cubic(a, b, to));
        self
    }
    pub fn close(&mut self) -> &mut Path {
        self.segs.push(Seg::Close);
        self
    }

    /// A polyline through `points`, closed when `closed`.
    pub fn polyline(points: &[[f64; 2]], closed: bool) -> Path {
        let mut p = Path::new();
        for (i, q) in points.iter().enumerate() {
            if i == 0 {
                p.move_to(q[0], q[1]);
            } else {
                p.line_to(q[0], q[1]);
            }
        }
        if closed {
            p.close();
        }
        p
    }

    pub fn rect(x: f64, y: f64, w: f64, h: f64) -> Path {
        let mut p = Path::new();
        p.move_to(x, y).line_to(x + w, y).line_to(x + w, y + h).line_to(x, y + h).close();
        p
    }

    pub fn round_rect(x: f64, y: f64, w: f64, h: f64, r: f64) -> Path {
        let (x0, x1) = (x.min(x + w), x.max(x + w));
        let (y0, y1) = (y.min(y + h), y.max(y + h));
        let t = CORNER * r;
        let mut p = Path::new();
        p.move_to(x0 + r, y0)
            .line_to(x1 - r, y0)
            .curve_to([x1 - t, y0], [x1, y0 + t], [x1, y0 + r])
            .line_to(x1, y1 - r)
            .curve_to([x1, y1 - t], [x1 - t, y1], [x1 - r, y1])
            .line_to(x0 + r, y1)
            .curve_to([x0 + t, y1], [x0, y1 - t], [x0, y1 - r])
            .line_to(x0, y0 + r)
            .curve_to([x0, y0 + t], [x0 + t, y0], [x0 + r, y0])
            .close();
        p
    }

    pub fn circle(cx: f64, cy: f64, r: f64) -> Path {
        let k = KAPPA * r;
        let mut p = Path::new();
        p.move_to(cx + r, cy)
            .curve_to([cx + r, cy + k], [cx + k, cy + r], [cx, cy + r])
            .curve_to([cx - k, cy + r], [cx - r, cy + k], [cx - r, cy])
            .curve_to([cx - r, cy - k], [cx - k, cy - r], [cx, cy - r])
            .curve_to([cx + k, cy - r], [cx + r, cy - k], [cx + r, cy])
            .close();
        p
    }
}

/// How a path's outline is drawn.
#[derive(Clone, Copy, Debug)]
pub struct Pen {
    pub color: Rgb,
    pub width: f64,
    pub cap: Cap,
    pub join: Join,
}

impl Pen {
    pub fn new(color: Rgb, width: f64) -> Pen {
        Pen { color, width, cap: Cap::Butt, join: Join::Miter }
    }
    pub fn round(self) -> Pen {
        Pen { cap: Cap::Round, join: Join::Round, ..self }
    }
    pub fn round_cap(self) -> Pen {
        Pen { cap: Cap::Round, ..self }
    }
}

/// A run of text in one font, size and colour, its baseline starting at `at`. `char_space` is
/// added after every character, and `word_space` after every space.
#[derive(Clone)]
pub struct Run {
    pub font: Arc<Font>,
    pub size: f64,
    pub at: [f64; 2],
    pub color: Rgb,
    pub char_space: f64,
    pub word_space: f64,
    pub text: String,
}

#[derive(Clone)]
pub enum Op {
    /// A path, filled (non-zero winding) and then outlined, either or both.
    Shape { path: Path, fill: Option<Rgb>, pen: Option<Pen> },
    Text(Run),
    /// A picture filling the rectangle at `at` of `size`, its first row at the top.
    Picture { image: Arc<RgbImage>, at: [f64; 2], size: [f64; 2] },
}

#[derive(Clone, Debug)]
pub enum Target {
    /// A page of the same document, by its index.
    Page(usize),
    Uri(String),
}

/// A rectangle `[x0, y0, x1, y1]` that links to `target`.
#[derive(Clone, Debug)]
pub struct Link {
    pub rect: [f64; 4],
    pub target: Target,
}

#[derive(Clone, Default)]
pub struct Page {
    pub ops: Vec<Op>,
    pub links: Vec<Link>,
}

impl Page {
    pub fn fill(&mut self, path: Path, color: Rgb) {
        self.ops.push(Op::Shape { path, fill: Some(color), pen: None });
    }
    pub fn stroke(&mut self, path: Path, pen: Pen) {
        self.ops.push(Op::Shape { path, fill: None, pen: Some(pen) });
    }
    pub fn fill_stroke(&mut self, path: Path, fill: Rgb, pen: Pen) {
        self.ops.push(Op::Shape { path, fill: Some(fill), pen: Some(pen) });
    }
    pub fn text(&mut self, run: Run) {
        self.ops.push(Op::Text(run));
    }
    pub fn picture(&mut self, image: Arc<RgbImage>, at: [f64; 2], size: [f64; 2]) {
        self.ops.push(Op::Picture { image, at, size });
    }
    pub fn link(&mut self, rect: [f64; 4], target: Target) {
        self.links.push(Link { rect, target });
    }
}
