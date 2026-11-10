//! Keep the LAN report subscription alive while an explicit printer command is running.
use crate::{
    config::Printer,
    state::{self, Activity},
};
use anyhow::{bail, Context, Result};
use rumqttc::{Client, Event, MqttOptions, Outgoing, Packet, QoS, TlsConfiguration, Transport};
use serde_json::{json, Value};
use std::{
    collections::VecDeque,
    sync::{
        atomic::{AtomicBool, Ordering},
        mpsc::{self, Receiver},
        Arc,
    },
    thread::{self, JoinHandle},
    time::{Duration, Instant, SystemTime, UNIX_EPOCH},
};

enum Notice {
    Ready,
    Report(Value),
    Sent(u16),
    Ack(u16),
    Error(String),
}
pub struct Connection {
    printer: Printer,
    client: Client,
    incoming: Receiver<Notice>,
    reports: VecDeque<Value>,
    timeout: Duration,
    stop: Arc<AtomicBool>,
    worker: Option<JoinHandle<()>>,
    pub state: Value,
}
impl Connection {
    pub fn open(printer: &Printer, timeout: Duration) -> Result<Self> {
        let mut options = MqttOptions::new(
            format!(
                "hsm-{}",
                SystemTime::now().duration_since(UNIX_EPOCH)?.as_nanos()
            ),
            &printer.host,
            8883,
        );
        options.set_credentials("bblp", &printer.access_code);
        options.set_keep_alive(Duration::from_secs(30));
        options.set_max_packet_size(1024 * 1024, 1024 * 1024);
        let connector = native_tls::TlsConnector::builder()
            .danger_accept_invalid_certs(true)
            .danger_accept_invalid_hostnames(true)
            .build()?;
        options.set_transport(Transport::Tls(TlsConfiguration::NativeConnector(connector)));
        let (client, mut connection) = Client::new(options, 32);
        connection
            .eventloop
            .network_options
            .set_connection_timeout(timeout.as_secs().max(1));
        client.subscribe(
            format!("device/{}/report", printer.serial),
            QoS::AtLeastOnce,
        )?;
        let (tx, incoming) = mpsc::channel();
        let stop = Arc::new(AtomicBool::new(false));
        let worker_stop = stop.clone();
        let worker = thread::spawn(move || {
            let mut connected = false;
            while !worker_stop.load(Ordering::Relaxed) {
                let event = match connection.recv_timeout(if connected {
                    Duration::from_millis(250)
                } else {
                    timeout
                }) {
                    Ok(Ok(event)) => event,
                    Ok(Err(error)) => {
                        let _ = tx.send(Notice::Error(format!("{error:?}")));
                        break;
                    }
                    Err(rumqttc::RecvTimeoutError::Timeout) => continue,
                    Err(error) => {
                        let _ = tx.send(Notice::Error(format!("{error:?}")));
                        break;
                    }
                };
                let notice = match event {
                    Event::Incoming(Packet::ConnAck(_)) => {
                        connected = true;
                        continue;
                    }
                    Event::Incoming(Packet::SubAck(ack)) => {
                        if ack
                            .return_codes
                            .iter()
                            .any(|code| matches!(code, rumqttc::SubscribeReasonCode::Failure))
                        {
                            Notice::Error("MQTT subscription failed".into())
                        } else {
                            Notice::Ready
                        }
                    }
                    Event::Incoming(Packet::Publish(message)) => {
                        match serde_json::from_slice(&message.payload) {
                            Ok(value) => Notice::Report(value),
                            Err(_) => continue,
                        }
                    }
                    Event::Incoming(Packet::PubAck(ack)) => Notice::Ack(ack.pkid),
                    Event::Outgoing(Outgoing::Publish(pkid)) => Notice::Sent(pkid),
                    _ => continue,
                };
                if tx.send(notice).is_err() {
                    break;
                }
            }
        });
        let mut result = Self {
            printer: printer.clone(),
            client,
            incoming,
            reports: VecDeque::new(),
            timeout,
            stop,
            worker: Some(worker),
            state: json!({}),
        };
        let deadline = Instant::now() + timeout;
        loop {
            match result.notice(deadline)? {
                Notice::Ready => return Ok(result),
                Notice::Report(report) => result.reports.push_back(report),
                _ => {}
            }
        }
    }
    fn notice(&mut self, deadline: Instant) -> Result<Notice> {
        let remaining = deadline.saturating_duration_since(Instant::now());
        if remaining.is_zero() {
            bail!(
                "{}: no matching printer response within {:?}",
                self.printer.name,
                self.timeout
            )
        }
        let notice = self
            .incoming
            .recv_timeout(remaining)
            .with_context(|| format!("{}: no matching printer response", self.printer.name))?;
        if let Notice::Error(error) = notice {
            bail!("{}: {error}", self.printer.name)
        }
        Ok(notice)
    }
    pub fn next(&mut self, wait: Duration) -> Result<Option<Value>> {
        if let Some(report) = self.reports.pop_front() {
            state::merge(&mut self.state, &report);
            return Ok(Some(report));
        }
        let deadline = Instant::now() + wait;
        loop {
            let notice = if wait.is_zero() {
                match self.incoming.try_recv() {
                    Ok(n) => n,
                    Err(mpsc::TryRecvError::Empty) => return Ok(None),
                    Err(error) => return Err(error.into()),
                }
            } else {
                match self
                    .incoming
                    .recv_timeout(deadline.saturating_duration_since(Instant::now()))
                {
                    Ok(n) => n,
                    Err(mpsc::RecvTimeoutError::Timeout) => return Ok(None),
                    Err(error) => return Err(error.into()),
                }
            };
            match notice {
                Notice::Report(report) => {
                    state::merge(&mut self.state, &report);
                    return Ok(Some(report));
                }
                Notice::Error(error) => bail!("{}: {error}", self.printer.name),
                _ => {}
            }
        }
    }
    pub fn send(&mut self, section: &str, command: &str, values: Value) -> Result<String> {
        let sequence =
            (SystemTime::now().duration_since(UNIX_EPOCH)?.as_nanos() % 1_000_000_000).to_string();
        let mut body = values.as_object().cloned().unwrap_or_default();
        body.insert("sequence_id".into(), json!(sequence));
        body.insert("command".into(), json!(command));
        let mut message = json!({});
        message[section] = json!(body);
        self.client.publish(
            format!("device/{}/request", self.printer.serial),
            QoS::AtLeastOnce,
            false,
            serde_json::to_vec(&message)?,
        )?;
        let deadline = Instant::now() + self.timeout;
        let mut packet = None;
        loop {
            match self.notice(deadline)? {
                Notice::Report(report) => self.reports.push_back(report),
                Notice::Sent(id) => packet = Some(id),
                Notice::Ack(id) if packet == Some(id) => return Ok(sequence),
                _ => {}
            }
        }
    }
    pub fn status(&mut self) -> Result<Value> {
        self.send("pushing", "pushall", json!({"version":1,"push_target":1}))?;
        let deadline = Instant::now() + self.timeout;
        while Instant::now() < deadline {
            if self
                .next(deadline.saturating_duration_since(Instant::now()))?
                .is_some()
                && self.state["print"].get("gcode_state").is_some()
                && self.state["print"].get("lights_report").is_some()
            {
                return Ok(self.state["print"].clone());
            }
        }
        bail!("{}: no complete printer status", self.printer.name)
    }
    pub fn light(&mut self, node: &str, mode: &str) -> Result<Value> {
        self.status()?;
        let sequence=self.send("system","ledctrl",json!({"led_node":node,"led_mode":mode,"led_on_time":500,"led_off_time":500,"loop_times":0,"interval_time":0}))?;
        let deadline = Instant::now() + self.timeout;
        let mut confirmed = false;
        while Instant::now() < deadline {
            if let Some(message) = self.next(deadline.saturating_duration_since(Instant::now()))? {
                if message["system"]["sequence_id"] == sequence {
                    if message["system"]["result"] != "success" {
                        bail!(
                            "{}: light command rejected: {}",
                            self.printer.name,
                            message["system"]["reason"]
                        )
                    }
                    confirmed = true;
                    break;
                }
            }
        }
        if !confirmed {
            bail!("{}: no light command response", self.printer.name)
        }
        self.send("pushing", "pushall", json!({"version":1,"push_target":1}))?;
        let deadline = Instant::now() + self.timeout;
        while Instant::now() < deadline {
            if let Some(message) = self.next(deadline.saturating_duration_since(Instant::now()))? {
                if message["print"]["lights_report"]
                    .as_array()
                    .is_some_and(|items| {
                        items
                            .iter()
                            .any(|item| item["node"] == node && item["mode"] == mode)
                    })
                {
                    return Ok(
                        json!({"printer":self.printer.name,"node":node,"mode":mode,"verified":true}),
                    );
                }
            }
        }
        bail!("{}: light state was not verified", self.printer.name)
    }
}
impl Drop for Connection {
    fn drop(&mut self) {
        let _ = self.client.try_disconnect();
        self.stop.store(true, Ordering::Relaxed);
        if let Some(worker) = self.worker.take() {
            let _ = worker.join();
        }
    }
}

