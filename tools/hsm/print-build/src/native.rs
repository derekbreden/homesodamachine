//! Native producer requests stage declared files and reuse the engine's program and result store.
use crate::{BuildChild, exit_code, wrapped};
use anyhow::{Context, Result, ensure};
use hsm_build_plan::{
    planning::{Action, RuntimeInput},
    receipt::{TargetReceipt, TargetStatus},
};
use hsm_run_slots::Lease;
use serde::{Deserialize, Serialize};
use serde_json::{Value, json};
use std::{
    collections::{BTreeMap, BTreeSet},
    env,
    fs::{self, File},
    os::unix::fs::{PermissionsExt, symlink},
    path::{Component, Path, PathBuf},
    sync::atomic::{AtomicU64, Ordering},
    time::Instant,
};

static STAGE_SERIAL: AtomicU64 = AtomicU64::new(0);

const TOOL_ENVIRONMENT: &[&str] = &[
    "PATH",
    "PUPPETEER_CACHE_DIR",
    "PUPPETEER_EXECUTABLE_PATH",
    "CHROME_BIN",
    "BLENDER",
    "BLENDER_USER_RESOURCES",
    "FONTCONFIG_PATH",
    "FONTCONFIG_FILE",
    "HSM_SKIP_MESH_PAYLOAD",
    "HSM_NODE",
    "HSM_BLENDER",
    "HSM_RENDERER",
    "HSM_PARSE_TIMEOUT",
    "HSM_CARD_TIMEOUT",
    "HSM_ZLIB_LIBRARY",
    "HSM_BIN",
    "HSM_SOCKET",
    "HSM_STORE",
    "HSM_KEEP_HOURS",
];

/// Explicit tool settings enter the producer identity while lease descriptors remain runtime-owned.
fn tool_environment(
    values: impl IntoIterator<Item = (String, String)>,
) -> BTreeMap<String, String> {
    values
        .into_iter()
        .filter(|(name, _)| TOOL_ENVIRONMENT.contains(&name.as_str()))
        .collect()
}

pub(crate) fn repository_path(name: &str) -> Result<&Path> {
    let path = Path::new(name);
    ensure!(
        !name.is_empty()
            && path
                .components()
                .all(|part| matches!(part, Component::Normal(_))),
        "declared repository path is not relative: {name}"
    );
    Ok(path)
}

/// A stage contains only this producer's runtime inputs and temporary generated files.
pub(crate) struct Stage {
    pub root: PathBuf,
    pub inputs: Vec<String>,
}

impl Drop for Stage {
    fn drop(&mut self) {
        let _ = fs::remove_dir_all(&self.root);
    }
}

impl Stage {
    pub fn prepare(
        workspace: &Path,
        run: &Path,
        target: &str,
        inputs: &BTreeMap<String, RuntimeInput>,
        completed: &BTreeMap<String, TargetReceipt>,
        retained: bool,
    ) -> Result<Self> {
        ensure!(
            Path::new(target).components().count() == 1 && repository_path(target).is_ok(),
            "native target name {target}"
        );
        let work = run.join("work");
        fs::create_dir_all(&work)?;
        let root = loop {
            let serial = STAGE_SERIAL.fetch_add(1, Ordering::Relaxed);
            let candidate = work.join(format!("{target}-{}-{serial}", std::process::id()));
            match fs::create_dir(&candidate) {
                Ok(()) => break candidate,
                Err(error) if error.kind() == std::io::ErrorKind::AlreadyExists => (),
                Err(error) => return Err(error.into()),
            }
        };
        let stage = Self {
            root,
            inputs: inputs.keys().cloned().collect(),
        };
        for (name, input) in inputs {
            let destination = stage.root.join(repository_path(name)?);
            if let Some(projection) = &input.projection {
                projection.write(workspace, &destination)?;
                continue;
            }
            let source = if retained {
                Some(workspace.join(name))
            } else {
                match input
                    .producer
                    .as_ref()
                    .and_then(|producer| completed.get(producer))
                {
                    Some(result) => result.outputs.get(name).cloned(),
                    None => Some(workspace.join(name)),
                }
            };
            // Absence is a declared input too; an unavailable fresh export never falls back to held bytes.
            let Some(source) = source.filter(|path| path.is_file()) else {
                continue;
            };
            fs::create_dir_all(destination.parent().context("staged input parent")?)?;
            snapshot_file(&source, &destination)
                .with_context(|| format!("stage {name} from {}", source.display()))?;
            let mode = source.metadata()?.permissions().mode() | 0o200;
            fs::set_permissions(&destination, fs::Permissions::from_mode(mode))?;
        }
        for packages in [
            "tools/render/node_modules",
            "web/node_modules",
            "hardware/pcb/pcba/node_modules",
        ] {
            let parent = Path::new(packages).parent().unwrap().to_string_lossy();
            if inputs
                .keys()
                .any(|name| name.starts_with(&format!("{parent}/")))
                && workspace.join(packages).is_dir()
            {
                let destination = stage.root.join(packages);
                fs::create_dir_all(destination.parent().unwrap())?;
                symlink(workspace.join(packages), destination)?;
            }
        }
        Ok(stage)
    }
}

