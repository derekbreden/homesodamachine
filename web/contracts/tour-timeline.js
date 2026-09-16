export function timelineFor(steps) {
  let at = 0;
  const beats = steps.map((step, index) => {
    const start = at;
    at += step.dwell;
    return { index, start, end: at, duration: step.dwell };
  });
  return { beats, duration: at };
}

export function locateTime(timeline, milliseconds) {
  const time = Math.max(0, Math.min(Number(milliseconds) || 0, timeline.duration));
  const beat = timeline.beats.find((b) => time < b.end) || timeline.beats.at(-1);
  return { ...beat, time, local: time - beat.start, progress: (time - beat.start) / beat.duration };
}

export function captionVtt(steps) {
  const stamp = (ms) => {
    const seconds = Math.floor(ms / 1000);
    return `${String(Math.floor(seconds / 3600)).padStart(2, "0")}:${String(Math.floor(seconds / 60) % 60).padStart(2, "0")}:${String(seconds % 60).padStart(2, "0")}.${String(ms % 1000).padStart(3, "0")}`;
  };
  return "WEBVTT\n\n" + timelineFor(steps).beats.map((b) =>
    `${b.index + 1}\n${stamp(b.start)} --> ${stamp(b.end)}\n${steps[b.index].body}\n`,
  ).join("\n");
}
