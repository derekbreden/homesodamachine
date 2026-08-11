// PanZoom — vanilla pan + pinch-zoom + wheel-zoom for any element.
//
// Generalized from the mermaid detail view in
// lib/templates/viewer-body.html. Same pinch math (anchor at
// the gesture midpoint, recompute pan so that midpoint stays put), same
// pointer state machine, just wrapped so the caller controls the target and
// container.
//
// Usage:
//   const pz = PanZoom.wrap(el, {
//     container,           // viewport element (defaults to el.parentElement)
//     initialFit: true,    // fit-to-container on mount
//     minScale, maxScale,
//     onTransformChange,   // ({scale,panX,panY}) — debounced ~250ms (persistence)
//     onTransformLive,     // ({scale,panX,panY}) — immediate, every change (minimap)
//     fitObstacles,        // [{left,top,right,bottom}] the fit keeps the content clear of
//   });
//   pz.fit(); pz.reset(); pz.setTransform({scale,panX,panY}); pz.getTransform();
//   pz.destroy();
//   PanZoom.measureObstacles(container, selectors) — those rects, off the live chrome
//
// PanZoom never restyles the wrapped element. It writes only `transform` and
// `transform-origin: 0 0`. The caller sets bg/border/etc. The caller should
// also give the container `overflow: hidden` and (recommended) `touch-action:
// none` so native page-level pinch/scroll doesn't fight the gesture.