pub struct Watch {
    pub connection: Connection,
    pub activity: Activity,
}
impl Watch {
    pub fn open(printer: &Printer) -> Result<Self> {
        let mut connection = Connection::open(printer, Duration::from_secs(12))?;
        let initial = connection.status()?;
        Ok(Self {
            connection,
            activity: Activity::new(initial),
        })
    }
    pub fn drain(&mut self, wait: Duration) -> Result<&Value> {
        let deadline = Instant::now() + wait;
        loop {
            let Some(message) = self
                .connection
                .next(deadline.saturating_duration_since(Instant::now()))?
            else {
                break;
            };
            self.activity.receive(&message);
        }
        Ok(&self.activity.reading)
    }
    pub fn fresh(&mut self) -> Result<&Value> {
        self.drain(Duration::ZERO)?;
        self.connection
            .send("pushing", "pushall", json!({"version":1,"push_target":1}))?;
        let deadline = Instant::now() + Duration::from_secs(12);
        while Instant::now() < deadline {
            if let Some(message) = self
                .connection
                .next(deadline.saturating_duration_since(Instant::now()))?
            {
                self.activity.receive(&message);
                if message["print"].get("gcode_state").is_some() {
                    return Ok(&self.activity.reading);
                }
            }
        }
        bail!("No fresh printer status; no further send will be attempted")
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn publication_waits_for_its_ack_and_retains_interleaved_reports() {
        let (client, _unpolled_transport) =
            Client::new(MqttOptions::new("fixture", "fixture.invalid", 8883), 32);
        let (tx, incoming) = mpsc::channel();
        let mut connection = Connection {
            printer: Printer {
                name: "fixture".into(),
                serial: "fixture".into(),
                host: "fixture.invalid".into(),
                access_code: "fixture-only".into(),
            },
            client,
            incoming,
            reports: VecDeque::new(),
            timeout: Duration::from_millis(50),
            stop: Arc::new(AtomicBool::new(false)),
            worker: None,
            state: json!({}),
        };
        let report = json!({"print":{"gcode_state":"IDLE","lights_report":[]}});
        tx.send(Notice::Report(report.clone())).unwrap();
        tx.send(Notice::Sent(41)).unwrap();
        tx.send(Notice::Ack(40)).unwrap();
        tx.send(Notice::Ack(41)).unwrap();
        connection
            .send("pushing", "pushall", json!({"version":1}))
            .unwrap();
        assert_eq!(connection.next(Duration::ZERO).unwrap(), Some(report));
        assert_eq!(connection.state["print"]["gcode_state"], "IDLE");
        tx.send(Notice::Sent(42)).unwrap();
        tx.send(Notice::Ack(41)).unwrap();
        drop(tx);
        assert!(connection
            .send("pushing", "pushall", json!({"version":1}))
            .is_err());
    }
    #[test]
    fn fresh_status_crosses_the_backlog_before_a_possible_send() {
        let (client, _unpolled_transport) =
            Client::new(MqttOptions::new("fixture", "fixture.invalid", 8883), 32);
        let (tx, incoming) = mpsc::channel();
        let before = json!({"job_id":"old","gcode_state":"FINISH"});
        let mut watch = Watch {
            connection: Connection {
                printer: Printer {
                    name: "fixture".into(),
                    serial: "fixture".into(),
                    host: "fixture.invalid".into(),
                    access_code: "fixture-only".into(),
                },
                client,
                incoming,
                reports: VecDeque::from([json!({"print":before})]),
                timeout: Duration::from_millis(200),
                stop: Arc::new(AtomicBool::new(false)),
                worker: None,
                state: json!({}),
            },
            activity: Activity::new(before.clone()),
        };
        let transport = thread::spawn(move || {
            thread::sleep(Duration::from_millis(15));
            tx.send(Notice::Sent(1)).unwrap();
            tx.send(Notice::Ack(1)).unwrap();
            tx.send(Notice::Report(json!({"print":{"job_id":"new","gcode_state":"RUNNING","subtask_name":"fixture.gcode.3mf"}}))).unwrap();
        });
        let current = watch.fresh().unwrap().clone();
        transport.join().unwrap();
        assert!(state::accepted(&before, &current, "fixture.gcode.3mf"));
        assert!(watch.activity.activity);
        assert!(!state::may_retry(
            &before,
            &current,
            watch.activity.activity,
            ""
        ));
    }
}
