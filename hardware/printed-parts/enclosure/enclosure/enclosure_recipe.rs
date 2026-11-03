//! Request-local common construction expressions, with ordered operands and source records.
use anyhow::{Context, Result, ensure};
use serde_json::Value;
use std::collections::HashMap;

pub(crate) struct Shared {
    pub(crate) aliases: Vec<usize>,
    pub(crate) inputs: Vec<Vec<usize>>,
}

impl Shared {
    pub(crate) fn new(nodes: &[Value]) -> Result<Self> {
        let mut aliases = Vec::with_capacity(nodes.len());
        let mut inputs = Vec::with_capacity(nodes.len());
        let mut expressions = HashMap::new();
        for (i, node) in nodes.iter().enumerate() {
            let operands = node["inputs"]
                .as_array()
                .context("node inputs")?
                .iter()
                .map(|input| {
                    let index = input.as_u64().context("node input index")? as usize;
                    ensure!(index < i, "construction order");
                    Ok(aliases[index])
                })
                .collect::<Result<Vec<_>>>()?;
            let mut expression = node.clone();
            expression["inputs"] = serde_json::to_value(&operands)?;
            let key = serde_json::to_vec(&expression)?;
            aliases.push(*expressions.entry(key).or_insert(i));
            inputs.push(operands);
        }
        Ok(Self { aliases, inputs })
    }
}
