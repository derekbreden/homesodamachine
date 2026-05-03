// Public landing page. Server-rendered via lib/shell.js so the head + nav
// + palette stay in sync with every other surface on the site.
//
// Above the fold: the GlassAnimation (the same one running on iOS, Android,
// and the S3 device — same constants, same physics) plus an h1, tagline,
// and a single email signup form. The submit button has a press state and
// an inline spinner that fills the wait between tap and "thanks."

import { renderHead, renderNav, renderFooter } from "./shell.js";

const PAGE_STYLES = `
main {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 2rem 1.5rem 3rem;
  text-align: center;
}
.glass-stage {
  width: min(280px, 60vw);
  aspect-ratio: 1 / 1;
  margin: 0 0 1.25rem;
}
.glass-stage canvas {
  width: 100%;
  height: 100%;
  display: block;
}
h1 {
  font-size: clamp(1.75rem, 5vw, 2.5rem);
  font-weight: 600;
  margin: 0 0 0.5rem;
  letter-spacing: -0.02em;
}
.tagline {
  color: var(--text-2);
  max-width: 30rem;
  margin: 0 0 2rem;
}
/* Mobile-first: stacked, both controls full-width — same shape as the
   iOS onboarding "Scan for Hardware" / "Enter Demo Mode" pills in
   ScanView.swift. Above ~480px there's room for them side-by-side, so
   we promote the form to a row. */
form {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  width: 100%;
  max-width: 24rem;
}
@media (min-width: 480px) {
  form {
    flex-direction: row;
  }
}
input[type="email"] {
  width: 100%;
  min-width: 0;
  padding: 0.75rem 1rem;
  font: inherit;
  font-size: 1rem;
  background: var(--surface);
  color: var(--text);
  border: 1px solid var(--border);
  border-radius: 6px;
  transition: border-color 0.15s;
}
@media (min-width: 480px) {
  input[type="email"] { flex: 1 1 auto; width: auto; }
}
input[type="email"]::placeholder { color: var(--text-3); }
input[type="email"]:focus {
  outline: none;
  border-color: var(--accent);
}
.signup-btn {
  position: relative;
  width: 100%;
  padding: 0.75rem 1.25rem;
  font: inherit;
  font-size: 1rem;
  font-weight: 500;
  background: var(--accent);
  color: #ffffff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.15s, transform 0.05s;
}
@media (min-width: 480px) {
  .signup-btn { width: auto; min-width: 7rem; }
}
.signup-btn:hover { background: #5599ff; }
.signup-btn:active { transform: scale(0.97); }
.signup-btn:disabled { cursor: default; }
.signup-btn .label {
  display: inline-block;
  transition: opacity 0.15s;
}
.signup-btn.loading .label { opacity: 0; }
.signup-btn.done { background: var(--ok); }
.signup-btn .spinner {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 18px;
  height: 18px;
  margin: -9px 0 0 -9px;
  border: 2px solid rgba(255, 255, 255, 0.35);
  border-top-color: #ffffff;
  border-radius: 50%;
  opacity: 0;
  animation: signup-spin 0.7s linear infinite;
  pointer-events: none;
}
.signup-btn.loading .spinner { opacity: 1; }
@keyframes signup-spin { to { transform: rotate(360deg); } }
.signup-btn .check {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 18px;
  height: 18px;
  margin: -9px 0 0 -9px;
  opacity: 0;
  transition: opacity 0.2s;
  pointer-events: none;
}
.signup-btn.done .label { opacity: 0; }
.signup-btn.done .check { opacity: 1; }
.status {
  min-height: 1.5rem;
  margin-top: 1rem;
  font-size: 0.9rem;
  color: var(--text-2);
  transition: color 0.2s;
}
.status.ok { color: var(--ok); }
.status.err { color: var(--err); }
@keyframes shake {
  0%, 100% { transform: translateX(0); }
  20%, 60% { transform: translateX(-6px); }
  40%, 80% { transform: translateX(6px); }
}
.signup-btn.shake { animation: shake 0.35s; }
`;

const BODY = `<main>
  <div class="glass-stage" aria-hidden="true">
    <canvas id="glass" width="1024" height="1024"></canvas>
  </div>
  <h1>Home Soda Machine</h1>
  <p class="tagline">
    this is a real project, no timeline, I'll bother you exactly once when
    pre-orders open, never otherwise
  </p>
  <form id="signup">
    <input
      type="email"
      name="email"
      placeholder="you@example.com"
      required
      autocomplete="email"
    />
    <button type="submit" class="signup-btn" id="signup-btn">
      <span class="label">Notify me</span>
      <span class="spinner" aria-hidden="true"></span>
      <svg class="check" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <polyline points="4 12 10 18 20 6"></polyline>
      </svg>
    </button>
  </form>
  <div id="status" class="status" aria-live="polite"></div>
</main>
<script src="/glass-animation.js"></script>
<script>
  // Mount the glass animation. Pauses on tab hide / offscreen via the
  // helper itself; nothing to clean up here.
  if (typeof mountGlassAnimation === "function") {
    mountGlassAnimation(document.getElementById("glass"));
  }

  const form = document.getElementById("signup");
  const btn = document.getElementById("signup-btn");
  const status = document.getElementById("status");

  function setState(state) {
    btn.classList.remove("loading", "done", "shake");
    if (state) btn.classList.add(state);
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = form.elements.email.value.trim();
    btn.disabled = true;
    setState("loading");
    status.className = "status";
    status.textContent = "";
    try {
      const r = await fetch("/api/subscribe", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ email }),
      });
      if (r.ok) {
        setState("done");
        status.className = "status ok";
        status.textContent = "Thanks — we'll be in touch.";
        form.reset();
        // After a beat, return the button to its idle state so the user
        // can submit another email if they want.
        setTimeout(() => {
          setState(null);
          btn.disabled = false;
        }, 1600);
      } else {
        const data = await r.json().catch(() => ({}));
        setState("shake");
        status.className = "status err";
        status.textContent = data.error || "Something went wrong.";
        btn.disabled = false;
      }
    } catch {
      setState("shake");
      status.className = "status err";
      status.textContent = "Network error. Try again.";
      btn.disabled = false;
    }
  });
</script>
`;

export function mountLandingRoutes(app) {
  app.get("/", (_req, res) => {
    res.set("Content-Type", "text/html; charset=utf-8");
    res.send(
      renderHead({
        title: "Home Soda Machine",
        pageStyles: PAGE_STYLES,
      }) +
      renderNav({ surface: "public", active: "home" }) +
      BODY +
      renderFooter(),
    );
  });
}
