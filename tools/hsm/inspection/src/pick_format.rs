//! Typed numeric picks use the browser's clipboard grammar and published model links.
use crate::math::*;
use anyhow::{Result, ensure};
use serde::{Deserialize, Serialize};
use std::path::{Component, Path, PathBuf};

pub const SITE: &str = "https://homesodamachine.com";
#[derive(Clone, Debug, Deserialize, Serialize, PartialEq, Eq)]
pub struct Via {
    pub src: Option<String>,
    pub op: Option<String>,
}
#[derive(Clone, Debug, Deserialize, Serialize, PartialEq, Eq)]
pub struct Source {
    pub src: Option<String>,
    pub op: Option<String>,
    pub via: Option<Via>,
}
#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(tag = "kind", rename_all = "kebab-case")]
pub enum Pick {
    Straight {
        a: V3,
        b: V3,
        #[serde(default)]
        label: Option<String>,
    },
    Arc {
        a: V3,
        b: V3,
        center: V3,
        axis: V3,
        r: f64,
        length: f64,
        #[serde(default)]
        label: Option<String>,
    },
    Circle {
        center: V3,
        d: f64,
        axis: V3,
        circumference: f64,
        #[serde(default)]
        label: Option<String>,
    },
    Plane {
        n: V3,
        thru: V3,
        #[serde(default)]
        label: Option<String>,
    },
    Cylinder {
        r: f64,
        axis: V3,
        dir: V3,
        #[serde(default)]
        label: Option<String>,
    },
    Curved {
        near: V3,
        #[serde(default)]
        label: Option<String>,
    },
    Click {
        point: V3,
        #[serde(default)]
        text: Option<String>,
    },
    Face {
        point: V3,
        #[serde(default)]
        text: Option<String>,
    },
    Box {
        lo: V3,
        hi: V3,
        #[serde(default)]
        text: Option<String>,
    },
    View {
        az: f64,
        el: f64,
    },
    Solid {
        name: String,
    },
    Sources {
        records: Vec<Option<Source>>,
    },
}
#[derive(Clone, Debug, Default, Deserialize, Serialize)]
pub struct Compose {
    #[serde(default)]
    pub model: Option<PathBuf>,
    #[serde(default)]
    pub surface: Option<String>,
    pub picks: Vec<Pick>,
}
pub fn fnum(value: f64) -> String {
    let value = format!("{value:.3}");
    if value == "-0.000" {
        "0.000".into()
    } else {
        value
    }
}
pub fn fpt(point: V3) -> String {
    format!(
        "x={} y={} z={}",
        fnum(point[0]),
        fnum(point[1]),
        fnum(point[2])
    )
}
fn said(line: String, text: &Option<String>) -> String {
    match text.as_deref().filter(|v| !v.is_empty()) {
        Some(text) => format!("{line} \"{text}\""),
        None => line,
    }
}
pub fn source_line(records: &[Option<Source>]) -> String {
    let source = |src: &Option<String>| {
        src.as_deref()
            .filter(|v| !v.is_empty())
            .unwrap_or("unknown source")
            .to_owned()
    };
    let records = if records.is_empty() {
        vec![None]
    } else {
        records.to_vec()
    };
    format!(
        "sources: {}",
        records
            .iter()
            .map(|record| match record {
                None => "unknown provenance".into(),
                Some(record) => {
                    let mut line = source(&record.src);
                    if let Some(op) = &record.op {
                        if !op.is_empty() {
                            line.push_str(&format!(" · {op}"));
                        }
                    }
                    if let Some(via) = &record.via {
                        line.push_str(" · via ");
                        if let Some(op) = &via.op {
                            if !op.is_empty() {
                                line.push_str(&format!("{op} at "));
                            }
                        }
                        line.push_str(&source(&via.src));
                    }
                    line
                }
            })
            .collect::<Vec<String>>()
            .join("; ")
    )
}
pub fn format(pick: &Pick) -> Result<String> {
    let point = |point: &V3| point.iter().all(|value| value.is_finite());
    let finite = match pick {
        Pick::Straight { a, b, .. } | Pick::Box { lo: a, hi: b, .. } => point(a) && point(b),
        Pick::Arc {
            a,
            b,
            center,
            axis,
            r,
            length,
            ..
        } => [a, b, center, axis].into_iter().all(point) && r.is_finite() && length.is_finite(),
        Pick::Circle {
            center,
            d,
            axis,
            circumference,
            ..
        } => point(center) && point(axis) && d.is_finite() && circumference.is_finite(),
        Pick::Plane { n, thru, .. } => point(n) && point(thru),
        Pick::Cylinder { r, axis, dir, .. } => r.is_finite() && point(axis) && point(dir),
        Pick::Curved { near, .. }
        | Pick::Click { point: near, .. }
        | Pick::Face { point: near, .. } => point(near),
        Pick::View { az, el } => az.is_finite() && el.is_finite(),
        Pick::Solid { .. } | Pick::Sources { .. } => true,
    };
    ensure!(finite, "pick coordinates must be finite");
    Ok(match pick {
        Pick::Straight { a, b, label } => format!(
            "{}: {} → {} · len {} · straight · dir {}",
            label.as_deref().unwrap_or("edge"),
            fpt(*a),
            fpt(*b),
            fnum(length(sub(*b, *a))),
            fpt(unit(sub(*b, *a)))
        ),
        Pick::Arc {
            a,
            b,
            center,
            axis,
            r,
            length,
            label,
        } => format!(
            "{}: {} → {} · len {} · arc r={} · center {} · axis {}",
            label.as_deref().unwrap_or("edge"),
            fpt(*a),
            fpt(*b),
            fnum(*length),
            fnum(*r),
            fpt(*center),
            fpt(*axis)
        ),
        Pick::Circle {
            center,
            d,
            axis,
            circumference,
            label,
        } => format!(
            "{}: circle ⌀{} · center {} · circumference {} · axis {}",
            label.as_deref().unwrap_or("edge"),
            fnum(*d),
            fpt(*center),
            fnum(*circumference),
            fpt(*axis)
        ),
        Pick::Plane { n, thru, label } => format!(
            "{}: plane · n {} · thru {}",
            label.as_deref().unwrap_or("face"),
            fpt(*n),
            fpt(*thru)
        ),
        Pick::Cylinder {
            r,
            axis,
            dir,
            label,
        } => format!(
            "{}: cylinder · r={} · axis {} · dir {}",
            label.as_deref().unwrap_or("face"),
            fnum(*r),
            fpt(*axis),
            fpt(*dir)
        ),
        Pick::Curved { near, label } => format!(
            "{}: curved · near {}",
            label.as_deref().unwrap_or("face"),
            fpt(*near)
        ),
        Pick::Click { point, text } => said(format!("click: {}", fpt(*point)), text),
        Pick::Face { point, text } => said(format!("face: {}", fpt(*point)), text),
        Pick::Box { lo, hi, text } => said(format!("box: {} to {}", fpt(*lo), fpt(*hi)), text),
        Pick::View { az, el } => format!("view: az={az} el={el}"),
        Pick::Solid { name } => format!("solid: {name}"),
        Pick::Sources { records } => source_line(records),
    })
}
pub fn relative(root: &Path, path: &Path) -> String {
    let path = if path.is_absolute() {
        path.to_owned()
    } else {
        root.join(path)
    };
    let mut normalized = PathBuf::new();
    for component in path.components() {
        match component {
            Component::CurDir => {}
            Component::ParentDir => {
                normalized.pop();
            }
            other => normalized.push(other.as_os_str()),
        }
    }
    normalized
        .strip_prefix(root)
        .unwrap_or(&normalized)
        .to_string_lossy()
        .replace('\\', "/")
}
pub fn file_line(root: &Path, path: &Path, surface: Option<&str>) -> String {
    let mut path = relative(root, path);
    if surface == Some("mesh") && !path.ends_with(".mesh") {
        path.push_str(".mesh");
    }
    format!("file: {path}")
}
pub fn compose(root: &Path, request: &Compose) -> Result<Vec<String>> {
    let mut lines = Vec::new();
    if let Some(model) = &request.model {
        lines.push(file_line(root, model, request.surface.as_deref()));
    }
    for pick in &request.picks {
        lines.push(format(pick)?);
    }
    Ok(lines)
}
pub fn encode(text: &str) -> String {
    let mut out = String::new();
    for byte in text.bytes() {
        if byte.is_ascii_alphanumeric() || b"-._~".contains(&byte) {
            out.push(byte as char);
        } else {
            out.push_str(&format!("%{byte:02X}"));
        }
    }
    out
}
pub fn link(root: &Path, model: &Path, text: &str, site: &str) -> String {
    let path = relative(root, model);
    let path = path.strip_prefix("hardware/").unwrap_or(&path);
    let path = path.strip_suffix(".mesh").unwrap_or(path);
    format!(
        "{}/3d#step:{}?find={}",
        site.trim_end_matches('/'),
        encode(path),
        encode(text.trim_end())
    )
}

