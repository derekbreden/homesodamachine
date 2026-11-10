//! The studio clock maps source motion, recorded words and picture contacts through authored holds.
use crate::{json, root};
use anyhow::{Context, Result, ensure};
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::{
    collections::BTreeMap,
    path::{Path, PathBuf},
};

pub fn here() -> PathBuf {
    root().join("marketing/video/one-less-errand/studio")
}
#[derive(Deserialize, Serialize, Clone, Default)]
pub struct Hold {
    pub source_frame: usize,
    pub frames: usize,
}
#[derive(Deserialize, Serialize, Clone)]
pub struct Shot {
    pub id: String,
    pub kind: String,
    pub start: f64,
    pub end: f64,
    pub frames: usize,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub asset: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub source_frames: Option<usize>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub extra_frames: Option<usize>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub motion_duration: Option<f64>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub motion_offset: Option<f64>,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub frame_holds: Vec<Hold>,
    #[serde(default, skip_serializing_if = "std::ops::Not::not")]
    pub hold: bool,
    #[serde(default)]
    pub can_actions: Actions,
    #[serde(flatten)]
    pub extra: BTreeMap<String, Value>,
}
#[derive(Deserialize, Serialize, Clone, Default)]
pub struct Cycle {
    pub remove: [f64; 2],
    pub restock: [f64; 2],
}
#[derive(Deserialize, Serialize, Clone, Default)]
pub struct Actions {
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub contact: Option<f64>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub expand: Option<[f64; 2]>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub cycles: Option<Vec<Cycle>>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub final_remove: Option<[f64; 2]>,
}
#[derive(Deserialize, Serialize, Clone)]
pub struct SoundEvent {
    pub id: String,
    pub kind: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub frame: Option<usize>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub time: Option<f64>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub variation: Option<usize>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub duration: Option<f64>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub gain: Option<f64>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub pan: Option<f64>,
}
#[derive(Deserialize, Serialize, Clone)]
pub struct Beat {
    pub id: String,
    pub after_scene: String,
    pub frames: usize,
    pub source_sample: usize,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub after_source_frame: Option<usize>,
}
#[derive(Deserialize, Serialize, Clone)]
pub struct PickupPhrase {
    pub text: String,
    pub scene: String,
    pub source_start: f64,
    pub source_end: f64,
    pub first_word: f64,
    pub last_word: f64,
    pub at: f64,
}
#[derive(Deserialize, Serialize, Clone)]
pub struct Pickup {
    pub source: String,
    pub replace_source: [f64; 2],
    pub phrases: Vec<PickupPhrase>,
}
#[derive(Deserialize, Serialize, Clone)]
pub struct Onset {
    pub text: String,
    pub source_time: f64,
    #[serde(default)]
    pub occurrence: Option<usize>,
}
#[derive(Deserialize, Serialize, Clone)]
pub struct Story {
    pub fps: f64,
    pub duration: f64,
    pub narration_offset: f64,
    pub scenes: Vec<Shot>,
    #[serde(default)]
    pub sound_events: Vec<SoundEvent>,
    #[serde(default)]
    pub narration_pauses: Vec<Beat>,
    #[serde(default)]
    pub type_timing: Value,
    #[serde(default)]
    pub score: Value,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub narration_pickup: Option<Pickup>,
    #[serde(default)]
    pub caption_source_onsets: Vec<Onset>,
    #[serde(default)]
    pub separate_benefit_captions: bool,
    #[serde(flatten)]
    pub extra: BTreeMap<String, Value>,
}
#[derive(Deserialize)]
struct Edit {
    beats: Vec<Beat>,
    #[serde(default)]
    extend_motion: Vec<String>,
    #[serde(default)]
    motion_preroll_frames: BTreeMap<String, usize>,
    #[serde(default)]
    type_timing: Value,
    #[serde(default)]
    score: Value,
    #[serde(default)]
    narration_pickup: Option<Pickup>,
    #[serde(default)]
    caption_source_onsets: Vec<Onset>,
    #[serde(default)]
    separate_benefit_captions: bool,
}
impl Story {
    pub fn read(timing: Option<&Path>) -> Result<Self> {
        let mut story: Self = serde_json::from_value(json(here().join("story.json"))?)?;
        let Some(timing) = timing else {
            return Ok(story);
        };
        let edit: Edit = serde_json::from_value(json(timing)?)?;
        let fps = story.fps;
        let originals: BTreeMap<_, _> = story
            .scenes
            .iter()
            .map(|s| (s.id.clone(), ((s.start * fps).round() as usize, s.frames)))
            .collect();
        let mut added = 0;
        for scene in &mut story.scenes {
            let selected: Vec<_> = edit
                .beats
                .iter()
                .filter(|b| b.after_scene == scene.id)
                .collect();
            let extra = selected.iter().map(|b| b.frames).sum::<usize>();
            let (start, frames) = originals[&scene.id];
            scene.start = (start + added) as f64 / fps;
            scene.frames += extra;
            scene.end = scene.start + scene.frames as f64 / fps;
            if extra > 0 {
                scene.extra_frames = Some(extra);
                if edit.extend_motion.contains(&scene.id) {
                    scene.source_frames = Some(scene.frames);
                    scene.motion_duration =
                        Some(scene.motion_duration.unwrap_or(scene.frames as f64 / fps));
                    let preroll = edit
                        .motion_preroll_frames
                        .get(&scene.id)
                        .copied()
                        .unwrap_or(0);
                    if preroll > 0 {
                        scene.motion_offset = Some(-(preroll as f64) / fps);
                        scene.motion_duration = Some((scene.frames - preroll) as f64 / fps);
                    }
                } else if ["can", "studio"].contains(&scene.kind.as_str()) && !scene.hold {
                    scene.source_frames = Some(frames);
                    scene.frame_holds = selected
                        .iter()
                        .map(|b| Hold {
                            source_frame: b.after_source_frame.unwrap_or(frames - 1),
                            frames: b.frames,
                        })
                        .collect();
                }
            }
            added += extra;
        }
        story.duration = ((story.duration * fps).round() as usize + added) as f64 / fps;
        for event in &mut story.sound_events {
            let frame = event.frame.context("picture sound frame")?;
            let (id, (start, _)) = originals
                .iter()
                .find(|(_, p)| p.0 <= frame && frame < p.0 + p.1)
                .context("sound event source scene")?;
            let scene = story.scenes.iter().find(|s| s.id == *id).unwrap();
            let local = frame - start;
            event.frame = Some(
                (scene.start * fps).round() as usize
                    + local
                    + scene
                        .frame_holds
                        .iter()
                        .filter(|h| local > h.source_frame)
                        .map(|h| h.frames)
                        .sum::<usize>(),
            );
        }
        story.narration_pauses = edit.beats;
        story.type_timing = edit.type_timing;
        story.score = edit.score;
        story.narration_pickup = edit.narration_pickup;
        story.caption_source_onsets = edit.caption_source_onsets;
        story.separate_benefit_captions = edit.separate_benefit_captions;
        Ok(story)
    }
    pub fn shot(&self, id: &str) -> Result<&Shot> {
        self.scenes
            .iter()
            .find(|s| s.id == id)
            .with_context(|| format!("story shot {id}"))
    }
    pub fn local_time(&self, id: &str, time: f64) -> Result<f64> {
        let shot = self.shot(id)?;
        Ok(time
            + shot
                .frame_holds
                .iter()
                .filter(|h| time * self.fps >= (h.source_frame + 1) as f64)
                .map(|h| h.frames as f64 / self.fps)
                .sum::<f64>())
    }
    pub fn picture_time(&self, time: f64, source_rate: f64) -> f64 {
        self.narration_offset
            + time
            + self
                .narration_pauses
                .iter()
                .filter(|b| (time * source_rate).round() as usize >= b.source_sample)
                .map(|b| b.frames as f64 / self.fps)
                .sum::<f64>()
    }
    pub fn source(&self) -> Self {
        let mut source = self.clone();
        for shot in &mut source.scenes {
            shot.frames = shot.source_frames.unwrap_or(shot.frames);
            shot.end = shot.start + shot.frames as f64 / self.fps;
        }
        source
    }
}
pub fn progress(time: f64, range: [f64; 2]) -> f64 {
    if range[1] <= range[0] {
        if time >= range[1] { 1. } else { 0. }
    } else {
        crate::scene::ease((time - range[0]) / (range[1] - range[0]))
    }
}
#[derive(Clone)]
pub struct PackPose {
    pub index: usize,
    pub offset: [f64; 3],
    pub cans: Vec<(bool, [f64; 3])>,
}
pub struct RoutinePose {
    pub context: String,
    pub offset: [f64; 3],
    pub expand: f64,
    pub packs: Vec<PackPose>,
}
pub fn routine(shot: &Shot, time: f64) -> Result<RoutinePose> {
    let duration = shot.end - shot.start;
    ensure!(
        duration > 0. && time.is_finite(),
        "finite routine time and positive duration"
    );
    let actions = &shot.can_actions;
    let time = time.max(0.);
    let id = shot.id.as_str();
    let mut result = RoutinePose {
        context: if ["repeat", "question"].contains(&id) {
            "shelf"
        } else {
            id
        }
        .into(),
        offset: [0.; 3],
        expand: 1.,
        packs: Vec::new(),
    };
    if id == "question" {
        return Ok(result);
    }
    if id != "repeat" {
        let contact = actions.contact.unwrap_or(0.36_f64.min(duration * 0.30));
        let z = if id == "case" {
            result.expand = progress(time, actions.expand.unwrap_or([0., duration * 0.66]));
            let lift = (contact - 0.85).max(0.);
            let crest = (contact - 0.30).max(0.);
            let z = if time < crest {
                -0.065 + 0.245 * progress(time, [lift, crest])
            } else {
                let fall = ((time - crest) / (contact - crest).max(0.001)).clamp(0., 1.);
                0.180 * (1. - fall * fall)
            };
            let arrival = progress(time, [(contact - 0.68).max(0.), (contact - 0.19).max(0.)]);
            result.offset = [0.66 * (1. - arrival), 0., 0.];
            z
        } else {
            let p = (time / contact.max(0.001)).min(1.);
            if p < 1. { 0.032 * (1. - p * p) } else { 0. }
        };
        result.packs.push(PackPose {
            index: 0,
            offset: [0., 0., z],
            cans: vec![(false, [0.; 3]); 12],
        });
        return Ok(result);
    }
    let cycles = actions.cycles.clone().unwrap_or_else(|| {
        vec![
            Cycle {
                remove: [duration * 0.01, duration * 0.18],
                restock: [duration * 0.22, duration * 0.31],
            },
            Cycle {
                remove: [duration * 0.33, duration * 0.48],
                restock: [duration * 0.51, duration * 0.60],
            },
            Cycle {
                remove: [duration * 0.63, duration * 0.77],
                restock: [duration * 0.80, duration * 0.87],
            },
        ]
    });
    let arrivals: Vec<_> = std::iter::once(None)
        .chain(cycles.iter().map(|c| Some(c.restock)))
        .collect();
    let removals: Vec<_> = cycles
        .iter()
        .map(|c| c.remove)
        .chain(std::iter::once(
            actions
                .final_remove
                .unwrap_or([duration * 0.90, duration * 0.98]),
        ))
        .collect();
    for (index, (arrival, removal)) in arrivals.iter().zip(removals).enumerate() {
        if arrival.is_some_and(|a| time < a[0]) {
            continue;
        }
        let entering = arrival.map_or(1., |a| progress(time, a));
        let end = arrivals
            .get(index + 1)
            .and_then(|a| *a)
            .map_or(duration, |a| a[0]);
        let end = if end <= removal[1] {
            removal[1] + 0.08
        } else {
            end
        };
        let leaving = progress(time, [removal[1], end]);
        if leaving >= 0.999 {
            continue;
        }
        let x = 0.64 * (1. - entering) - 0.64 * leaving;
        let y = -0.36 * ((1. - entering) + leaving);
        let z = if entering < 1. {
            0.016 * (std::f64::consts::PI * entering).sin()
        } else {
            0.
        } + if leaving > 0. {
            0.016 * (std::f64::consts::PI * leaving).sin()
        } else {
            0.
        };
        let spacing = (removal[1] - removal[0]).max(0.01) / 15.;
        let travel = ((removal[1] - removal[0]) - 11. * spacing).max(0.07);
        let cans = (0..12)
            .map(|i| {
                let p = progress(
                    time,
                    [
                        removal[0] + i as f64 * spacing,
                        removal[0] + i as f64 * spacing + travel,
                    ],
                );
                (
                    p > 0.995,
                    [
                        0.,
                        -0.80 * progress(p, [0.18, 1.]),
                        0.030 * progress(p, [0., 0.18]),
                    ],
                )
            })
            .collect();
        result.packs.push(PackPose {
            index,
            offset: [x, y, z],
            cans,
        });
    }
    Ok(result)
}
