//! JSON that keeps its keys in order, written the way Bambu Studio's own settings files are.
//!
//! A saved project's settings are read, changed in a few keys and written back; the order of
//! the rest is the project's, and new keys go at the end.

use anyhow::{bail, Context, Result};
use std::fmt::Write as _;

#[derive(Clone, Debug, PartialEq)]
pub enum Json {
    Null,
    Bool(bool),
    /// The number as written, and its value.
    Number(String, f64),
    Text(String),
    List(Vec<Json>),
    Map(Vec<(String, Json)>),
}

impl Json {
    pub fn parse(text: &str) -> Result<Json> {
        let mut reader = Reader { bytes: text.as_bytes(), at: 0 };
        let value = reader.value()?;
        reader.space();
        if reader.at != reader.bytes.len() {
            bail!("trailing text after JSON at byte {}", reader.at);
        }
        Ok(value)
    }

    pub fn get(&self, key: &str) -> Option<&Json> {
        match self {
            Json::Map(entries) => entries.iter().find(|(k, _)| k == key).map(|(_, v)| v),
            _ => None,
        }
    }

    /// Set `key`, keeping its place if it is there and adding it at the end if not.
    pub fn set(&mut self, key: &str, value: Json) {
        if let Json::Map(entries) = self {
            if let Some(slot) = entries.iter_mut().find(|(k, _)| k == key) {
                slot.1 = value;
            } else {
                entries.push((key.to_string(), value));
            }
        }
    }

    pub fn text(&self) -> Option<&str> {
        match self {
            Json::Text(s) => Some(s),
            _ => None,
        }
    }

    pub fn list(&self) -> &[Json] {
        match self {
            Json::List(items) => items,
            _ => &[],
        }
    }

    /// The text of a key, or of a list's first item.
    pub fn first_text(&self, key: &str) -> Option<&str> {
        match self.get(key)? {
            Json::Text(s) => Some(s),
            Json::List(items) => items.first().and_then(Json::text),
            _ => None,
        }
    }

    /// `json.dumps(value, indent=2)`.
    pub fn dumps(&self) -> String {
        let mut out = String::new();
        self.write(&mut out, 0);
        out
    }

    fn write(&self, out: &mut String, level: usize) {
        match self {
            Json::Null => out.push_str("null"),
            Json::Bool(b) => out.push_str(if *b { "true" } else { "false" }),
            Json::Number(text, value) => {
                // Python keeps an integer an int and writes a float with its repr.
                match text.parse::<i128>() {
                    Ok(int) => out.push_str(&int.to_string()),
                    Err(_) => out.push_str(&python_number(*value)),
                }
            }
            Json::Text(s) => quote(out, s),
            Json::List(items) if items.is_empty() => out.push_str("[]"),
            Json::Map(entries) if entries.is_empty() => out.push_str("{}"),
            Json::List(items) => {
                out.push('[');
                for (i, item) in items.iter().enumerate() {
                    out.push_str(if i == 0 { "\n" } else { ",\n" });
                    indent(out, level + 1);
                    item.write(out, level + 1);
                }
                out.push('\n');
                indent(out, level);
                out.push(']');
            }
            Json::Map(entries) => {
                out.push('{');
                for (i, (key, value)) in entries.iter().enumerate() {
                    out.push_str(if i == 0 { "\n" } else { ",\n" });
                    indent(out, level + 1);
                    quote(out, key);
                    out.push_str(": ");
                    value.write(out, level + 1);
                }
                out.push('\n');
                indent(out, level);
                out.push('}');
            }
        }
    }

    pub fn to_value(&self) -> serde_json::Value {
        use serde_json::Value;
        match self {
            Json::Null => Value::Null,
            Json::Bool(b) => Value::Bool(*b),
            Json::Number(text, value) => serde_json::from_str(text).unwrap_or_else(|_| serde_json::json!(value)),
            Json::Text(s) => Value::String(s.clone()),
            Json::List(items) => Value::Array(items.iter().map(Json::to_value).collect()),
            Json::Map(entries) => Value::Object(entries.iter().map(|(k, v)| (k.clone(), v.to_value())).collect()),
        }
    }

