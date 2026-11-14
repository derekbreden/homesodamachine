//! Writes numbers, text and JSON the way the trial preparers' Python writes them.
//!
//! The plate sequencer and the shaft join's cooling read and write through these: `repr`, the
//! `g` format, `str.strip`, `str.splitlines`, `json.loads` and `json.dumps`.

use anyhow::{bail, Context, Result};

/// `repr(x)`: the shortest digits that read back as `x`, in exponent form only for very large or
/// small values.
pub fn repr(x: f64) -> String {
    if !x.is_finite() {
        return if x.is_nan() { "nan" } else if x > 0.0 { "inf" } else { "-inf" }.into();
    }
    if x == 0.0 {
        return if x.is_sign_negative() { "-0.0" } else { "0.0" }.into();
    }
    let shortest = format!("{x:e}");
    let (sign, digits, exponent) = scientific(&shortest);
    if (-4..16).contains(&exponent) {
        let point = exponent + 1;
        if point <= 0 {
            format!("{sign}0.{}{digits}", "0".repeat(-point as usize))
        } else if point as usize >= digits.len() {
            format!("{sign}{digits}{}.0", "0".repeat(point as usize - digits.len()))
        } else {
            let (whole, fraction) = digits.split_at(point as usize);
            format!("{sign}{whole}.{fraction}")
        }
    } else {
        let (first, rest) = digits.split_at(1);
        let mantissa = if rest.is_empty() { first.to_string() } else { format!("{first}.{rest}") };
        format!("{sign}{mantissa}{}", exponent_suffix(exponent))
    }
}

/// `format(x, 'g')`: the general format's significant digits, without trailing zeros.
pub fn g(x: f64) -> String {
    if !x.is_finite() {
        return if x.is_nan() { "nan" } else if x > 0.0 { "inf" } else { "-inf" }.into();
    }
    if x == 0.0 {
        return if x.is_sign_negative() { "-0" } else { "0" }.into();
    }
    let rounded = format!("{x:.5e}");
    let (mantissa, exponent) = rounded.split_once('e').expect("exponent form");
    let exponent: i32 = exponent.parse().expect("exponent");
    if (-4..6).contains(&exponent) {
        trim_zeros(format!("{x:.*}", (5 - exponent) as usize))
    } else {
        format!("{}{}", trim_zeros(mantissa.to_string()), exponent_suffix(exponent))
    }
}

/// The sign, digits and exponent of a number Rust wrote in exponent form.
fn scientific(text: &str) -> (&str, String, i32) {
    let (mantissa, exponent) = text.split_once('e').expect("exponent form");
    let (sign, mantissa) = match mantissa.strip_prefix('-') {
        Some(rest) => ("-", rest),
        None => ("", mantissa),
    };
    (sign, mantissa.replace('.', ""), exponent.parse().expect("exponent"))
}

fn exponent_suffix(exponent: i32) -> String {
    format!("e{}{:02}", if exponent < 0 { '-' } else { '+' }, exponent.unsigned_abs())
}

fn trim_zeros(mut text: String) -> String {
    if text.contains('.') {
        while text.ends_with('0') {
            text.pop();
        }
        if text.ends_with('.') {
            text.pop();
        }
    }
    text
}

/// `min(a, b, c)` on floats: the first of the smallest.
pub fn min3(a: f64, b: f64, c: f64) -> f64 {
    let mut m = a;
    if b < m {
        m = b;
    }
    if c < m {
        m = c;
    }
    m
}

/// `max(a, b, c)` on floats: the first of the largest.
pub fn max3(a: f64, b: f64, c: f64) -> f64 {
    let mut m = a;
    if b > m {
        m = b;
    }
    if c > m {
        m = c;
    }
    m
}

fn is_space(c: char) -> bool {
    c.is_whitespace() || ('\x1c'..='\x1f').contains(&c)
}

/// `text.strip()`.
pub fn strip(text: &str) -> &str {
    text.trim_matches(is_space)
}

/// `text.lstrip()`.
pub fn lstrip(text: &str) -> &str {
    text.trim_start_matches(is_space)
}

/// `float(text)`.
pub fn float(text: &str) -> Result<f64> {
    strip(text).parse().with_context(|| format!("could not convert string to float: {text:?}"))
}