(function () {
  function getNaturalSize(el) {
    if (el instanceof HTMLImageElement && el.naturalWidth) {
      return { w: el.naturalWidth, h: el.naturalHeight };
    }
    if (el instanceof SVGSVGElement) {
      const vb = el.viewBox && el.viewBox.baseVal;
      const w = (vb && vb.width) || parseFloat(el.getAttribute("width")) || 0;
      const h = (vb && vb.height) || parseFloat(el.getAttribute("height")) || 0;
      if (w && h) return { w, h };
    }
    // Declared size, if the element states one (an <iframe> hosting a
    // fixed-size document, say). Taken before measuring because measuring can't
    // be trusted through a transformed ancestor: clearing our own transform
    // still leaves an animating modal's scale in the returned rect, so a fit
    // computed during the open animation lands short and never re-runs. An
    // element that declares its size doesn't need to be measured at all. Same
    // attributes pan-zoom-extras' naturalSize reads, so the minimap and the fit
    // agree on what "natural" means.
    const aw = parseFloat(el.getAttribute && el.getAttribute("width")) || 0;
    const ah = parseFloat(el.getAttribute && el.getAttribute("height")) || 0;
    if (aw && ah) return { w: aw, h: ah };
    // Fall back to the unscaled rect — measure with no transform applied so
    // we get the element's natural box, not the scaled one.
    const prev = el.style.transform;
    el.style.transform = "none";
    const r = el.getBoundingClientRect();
    el.style.transform = prev;
    return { w: r.width, h: r.height };
  }

  // Largest scale at which the content, centered in a vw×vh viewport, clears
  // every obstacle rect (container-local px, {left,top,right,bottom}). With no
  // obstacles this is the plain min-fit. The centered box grows monotonically
  // from the centre, so a binary search finds the threshold — and a corner
  // widget (e.g. the minimap) only constrains the fit once the box actually
  // grows under it, instead of stealing a full-width band. Exposed so the
  // minimap can derive the same "default view" rectangle PanZoom fits to.
  function computeFitScale(vw, vh, natW, natH, obstacles) {
    const base = Math.min(vw / natW, vh / natH);
    if (!obstacles || !obstacles.length || !(base > 0)) return base;
    const hits = (s) => {
      const cw = natW * s, ch = natH * s;
      const bl = (vw - cw) / 2, bt = (vh - ch) / 2, br = bl + cw, bb = bt + ch;
      for (const o of obstacles) {
        if (bl < o.right && br > o.left && bt < o.bottom && bb > o.top) return true;
      }
      return false;
    };
    if (!hits(base)) return base;
    let lo = 0, hi = base;
    for (let i = 0; i < 40; i++) {
      const mid = (lo + hi) / 2;
      if (hits(mid)) hi = mid; else lo = mid;
    }
    return lo > 0 ? lo : base; // centre itself blocked ⇒ degenerate; ignore
  }

  // What `selectors` occupy inside `container`, as fitObstacles rects: container-
  // local, in the layout px (clientWidth/Height) the fit math works in, each one
  // grown by `gap` so the content keeps a margin off it.
  //
  // getBoundingClientRect comes back multiplied by every transform above the
  // element, and a modal's open animation scales its card 0.96 → 1 — so the
  // offsets are divided by the container's own live scale. A fit measured
  // mid-animation lands in the same place as one measured after it settles.
  function measureObstacles(container, selectors, gap) {
    if (!container) return [];
    const cr = container.getBoundingClientRect();
    const cw = container.clientWidth, ch = container.clientHeight;
    if (!cr.width || !cr.height || !cw || !ch) return [];
    const sx = cr.width / cw, sy = cr.height / ch;
    const g = gap == null ? 12 : gap;
    const rects = [];
    for (const sel of selectors) {
      for (const el of document.querySelectorAll(sel)) {
        const r = el.getBoundingClientRect();
        if (!r.width || !r.height) continue;
        rects.push({
          left: (r.left - cr.left) / sx - g,
          top: (r.top - cr.top) / sy - g,
          right: (r.right - cr.left) / sx + g,
          bottom: (r.bottom - cr.top) / sy + g,
        });
      }
    }
    return rects;
  }

  function wrap(el, opts) {
    if (!el) throw new Error("PanZoom.wrap: element required");
    opts = opts || {};
    const container = opts.container || el.parentElement;
    if (!container) throw new Error("PanZoom.wrap: container required");
    const minScale = opts.minScale != null ? opts.minScale : 0.1;
    const maxScale = opts.maxScale != null ? opts.maxScale : 10;
    const onChange = opts.onTransformChange || null;
    const onLive = opts.onTransformLive || null;
    // Optional fit obstacles: rectangles (container-local px, {left,top,right,
    // bottom}) the fitted content must clear — the overlaid chrome (PCB toggle /
    // minimap / readout pills). The fit (and the zoom-out floor, which IS the fit
    // scale) shrink only as far as needed to keep the centered content out of
    // them, so a corner widget constrains the fit only when the content grows
    // under it. Read live so a caller can measure its chrome after layout and
    // mutate the same array in place. Absent ⇒ plain fit (no change).
    const fitObstacles = opts.fitObstacles || null;

    let scale = 1, panX = 0, panY = 0;
    const active = new Map(); // pointerId -> {x,y}
    let dragStart = null;     // {startX,startY,panX,panY}
    let pinchStart = null;    // {dist,midX,midY,panX,panY,scale}
    let changeTimer = null;
    let destroyed = false;

    el.style.transformOrigin = "0 0";

    function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }

    // The fit scale (the scale at which the content fully fits the
    // container). Acts as the dynamic floor for the user's zoom — they can
    // never pinch/wheel below "fully visible," because there's nothing to
    // see down there. Returns 0 if the layout isn't ready yet.
    // Viewport SIZE for fit/pan math. clientWidth/Height are layout px — NOT
    // affected by an ancestor CSS transform (the modal card animates scale
    // 0.96→1 on open), unlike getBoundingClientRect. Using them makes the fit
    // and centering correct mid-animation, so no settle-timing dance is needed.
    // (Pointer handlers still read getBoundingClientRect for the screen origin.)
    function viewportSize() {
      return { width: container.clientWidth, height: container.clientHeight };
    }

    function fitScale() {
      const viewport = viewportSize();
      const nat = getNaturalSize(el);
      if (!nat.w || !nat.h || !viewport.width || !viewport.height) return 0;
      return computeFitScale(viewport.width, viewport.height, nat.w, nat.h, fitObstacles);
    }

    // Pan limits given a scale. When content is smaller than the viewport
    // along an axis, that axis is locked to centered (min == max). When
    // larger, pan is allowed only enough to keep some content visible —
    // dragging stops the moment an edge meets the corresponding container
    // edge, with no overscroll into empty space. Same category of fix as
    // capping body min-height to 100svh on iOS Safari.
    function panBounds(s) {
      const viewport = viewportSize();
      const nat = getNaturalSize(el);
      if (!nat.w || !nat.h || !viewport.width || !viewport.height) {
        return { minX: -Infinity, maxX: Infinity, minY: -Infinity, maxY: Infinity };
      }
      const cw = nat.w * s, ch = nat.h * s;
      // Centered when the content fits the viewport on an axis (it sits centred
      // at the fit scale, clear of the obstacles by construction); pannable to
      // the edges once larger (it may slide under chrome when zoomed in).
      const bx = cw <= viewport.width
        ? { min: (viewport.width - cw) / 2, max: (viewport.width - cw) / 2 }
        : { min: viewport.width - cw, max: 0 };
      const by = ch <= viewport.height
        ? { min: (viewport.height - ch) / 2, max: (viewport.height - ch) / 2 }
        : { min: viewport.height - ch, max: 0 };
      return { minX: bx.min, maxX: bx.max, minY: by.min, maxY: by.max };
    }

    // Scale bounds for the current layout. Floor is the fit scale (no
    // pinching below "fully visible"). Ceiling grows with fit too, so an
    // SVG drawn in large natural units (a quickstart sheet in mm, fit
    // scale ~2x) zooms to the same perceived depth as a part SVG drawn
    // in small CAD units (fit scale ~1x). maxScale is interpreted as a
    // multiplier above the fit scale, with an absolute floor of maxScale
    // itself so tiny content still allows zooming up to its native size.
    function scaleBounds() {
      const fs = fitScale();
      if (fs <= 0) return { lo: minScale, hi: maxScale };
      return { lo: Math.max(minScale, fs), hi: Math.max(maxScale, fs * maxScale) };
    }

    // The single state-mutating path. Every gesture / API call funnels
    // through this so the clamping rules stay consistent.
    function commit(s, px, py) {
      const sb = scaleBounds();
      s = clamp(s, sb.lo, sb.hi);
      const b = panBounds(s);
      px = clamp(px, b.minX, b.maxX);
      py = clamp(py, b.minY, b.maxY);
      scale = s; panX = px; panY = py;
      apply();
    }

    // `persist` marks a committed view — the user's, and the one worth
    // restoring next open. The identity below is the placeholder this mounts
    // with while it waits for a measurable container; saved, it becomes a
    // stored "view" no gesture produced, and every later open restores that
    // instead of fitting.
    function apply(persist) {
      el.style.transform =
        "translate(" + panX + "px, " + panY + "px) scale(" + scale + ")";
      if (onLive) {
        try { onLive({ scale: scale, panX: panX, panY: panY }); } catch (_) {}
      }
      if (onChange && persist !== false) {
        if (changeTimer) clearTimeout(changeTimer);
        changeTimer = setTimeout(function () {
          onChange({ scale: scale, panX: panX, panY: panY });
        }, 250);
      }
    }

    function fit() {
      const fs = fitScale();
      if (!fs) {
        // Container not laid out yet (e.g. inside a <dialog> that hasn't
        // been showModal'd). Retry once layout is real.
        if (typeof requestAnimationFrame === "function" && !destroyed) {
          requestAnimationFrame(function () { if (!destroyed) fit(); });
        }
        return;
      }
      commit(fs, 0, 0);  // commit will center via panBounds
    }

    function reset() { commit(1, 0, 0); }

    function setTransform(t) {
      commit(
        t.scale != null ? t.scale : scale,
        t.panX != null ? t.panX : panX,
        t.panY != null ? t.panY : panY,
      );
    }
    function getTransform() { return { scale: scale, panX: panX, panY: panY }; }

    function onPointerDown(e) {
      if (e.target.closest && e.target.closest("button")) return;
      if (e.pointerType === "mouse" && e.button !== 0) return;
      try { container.setPointerCapture(e.pointerId); } catch (_) {}
      active.set(e.pointerId, { x: e.clientX, y: e.clientY });
      if (active.size === 1) {
        dragStart = { startX: e.clientX, startY: e.clientY, panX: panX, panY: panY };
      } else if (active.size === 2) {
        const pts = Array.from(active.values());
        const p1 = pts[0], p2 = pts[1];
        pinchStart = {
          dist: Math.hypot(p2.x - p1.x, p2.y - p1.y) || 1,
          midX: (p1.x + p2.x) / 2,
          midY: (p1.y + p2.y) / 2,
          panX: panX, panY: panY, scale: scale,
        };
        dragStart = null;
      }
    }
    function onPointerMove(e) {
      if (!active.has(e.pointerId)) return;
      active.set(e.pointerId, { x: e.clientX, y: e.clientY });
      if (active.size === 2 && pinchStart) {
        const pts = Array.from(active.values());
        const p1 = pts[0], p2 = pts[1];
        const dist = Math.hypot(p2.x - p1.x, p2.y - p1.y) || 1;
        const midX = (p1.x + p2.x) / 2;
        const midY = (p1.y + p2.y) / 2;
        // Pre-clamp the target scale so the anchor pan is computed against
        // the actual final scale. Without this, pinching past the cap
        // drives pan past the bounds every frame and the view drifts.
        const sb = scaleBounds();
        const ns = clamp(pinchStart.scale * (dist / pinchStart.dist), sb.lo, sb.hi);
        const dx = (pinchStart.midX - pinchStart.panX) / pinchStart.scale;
        const dy = (pinchStart.midY - pinchStart.panY) / pinchStart.scale;
        commit(ns, midX - dx * ns, midY - dy * ns);
      } else if (active.size === 1 && dragStart) {
        commit(
          scale,
          dragStart.panX + (e.clientX - dragStart.startX),
          dragStart.panY + (e.clientY - dragStart.startY),
        );
      }
    }
    function onPointerEnd(e) {
      if (!active.delete(e.pointerId)) return;
      if (active.size === 0) {
        dragStart = null; pinchStart = null;
      } else if (active.size === 1) {
        pinchStart = null;
        const p = active.values().next().value;
        dragStart = { startX: p.x, startY: p.y, panX: panX, panY: panY };
      }
    }
    function onWheel(e) {
      e.preventDefault();
      const rect = container.getBoundingClientRect();
      const mx = e.clientX - rect.left, my = e.clientY - rect.top;
      const dx = (mx - panX) / scale, dy = (my - panY) / scale;
      // Trackpad pinch on macOS arrives as wheel + ctrlKey with small deltaY.
      // Bigger deltas need a stronger response, so scale the factor by deltaY.
      const intensity = e.ctrlKey ? 0.01 : 0.0015;
      const factor = Math.exp(-e.deltaY * intensity);
      // Pre-clamp scale to its allowed range BEFORE computing the anchor
      // pan. Otherwise commit clamps scale to the cap but the pan term
      // keeps using the unclamped target, so each tick over the cap
      // drives pan further past the bounds — visible as the view
      // whipping to a corner the moment max zoom is reached.
      const sb = scaleBounds();
      const ns = clamp(scale * factor, sb.lo, sb.hi);
      commit(ns, mx - dx * ns, my - dy * ns);
    }

    container.addEventListener("pointerdown", onPointerDown);
    container.addEventListener("pointermove", onPointerMove);
    container.addEventListener("pointerup", onPointerEnd);
    container.addEventListener("pointercancel", onPointerEnd);
    container.addEventListener("wheel", onWheel, { passive: false });

    let fitObserver = null;
    function maybeFit() {
      // initialFit: false means the caller sets the view itself, on the line
      // after this one — the identity here is only what renders until it does.
      if (opts.initialFit === false) { apply(false); return; }
      // Always set an initial identity transform so the element renders
      // somewhere sane while we wait for layout / image load. fit() will
      // overwrite this once dimensions are known.
      apply(false);
      const tryFit = function () {
        if (destroyed) return false;
        const fs = fitScale();
        if (fs > 0) { commit(fs, 0, 0); return true; }
        return false;
      };
      const onReady = function () {
        if (tryFit()) return;
        // Container or element has no dimensions yet (detached, hidden,
        // dialog not yet shown, etc.). Watch the container until it
        // becomes measurable, then fit once. Falls back to a single rAF
        // retry if ResizeObserver isn't available.
        if (typeof ResizeObserver === "function") {
          fitObserver = new ResizeObserver(function () {
            if (destroyed) { fitObserver.disconnect(); return; }
            if (tryFit()) {
              fitObserver.disconnect();
              fitObserver = null;
            }
          });
          fitObserver.observe(container);
        } else if (typeof requestAnimationFrame === "function") {
          requestAnimationFrame(function () { if (!destroyed) onReady(); });
        }
      };
      // If wrapped element is an <img> still loading, wait for it so we
      // can measure naturalWidth/Height before fitting.
      if (el instanceof HTMLImageElement && !el.complete) {
        el.addEventListener("load", function once() {
          el.removeEventListener("load", once);
          onReady();
        });
      } else {
        onReady();
      }
    }
    maybeFit();

    function destroy() {
      destroyed = true;
      container.removeEventListener("pointerdown", onPointerDown);
      container.removeEventListener("pointermove", onPointerMove);
      container.removeEventListener("pointerup", onPointerEnd);
      container.removeEventListener("pointercancel", onPointerEnd);
      container.removeEventListener("wheel", onWheel);
      if (changeTimer) clearTimeout(changeTimer);
      if (fitObserver) { fitObserver.disconnect(); fitObserver = null; }
    }

    return {
      fit: fit,
      reset: reset,
      setTransform: setTransform,
      getTransform: getTransform,
      destroy: destroy,
    };
  }

  window.PanZoom = {
    wrap: wrap,
    fitScale: computeFitScale,
    measureObstacles: measureObstacles,
  };
})();