    pub fn from_value(value: &serde_json::Value) -> Json {
        use serde_json::Value;
        match value {
            Value::Null => Json::Null,
            Value::Bool(b) => Json::Bool(*b),
            Value::Number(n) => Json::Number(n.to_string(), n.as_f64().unwrap_or(0.0)),
            Value::String(s) => Json::Text(s.clone()),
            Value::Array(items) => Json::List(items.iter().map(Json::from_value).collect()),
            Value::Object(map) => Json::Map(map.iter().map(|(k, v)| (k.clone(), Json::from_value(v))).collect()),
        }
    }
}

fn indent(out: &mut String, level: usize) {
    for _ in 0..level {
        out.push_str("  ");
    }
}

fn quote(out: &mut String, s: &str) {
    out.push('"');
    for c in s.chars() {
        match c {
            '"' => out.push_str("\\\""),
            '\\' => out.push_str("\\\\"),
            '\n' => out.push_str("\\n"),
            '\r' => out.push_str("\\r"),
            '\t' => out.push_str("\\t"),
            '\u{8}' => out.push_str("\\b"),
            '\u{c}' => out.push_str("\\f"),
            c if (c as u32) < 0x20 || (c as u32) > 0x7e => {
                let mut units = [0u16; 2];
                for unit in c.encode_utf16(&mut units) {
                    let _ = write!(out, "\\u{:04x}", unit);
                }
            }
            c => out.push(c),
        }
    }
    out.push('"');
}

/// Python's `repr` of a float, which `json.dumps` writes; whole numbers print as integers only
/// when they were integers in the source, which the caller keeps as written text.
pub fn python_number(value: f64) -> String {
    if value.is_nan() {
        return "NaN".into();
    }
    if value.is_infinite() {
        return if value > 0.0 { "Infinity".into() } else { "-Infinity".into() };
    }
    if value == value.trunc() && value.abs() < 1e16 {
        return format!("{:.1}", value);
    }
    let sci = format!("{:e}", value);
    let (mantissa, exponent) = sci.split_once('e').unwrap();
    let exponent: i32 = exponent.parse().unwrap();
    if (-4..16).contains(&exponent) {
        let digits: String = mantissa.chars().filter(|c| c.is_ascii_digit()).collect();
        let negative = value < 0.0;
        let point = exponent + 1;
        let body = if point <= 0 {
            format!("0.{}{}", "0".repeat((-point) as usize), digits)
        } else if point as usize >= digits.len() {
            format!("{}{}.0", digits, "0".repeat(point as usize - digits.len()))
        } else {
            format!("{}.{}", &digits[..point as usize], &digits[point as usize..])
        };
        format!("{}{}", if negative { "-" } else { "" }, body)
    } else {
        format!("{}e{}{:02}", mantissa, if exponent < 0 { "-" } else { "+" }, exponent.abs())
    }
}

struct Reader<'a> {
    bytes: &'a [u8],
    at: usize,
}

