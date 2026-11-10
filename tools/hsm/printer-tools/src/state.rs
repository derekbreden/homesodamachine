//! Merge sparse printer reports and keep acceptance and repeat-send decisions explicit.
use serde_json::{json, Value};

pub fn merge(destination: &mut Value, update: &Value) {
    if let (Some(dst), Some(src)) = (destination.as_object_mut(), update.as_object()) {
        for (key, value) in src {
            if value.is_object() && dst.get(key).is_some_and(Value::is_object) {
                merge(dst.get_mut(key).unwrap(), value);
            } else {
                dst.insert(key.clone(), value.clone());
            }
        }
    } else {
        *destination = update.clone();
    }
}
pub fn text(value: &Value) -> String {
    if value.is_null() {
        String::new()
    } else {
        value
            .as_str()
            .map(str::to_owned)
            .unwrap_or_else(|| value.to_string())
    }
}
pub fn truth(value: &Value) -> bool {
    match value {
        Value::Null => false,
        Value::Bool(b) => *b,
        Value::Number(n) => n.as_f64() != Some(0.),
        Value::String(s) => !s.is_empty(),
        Value::Array(a) => !a.is_empty(),
        Value::Object(o) => !o.is_empty(),
    }
}
fn or(value: &Value, fallback: Value) -> Value {
    if truth(value) {
        value.clone()
    } else {
        fallback
    }
}
pub fn busy(reading: &Value) -> bool {
    matches!(
        reading["gcode_state"].as_str(),
        Some("PREPARE" | "RUNNING" | "PAUSE")
    )
}
pub fn accepted(before: &Value, reading: &Value, name: &str) -> bool {
    !text(&reading["job_id"]).is_empty()
        && text(&reading["job_id"]) != text(&before["job_id"])
        && reading["subtask_name"] == name
        && matches!(reading["gcode_state"].as_str(), Some("PREPARE" | "RUNNING"))
        && !truth(&reading["print_error"])
}
pub fn may_retry(before: &Value, reading: &Value, activity: bool, page: &str) -> bool {
    let known_idle = !text(&before["job_id"]).is_empty()
        || (before["gcode_state"] == "IDLE"
            && reading["gcode_state"] == "IDLE"
            && !truth(&before["subtask_name"])
            && !truth(&reading["subtask_name"]));
    let page = page.to_lowercase();
    !activity
        && known_idle
        && text(&reading["job_id"]) == text(&before["job_id"])
        && matches!(
            reading["gcode_state"].as_str(),
            Some("IDLE" | "FINISH" | "FAILED")
        )
        && matches!(reading["upload"]["status"].as_str(), None | Some("idle"))
        && or(&reading["print_error"], json!(0)) == or(&before["print_error"], json!(0))
        && or(&reading["hms"], json!([])) == or(&before["hms"], json!([]))
        && !truth(&reading["nozzle_target_temper"])
        && !truth(&reading["bed_target_temper"])
        && !["sending", "uploading", "downloading"]
            .iter()
            .any(|word| page.contains(word))
}
pub fn manual_heat(reading: &Value) -> bool {
    !busy(reading)
        && ["nozzle_target_temper", "bed_target_temper"]
            .iter()
            .any(|key| reading[*key].as_f64().unwrap_or(0.) > 0.)
}

#[derive(Default)]
pub struct Activity {
    pub reading: Value,
    pub initial: Value,
    pub events: Vec<Value>,
    pub activity: bool,
    pub reply: Option<Value>,
    last_event: Value,
}
impl Activity {
    pub fn new(reading: Value) -> Self {
        Self {
            initial: reading.clone(),
            reading,
            ..Default::default()
        }
    }
    pub fn receive(&mut self, message: &Value) {
        let update = &message["print"];
        if !update.is_object() {
            return;
        }
        merge(&mut self.reading, update);
        if update["command"] == "project_file" {
            let reply = json!({"command":update["command"],"result":update["result"],"reason":update["reason"],"err_code":update["err_code"]});
            self.events.push(reply.clone());
            self.reply = Some(reply);
            self.activity = true;
        }
        if text(&self.reading["job_id"]) != text(&self.initial["job_id"])
            || busy(&self.reading)
            || !matches!(
                self.reading["upload"]["status"].as_str(),
                None | Some("idle")
            )
        {
            self.activity = true;
        }
        let mut event = json!({});
        for key in [
            "job_id",
            "subtask_name",
            "gcode_state",
            "print_error",
            "hms",
            "layer_num",
        ] {
            event[key] = self.reading[key].clone();
        }
        if event != self.last_event {
            self.events.push(event.clone());
            self.last_event = event;
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn ambiguous_and_transient_activity_never_allow_a_second_send() {
        let before = json!({"job_id":"old","gcode_state":"FINISH","hms":[],"print_error":0});
        assert!(may_retry(&before, &before, false, "Idle"));
        assert!(!may_retry(
            &json!({}),
            &json!({"gcode_state":"IDLE"}),
            false,
            ""
        ));
        for patch in [
            json!({"job_id":"new"}),
            json!({"nozzle_target_temper":200}),
            json!({"upload":{"status":"uploading"}}),
            json!({"hms":[1]}),
            json!({"print_error":1}),
        ] {
            let mut reading = before.clone();
            merge(&mut reading, &patch);
            assert!(!may_retry(&before, &reading, false, ""));
        }
        assert!(!may_retry(&before, &before, false, "Downloading"));
        let mut watch = Activity::new(before.clone());
        watch.receive(&json!({"print":{"upload":{"status":"uploading"}}}));
        watch.receive(&json!({"print":{"upload":{"status":"idle"}}}));
        assert!(!may_retry(&before, &watch.reading, watch.activity, ""));
        let mut watch = Activity::new(before.clone());
        watch.receive(&json!({"print":{"command":"project_file","result":"fail"}}));
        assert!(watch.activity && watch.reply.is_some());
        assert!(!may_retry(&before, &watch.reading, watch.activity, ""));
    }
    #[test]
    fn acceptance_requires_a_new_job_and_the_exact_archive() {
        let before = json!({"job_id":7});
        let mut current = json!({"job_id":8,"subtask_name":"test.gcode.3mf","gcode_state":"PREPARE","print_error":0});
        assert!(accepted(&before, &current, "test.gcode.3mf"));
        current["job_id"] = json!(7);
        assert!(!accepted(&before, &current, "test.gcode.3mf"));
        current["job_id"] = json!(8);
        current["print_error"] = json!(1);
        assert!(!accepted(&before, &current, "test.gcode.3mf"));
        current["print_error"] = json!(0);
        assert!(!accepted(&before, &current, "other.gcode.3mf"));
    }
}