/// `int(text)`.
pub fn int(text: &str) -> Result<i64> {
    strip(text).parse().with_context(|| format!("invalid literal for int(): {text:?}"))
}

/// A file read as Python's `read_text` reads it, with its line endings made universal.
pub fn read_text(path: &std::path::Path) -> Result<String> {
    let text = String::from_utf8(std::fs::read(path).with_context(|| format!("reading {}", path.display()))?)
        .with_context(|| format!("{} is not UTF-8", path.display()))?;
    Ok(if text.contains('\r') { text.replace("\r\n", "\n").replace('\r', "\n") } else { text })
}

/// `text.splitlines(keepends=True)`.
pub fn splitlines(text: &str) -> Vec<&str> {
    let bytes = text.as_bytes();
    let mut lines = Vec::new();
    let mut start = 0;
    let mut at = 0;
    while at < bytes.len() {
        let end = match bytes[at] {
            b'\n' | b'\x0b' | b'\x0c' | b'\x1c' | b'\x1d' | b'\x1e' => at + 1,
            b'\r' if bytes.get(at + 1) == Some(&b'\n') => at + 2,
            b'\r' => at + 1,
            0xc2 if bytes.get(at + 1) == Some(&0x85) => at + 2,
            0xe2 if bytes.get(at + 1) == Some(&0x80) && matches!(bytes.get(at + 2), Some(0xa8 | 0xa9)) => at + 3,
            _ => {
                at += 1;
                continue;
            }
        };
        lines.push(&text[start..end]);
        start = end;
        at = end;
    }
    if start < bytes.len() {
        lines.push(&text[start..]);
    }
    lines
}

/// A JSON value as Python holds one: integers apart from floats, and objects in their order.
#[derive(Clone, Debug, PartialEq)]
pub enum Json {
    Null,
    Bool(bool),
    Int(i64),
    Float(f64),
    Str(String),
    List(Vec<Json>),
    Dict(Vec<(String, Json)>),
}

impl Json {
    pub fn get(&self, key: &str) -> Option<&Json> {
        match self {
            Json::Dict(items) => items.iter().find(|(k, _)| k == key).map(|(_, v)| v),
            _ => None,
        }
    }

    /// `value[key] = item`: in place when the key is there, otherwise at the end.
    pub fn set(&mut self, key: &str, item: Json) {
        if let Json::Dict(items) = self {
            match items.iter_mut().find(|(k, _)| k == key) {
                Some(slot) => slot.1 = item,
                None => items.push((key.to_string(), item)),
            }
        }
    }

    /// `json.dumps(value)`.
    pub fn dumps(&self) -> String {
        self.write(&Style { indent: None, item: ", ", key: ": " })
    }

    /// `json.dumps(value, indent=2)`.
    pub fn dumps_indented(&self) -> String {
        self.write(&Style { indent: Some(2), item: ",", key: ": " })
    }

    fn write(&self, style: &Style) -> String {
        let mut out = String::new();
        dump(self, style, 0, &mut out);
        out
    }

    /// `json.loads(text)`.
    pub fn loads(text: &str) -> Result<Json> {
        let mut parser = Parser { text: text.as_bytes(), at: 0 };
        let value = parser.value()?;
        parser.space();
        if parser.at != parser.text.len() {
            bail!("extra data at {}", parser.at);
        }
        Ok(value)
    }
}

struct Style {
    indent: Option<usize>,
    item: &'static str,
    key: &'static str,
}

fn newline(style: &Style, level: usize, out: &mut String) {
    if let Some(indent) = style.indent {
        out.push('\n');
        out.push_str(&" ".repeat(indent * level));
    }
}

