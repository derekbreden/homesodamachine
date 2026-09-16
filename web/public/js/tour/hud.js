// Captions, chapter navigation, and playback controls for the guided tour.
import { leafOf } from "/contracts/body-path.js";

const svg = (path) => `<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path fill="currentColor" d="${path}"/></svg>`;
const PLAY = svg("M8 5v14l11-7z");
const PAUSE = svg("M6 5h4v14H6zM14 5h4v14h-4z");
const PREV = svg("M18 5v14l-9-7zM7 5h2v14H7z");
const NEXT = svg("M6 5l9 7-9 7zM15 5h2v14h-2z");
const REPLAY = svg("M12 4a8 8 0 1 1-7.4 11H7a5.8 5.8 0 1 0 1.1-6.9L11 11H3V3l3.5 3.5A8 8 0 0 1 12 4z");
const FULLSCREEN = svg("M4 4h6v2H6v4H4zm10 0h6v6h-2V6h-4zM4 14h2v4h4v2H4zm14 0h2v6h-6v-2h4z");
const EXIT_FULLSCREEN = svg("M8 4h2v6H4V8h4zm6 0h2v4h4v2h-6zM4 14h6v6H8v-4H4zm10 0h6v2h-4v4h-2z");
const CHIP_LIMIT = 7;

function el(tag, cls, text) {
  const node = document.createElement(tag);
  if (cls) node.className = cls;
  if (text != null) node.textContent = text;
  return node;
}

function button(cls, label, icon) {
  const node = el("button", cls);
  node.type = "button";
  node.title = label;
  node.ariaLabel = label;
  if (icon) node.innerHTML = icon;
  return node;
}

function clock(ms) {
  const seconds = Math.max(0, Math.floor((Number(ms) || 0) / 1000));
  return `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, "0")}`;
}

