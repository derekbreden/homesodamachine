//! Construction identities follow existing face records through geometry operations and imports.
use anyhow::{Context, Result};
use serde_json::{Value, json};
use std::{collections::BTreeMap, sync::Mutex};

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Feature {
    pub id: String,
    pub label: String,
    pub parent: Option<String>,
    pub related: Vec<String>,
    pub source: String,
}

impl Feature {
    pub fn json(&self) -> Value {
        let mut value = json!({"id":self.id,"label":self.label,"source":self.source});
        if let Some(parent) = &self.parent { value["parent"] = json!(parent); }
        if !self.related.is_empty() { value["related"] = json!(self.related); }
        value
    }

    pub fn read(value: &Value) -> Result<Self> {
        let text = |key| value[key].as_str().map(str::to_owned).with_context(|| format!("feature {key}"));
        Ok(Self { id: text("id")?, label: text("label")?, source: text("source")?,
            parent: value["parent"].as_str().map(str::to_owned),
            related: value["related"].as_array().into_iter().flatten().filter_map(Value::as_str).map(str::to_owned).collect() })
    }
}

/// Intern an authored identity once; face records share its reference rather than its text.
pub fn intern(feature: Feature) -> &'static Feature {
    static FEATURES: Mutex<BTreeMap<String, &'static Feature>> = Mutex::new(BTreeMap::new());
    let key = feature.json().to_string();
    let mut features = FEATURES.lock().unwrap_or_else(|e| e.into_inner());
    *features.entry(key).or_insert_with(|| Box::leak(Box::new(feature)))
}
