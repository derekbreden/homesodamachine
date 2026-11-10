//! Read the existing private printer configuration without displaying credentials.
use anyhow::{bail, Context, Result};
use serde_json::Value;
use std::{collections::BTreeMap, fs, path::Path};

#[derive(Clone)]
pub struct Printer {
    pub name: String,
    pub serial: String,
    pub host: String,
    pub access_code: String,
}

pub fn configured(home: &Path) -> Result<BTreeMap<String, Printer>> {
    let config =
        fs::read_to_string(home.join("Library/Application Support/BambuStudio/BambuStudio.conf"))?;
    let runner = fs::read_to_string(home.join(".config/h2c-gc/run.sh"))?;
    parse(&config, &runner)
}

fn words(line: &str) -> Result<Vec<String>> {
    let mut out = Vec::new();
    let mut word = String::new();
    let mut quote = None;
    let mut escaped = false;
    let mut active = false;
    for c in line.chars() {
        if escaped {
            if quote == Some('"') && c != '"' && c != '\\' {
                word.push('\\');
            }
            word.push(c);
            escaped = false;
            active = true;
        } else if c == '\\' && quote != Some('\'') {
            escaped = true;
        } else if quote == Some(c) {
            quote = None;
        } else if quote.is_some() {
            word.push(c);
        } else if c == '\'' || c == '"' {
            quote = Some(c);
            active = true;
        } else if c == '#' {
            break;
        } else if c.is_whitespace() {
            if active {
                out.push(std::mem::take(&mut word));
                active = false;
            }
        } else {
            word.push(c);
            active = true;
        }
    }
    if quote.is_some() || escaped {
        bail!("Unclosed quoting in the printer runner")
    }
    if active {
        out.push(word);
    }
    Ok(out)
}

pub fn parse(config: &str, runner: &str) -> Result<BTreeMap<String, Printer>> {
    let value: Value = serde_json::from_str(config).context("Read Bambu Studio configuration")?;
    let codes = value
        .get("access_code")
        .and_then(Value::as_object)
        .context("Bambu Studio has no access-code map")?;
    let mut printers = BTreeMap::new();
    for line in runner.lines().map(str::trim_start) {
        if !line.starts_with("gc ") && !line.starts_with("gc\t") {
            continue;
        }
        let fields = words(line)?;
        if fields.len() != 4 {
            bail!("Expected gc <name> <host> <access code> in the printer runner")
        }
        let serials: Vec<_> = codes
            .iter()
            .filter(|(_, code)| code.as_str() == Some(&fields[3]))
            .collect();
        if serials.len() != 1 {
            bail!(
                "{}: expected one matching printer in Bambu Studio",
                fields[1]
            )
        }
        let printer = Printer {
            name: fields[1].clone(),
            host: fields[2].clone(),
            access_code: fields[3].clone(),
            serial: serials[0].0.clone(),
        };
        if printers.insert(printer.name.clone(), printer).is_some() {
            bail!("Duplicate printer name: {}", fields[1])
        }
    }
    if printers.is_empty() {
        bail!("No printers configured in the timelapse runner")
    }
    Ok(printers)
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn credentials_match_a_single_serial_and_shell_quoting() {
        let config = r#"{"access_code":{"serial-a":"a # b","serial-b":"other"}}"#;
        let parsed = parse(
            config,
            "gc H2C 'fixture.invalid' 'a # b' # retained comment",
        )
        .unwrap();
        assert_eq!(parsed["H2C"].serial, "serial-a");
        assert_eq!(parsed["H2C"].access_code, "a # b");
        assert!(parse(config, "gc H2C host missing").is_err());
        assert!(parse(
            r#"{"access_code":{"a":"code","b":"code"}}"#,
            "gc H2C host code"
        )
        .is_err());
        assert!(parse(config, "gc H2C host 'a # b'\ngc H2C host 'a # b'").is_err());
        let escaped = parse(
            r#"{"access_code":{"s":"a\\#b"}}"#,
            r#"gc H2C fixture.invalid "a\#b""#,
        )
        .unwrap();
        assert_eq!(escaped["H2C"].access_code, r#"a\#b"#);
    }
}