export function mountHud(host, { steps, title: titleText, subtitle, on }) {
  const hud = el("div", "tour-hud");
  const stage = host.closest(".tour-stage") || host.parentElement;

  const banner = el("div", "tour-banner");
  const bannerTitle = el("span", "tour-banner-title", titleText);
  const bannerSub = el("span", "tour-banner-sub", subtitle || "A guided look inside");
  banner.append(bannerTitle, bannerSub);

  const footer = el("div", "tour-footer");
  const card = el("section", "tour-card");
  card.ariaLabel = "Tour captions";
  card.setAttribute("aria-live", "polite");
  card.setAttribute("aria-atomic", "true");
  const kicker = el("div", "tour-kicker");
  const kickerName = el("span", "tour-kicker-name");
  const kickerCount = el("span", "tour-kicker-count");
  kicker.append(kickerName, kickerCount);
  const heading = el("h2", "tour-title");
  const body = el("p", "tour-body");
  const chips = el("div", "tour-chips tour-dev");
  card.append(kicker, heading, body, chips);

  const transport = el("div", "tour-transport");
  const rail = el("nav", "tour-rail");
  rail.ariaLabel = "Tour chapters";
  const chapters = [];
  const dots = steps.map((step, i) => {
    const chapterName = step.chapter || "The tour";
    let chapter = chapters[chapters.length - 1];
    if (!chapter || chapter.name !== chapterName) {
      const group = el("div", "tour-chapter");
      const label = el("span", "tour-chapter-label", chapterName);
      const beats = el("div", "tour-chapter-beats");
      group.append(label, beats);
      rail.append(group);
      chapter = { name: chapterName, group, beats, first: i, last: i };
      chapters.push(chapter);
    }
    chapter.last = i;
    const dot = button("tour-dot", `${i + 1}. ${step.title}`);
    dot.append(el("span", "tour-dot-fill"));
    dot.addEventListener("click", () => on.goto(i));
    chapter.beats.append(dot);
    return dot;
  });
  for (const chapter of chapters) chapter.group.style.flexGrow = String(chapter.last - chapter.first + 1);

  const bar = el("div", "tour-bar");
  const playback = el("div", "tour-playback");
  const prev = button("tour-btn", "Previous scene (←)", PREV);
  const play = button("tour-btn tour-play", "Pause (space)", PAUSE);
  const next = button("tour-btn", "Next scene (→)", NEXT);
  const time = el("span", "tour-time", "0:00 / 0:00");
  time.ariaLabel = "Playback time";
  playback.append(prev, play, next, time);

  const options = el("div", "tour-options");
  const speed = button("tour-chip-btn", "Playback speed");
  speed.textContent = "1×";
  const captions = button("tour-chip-btn tour-captions on", "Hide captions (C)");
  captions.textContent = "CC";
  captions.setAttribute("aria-pressed", "true");
  const fullscreen = button("tour-btn tour-fullscreen", "Enter fullscreen", FULLSCREEN);
  const ghost = button("tour-chip-btn tour-dev", "Show all bodies as an X-ray");
  ghost.textContent = "Ghost";
  const pose = button("tour-chip-btn tour-dev", "Copy camera position");
  pose.textContent = "Pose";
  options.append(ghost, pose, speed, captions);
  if (stage.requestFullscreen && document.fullscreenEnabled) options.append(fullscreen);
  bar.append(playback, options);
  transport.append(rail, bar);
  footer.append(card, transport);

  const resume = button("tour-resume", "Return to the guided camera");
  resume.textContent = "Resume tour";
  hud.append(banner, resume, footer);
  host.append(hud);

  let shownIndex = -1;
  let playing = true;
  let ended = false;
  let captionsVisible = true;
  let timeText = "";

  function updatePlay() {
    play.innerHTML = ended ? REPLAY : (playing ? PAUSE : PLAY);
    play.ariaLabel = ended ? "Replay tour (space)" : (playing ? "Pause (space)" : "Play (space)");
    play.title = play.ariaLabel;
    hud.classList.toggle("paused", !playing);
    hud.classList.toggle("ended", ended);
  }

  function setCaptions(visible) {
    captionsVisible = !!visible;
    hud.classList.toggle("captions-off", !captionsVisible);
    card.setAttribute("aria-hidden", String(!captionsVisible));
    captions.classList.toggle("on", captionsVisible);
    captions.setAttribute("aria-pressed", String(captionsVisible));
    captions.ariaLabel = captionsVisible ? "Hide captions (C)" : "Show captions (C)";
    captions.title = captions.ariaLabel;
  }

  function setStep(i, step, missing = []) {
    dots.forEach((dot, n) => {
      dot.classList.toggle("done", n < i);
      dot.classList.toggle("now", n === i);
      dot.style.setProperty("--fill-x", n < i ? "1" : "0");
      if (n === i) dot.setAttribute("aria-current", "step");
      else dot.removeAttribute("aria-current");
    });
    chapters.forEach(({ group, first, last }) => group.classList.toggle("now", i >= first && i <= last));
    prev.disabled = i <= 0;
    next.disabled = i >= steps.length - 1;
    if (i === shownIndex) return;
    shownIndex = i;
    card.classList.remove("in");
    const replaceCaption = () => {
      kickerName.textContent = step.chapter || "Inside the machine";
      kickerCount.textContent = `${String(i + 1).padStart(2, "0")} / ${String(steps.length).padStart(2, "0")}`;
      heading.textContent = step.title;
      body.textContent = step.body;
      chips.replaceChildren();
      const named = step.parts || [];
      const gone = new Set(missing);
      for (const part of named.slice(0, CHIP_LIMIT)) {
        const chip = el("span", `tour-chip${gone.has(part) ? " tour-chip-missing" : ""}`, leafOf(part));
        chip.title = gone.has(part) ? `${part} — missing from the model` : part;
        chips.append(chip);
      }
      if (named.length > CHIP_LIMIT) chips.append(el("span", "tour-chip", `+${named.length - CHIP_LIMIT} more`));
      card.classList.add("in");
    };
    replaceCaption();
  }

  prev.addEventListener("click", () => on.prev());
  next.addEventListener("click", () => on.next());
  play.addEventListener("click", () => on.togglePlay());
  speed.addEventListener("click", () => on.cycleSpeed());
  captions.addEventListener("click", () => setCaptions(!captionsVisible));
  ghost.addEventListener("click", () => on.toggleGhost());
  pose.addEventListener("click", () => on.copyPose());
  resume.addEventListener("click", () => on.resume());
  fullscreen.addEventListener("click", async () => {
    try {
      if (document.fullscreenElement === stage) await document.exitFullscreen();
      else await stage.requestFullscreen();
    } catch { /* A browser may decline fullscreen without changing playback. */ }
  });
  document.addEventListener("fullscreenchange", () => {
    const active = document.fullscreenElement === stage;
    fullscreen.innerHTML = active ? EXIT_FULLSCREEN : FULLSCREEN;
    fullscreen.ariaLabel = active ? "Exit fullscreen" : "Enter fullscreen";
    fullscreen.title = fullscreen.ariaLabel;
  });
  document.addEventListener("keydown", (event) => {
    if (event.code !== "KeyC" || event.metaKey || event.ctrlKey || event.altKey) return;
    if (event.target.closest?.("input, textarea, select, [contenteditable=true]")) return;
    event.preventDefault();
    setCaptions(!captionsVisible);
  });

  return {
    setStep,
    setProgress(i, fraction) {
      dots[i]?.style.setProperty("--fill-x", String(Math.max(0, Math.min(fraction, 1))));
    },
    setTime(elapsedMs, totalMs) {
      const nextText = `${clock(elapsedMs)} / ${clock(totalMs)}`;
      if (nextText !== timeText) {
        time.textContent = nextText;
        timeText = nextText;
      }
    },
    setPlaying(value) { playing = !!value; updatePlay(); },
    setEnded(value) {
      if (ended === !!value) return;
      ended = !!value;
      updatePlay();
    },
    setGrabbed(value) { hud.classList.toggle("grabbed", !!value); },
    setCaptions,
    setSpeed(value) { speed.textContent = `${value}×`; speed.ariaLabel = `Playback speed: ${value} times`; },
    setGhost(value) { ghost.classList.toggle("on", !!value); ghost.setAttribute("aria-pressed", String(!!value)); },
    flash(message) {
      const flash = el("div", "tour-flash", message);
      flash.setAttribute("role", "status");
      hud.append(flash);
      requestAnimationFrame(() => flash.classList.add("in"));
      setTimeout(() => { flash.classList.remove("in"); setTimeout(() => flash.remove(), 300); }, 1800);
    },
    showTitle(value) { banner.classList.toggle("intro", !!value); },
    setCardVisible(value) { card.classList.toggle("gone", !value); },
    element: hud,
  };
}
