//! Site timing reads the deployed commit and the repository's deployment filter when someone asks for the wait.
use anyhow::{Context, Result};
use std::{
    path::Path,
    process::Command,
    time::{Duration, Instant},
};

fn list(text: &str, key: &str) -> Vec<String> {
    let mut found = false;
    let mut values = Vec::new();
    for line in text.lines() {
        let trimmed = line.trim();
        if !found {
            found = trimmed == format!("{key}:");
            continue;
        }
        if trimmed.is_empty() || trimmed.starts_with('#') {
            continue;
        }
        if let Some(value) = trimmed.strip_prefix("- ") {
            values.push(value.trim_matches(['\'', '"']).to_owned())
        } else {
            break;
        }
    }
    values
}
fn filter(root: &Path) -> Result<(Vec<String>, Vec<String>)> {
    let text = crate::text(root.join("render.yaml"))?;
    let body = text.split_once("buildFilter:").map_or("", |(_, body)| body);
    let mut paths = list(body, "paths");
    if paths.is_empty() {
        paths = [
            "web/**",
            "hardware/cad-artifacts.json",
            "updates/**",
            "render.yaml",
        ]
        .map(str::to_owned)
        .into()
    }
    Ok((paths, list(body, "ignoredPaths")))
}
fn under(path: &str, patterns: &[String]) -> bool {
    patterns.iter().any(|p| {
        crate::wildcard(p, path) || (p.ends_with("/**") && path.starts_with(&p[..p.len() - 2]))
    })
}
fn deploys(root: &Path, sha: &str, paths: &[String], ignored: &[String]) -> Result<bool> {
    Ok(
        crate::git(root, &["show", "--name-only", "--format=", sha])?
            .lines()
            .any(|p| under(p, paths) && !under(p, ignored)),
    )
}
fn live(url: &str) -> String {
    Command::new("curl")
        .args(["--silent", "--fail", "--max-time", "20", url])
        .output()
        .ok()
        .filter(|o| o.status.success())
        .and_then(|o| serde_json::from_slice::<serde_json::Value>(&o.stdout).ok())
        .and_then(|v| v["commit"].as_str().map(str::to_owned))
        .unwrap_or_default()
}
fn age(root: &Path, sha: &str) -> Result<f64> {
    Ok(crate::now()
        - crate::git(root, &["show", "-s", "--format=%ct", sha])?
            .parse::<f64>()
            .unwrap_or(crate::now()))
}
fn human(seconds: f64) -> String {
    if seconds < 90. {
        format!("{seconds:.0}s")
    } else if seconds < 5400. {
        format!("{:.1} min", seconds / 60.)
    } else {
        format!("{:.1} h", seconds / 3600.)
    }
}
fn fetch(root: &Path) -> Result<()> {
    let _ = crate::command(root, "git", &["fetch", "--quiet", "origin", "main"])?;
    Ok(())
}
fn known(root: &Path, sha: &str) -> Result<bool> {
    Ok(crate::git(root, &["cat-file", "-t", sha])? == "commit")
}
fn short(s: &str) -> &str {
    &s[..s.len().min(8)]
}
fn report(root: &Path, url: &str) -> Result<i32> {
    fetch(root)?;
    let served = live(url);
    if served.is_empty() {
        println!("  {url} did not answer; nothing can be said about the lag");
        return Ok(1);
    }
    let known = known(root, &served)?;
    println!(
        "  live   {}  {}",
        short(&served),
        if known {
            format!("served {} ago", human(age(root, &served)?))
        } else {
            "(not in this checkout)".into()
        }
    );
    if !known {
        return Ok(0);
    }
    let (paths, ignored) = filter(root)?;
    let ahead = crate::git(root, &["rev-list", &format!("{served}..origin/main")])?;
    let ahead: Vec<_> = ahead.lines().collect();
    let mut waiting = Vec::new();
    for sha in &ahead {
        if deploys(root, sha, &paths, &ignored)? {
            waiting.push(*sha)
        }
    }
    println!(
        "  origin {}  {} commit(s) past what is live, {} of them deploying",
        crate::git(root, &["rev-parse", "--short", "origin/main"])?,
        ahead.len(),
        waiting.len()
    );
    let Some(oldest) = waiting.last() else {
        println!(
            "\n  nothing is waiting: every commit past the live one touches no deploying path"
        );
        return Ok(0);
    };
    println!(
        "\n  oldest change not yet visible: {}  committed {} ago",
        short(oldest),
        human(age(root, oldest)?)
    );
    for sha in waiting.iter().rev().take(5) {
        let subject = crate::git(root, &["show", "-s", "--format=%s", sha])?;
        println!(
            "    {}  {:>8} ago  {}",
            short(sha),
            human(age(root, sha)?),
            subject.chars().take(56).collect::<String>()
        );
    }
    Ok(0)
}
pub fn cli(root: &Path, args: &[String]) -> Result<i32> {
    let mut watch = false;
    let mut timeout = 1800.;
    let mut url = "https://homesodamachine.com/api/version".to_owned();
    let mut args = args.iter();
    while let Some(arg) = args.next() {
        match arg.as_str() {
            "--watch" => watch = true,
            "--timeout" => timeout = args.next().context("--timeout needs seconds")?.parse()?,
            "--version-url" => url = args.next().context("--version-url needs a URL")?.to_owned(),
            "--help" | "-h" => {
                println!(
                    "repo-tools time-to-site [--watch] [--timeout seconds]\nReads /api/version and render.yaml's deployment filter. No build or commit starts it."
                );
                return Ok(0);
            }
            _ => anyhow::bail!("unknown time-to-site option {arg}"),
        }
    }
    if !watch {
        return report(root, &url);
    }
    let start = live(&url);
    println!(
        "  live now: {} - waiting for it to move",
        if start.is_empty() {
            "(no answer)"
        } else {
            short(&start)
        }
    );
    let began = Instant::now();
    while began.elapsed().as_secs_f64() < timeout {
        std::thread::sleep(Duration::from_secs(15));
        let current = live(&url);
        if !current.is_empty() && current != start {
            fetch(root)?;
            println!(
                "  live moved to {} after {} of waiting",
                short(&current),
                human(began.elapsed().as_secs_f64())
            );
            if known(root, &current)? {
                println!(
                    "  that commit was made {} ago - commit to visible, whole path",
                    human(age(root, &current)?)
                )
            }
            return Ok(0);
        }
    }
    println!("  the site did not move within {}", human(timeout));
    Ok(1)
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn deployment_filter_keeps_both_halves() {
        let text = "paths:\n - web/**\n - hardware/cad-artifacts.json\nignoredPaths:\n # data may update live\n - web/public/checks.json\n";
        let paths = list(text, "paths");
        let ignored = list(text, "ignoredPaths");
        assert!(under("web/lib/shell.js", &paths));
        assert!(under("web/public/checks.json", &ignored));
        assert!(!under("hardware/ledger/tools.md", &paths));
    }
}
