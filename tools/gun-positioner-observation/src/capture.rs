//! A source delivers timestamped frames, declared drops and helper events.
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::collections::BTreeMap;

#[derive(Clone, Debug, PartialEq, Eq)]
pub enum Codec {
    Jpeg,
    Gray8,
    Gray16,
    Nv12,
    Other(String),
}
impl Serialize for Codec {
    fn serialize<S: serde::Serializer>(&self, serializer: S) -> Result<S::Ok, S::Error> {
        serializer.serialize_str(match self {
            Self::Jpeg => "jpeg",
            Self::Gray8 => "gray8",
            Self::Gray16 => "gray16",
            Self::Nv12 => "nv12",
            Self::Other(value) => value,
        })
    }
}
impl<'de> Deserialize<'de> for Codec {
    fn deserialize<D: serde::Deserializer<'de>>(deserializer: D) -> Result<Self, D::Error> {
        let value = String::deserialize(deserializer)?;
        Ok(match value.as_str() {
            "jpeg" => Self::Jpeg,
            "gray8" => Self::Gray8,
            "gray16" => Self::Gray16,
            "nv12" => Self::Nv12,
            _ => Self::Other(value),
        })
    }
}

#[derive(Clone, Debug)]
pub struct RawFrame {
    pub payload: Vec<u8>,
    pub codec: Codec,
    pub width: Option<usize>,
    pub height: Option<usize>,
    pub source_seq: Option<u64>,
    pub device_pts_ns: Option<u64>,
    pub source_host_ns: Option<u64>,
    pub duration_ns: Option<u64>,
    pub subtype: Option<String>,
}

#[derive(Clone, Debug)]
pub enum SourceItem {
    Frame(RawFrame),
    Drop {
        device_pts_ns: Option<u64>,
        reason: String,
    },
    Event {
        event: String,
        detail: BTreeMap<String, Value>,
    },
}
