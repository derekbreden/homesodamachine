// EVERYTHING ON SCREEN THAT IS NOT THE MACHINE. The narration card, the
// transport, the rail of steps, and the two toggles.
//
// The card is the modal the tour narrates through: it holds a beat's title,
// two or three sentences, and the bodies that beat lights, and it cross-fades
// rather than swapping, so a step change is one event to the eye and not two.
// It stands in the corner the shot is composed away from rather than over the
// middle, because the subject is the point and the words are the caption.
//
// THE RAIL IS THE FAST WAY IN. Every step is a dot, the dot is a link, and the
// step the player is on is written into the URL — so a reload, a deploy that
// reloads the page under you, or a pasted link all land on the same beat
// instead of at the top. Iterating on beat nine costs one reload, not the
// eight beats before it.

import { leafOf } from "/contracts/body-path.js";

const PLAY = `<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path fill="currentColor" d="M8 5v14l11-7z"/></svg>`;
const PAUSE = `<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path fill="currentColor" d="M6 5h4v14H6zM14 5h4v14h-4z"/></svg>`;
const PREV = `<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path fill="currentColor" d="M18 5v14l-9-7zM7 5h2v14H7z"/></svg>`;
const NEXT = `<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path fill="currentColor" d="M6 5l9 7-9 7zM15 5h2v14h-2z"/></svg>`;

const CHIP_LIMIT = 7;

// A body inside a sub-assembly carries its path — `cold-core/sparge-stone`.
// The chip shows the body's own name and keeps the whole of it on hover: the
// path is what the model calls it and the leaf is what the sentence calls it,
// and a row of chips is reading, not addressing.
//
// From the contract rather than inline, because there is one rule for reading a
// body's path and it has a test. The contract is pure — no three.js, no viewer
// state — so a caption can have it without pulling the picker in behind it.

const el = (tag, cls, html) => {
  const n = document.createElement(tag);
  if (cls) n.className = cls;
  if (html != null) n.innerHTML = html;
  return n;
};

const escapeText = (v) => String(v == null ? "" : v);

// The two announcements are shown by setting opacity and transform on the
// element rather than by toggling a class the stylesheet answers. Both work;
// this one puts the state where it can be read straight off the node, which is
// worth something on an overlay that is only up for two seconds at a time and
// is otherwise very hard to catch in the act.
function show(node, on) {
  node.style.opacity = on ? "1" : "0";
  node.style.transform = node.dataset.rest && !on
    ? node.dataset.rest
    : (node.dataset.shown || "none");
}

