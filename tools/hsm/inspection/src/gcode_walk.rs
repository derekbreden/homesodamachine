//! A plate's commands read line by line with the state each one runs in, for the readers that ask
//! what a plate commands: the part, feature and phase, the feed, the three fans, the nozzle
//! temperature and acceleration, and each move's ends.
use hsm_print_prep::gcode::words;
use hsm_print_prep::motion::arc;

/// The state a line runs in.
#[derive(Clone, Default)]
pub struct State {
    /// The plate object the line belongs to, from Bambu's markers or the sloped underside's.
    pub object: Option<i64>,
    pub feature: String,
    pub phase: String,
    /// The modal feed, in mm/s.
    pub feed: f64,
    /// The part, auxiliary and chamber fans, in percent.
    pub fans: [f64; 3],
    pub temperature: Option<f64>,
    pub acceleration: Option<f64>,
    /// Layer changes the plate has announced so far.
    pub layer: usize,
    /// Whether the plate has started laying its objects.
    pub started: bool,
    /// Inside the sloped underside's preamble, which lays the base before the slicer's layers.
    pub underside: bool,
    pub position: [f64; 3],
    relative: bool,
}

/// One command line of the plate, after its words have been read.
pub struct Line<'a> {
    /// The line number, counted from one.
    pub number: usize,
    pub command: &'a str,
    pub words: Vec<(u8, f64)>,
    /// The code before any comment.
    pub code: &'a str,
}

impl Line<'_> {
    pub fn word(&self, key: u8) -> Option<f64> {
        self.words.iter().find(|(k, _)| *k == key).map(|(_, v)| *v)
    }

    pub fn is_move(&self) -> bool {
        matches!(self.command, "G0" | "G1" | "G2" | "G3")
    }
}

/// The points a move passes through after its start: an arc's, or the end alone.
pub fn path(line: &Line, from: [f64; 3], to: [f64; 3]) -> Vec<[f64; 3]> {
    if matches!(line.command, "G2" | "G3") && (line.word(b'I').is_some() || line.word(b'J').is_some()) {
        arc(from, to, &line.words, line.command == "G2")
    } else {
        vec![to]
    }
}

/// The XY length of a move along its path.
pub fn xy_length(line: &Line, from: [f64; 3], to: [f64; 3]) -> f64 {
    let mut at = from;
    let mut total = 0.;
    for p in path(line, from, to) {
        total += (p[0] - at[0]).hypot(p[1] - at[1]);
        at = p;
    }
    total
}

/// Walks `text`, calling `visit` for each command line with the state before the line and, for
/// a move, its start and end. Markers and settings update the state.
pub fn walk(text: &str, mut visit: impl FnMut(&State, &Line, [f64; 3], [f64; 3])) {
    let mut state = State::default();
    for (index, raw) in text.lines().enumerate() {
        if let Some(comment) = raw.strip_prefix(';') {
            let comment = comment.trim();
            if let Some(value) = comment.strip_prefix("FEATURE:") {
                state.feature = value.trim().to_string();
            } else if let Some(value) = comment.strip_prefix("start printing object, unique label id:") {
                state.object = value.trim().parse().ok();
                state.started = true;
            } else if comment.starts_with("stop printing object") {
                state.object = None;
            } else if comment.starts_with("===== sloped underside") {
                state.started = true;
                state.underside = true;
                state.object = Some(1901);
            } else if comment.starts_with("===== end of the sloped underside") {
                state.underside = false;
                state.object = None;
            } else if let Some(value) = comment.strip_prefix("HSM_PHASE:") {
                state.phase = value.trim().to_string();
            } else if comment == "CHANGE_LAYER" {
                state.layer += 1;
            }
            continue;
        }
        let code = raw.split(';').next().unwrap_or("").trim();
        let Some(command) = code.split_whitespace().next() else {
            continue;
        };
        let line = Line { number: index + 1, command, words: words(&code[command.len()..]), code };
        match command {
            "G90" => state.relative = false,
            "G91" => state.relative = true,
            "M106" => {
                let fan = line.word(b'P').map_or(1, |p| p as usize);
                if (1..=3).contains(&fan) {
                    if let Some(s) = line.word(b'S') {
                        state.fans[fan - 1] = s / 2.55;
                    }
                }
            }
            "M107" => state.fans[0] = 0.,
            "M104" | "M109" if line.word(b'T').is_none() => {
                if let Some(s) = line.word(b'S') {
                    state.temperature = Some(s);
                }
            }
            "M204" => {
                if let Some(s) = line.word(b'S') {
                    state.acceleration = Some(s);
                }
            }
            _ => {}
        }
        if line.is_move() {
            if let Some(f) = line.word(b'F') {
                state.feed = f / 60.;
            }
            let from = state.position;
            let mut to = from;
            for (i, key) in b"XYZ".iter().enumerate() {
                if let Some(v) = line.word(*key) {
                    to[i] = if state.relative { from[i] + v } else { v };
                }
            }
            visit(&state, &line, from, to);
            state.position = to;
        } else {
            visit(&state, &line, state.position, state.position);
        }
    }
}