impl Reader<'_> {
    fn space(&mut self) {
        while self.at < self.bytes.len() && matches!(self.bytes[self.at], b' ' | b'\n' | b'\r' | b'\t') {
            self.at += 1;
        }
    }

    fn value(&mut self) -> Result<Json> {
        self.space();
        match self.bytes.get(self.at).copied().context("unexpected end of JSON")? {
            b'{' => {
                self.at += 1;
                let mut entries = Vec::new();
                self.space();
                if self.bytes.get(self.at) == Some(&b'}') {
                    self.at += 1;
                    return Ok(Json::Map(entries));
                }
                loop {
                    self.space();
                    let key = self.string()?;
                    self.space();
                    if self.bytes.get(self.at) != Some(&b':') {
                        bail!("expected ':' at byte {}", self.at);
                    }
                    self.at += 1;
                    let value = self.value()?;
                    entries.push((key, value));
                    self.space();
                    match self.bytes.get(self.at) {
                        Some(b',') => self.at += 1,
                        Some(b'}') => {
                            self.at += 1;
                            return Ok(Json::Map(entries));
                        }
                        _ => bail!("expected ',' or '}}' at byte {}", self.at),
                    }
                }
            }
            b'[' => {
                self.at += 1;
                let mut items = Vec::new();
                self.space();
                if self.bytes.get(self.at) == Some(&b']') {
                    self.at += 1;
                    return Ok(Json::List(items));
                }
                loop {
                    items.push(self.value()?);
                    self.space();
                    match self.bytes.get(self.at) {
                        Some(b',') => self.at += 1,
                        Some(b']') => {
                            self.at += 1;
                            return Ok(Json::List(items));
                        }
                        _ => bail!("expected ',' or ']' at byte {}", self.at),
                    }
                }
            }
            b'"' => Ok(Json::Text(self.string()?)),
            b't' => self.word("true", Json::Bool(true)),
            b'f' => self.word("false", Json::Bool(false)),
            b'n' => self.word("null", Json::Null),
            b'N' => self.word("NaN", Json::Number("NaN".into(), f64::NAN)),
            b'I' => self.word("Infinity", Json::Number("Infinity".into(), f64::INFINITY)),
            _ => {
                let start = self.at;
                if self.bytes[self.at] == b'-' && self.bytes.get(self.at + 1) == Some(&b'I') {
                    self.at += 1;
                    self.word("Infinity", Json::Null)?;
                    return Ok(Json::Number("-Infinity".into(), f64::NEG_INFINITY));
                }
                while self.at < self.bytes.len() && matches!(self.bytes[self.at], b'-' | b'+' | b'.' | b'e' | b'E' | b'0'..=b'9') {
                    self.at += 1;
                }
                let text = std::str::from_utf8(&self.bytes[start..self.at])?.to_string();
                let value: f64 = text.parse().with_context(|| format!("bad number {text:?}"))?;
                Ok(Json::Number(text, value))
            }
        }
    }

    fn word(&mut self, word: &str, value: Json) -> Result<Json> {
        if self.bytes[self.at..].starts_with(word.as_bytes()) {
            self.at += word.len();
            Ok(value)
        } else {
            bail!("unexpected text at byte {}", self.at)
        }
    }

    fn string(&mut self) -> Result<String> {
        if self.bytes.get(self.at) != Some(&b'"') {
            bail!("expected a string at byte {}", self.at);
        }
        self.at += 1;
        let mut out = String::new();
        let mut pending: Option<u16> = None;
        loop {
            let b = *self.bytes.get(self.at).context("unterminated string")?;
            self.at += 1;
            match b {
                b'"' => return Ok(out),
                b'\\' => {
                    let e = *self.bytes.get(self.at).context("unterminated escape")?;
                    self.at += 1;
                    match e {
                        b'"' => out.push('"'),
                        b'\\' => out.push('\\'),
                        b'/' => out.push('/'),
                        b'n' => out.push('\n'),
                        b'r' => out.push('\r'),
                        b't' => out.push('\t'),
                        b'b' => out.push('\u{8}'),
                        b'f' => out.push('\u{c}'),
                        b'u' => {
                            let hex = std::str::from_utf8(&self.bytes[self.at..self.at + 4])?;
                            self.at += 4;
                            let unit = u16::from_str_radix(hex, 16)?;
                            if let Some(high) = pending.take() {
                                let code = 0x10000 + (((high as u32) - 0xD800) << 10) + ((unit as u32) - 0xDC00);
                                out.push(char::from_u32(code).context("bad surrogate pair")?);
                            } else if (0xD800..0xDC00).contains(&unit) {
                                pending = Some(unit);
                            } else {
                                out.push(char::from_u32(unit as u32).context("bad escape")?);
                            }
                        }
                        _ => bail!("bad escape at byte {}", self.at),
                    }
                }
                _ => {
                    // UTF-8 continuation bytes are copied through as a whole character.
                    let start = self.at - 1;
                    let len = match b {
                        0x00..=0x7f => 1,
                        0xc0..=0xdf => 2,
                        0xe0..=0xef => 3,
                        _ => 4,
                    };
                    out.push_str(std::str::from_utf8(&self.bytes[start..start + len])?);
                    self.at = start + len;
                }
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn round_trips_in_python_style() {
        let text = "{\n  \"b\": [\n    \"1\",\n    \"x\\u00e9\"\n  ],\n  \"a\": {},\n  \"c\": 0.5,\n  \"d\": []\n}";
        assert_eq!(Json::parse(text).unwrap().dumps(), text);
    }

    #[test]
    fn floats_print_as_python_does() {
        assert_eq!(python_number(1e-5), "1e-05");
        assert_eq!(python_number(0.0001), "0.0001");
        assert_eq!(python_number(1e16), "1e+16");
        assert_eq!(python_number(2.5), "2.5");
        assert_eq!(python_number(3.0), "3.0");
    }
}
