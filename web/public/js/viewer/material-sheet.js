// The Materials pane on a phone: a sheet under the model that rests at one of three heights.
// Scrolling its list raises it first, to the top height, and only then scrolls the list; pulling
// down with the list at its top lowers it again; dragging, pinching or wheeling the model lowers
// it out of the way. A part chosen in the list brings it no higher than half, so the model can
// show the part. Wider screens keep the pane beside the model and none of this runs.
//
// The drag follows the bottom sheets that have settled the pattern (vaul, Ionic's sheet modal):
// below the top height the list does not scroll natively, so a drag moves the sheet; release
// snaps to the height nearest where the finger's speed was taking it, and a flick goes one
// further. Unlike them, one stroke carries on into the list once the sheet is up, with the
// list's momentum after release.
import { renderer, setViewInset } from "./scene.js";

const PHONE = matchMedia("(max-width: 700px)");
const SLOP = 8;          // px of finger travel before a touch becomes a drag
const FLICK = 0.5;       // px/ms that carries a release to the next height
const PROJECT = 300;     // ms of the finger's speed a release coasts through
const DURATION = 400;    // ms to settle at a height

// The settle curve of iOS sheets, as vaul and Ionic both use it: cubic-bezier(.32, .72, 0, 1).
function settle(t) {
  const x1 = 0.32, y1 = 0.72, x2 = 0, y2 = 1;
  const bez = (p1, p2, s) => 3 * p1 * s * (1 - s) ** 2 + 3 * p2 * s * s * (1 - s) + s ** 3;
  let lo = 0, hi = 1, s = t;
  for (let i = 0; i < 20; i++) {
    s = (lo + hi) / 2;
    if (bez(x1, x2, s) < t) lo = s; else hi = s;
  }
  return bez(y1, y2, s);
}