/// Filesystem snapshots retain independent staged bytes without copying an entire build tree.
fn snapshot_file(source: &Path, destination: &Path) -> Result<()> {
    #[cfg(target_os = "macos")]
    {
        use std::{ffi::CString, os::unix::ffi::OsStrExt};
        let source = CString::new(source.as_os_str().as_bytes())?;
        let target = CString::new(destination.as_os_str().as_bytes())?;
        if unsafe { libc::clonefile(source.as_ptr(), target.as_ptr(), 0) } == 0 {
            return Ok(());
        }
    }
    fs::copy(source, destination)?;
    Ok(())
}

#[derive(Debug, Serialize)]
pub(crate) struct RunAsk {
    pub op: &'static str,
    pub workspace: PathBuf,
    pub root: PathBuf,
    #[serde(rename = "crate")]
    pub krate: String,
    pub name: String,
    pub args: Vec<String>,
    pub inputs: Vec<String>,
    pub outputs: Vec<String>,
    pub compiler_inputs: Vec<String>,
    pub environment: BTreeMap<String, String>,
    pub allow_compile: bool,
    pub cache_only: bool,
}

impl RunAsk {
    pub fn new(
        workspace: &Path,
        stage: &Stage,
        action: &Action,
        progress: &Path,
        preview: bool,
        cache_only: bool,
    ) -> Self {
        let mut environment = tool_environment(env::vars());
        environment.insert(
            "HSM_BUILD_PROGRESS".into(),
            progress.to_string_lossy().into_owned(),
        );
        Self {
            op: "run",
            workspace: workspace.to_path_buf(),
            root: stage.root.clone(),
            krate: action.program.krate.clone(),
            name: action.program.name.clone(),
            args: if preview {
                vec!["--placements-only".into()]
            } else {
                Vec::new()
            },
            inputs: stage.inputs.clone(),
            outputs: action
                .outputs()
                .filter(|name| !preview || name.ends_with("/enclosure-assembly.step.mesh"))
                .map(str::to_owned)
                .collect(),
            compiler_inputs: action.program.sources.iter().cloned().collect(),
            environment,
            allow_compile: !preview,
            cache_only,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn renderer_settings_and_nested_retention_survive_without_host_lease_or_secret_values() {
        let selected = tool_environment([
            ("PUPPETEER_CACHE_DIR".into(), "/opt/browser cache".into()),
            ("FONTCONFIG_FILE".into(), "/fonts/config.xml".into()),
            ("HSM_BLENDER".into(), "/opt/blender/bin/blender".into()),
            ("HSM_KEEP_HOURS".into(), "retention setting".into()),
            ("HSM_RUN_LEASE".into(), "unverified descriptors".into()),
            ("HSM_CAD_LEASE".into(), "unverified CAD descriptor".into()),
            (
                "HSM_COMPILER_LEASE".into(),
                "unverified compiler descriptor".into(),
            ),
            ("HSM_RUN_BROKER".into(), "unverified broker".into()),
            ("GITHUB_TOKEN".into(), "private token".into()),
        ]);
        assert_eq!(selected.len(), 4);
        assert_eq!(selected["PUPPETEER_CACHE_DIR"], "/opt/browser cache");
        assert_eq!(selected["FONTCONFIG_FILE"], "/fonts/config.xml");
        assert_eq!(selected["HSM_BLENDER"], "/opt/blender/bin/blender");
        assert_eq!(selected["HSM_KEEP_HOURS"], "retention setting");
    }
}

fn available() -> bool {
    true
}

#[derive(Debug, Default, Deserialize)]
pub(crate) struct Answer {
    #[serde(default = "available")]
    pub available: bool,
    #[serde(default)]
    pub hit: bool,
    #[serde(default)]
    pub compiled: bool,
    #[serde(default)]
    pub artifacts: BTreeMap<String, PathBuf>,
    #[serde(default)]
    pub file_hashes: BTreeMap<String, String>,
    #[serde(default)]
    pub missing_outputs: Vec<String>,
    #[serde(default)]
    pub stdout: String,
    #[serde(default)]
    pub stderr: String,
    #[serde(default)]
    pub program_seconds: f64,
    #[serde(default)]
    pub seconds: f64,
    #[serde(default)]
    pub code: String,
    #[serde(default)]
    pub key: String,
}

pub(crate) struct Completion {
    pub target: String,
    pub _stage: Stage,
    pub exit_code: i32,
    pub seconds: f64,
    pub answer: std::result::Result<Answer, String>,
}

impl Completion {
    pub fn receipt(&self, declared_outputs: Vec<String>) -> TargetReceipt {
        let mut result = TargetReceipt {
            declared_outputs,
            ..TargetReceipt::default()
        };
        result.extra.insert("seconds".into(), json!(self.seconds));
        result
            .extra
            .insert("exit_code".into(), json!(self.exit_code));
        match &self.answer {
            Err(error) => {
                result.status = TargetStatus::Failed;
                result.extra.insert("error".into(), json!(error));
            }
            Ok(answer) => {
                result.status = if !answer.available {
                    TargetStatus::NotCurrent
                } else if answer.hit {
                    TargetStatus::Cached
                } else {
                    TargetStatus::Built
                };
                let declared: BTreeSet<_> = result.declared_outputs.iter().collect();
                result.outputs = answer
                    .artifacts
                    .iter()
                    .filter(|(name, _)| declared.contains(name))
                    .map(|(name, path)| (name.clone(), path.clone()))
                    .collect();
                for (name, value) in [
                    ("hit", json!(answer.hit)),
                    ("compiled", json!(answer.compiled)),
                    ("program_seconds", json!(answer.program_seconds)),
                    ("engine_seconds", json!(answer.seconds)),
                    ("code", json!(answer.code)),
                    ("key", json!(answer.key)),
                    ("file_hashes", json!(answer.file_hashes)),
                    ("missing_outputs", json!(answer.missing_outputs)),
                ] {
                    result.extra.insert(name.into(), value);
                }
            }
        }
        result
    }
}

/// One asynchronous engine client lets completed producers reach the viewer before other replies.
pub(crate) struct Invocation {
    target: String,
    stage: Option<Stage>,
    process: BuildChild,
    response: PathBuf,
    diagnostics: PathBuf,
    started: Instant,
}

impl Invocation {
    pub fn start(
        workspace: &Path,
        run: &Path,
        runner: &Path,
        engine: &Path,
        lease: &Lease,
        target: &str,
        stage: Stage,
        ask: RunAsk,
    ) -> Result<Self> {
        let response = run.join(format!("{target}.response.json"));
        let diagnostics = run.join(format!("{target}.log"));
        let args = vec![
            "--root".to_owned(),
            workspace.to_string_lossy().into_owned(),
            "request".into(),
            serde_json::to_string(&ask)?,
        ];
        let mut command = wrapped(runner, workspace, engine, &args, lease)?;
        command
            .stdout(File::create(&response)?)
            .stderr(File::create(&diagnostics)?);
        let process = BuildChild(
            command
                .spawn()
                .with_context(|| format!("start native producer {target}"))?,
        );
        Ok(Self {
            target: target.to_owned(),
            stage: Some(stage),
            process,
            response,
            diagnostics,
            started: Instant::now(),
        })
    }
    pub fn poll(&mut self) -> Result<Option<Completion>> {
        let Some(status) = self.process.0.try_wait()? else {
            return Ok(None);
        };
        let code = exit_code(status);
        let answer = (|| -> Result<Answer> {
            let response: Value = serde_json::from_slice(&fs::read(&self.response)?)?;
            ensure!(
                status.success() && response["ok"] == true,
                "{}",
                response["error"]
                    .as_str()
                    .map(str::to_owned)
                    .unwrap_or_else(|| format!(
                        "engine client exited {code}: {}",
                        fs::read_to_string(&self.diagnostics).unwrap_or_default()
                    ))
            );
            let answer: Answer = serde_json::from_value(response["result"].clone())?;
            if !answer.stdout.is_empty() || !answer.stderr.is_empty() {
                let mut text = answer.stdout.clone();
                text.push_str(&answer.stderr);
                fs::write(&self.diagnostics, text)?;
            }
            Ok(answer)
        })()
        .map_err(|error| format!("{error:#}"));
        let _ = fs::remove_file(&self.response);
        Ok(Some(Completion {
            target: self.target.clone(),
            _stage: self.stage.take().context("completed native stage")?,
            exit_code: code,
            seconds: self.started.elapsed().as_secs_f64(),
            answer,
        }))
    }
}