export function mountHud(host, { steps, title: titleText, subtitle, on }) {
  const hud = el("div", "tour-hud");

  // --- the narration card -------------------------------------------------
  const card = el("div", "tour-card");
  const kicker = el("div", "tour-kicker");
  const kickerName = el("span", "tour-kicker-name");
  const kickerCount = el("span", "tour-kicker-count");
  kicker.append(kickerName, kickerCount);
  const heading = el("h2", "tour-title");
  const body = el("p", "tour-body");
  const chips = el("div", "tour-chips");
  card.append(kicker, heading, body, chips);

  // --- transport ----------------------------------------------------------
  const bar = el("div", "tour-bar");
  const prev = el("button", "tour-btn", PREV);
  prev.type = "button"; prev.title = "Previous step (←)"; prev.ariaLabel = "Previous step";
  const play = el("button", "tour-btn tour-play", PAUSE);
  play.type = "button"; play.title = "Play / pause (space)"; play.ariaLabel = "Play or pause";
  const next = el("button", "tour-btn", NEXT);
  next.type = "button"; next.title = "Next step (→)"; next.ariaLabel = "Next step";

  const rail = el("div", "tour-rail");
  const dots = steps.map((s, i) => {
    const d = el("button", "tour-dot");
    d.type = "button";
    d.title = `${i + 1}. ${s.title}`;
    d.ariaLabel = d.title;
    d.append(el("span", "tour-dot-fill"));
    d.addEventListener("click", () => on.goto(i));
    rail.append(d);
    return d;
  });

  const speed = el("button", "tour-chip-btn", "1&times;");
  speed.type = "button"; speed.title = "Playback speed";
  const ghost = el("button", "tour-chip-btn", "Ghost");
  ghost.type = "button"; ghost.title = "X-ray: ghost every solid and draw its feature edges";
  const pose = el("button", "tour-chip-btn tour-dev", "Pose");
  pose.type = "button";
  pose.title = "Copy this camera as the dir/pad the tour data wants";

  speed.addEventListener("click", () => on.cycleSpeed());
  ghost.addEventListener("click", () => on.toggleGhost());
  pose.addEventListener("click", () => on.copyPose());
  prev.addEventListener("click", () => on.prev());
  next.addEventListener("click", () => on.next());
  play.addEventListener("click", () => on.togglePlay());

  bar.append(prev, play, next, rail, speed, ghost, pose);

  // --- the resume shade, for a tour someone has grabbed --------------------
  const resume = el("button", "tour-resume", "Resume tour");
  resume.type = "button";
  resume.addEventListener("click", () => on.resume());

  const banner = el("div", "tour-banner");
  banner.append(el("span", "tour-banner-title", escapeText(titleText)),
                el("span", "tour-banner-sub", escapeText(subtitle || "")));

  // ── the chapter's name, when the chapter turns over ─────────────────────
  // Fifty-six beats in a row is a list. Eleven names that arrive over the shot
  // and leave again is a piece with movements in it, and it costs the reader
  // nothing to ignore.
  const chapterCard = el("div", "tour-chapter-card");
  chapterCard.dataset.rest = "translateY(10px)";
  chapterCard.dataset.shown = "none";
  const chapterName = el("div", "tour-chapter-name");
  chapterCard.append(chapterName);

  // ── the title, over the machine while it is still solid ─────────────────
  const title = el("div", "tour-title-card");
  title.dataset.rest = "translate(-50%, -50%) scale(0.985)";
  title.dataset.shown = "translate(-50%, -50%) scale(1)";
  title.append(el("div", "tour-title-main", escapeText(titleText)),
               el("div", "tour-title-sub", escapeText(subtitle || "")));

  hud.append(banner, chapterCard, title, card, resume, bar);
  host.append(hud);

  let shownIndex = -1;
  let swapTimer = null;
  let shownChapter = null;
  let chapterTimer = null;

  function setStep(i, step, missing = []) {
    dots.forEach((d, n) => {
      d.classList.toggle("done", n < i);
      d.classList.toggle("now", n === i);
    });
    if (i === shownIndex) return;
    const first = shownIndex < 0;
    shownIndex = i;

    // A NEW CHAPTER ANNOUNCES ITSELF, except the first one — the title is
    // already on screen there and two cards arriving together is neither.
    if (step.chapter && step.chapter !== shownChapter) {
      shownChapter = step.chapter;
      if (!first) {
        chapterName.textContent = step.chapter;
        show(chapterCard, true);
        clearTimeout(chapterTimer);
        chapterTimer = setTimeout(() => show(chapterCard, false), 2100);
      }
    }

    // Out, then in: the card fades down, swaps its words while it is
    // invisible, and comes back — so a step change never shows two texts. On a
    // timer rather than on frames, because a page nobody is looking at is a
    // page with no frames, and it still has to be showing the right beat when
    // someone looks back at it.
    card.classList.remove("in");
    clearTimeout(swapTimer);
    swapTimer = setTimeout(() => {
      kickerName.textContent = step.chapter || "";
      kickerCount.textContent = `${i + 1} / ${steps.length}`;
      heading.textContent = step.title;
      body.textContent = step.body;
      chips.textContent = "";
      // A beat that lights eighteen bodies is a beat about the whole run, and
      // eighteen chips under three sentences is a wall. Name a few and count
      // the rest.
      const named = step.parts || [];
      const gone = new Set(missing);
      for (const p of named.slice(0, CHIP_LIMIT)) {
        const c = el("span", `tour-chip${gone.has(p) ? " tour-chip-missing" : ""}`, leafOf(p));
        c.title = gone.has(p) ? `${p} — this model carries no body by that name` : p;
        chips.append(c);
      }
      if (named.length > CHIP_LIMIT) {
        chips.append(el("span", "tour-chip tour-chip-more",
                        `+${named.length - CHIP_LIMIT} more`));
      }
      void card.offsetWidth; // restart the transition rather than continue it
      card.classList.add("in");
    }, 220);
  }

  // How far through the beat the player is, as the scale of the dot's fill.
  function setProgress(i, frac) {
    const d = dots[i];
    if (d) d.style.setProperty("--fill-x", String(Math.max(0, Math.min(frac, 1))));
  }

  return {
    setStep,
    setProgress,
    setPlaying(playing) {
      play.innerHTML = playing ? PAUSE : PLAY;
      hud.classList.toggle("grabbed", !playing);
    },
    setGrabbed(grabbed) { hud.classList.toggle("grabbed", grabbed); },
    setSpeed(x) { speed.innerHTML = `${x}&times;`; },
    setGhost(onNow) { ghost.classList.toggle("on", !!onNow); },
    flash(msg) {
      const t = el("div", "tour-flash", msg);
      hud.append(t);
      requestAnimationFrame(() => t.classList.add("in"));
      setTimeout(() => { t.classList.remove("in"); setTimeout(() => t.remove(), 300); }, 1600);
    },
    element: hud,
    /** The title, over the machine while it is still solid at the top of the
     *  tour. It leaves as the machine dissolves, so the two motions are one. */
    showTitle(on) { show(title, !!on); },
    /** The last beat is the machine and the line and nothing else. */
    setCardVisible(on) { card.classList.toggle("gone", !on); },
  };
}
