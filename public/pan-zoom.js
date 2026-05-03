// PanZoom — vanilla pan + pinch-zoom + wheel-zoom for any element.
//
// Generalized from the mermaid detail view in
// tools/step-viewer/templates/viewer-body.html. Same pinch math (anchor at
// the gesture midpoint, recompute pan so that midpoint stays put), same
// pointer state machine, just wrapped so the caller controls the target and
// container.
//
// Usage:
//   const pz = PanZoom.wrap(el, {
//     container,           // viewport element (defaults to el.parentElement)
//     initialFit: true,    // fit-to-container on mount
//     minScale, maxScale,
//     onTransformChange,   // ({scale,panX,panY}) — debounced ~250ms
//   });
//   pz.fit(); pz.reset(); pz.setTransform({scale,panX,panY}); pz.getTransform();
//   pz.destroy();
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
    // Fall back to the unscaled rect — measure with no transform applied so
    // we get the element's natural box, not the scaled one.
    const prev = el.style.transform;
    el.style.transform = "none";
    const r = el.getBoundingClientRect();
    el.style.transform = prev;
    return { w: r.width, h: r.height };
  }

  function wrap(el, opts) {
    if (!el) throw new Error("PanZoom.wrap: element required");
    opts = opts || {};
    const container = opts.container || el.parentElement;
    if (!container) throw new Error("PanZoom.wrap: container required");
    const minScale = opts.minScale != null ? opts.minScale : 0.1;
    const maxScale = opts.maxScale != null ? opts.maxScale : 10;
    const onChange = opts.onTransformChange || null;

    let scale = 1, panX = 0, panY = 0;
    const active = new Map(); // pointerId -> {x,y}
    let dragStart = null;     // {startX,startY,panX,panY}
    let pinchStart = null;    // {dist,midX,midY,panX,panY,scale}
    let changeTimer = null;
    let destroyed = false;

    el.style.transformOrigin = "0 0";

    function apply() {
      el.style.transform =
        "translate(" + panX + "px, " + panY + "px) scale(" + scale + ")";
      if (onChange) {
        if (changeTimer) clearTimeout(changeTimer);
        changeTimer = setTimeout(function () {
          onChange({ scale: scale, panX: panX, panY: panY });
        }, 250);
      }
    }

    function fit() {
      const viewport = container.getBoundingClientRect();
      const nat = getNaturalSize(el);
      if (!nat.w || !nat.h) return;
      // Container not laid out yet (e.g. inside a <dialog> that hasn't been
      // showModal'd, or detached from the DOM). Retry once layout is real.
      if (!viewport.width || !viewport.height) {
        if (typeof requestAnimationFrame === "function" && !destroyed) {
          requestAnimationFrame(function () { if (!destroyed) fit(); });
        }
        return;
      }
      const padding = 0;
      const sx = (viewport.width - padding * 2) / nat.w;
      const sy = (viewport.height - padding * 2) / nat.h;
      scale = Math.min(sx, sy);
      panX = (viewport.width - nat.w * scale) / 2;
      panY = (viewport.height - nat.h * scale) / 2;
      apply();
    }

    function reset() { scale = 1; panX = 0; panY = 0; apply(); }

    function setTransform(t) {
      if (t.scale != null) scale = clamp(t.scale, minScale, maxScale);
      if (t.panX != null) panX = t.panX;
      if (t.panY != null) panY = t.panY;
      apply();
    }
    function getTransform() { return { scale: scale, panX: panX, panY: panY }; }
    function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }

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
        const ns = clamp(pinchStart.scale * (dist / pinchStart.dist), minScale, maxScale);
        const dx = (pinchStart.midX - pinchStart.panX) / pinchStart.scale;
        const dy = (pinchStart.midY - pinchStart.panY) / pinchStart.scale;
        panX = midX - dx * ns;
        panY = midY - dy * ns;
        scale = ns;
        apply();
      } else if (active.size === 1 && dragStart) {
        panX = dragStart.panX + (e.clientX - dragStart.startX);
        panY = dragStart.panY + (e.clientY - dragStart.startY);
        apply();
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
      const ns = clamp(scale * factor, minScale, maxScale);
      panX = mx - dx * ns; panY = my - dy * ns; scale = ns;
      apply();
    }

    container.addEventListener("pointerdown", onPointerDown);
    container.addEventListener("pointermove", onPointerMove);
    container.addEventListener("pointerup", onPointerEnd);
    container.addEventListener("pointercancel", onPointerEnd);
    container.addEventListener("wheel", onWheel, { passive: false });

    function maybeFit() {
      if (opts.initialFit === false) { apply(); return; }
      // If wrapped element is an <img> still loading, wait for it so we can
      // measure naturalWidth/Height.
      if (el instanceof HTMLImageElement && !el.complete) {
        el.addEventListener("load", function once() {
          el.removeEventListener("load", once);
          if (!destroyed) fit();
        });
        // Apply an initial identity so the element is positioned somewhere
        // sane until the load fires.
        apply();
      } else {
        fit();
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
    }

    return {
      fit: fit,
      reset: reset,
      setTransform: setTransform,
      getTransform: getTransform,
      destroy: destroy,
    };
  }

  window.PanZoom = { wrap: wrap };
})();
