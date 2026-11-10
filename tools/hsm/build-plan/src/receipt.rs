//! Native receipts retain each selected producer's completed exports and execution status.
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::{
    collections::{BTreeMap, BTreeSet},
    path::PathBuf,
};

#[derive(Debug, Clone, Copy, Default, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "kebab-case")]
pub enum TargetStatus {
    Built,
    Cached,
    Failed,
    #[default]
    Blocked,
    NotCurrent,
}

impl TargetStatus {
    pub fn usable(self) -> bool {
        matches!(self, Self::Built | Self::Cached)
    }
}

#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct TargetReceipt {
    pub status: TargetStatus,
    #[serde(default)]
    pub declared_outputs: Vec<String>,
    #[serde(default)]
    pub outputs: BTreeMap<String, PathBuf>,
    #[serde(default, flatten)]
    pub extra: BTreeMap<String, Value>,
}

fn schema() -> u32 {
    1
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RunReceipt {
    pub schema: u32,
    #[serde(default)]
    pub requested: BTreeSet<String>,
    #[serde(default)]
    pub selected: BTreeSet<String>,
    #[serde(default)]
    pub targets: BTreeMap<String, TargetReceipt>,
    #[serde(default, flatten)]
    pub extra: BTreeMap<String, Value>,
}

impl Default for RunReceipt {
    fn default() -> Self {
        Self {
            schema: schema(),
            requested: BTreeSet::new(),
            selected: BTreeSet::new(),
            targets: BTreeMap::new(),
            extra: BTreeMap::new(),
        }
    }
}

impl RunReceipt {
    pub fn unavailable_targets(&self) -> BTreeSet<String> {
        self.targets
            .iter()
            .filter(|(_, result)| !result.status.usable())
            .map(|(name, _)| name.clone())
            .collect()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;
    #[test]
    fn native_status_and_optional_execution_metrics_survive_rereading() {
        let value = json!({"schema":1,"requested":["part"],"selected":["part"],"execution_count":2,"targets":{"part":{"status":"not-current","declared_outputs":["part.step"],"outputs":{},"engine":"retained"}}});
        let receipt: RunReceipt = serde_json::from_value(value.clone()).unwrap();
        assert_eq!(receipt.targets["part"].status, TargetStatus::NotCurrent);
        assert_eq!(
            receipt.unavailable_targets(),
            BTreeSet::from(["part".to_owned()])
        );
        assert_eq!(serde_json::to_value(receipt).unwrap(), value);
    }
}
