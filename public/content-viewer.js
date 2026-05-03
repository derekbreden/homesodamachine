// ContentViewer — modal frame for showing arbitrary content (images, SVGs,
// long text, mermaid, eventually STEP). Native <dialog> for backdrop +
// focus trap + Escape; bespoke open/close transitions and a top drag area
// that swipe-down dismisses on touch.
//
// Singleton: only one viewer open at a time.
//
// Visuals match the subscribe-modal pattern in lib/settings.js:
// rounded card, dimmed backdrop, white-on-dark chrome — extended here to
// also support a borderless content-fills-the-card mode (because the
// content IS the focus).
//
// API:
//   ContentViewer.open({ content, filename, onOpen, onClose });
//   ContentViewer.close();
//   ContentViewer.isOpen();

(function () {
  const STYLE_ID = "content-viewer-styles";

  function ensureStyles() {
    if (document.getElementById(STYLE_ID)) return;
    const style = document.createElement("style");
    style.id = STYLE_ID;
    style.textContent = `
.cv-dialog {
  border: none;
  padding: 0;
  margin: 0;
  background: transparent;
  color: inherit;
  width: 100vw;
  height: 100vh;
  max-width: 100vw;
  max-height: 100vh;
  inset: 0;
}
.cv-dialog::backdrop { background: transparent; }
.cv-dialog[open] { display: flex; align-items: center; justify-content: center; }
.cv-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.85);
  opacity: 0;
  transition: opacity 180ms ease-out;
  z-index: 0;
}
@supports (backdrop-filter: blur(8px)) or (-webkit-backdrop-filter: blur(8px)) {
  .cv-backdrop {
    background: rgba(0, 0, 0, 0.7);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
  }
}
.cv-dialog.cv-open .cv-backdrop { opacity: 1; }
.cv-card {
  position: relative;
  background: #1a1a2e;
  border-radius: 10px;
  padding: 0;
  max-width: calc(100vw - 32px);
  max-height: calc(100vh - 32px);
  width: calc(100vw - 32px);
  height: calc(100vh - 32px);
  overflow: hidden;
  opacity: 0;
  transform: scale(0.96);
  transition: opacity 180ms ease-out, transform 180ms ease-out;
  z-index: 1;
  display: flex;
  flex-direction: column;
  touch-action: none;
}
.cv-dialog.cv-open .cv-card { opacity: 1; transform: scale(1); }
.cv-dialog.cv-closing .cv-backdrop { opacity: 0; transition: opacity 150ms ease-in; }
.cv-dialog.cv-closing .cv-card {
  opacity: 0;
  transform: scale(0.96);
  transition: opacity 150ms ease-in, transform 150ms ease-in;
}
.cv-dialog.cv-swiping .cv-card,
.cv-dialog.cv-swiping .cv-backdrop { transition: none; }

.cv-content {
  flex: 1;
  min-height: 0;
  width: 100%;
  position: relative;
  overflow: hidden;
}
.cv-content > * {
  width: 100%;
  height: 100%;
}

.cv-drag {
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 80px;
  z-index: 5;
  pointer-events: none;
}

.cv-filename {
  position: absolute;
  top: 12px;
  left: 12px;
  background: rgba(35, 35, 66, 0.85);
  border: 1px solid rgba(58, 58, 90, 0.9);
  color: #ffffff;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 13px;
  font-family: "Montserrat", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  z-index: 10;
  -webkit-backdrop-filter: blur(4px);
  backdrop-filter: blur(4px);
  max-width: calc(100% - 80px);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  pointer-events: none;
}

.cv-close {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(35, 35, 66, 0.85);
  border: 1px solid rgba(58, 58, 90, 0.9);
  color: #ffffff;
  cursor: pointer;
  z-index: 11;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  -webkit-backdrop-filter: blur(4px);
  backdrop-filter: blur(4px);
  transition: background 0.15s;
}
.cv-close:hover { background: rgba(58, 58, 90, 0.95); }
.cv-close svg { width: 18px; height: 18px; display: block; pointer-events: none; }

body.cv-locked { overflow: hidden !important; }
`;
    document.head.appendChild(style);
  }

  let current = null; // { dialog, card, content, onClose, restoreOverflow }

  function isOpen() { return current !== null; }

  function close() {
    if (!current) return;
    const c = current;
    current = null;
    c.dialog.classList.add("cv-closing");
    c.dialog.classList.remove("cv-open");
    const finish = function () {
      try { c.dialog.close(); } catch (_) {}
      try { c.dialog.remove(); } catch (_) {}
      document.body.classList.remove("cv-locked");
      if (c.restoreOverflow != null) document.body.style.overflow = c.restoreOverflow;
      if (c.onClose) {
        try { c.onClose(); } catch (e) { console.warn("ContentViewer onClose:", e); }
      }
    };
    setTimeout(finish, 160);
  }

  function open(opts) {
    if (!opts || !opts.content) throw new Error("ContentViewer.open: content required");
    ensureStyles();

    // Singleton — close prior viewer (synchronously, then continue).
    if (current) {
      const prev = current;
      current = null;
      try { prev.dialog.close(); } catch (_) {}
      try { prev.dialog.remove(); } catch (_) {}
      if (prev.onClose) { try { prev.onClose(); } catch (_) {} }
    }

    const dialog = document.createElement("dialog");
    dialog.className = "cv-dialog";

    const backdrop = document.createElement("div");
    backdrop.className = "cv-backdrop";
    dialog.appendChild(backdrop);

    const card = document.createElement("div");
    card.className = "cv-card";
    dialog.appendChild(card);

    const contentSlot = document.createElement("div");
    contentSlot.className = "cv-content";
    contentSlot.appendChild(opts.content);
    card.appendChild(contentSlot);

    const drag = document.createElement("div");
    drag.className = "cv-drag";
    card.appendChild(drag);

    if (opts.filename) {
      const pill = document.createElement("div");
      pill.className = "cv-filename";
      pill.textContent = opts.filename;
      card.appendChild(pill);
    }

    const closeBtn = document.createElement("button");
    closeBtn.type = "button";
    closeBtn.className = "cv-close";
    closeBtn.setAttribute("aria-label", "Close");
    closeBtn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>';
    closeBtn.addEventListener("click", function (e) { e.stopPropagation(); close(); });
    card.appendChild(closeBtn);

    document.body.appendChild(dialog);

    // Body scroll lock.
    const restoreOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    document.body.classList.add("cv-locked");

    current = {
      dialog: dialog,
      card: card,
      content: contentSlot,
      onClose: opts.onClose || null,
      restoreOverflow: restoreOverflow,
    };

    // Backdrop click — clicking the dialog itself (the flex container around
    // the card) means the user missed the card.
    dialog.addEventListener("click", function (e) {
      if (e.target === dialog) close();
    });

    // Native dialog Escape fires "cancel" before close — intercept so we run
    // our animated close instead of the abrupt native one.
    dialog.addEventListener("cancel", function (e) { e.preventDefault(); close(); });

    // Swipe-down on the top drag area to dismiss.
    let swipe = null;
    drag.style.pointerEvents = "auto";
    drag.addEventListener("pointerdown", function (e) {
      if (e.pointerType !== "touch") return;
      swipe = { startY: e.clientY, startX: e.clientX, id: e.pointerId, active: false };
    });
    drag.addEventListener("pointermove", function (e) {
      if (!swipe || swipe.id !== e.pointerId) return;
      const dy = e.clientY - swipe.startY;
      const dx = Math.abs(e.clientX - swipe.startX);
      if (dy > 8 && dy > dx) {
        swipe.active = true;
        dialog.classList.add("cv-swiping");
        const t = Math.max(0, dy);
        card.style.transform = "translateY(" + t + "px) scale(1)";
        backdrop.style.opacity = String(Math.max(0, 1 - t / 400));
      }
    });
    function endSwipe(e) {
      if (!swipe || swipe.id !== e.pointerId) return;
      const dy = e.clientY - swipe.startY;
      const wasActive = swipe.active;
      swipe = null;
      dialog.classList.remove("cv-swiping");
      if (wasActive && dy > 40) {
        close();
      } else {
        card.style.transform = "";
        backdrop.style.opacity = "";
      }
    }
    drag.addEventListener("pointerup", endSwipe);
    drag.addEventListener("pointercancel", endSwipe);

    dialog.showModal();

    // Trigger transitions on next frame.
    requestAnimationFrame(function () {
      requestAnimationFrame(function () {
        dialog.classList.add("cv-open");
        if (opts.onOpen) {
          try { opts.onOpen(); } catch (e) { console.warn("ContentViewer onOpen:", e); }
        }
      });
    });
  }

  window.ContentViewer = { open: open, close: close, isOpen: isOpen };
})();
