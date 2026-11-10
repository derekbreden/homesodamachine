//! Use the installed native curl FTPS transport, with its control/data TLS session cache enabled.
use crate::gc::{Clip, Remote};
use anyhow::{bail, Context, Result};
use std::{
    ffi::CString,
    io::{Read, Write},
    process::{Command, Stdio},
    time::Duration,
};

pub struct Ftp {
    host: String,
    port: u16,
    user: String,
    code: String,
    timeout: Duration,
}
impl Ftp {
    pub fn new(
        host: String,
        port: u16,
        user: String,
        code: String,
        timeout: Duration,
    ) -> Result<Self> {
        if host.contains(['\r', '\n', '/', '@']) || host.is_empty() {
            bail!("Invalid FTPS host")
        }
        Ok(Self {
            host,
            port,
            user,
            code,
            timeout,
        })
    }
    fn config(&self, path: &str, extra: &[(&str, String)]) -> Result<String> {
        fn quoted(value: &str) -> Result<String> {
            if value.contains(['\r', '\n', '\0']) {
                bail!("Invalid line break in FTPS configuration")
            };
            Ok(format!(
                "\"{}\"",
                value.replace('\\', "\\\\").replace('"', "\\\"")
            ))
        }
        let host = if self.host.contains(':') {
            format!("[{}]", self.host)
        } else {
            self.host.clone()
        };
        let path = path
            .as_bytes()
            .iter()
            .map(|b| {
                if b.is_ascii_alphanumeric() || b"/-._~".contains(b) {
                    (*b as char).to_string()
                } else {
                    format!("%{b:02X}")
                }
            })
            .collect::<String>();
        let mut config=format!("silent\nshow-error\ninsecure\nssl-reqd\nsessionid\nnoproxy = \"*\"\nconnect-timeout = {}\nspeed-limit = 1\nspeed-time = {}\nurl = {}\nuser = {}\n",self.timeout.as_secs_f64(),self.timeout.as_secs().max(1),quoted(&format!("ftps://{host}:{}{path}",self.port))?,quoted(&format!("{}:{}",self.user,self.code))?);
        if !extra.is_empty() {
            config.push_str(&format!("max-time = {}\n", self.timeout.as_secs_f64()));
        }
        for (key, value) in extra {
            config.push_str(key);
            if !value.is_empty() {
                config.push_str(" = ");
                config.push_str(&quoted(value)?)
            }
            config.push('\n')
        }
        Ok(config)
    }
    fn perform(&self, path: &str, extra: &[(&str, String)], sink: &mut dyn Write) -> Result<()> {
        let config = self.config(path, extra)?;
        let mut child = Command::new("curl")
            .args(["--disable", "--config", "-"])
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .spawn()
            .context("Start native FTPS transport")?;
        child.stdin.take().unwrap().write_all(config.as_bytes())?;
        let mut stdout = child.stdout.take().unwrap();
        let mut stderr = child.stderr.take().unwrap();
        let error_reader = std::thread::spawn(move || {
            let mut bytes = Vec::new();
            let _ = stderr.read_to_end(&mut bytes);
            bytes
        });
        let copy = std::io::copy(&mut stdout, sink);
        if copy.is_err() {
            let _ = child.kill();
        }
        let status = child.wait()?;
        let error = error_reader.join().unwrap_or_default();
        copy?;
        if !status.success() {
            let safe = String::from_utf8_lossy(&error).replace(&self.code, "[access code]");
            bail!("FTPS transport failed ({status}): {}", safe.trim())
        }
        Ok(())
    }
    fn read(&self, path: &str, extra: &[(&str, String)]) -> Result<String> {
        let mut data = Vec::new();
        self.perform(path, extra, &mut data)?;
        Ok(String::from_utf8(data)?)
    }
    pub fn list(&mut self, folder: &str, pattern: &str) -> Result<Vec<Clip>> {
        let folder = format!("/{}/", folder.trim_matches('/'));
        if let Ok(listing) = self.read(&folder, &[("request", "MLSD".into())]) {
            let mut parsed = Vec::new();
            let mut valid = true;
            for line in listing.lines().filter(|line| !line.trim().is_empty()) {
                let Some((facts, name)) = line.split_once(' ') else {
                    valid = false;
                    break;
                };
                let facts: std::collections::BTreeMap<_, _> = facts
                    .split(';')
                    .filter_map(|fact| fact.split_once('='))
                    .map(|(key, value)| (key.to_ascii_lowercase(), value))
                    .collect();
                if facts.get("type") != Some(&"file")
                    || matches!(name, "." | "..")
                    || !glob(pattern, name)
                {
                    continue;
                }
                parsed.push(Clip {
                    name: name.into(),
                    path: format!("{folder}{name}"),
                    size: facts.get("size").and_then(|s| s.parse().ok()).unwrap_or(0),
                    mtime: facts.get("modify").and_then(|s| parse_ftp_time(s)),
                });
            }
            if valid {
                return Ok(parsed);
            }
        }
        let listing = match self.read(&folder, &[("list-only", String::new())]) {
            Ok(listing) => listing,
            Err(error)
                if error.to_string().contains("(78)")
                    || error.to_string().contains("450")
                    || error.to_string().contains("550") =>
            {
                return Ok(Vec::new())
            }
            Err(error) => return Err(error),
        };
        let mut clips = Vec::new();
        for entry in listing.lines() {
            let name = entry.rsplit('/').next().unwrap_or("");
            if matches!(name, "" | "." | "..") || !glob(pattern, name) {
                continue;
            }
            let path = format!("{folder}{name}");
            let metadata = self.metadata(&path).ok();
            clips.push(Clip {
                name: name.into(),
                path,
                size: metadata.map(|m| m.0).unwrap_or(0),
                mtime: metadata.map(|m| m.1),
            });
        }
        Ok(clips)
    }
}
impl Remote for Ftp {
    fn metadata(&mut self, path: &str) -> Result<(u64, i64)> {
        let headers = self.read(path, &[("head", String::new())])?;
        let mut size = None;
        let mut mtime = None;
        for line in headers.lines() {
            if let Some((key, value)) = line.split_once(':') {
                match key.to_ascii_lowercase().as_str() {
                    "content-length" => size = value.trim().parse().ok(),
                    "last-modified" => {
                        mtime = parse_time(value.trim(), "%a, %d %b %Y %H:%M:%S GMT")
                    }
                    _ => {}
                }
            }
        }
        match (size, mtime) {
            (Some(size), Some(time)) if size > 0 => Ok((size, time)),
            _ => bail!("Cannot verify remote clip metadata: {path}"),
        }
    }
    fn retrieve(&mut self, path: &str, sink: &mut dyn Write) -> Result<()> {
        self.perform(path, &[], sink)
    }
    fn delete(&mut self, path: &str) -> Result<()> {
        if path.contains(['\r', '\n', '\0']) {
            bail!("Invalid remote path")
        }
        self.perform(
            "/",
            &[("head", String::new()), ("quote", format!("DELE {path}"))],
            &mut std::io::sink(),
        )
    }
}
fn parse_time(value: &str, format: &str) -> Option<i64> {
    let value = CString::new(value).ok()?;
    let format = CString::new(format).ok()?;
    let mut time: libc::tm = unsafe { std::mem::zeroed() };
    let end = unsafe { libc::strptime(value.as_ptr(), format.as_ptr(), &mut time) };
    if end.is_null() || unsafe { *end } != 0 {
        return None;
    }
    let epoch = unsafe { libc::timegm(&mut time) };
    (epoch >= 0).then_some(epoch as i64)
}
pub fn parse_ftp_time(value: &str) -> Option<i64> {
    parse_time(value.trim().split('.').next()?, "%Y%m%d%H%M%S")
}
fn glob(pattern: &str, name: &str) -> bool {
    let Ok(pattern) = CString::new(pattern) else {
        return false;
    };
    let Ok(name) = CString::new(name) else {
        return false;
    };
    unsafe { libc::fnmatch(pattern.as_ptr(), name.as_ptr(), 0) == 0 }
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn private_transport_configuration_is_escaped_and_keeps_tls_session_cache() {
        let ftp = Ftp::new(
            "fixture.invalid".into(),
            990,
            "bblp".into(),
            "a\"b\\c".into(),
            Duration::from_secs(30),
        )
        .unwrap();
        let config = ftp.config("/timelapse/a b.mp4", &[]).unwrap();
        assert!(config.contains("sessionid\n"));
        assert!(config.contains("a\\\"b\\\\c"));
        assert!(config.contains("a%20b.mp4"));
        assert!(ftp
            .config("/a", &[("quote", "DELE /a\nDELE /b".into())])
            .is_err());
        assert_eq!(
            parse_ftp_time("20260102030405.123"),
            parse_time("Fri, 02 Jan 2026 03:04:05 GMT", "%a, %d %b %Y %H:%M:%S GMT")
        );
    }
}