fn dump(value: &Json, style: &Style, level: usize, out: &mut String) {
    match value {
        Json::Null => out.push_str("null"),
        Json::Bool(b) => out.push_str(if *b { "true" } else { "false" }),
        Json::Int(i) => out.push_str(&i.to_string()),
        Json::Float(x) if x.is_nan() => out.push_str("NaN"),
        Json::Float(x) if x.is_infinite() => out.push_str(if *x > 0.0 { "Infinity" } else { "-Infinity" }),
        Json::Float(x) => out.push_str(&repr(*x)),
        Json::Str(s) => string(s, out),
        Json::List(items) if items.is_empty() => out.push_str("[]"),
        Json::Dict(items) if items.is_empty() => out.push_str("{}"),
        Json::List(items) => {
            out.push('[');
            for (n, item) in items.iter().enumerate() {
                if n > 0 {
                    out.push_str(style.item);
                }
                newline(style, level + 1, out);
                dump(item, style, level + 1, out);
            }
            newline(style, level, out);
            out.push(']');
        }
        Json::Dict(items) => {
            out.push('{');
            for (n, (key, item)) in items.iter().enumerate() {
                if n > 0 {
                    out.push_str(style.item);
                }
                newline(style, level + 1, out);
                string(key, out);
                out.push_str(style.key);
                dump(item, style, level + 1, out);
            }
            newline(style, level, out);
            out.push('}');
        }
    }
}

fn string(text: &str, out: &mut String) {
    out.push('"');
    for c in text.chars() {
        match c {
            '"' => out.push_str("\\\""),
            '\\' => out.push_str("\\\\"),
            '\n' => out.push_str("\\n"),
            '\r' => out.push_str("\\r"),
            '\t' => out.push_str("\\t"),
            '\u{8}' => out.push_str("\\b"),
            '\u{c}' => out.push_str("\\f"),
            ' '..='~' => out.push(c),
            _ => {
                let mut units = [0u16; 2];
                for unit in c.encode_utf16(&mut units) {
                    out.push_str(&format!("\\u{unit:04x}"));
                }
            }
        }
    }
    out.push('"');
}

struct Parser<'a> {
    text: &'a [u8],
    at: usize,
}