export function mountMaterialSheet({ workspace, panel }) {
  const header = workspace.querySelector(".cad-workspace-header");
  const grabber = document.createElement("div");
  grabber.className = "material-sheet-grabber";
  grabber.setAttribute("aria-hidden", "true");
  panel.prepend(grabber);

  let open = false;
  let height = 0;        // the sheet's height now
  let level = 1;         // the height it rests at: 0 low, 1 half, 2 top
  let animation = 0;
  let fling = 0;
  const active = () => open && PHONE.matches;

  // The three heights, from the room under the header.
  function heights() {
    const room = Math.max(0, workspace.clientHeight - (header?.offsetHeight || 0));
    const low = Math.round(Math.max(150, room * 0.28));
    const half = Math.round(Math.max(low, room * 0.5));
    const top = Math.round(Math.max(half, room - Math.max(96, room * 0.12)));
    return [low, half, top];
  }

  function apply(px, { hold = true, goal = px } = {}) {
    px = Math.round(px);
    height = px;
    workspace.style.setProperty("--sheet-height", px + "px");
    panel.classList.toggle("sheet-top", px >= heights()[2] - 1);
    setViewInset(px, { hold, goal });
  }

  function stop() {
    cancelAnimationFrame(animation); animation = 0;
    cancelAnimationFrame(fling); fling = 0;
  }

  function settleAt(next, { hold = true } = {}) {
    stop();
    level = next;
    const from = height, to = heights()[next];
    const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduce || Math.abs(to - from) < 1) { apply(to, { hold }); return; }
    const t0 = performance.now();
    const frame = (now) => {
      const t = Math.min((now - t0) / DURATION, 1);
      apply(from + (to - from) * settle(t), { hold, goal: to });
      if (t < 1) animation = requestAnimationFrame(frame); else animation = 0;
    };
    animation = requestAnimationFrame(frame);
  }

  function nearest(px) {
    const all = heights();
    return all.reduce((best, h, i) => Math.abs(h - px) < Math.abs(all[best] - px) ? i : best, 0);
  }

  // Momentum for the list after a stroke carried into it, decaying the way iOS lists do.
  function coast(velocity) {
    let v = velocity, last = performance.now();
    const frame = (now) => {
      const dt = now - last; last = now;
      const before = panel.scrollTop;
      panel.scrollTop += v * dt;
      v *= 0.998 ** dt;
      if (Math.abs(v) > 0.02 && panel.scrollTop !== before) fling = requestAnimationFrame(frame);
      else fling = 0;
    };
    fling = requestAnimationFrame(frame);
  }

  // --- A finger on the sheet ---
  let mode = null;       // null, "pending", "sheet" or "native"
  let startY = 0, lastY = 0, samples = [], onGrabber = false, carried = false;

  function speed(now) {
    const recent = samples.filter(([t]) => now - t <= 100);
    if (recent.length < 2) return 0;
    const [t1, y1] = recent[0], [t2, y2] = recent[recent.length - 1];
    return t2 > t1 ? (y2 - y1) / (t2 - t1) : 0; // px/ms, positive downward
  }

  function begin(y, target, now) {
    stop();
    startY = lastY = y;
    samples = [[now, y]];
    onGrabber = grabber.contains(target);
    carried = false;
    mode = "pending";
  }

  // Returns true when the move belongs to the sheet and the page must not scroll for it.
  function move(y, now) {
    const dy = y - lastY;
    lastY = y;
    samples.push([now, y]);
    const all = heights();
    if (mode === "pending") {
      if (height >= all[2] - 1 && !onGrabber) {
        // At the top, the list scrolls unless it is at its own top and the finger pulls down.
        if (dy < 0 || panel.scrollTop > 0) { mode = "native"; return false; }
        if (dy === 0) return false;
      }
      if (Math.abs(y - startY) < SLOP) return true;
      mode = "sheet";
    }
    let next = height - dy;
    if (next > all[2]) {
      // Up past the top height: the rest of the stroke scrolls the list.
      if (!onGrabber) { panel.scrollTop += next - all[2]; carried = true; }
      next = all[2];
    } else if (carried && dy > 0 && panel.scrollTop > 0) {
      // Back down after carrying on: the list gives back its scroll before the sheet lowers.
      const back = Math.min(dy, panel.scrollTop);
      panel.scrollTop -= back;
      next = height - (dy - back);
    }
    if (next < all[0]) next = all[0] - (all[0] - next) * 0.35; // resist below the lowest height
    apply(next);
    return true;
  }

  function end(now) {
    const was = mode;
    mode = null;
    if (was !== "sheet") return false;
    const v = speed(now);
    const all = heights();
    if (carried && height >= all[2] - 1) {
      settleAt(2);
      if (v < 0) coast(-v);
      return true;
    }
    let next = nearest(height - v * PROJECT);
    if (Math.abs(v) > FLICK && next === nearest(height)) next = Math.max(0, Math.min(2, next + (v > 0 ? -1 : 1)));
    settleAt(next);
    return true;
  }

  const ignored = (target) => !!target.closest?.(".material-search-results");
  const onTouchStart = (e) => {
    if (!active()) return;
    if (e.touches.length > 1 || ignored(e.target)) { mode = "native"; return; }
    begin(e.touches[0].clientY, e.target, e.timeStamp);
  };
  const onTouchMove = (e) => {
    if (!mode || mode === "native" || e.touches.length > 1) return;
    if (move(e.touches[0].clientY, e.timeStamp) && e.cancelable) e.preventDefault();
  };
  const onTouchEnd = (e) => { if (mode) end(e.timeStamp); };
  panel.addEventListener("touchstart", onTouchStart, { passive: true });
  panel.addEventListener("touchmove", onTouchMove, { passive: false });
  panel.addEventListener("touchend", onTouchEnd);
  panel.addEventListener("touchcancel", onTouchEnd);

  // A mouse drags the grabber, and a click on it raises the sheet or brings it back to half.
  let mouseDrag = false;
  const onGrabDown = (e) => {
    if (!active() || e.pointerType === "touch") return;
    grabber.setPointerCapture(e.pointerId);
    begin(e.clientY, grabber, e.timeStamp);
    mouseDrag = true;
  };
  const onGrabMove = (e) => { if (mouseDrag && mode) move(e.clientY, e.timeStamp); };
  const onGrabUp = (e) => {
    if (!mouseDrag) return;
    mouseDrag = false;
    if (!end(e.timeStamp)) settleAt(level === 2 ? 1 : 2);
  };
  grabber.addEventListener("pointerdown", onGrabDown);
  grabber.addEventListener("pointermove", onGrabMove);
  grabber.addEventListener("pointerup", onGrabUp);
  grabber.addEventListener("pointercancel", onGrabUp);
  const onGrabTap = (e) => { if (active() && e.pointerType === "touch") settleAt(level === 2 ? 1 : 2); };
  grabber.addEventListener("click", onGrabTap);

  // A wheel over the list raises the sheet before it scrolls, and lowers it from the list's top.
  let wheelRest = 0;
  const onWheel = (e) => {
    if (!active() || ignored(e.target)) return;
    const all = heights();
    const atTop = height >= all[2] - 1;
    if (atTop && (e.deltaY > 0 || panel.scrollTop > 0)) return;
    e.preventDefault();
    stop();
    apply(Math.max(all[0], Math.min(all[2], height + e.deltaY)));
    clearTimeout(wheelRest);
    wheelRest = setTimeout(() => settleAt(nearest(height)), 160);
  };
  panel.addEventListener("wheel", onWheel, { passive: false });

  // Typing a search wants the room above a phone's keyboard, so the sheet rises for it.
  const onFocus = (e) => { if (active() && level < 2 && e.target.matches?.(".material-search input")) settleAt(2); };
  panel.addEventListener("focusin", onFocus);

  // --- The model makes room for itself ---
  // A drag, a pinch or a wheel on the model lowers the sheet; a tap on it does not.
  const canvas = renderer.domElement;
  const presses = new Map();
  let lowered = false;
  const lower = () => {
    if (lowered || !active() || level === 0) return;
    lowered = true;
    settleAt(0);
  };
  const onCanvasDown = (e) => {
    if (!active()) return;
    if (!presses.size) lowered = false;
    presses.set(e.pointerId, [e.clientX, e.clientY]);
    if (presses.size > 1) lower();
  };
  const onCanvasMove = (e) => {
    const at = presses.get(e.pointerId);
    if (at && Math.hypot(e.clientX - at[0], e.clientY - at[1]) > SLOP) lower();
  };
  const onCanvasUp = (e) => { presses.delete(e.pointerId); };
  const onCanvasWheel = () => { lowered = false; lower(); };
  canvas.addEventListener("pointerdown", onCanvasDown, true);
  canvas.addEventListener("pointermove", onCanvasMove, true);
  document.addEventListener("pointerup", onCanvasUp, true);
  document.addEventListener("pointercancel", onCanvasUp, true);
  canvas.addEventListener("wheel", onCanvasWheel, { capture: true, passive: true });
  canvas.addEventListener("gesturestart", lower, true);

  // --- Opening, closing and the screen changing size ---
  function sync({ recentre = false } = {}) {
    stop();
    if (!active()) {
      workspace.style.removeProperty("--sheet-height");
      panel.classList.remove("sheet-top");
      height = 0;
      setViewInset(0, { hold: false });
      return;
    }
    apply(heights()[level], { hold: !recentre });
  }
  const resize = new ResizeObserver(() => { if (active() && !animation && !mode) apply(heights()[level]); });
  resize.observe(workspace);
  const onLayout = () => sync({ recentre: true });
  PHONE.addEventListener("change", onLayout);

  return {
    // The pane opened or closed: it opens at half, with the model centred in what is left.
    setOpen(next) {
      if (next === open) return;
      open = next;
      level = 1;
      sync({ recentre: true });
    },
    // A part chosen in the list: the sheet comes down to half if it stands higher, and the
    // model's framing aims at the room that leaves.
    reveal() {
      if (active() && level === 2) settleAt(1, { hold: false });
    },
    dispose() {
      stop();
      clearTimeout(wheelRest);
      resize.disconnect();
      PHONE.removeEventListener("change", onLayout);
      canvas.removeEventListener("pointerdown", onCanvasDown, true);
      canvas.removeEventListener("pointermove", onCanvasMove, true);
      document.removeEventListener("pointerup", onCanvasUp, true);
      document.removeEventListener("pointercancel", onCanvasUp, true);
      canvas.removeEventListener("wheel", onCanvasWheel, true);
      canvas.removeEventListener("gesturestart", lower, true);
      if (open) setViewInset(0, { hold: false });
      grabber.remove();
    },
  };
}
