//! Token-boundary validity for preserving a Python file while it is being edited.
use anyhow::{Result, bail, ensure};

fn quoted(text: &str, quote: usize) -> Result<usize> {
    let bytes = text.as_bytes();
    let c = bytes[quote];
    let triple = bytes.get(quote..quote + 3) == Some(&[c, c, c]);
    let width = if triple { 3 } else { 1 };
    let (_, formatted) = super::string_prefix(text, quote);
    let mut pos = quote + width;
    while pos < bytes.len() {
        if bytes[pos] == b'\\' {
            pos = (pos + 2).min(bytes.len());
        } else if bytes[pos] == c && (!triple || bytes.get(pos..pos + 3) == Some(&[c, c, c])) {
            return Ok(pos + width);
        } else if !triple && bytes[pos] == b'\n' {
            bail!("unterminated Python string")
        } else if formatted
            && bytes
                .get(pos..pos + 2)
                .is_some_and(|v| v == b"{{" || v == b"}}")
        {
            pos += 2;
        } else if formatted && bytes[pos] == b'{' {
            pos = field(text, pos + 1)?;
        } else if formatted && bytes[pos] == b'}' {
            bail!("unmatched Python f-string brace")
        } else {
            pos += 1;
        }
    }
    bail!("unterminated Python string")
}
fn field(text: &str, mut pos: usize) -> Result<usize> {
    let bytes = text.as_bytes();
    let mut grouping = vec![];
    while pos < bytes.len() {
        match bytes[pos] {
            b'\'' | b'"' => pos = quoted(text, pos)?,
            b'#' => pos = text[pos..].find('\n').map_or(bytes.len(), |n| pos + n),
            b'(' | b'[' | b'{' => {
                grouping.push(bytes[pos]);
                pos += 1;
            }
            b'}' if grouping.is_empty() => return Ok(pos + 1),
            b')' | b']' | b'}' => {
                let expected = match bytes[pos] {
                    b')' => b'(',
                    b']' => b'[',
                    _ => b'{',
                };
                ensure!(
                    grouping.pop() == Some(expected),
                    "mismatched Python f-string delimiter"
                );
                pos += 1;
            }
            b':' if grouping.is_empty() => {
                pos += 1;
                while pos < bytes.len() {
                    if bytes[pos] == b'{' {
                        pos = field(text, pos + 1)?;
                    } else if bytes[pos] == b'}' {
                        return Ok(pos + 1);
                    } else {
                        pos += 1;
                    }
                }
            }
            _ => pos += 1,
        }
    }
    bail!("unterminated Python f-string field")
}
pub fn validate(text: &str) -> Result<()> {
    let bytes = text.as_bytes();
    let mut pos = 0;
    let mut groups = vec![];
    let mut indents = vec![0];
    let mut line_start = true;
    let mut continued = false;
    while pos < bytes.len() {
        if line_start {
            let mut width = 0;
            while pos < bytes.len() && matches!(bytes[pos], b' ' | b'\t' | b'\x0c') {
                width = if bytes[pos] == b'\t' {
                    (width / 8 + 1) * 8
                } else if bytes[pos] == b'\x0c' {
                    0
                } else {
                    width + 1
                };
                pos += 1;
            }
            if pos == bytes.len() {
                break;
            }
            if groups.is_empty() && !continued && !matches!(bytes[pos], b'#' | b'\r' | b'\n') {
                if width > *indents.last().unwrap() {
                    indents.push(width)
                } else {
                    while width < *indents.last().unwrap() {
                        indents.pop();
                    }
                    ensure!(
                        width == *indents.last().unwrap(),
                        "inconsistent Python indentation"
                    );
                }
            }
            line_start = false;
            continued = false;
        }
        match bytes[pos] {
            b'\'' | b'"' => pos = quoted(text, pos)?,
            b'#' => pos = text[pos..].find('\n').map_or(bytes.len(), |n| pos + n),
            b'(' | b'[' | b'{' => {
                groups.push(bytes[pos]);
                pos += 1;
            }
            b')' | b']' | b'}' => {
                let expected = match bytes[pos] {
                    b')' => b'(',
                    b']' => b'[',
                    _ => b'{',
                };
                ensure!(
                    groups.pop() == Some(expected),
                    "mismatched Python delimiter"
                );
                pos += 1;
            }
            b'\\' if matches!(bytes.get(pos + 1), Some(b'\n')) => {
                pos += 2;
                line_start = true;
                continued = true;
            }
            b'\n' => {
                pos += 1;
                line_start = true;
            }
            _ => pos += 1,
        }
    }
    ensure!(
        groups.is_empty() && !continued,
        "EOF in multi-line Python statement"
    );
    Ok(())
}