pub fn demo() -> Compose {
    Compose {
        model: None,
        surface: None,
        picks: vec![
            Pick::Straight {
                a: [-10., -5., -2.],
                b: [7., -5., -2.],
                label: None,
            },
            Pick::Arc {
                a: [7., 5., -2.],
                b: [10., 2., -2.],
                center: [7., 2., -2.],
                axis: [0., 0., 1.],
                r: 3.,
                length: std::f64::consts::FRAC_PI_2 * 3.,
                label: None,
            },
            Pick::Circle {
                center: [0., 0., 2.],
                d: 4.,
                axis: [0., 0., 1.],
                circumference: std::f64::consts::TAU * 2.,
                label: None,
            },
            Pick::Plane {
                n: [0., 0., 1.],
                thru: [0., 0., 2.],
                label: Some("faceA".into()),
            },
            Pick::Cylinder {
                r: 2.,
                axis: [0., 0., 0.],
                dir: [0., 0., 1.],
                label: Some("faceB".into()),
            },
            Pick::Click {
                point: [1., -2.5, 3.75],
                text: Some("the click · 3.75 up".into()),
            },
            Pick::Face {
                point: [0., 0., 2.],
                text: None,
            },
            Pick::Box {
                lo: [-10., -5., -2.],
                hi: [-6., 5., 2.],
                text: Some("the far end".into()),
            },
        ],
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn negative_zero_and_link() {
        assert_eq!(fnum(-0.0001), "0.000");
        assert_eq!(
            link(
                Path::new("/repo"),
                Path::new("hardware/part name.step"),
                "click: x=1\n",
                SITE
            ),
            "https://homesodamachine.com/3d#step:part%20name.step?find=click%3A%20x%3D1"
        );
    }
    #[test]
    fn complete_sources_stay_complete() {
        assert_eq!(
            source_line(&[
                None,
                Some(Source {
                    src: Some("part.rs:8".into()),
                    op: Some("union".into()),
                    via: Some(Via {
                        src: None,
                        op: Some("import".into())
                    })
                })
            ]),
            "sources: unknown provenance; part.rs:8 · union · via import at unknown source"
        );
    }
    #[test]
    fn nonfinite_numbers_fail_in_typed_api() {
        assert!(
            format(&Pick::Click {
                point: [f64::NAN, 0., 0.],
                text: None
            })
            .is_err()
        );
        assert!(
            format(&Pick::View {
                az: 0.,
                el: f64::INFINITY
            })
            .is_err()
        );
    }
    #[test]
    fn browser_fixture_matches_composer() {
        #[derive(Deserialize)]
        struct Fixture {
            request: Compose,
            text: String,
        }
        let fixture: Fixture =
            serde_json::from_str(include_str!("../fixtures/picks.json")).unwrap();
        assert_eq!(
            compose(Path::new("/repo"), &fixture.request)
                .unwrap()
                .join("\n"),
            fixture.text
        );
    }
}