impl Parser<'_> {
    fn space(&mut self) {
        while matches!(self.text.get(self.at), Some(b' ' | b'\t' | b'\n' | b'\r')) {
            self.at += 1;
        }
    }

    fn literal(&mut self, word: &str, value: Json) -> Result<Json> {
        if !self.text[self.at..].starts_with(word.as_bytes()) {
            bail!("expecting value at {}", self.at);
        }
        self.at += word.len();
        Ok(value)
    }

    fn value(&mut self) -> Result<Json> {
        self.space();
        match self.text.get(self.at) {
            Some(b'{') => self.object(),
            Some(b'[') => self.array(),
            Some(b'"') => Ok(Json::Str(self.string()?)),
            Some(b't') => self.literal("true", Json::Bool(true)),
            Some(b'f') => self.literal("false", Json::Bool(false)),
            Some(b'n') => self.literal("null", Json::Null),
            Some(b'N') => self.literal("NaN", Json::Float(f64::NAN)),
            Some(b'I') => self.literal("Infinity", Json::Float(f64::INFINITY)),
            Some(b'-') if self.text.get(self.at + 1) == Some(&b'I') => self.literal("-Infinity", Json::Float(f64::NEG_INFINITY)),
            _ => self.number(),
        }
    }

    fn digits(&mut self) -> usize {
        let from = self.at;
        while matches!(self.text.get(self.at), Some(b'0'..=b'9')) {
            self.at += 1;
        }
        self.at - from
    }

    fn number(&mut self) -> Result<Json> {
        let from = self.at;
        if self.text.get(self.at) == Some(&b'-') {
            self.at += 1;
        }
        if self.text.get(self.at) == Some(&b'0') {
            self.at += 1;
        } else if self.digits() == 0 {
            bail!("expecting value at {from}");
        }
        let mut float = false;
        if self.text.get(self.at) == Some(&b'.') && matches!(self.text.get(self.at + 1), Some(b'0'..=b'9')) {
            self.at += 1;
            self.digits();
            float = true;
        }
        if matches!(self.text.get(self.at), Some(b'e' | b'E')) {
            let mark = self.at;
            self.at += 1;
            if matches!(self.text.get(self.at), Some(b'+' | b'-')) {
                self.at += 1;
            }
            if self.digits() == 0 {
                self.at = mark;
            } else {
                float = true;
            }
        }
        let text = std::str::from_utf8(&self.text[from..self.at])?;
        Ok(if float { Json::Float(text.parse()?) } else { Json::Int(text.parse().with_context(|| format!("integer {text}"))?) })
    }

    fn string(&mut self) -> Result<String> {
        self.at += 1;
        let mut out: Vec<u16> = Vec::new();
        let mut plain = Vec::new();
        loop {
            let Some(&c) = self.text.get(self.at) else { bail!("unterminated string") };
            self.at += 1;
            match c {
                b'"' => break,
                b'\\' => {
                    flush(&mut plain, &mut out)?;
                    let Some(&kind) = self.text.get(self.at) else { bail!("unterminated string") };
                    self.at += 1;
                    match kind {
                        b'"' => out.push(b'"' as u16),
                        b'\\' => out.push(b'\\' as u16),
                        b'/' => out.push(b'/' as u16),
                        b'b' => out.push(8),
                        b'f' => out.push(12),
                        b'n' => out.push(b'\n' as u16),
                        b'r' => out.push(b'\r' as u16),
                        b't' => out.push(b'\t' as u16),
                        b'u' => {
                            let hex = self.text.get(self.at..self.at + 4).context("short \\u escape")?;
                            out.push(u16::from_str_radix(std::str::from_utf8(hex)?, 16)?);
                            self.at += 4;
                        }
                        _ => bail!("invalid escape at {}", self.at),
                    }
                }
                c if c < 0x20 => bail!("invalid control character at {}", self.at),
                c => plain.push(c),
            }
        }
        flush(&mut plain, &mut out)?;
        String::from_utf16(&out).context("a lone surrogate in a JSON string")
    }

    fn array(&mut self) -> Result<Json> {
        self.at += 1;
        let mut items = Vec::new();
        self.space();
        if self.text.get(self.at) == Some(&b']') {
            self.at += 1;
            return Ok(Json::List(items));
        }
        loop {
            items.push(self.value()?);
            self.space();
            match self.text.get(self.at) {
                Some(b',') => self.at += 1,
                Some(b']') => {
                    self.at += 1;
                    return Ok(Json::List(items));
                }
                _ => bail!("expecting ',' delimiter at {}", self.at),
            }
        }
    }

    fn object(&mut self) -> Result<Json> {
        self.at += 1;
        let mut object = Json::Dict(Vec::new());
        self.space();
        if self.text.get(self.at) == Some(&b'}') {
            self.at += 1;
            return Ok(object);
        }
        loop {
            self.space();
            if self.text.get(self.at) != Some(&b'"') {
                bail!("expecting property name at {}", self.at);
            }
            let key = self.string()?;
            self.space();
            if self.text.get(self.at) != Some(&b':') {
                bail!("expecting ':' delimiter at {}", self.at);
            }
            self.at += 1;
            let value = self.value()?;
            object.set(&key, value);
            self.space();
            match self.text.get(self.at) {
                Some(b',') => self.at += 1,
                Some(b'}') => {
                    self.at += 1;
                    return Ok(object);
                }
                _ => bail!("expecting ',' delimiter at {}", self.at),
            }
        }
    }
}

fn flush(plain: &mut Vec<u8>, out: &mut Vec<u16>) -> Result<()> {
    out.extend(std::str::from_utf8(plain)?.encode_utf16());
    plain.clear();
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn numbers_read_as_python_writes_them() {
        assert_eq!(repr(0.0001), "0.0001");
        assert_eq!(repr(1e-5), "1e-05");
        assert_eq!(repr(1e16), "1e+16");
        assert_eq!(repr(123.0), "123.0");
        assert_eq!(g(255.0), "255");
        assert_eq!(g(0.42), "0.42");
        assert_eq!(g(1234567.0), "1.23457e+06");
    }

    #[test]
    fn json_keeps_order_and_kind() {
        let value = Json::loads(r#"{"b":1,"a":[0.5,2.0],"c":"\u00e9"}"#).unwrap();
        assert_eq!(value.dumps(), r#"{"b": 1, "a": [0.5, 2.0], "c": "\u00e9"}"#);
        assert_eq!(value.dumps_indented(), "{\n  \"b\": 1,\n  \"a\": [\n    0.5,\n    2.0\n  ],\n  \"c\": \"\\u00e9\"\n}");
    }
}
