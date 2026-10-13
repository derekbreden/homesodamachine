// Public landing page, using the shared Big Blue palette and faucet mark.

import { renderHead, renderNav, renderFooter } from "./shell.js";

export const SIGNUP_BUTTON_CSS = `
.signup-btn:focus-visible { outline: 2px solid var(--text); outline-offset: 2px; }
.signup-btn {
  position: relative;
  width: 100%;
  padding: 0.75rem 1.25rem;
  font: inherit;
  font-size: 1rem;
  font-weight: 500;
  background: var(--action);
  color: var(--on-action);
  /* 1px, transparent — the input spends the same on its border, and stacked
     the two pills stand at one height. */
  border: 1px solid transparent;
  border-radius: 6px;
  cursor: pointer;
  white-space: nowrap;
  transition: background 0.15s, transform 0.05s;
}
@media (min-width: 520px) {
  /* The label does not wrap, so the button must not be squeezed under it. */
  .signup-btn { width: auto; min-width: 7rem; flex-shrink: 0; }
}
.signup-btn:hover:not(:disabled) { background: var(--action-hover); }
.signup-btn:active { transform: scale(0.97); }
.signup-btn:disabled { cursor: default; }
.signup-btn .label {
  display: inline-block;
  transition: opacity 0.15s;
}
.signup-btn.loading .label { opacity: 0; }
.signup-btn.done { background: var(--ok); color: var(--brand-navy); }
.signup-btn .spinner {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 18px;
  height: 18px;
  margin: -9px 0 0 -9px;
  border: 2px solid rgba(16, 49, 156, 0.25);
  border-top-color: var(--on-action);
  border-radius: 50%;
  opacity: 0;
  transition: opacity 0.15s;
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
`;

const PAGE_STYLES = `
main { background: var(--brand-blue); }
main {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  /* Safe-area on sides (for iPhone landscape rounded corners) and bottom
     (for PWA home indicator). Top doesn't need it — the sticky nav above
     already eats safe-area-top. */
  /* The bottom clears a notification toast, which is fixed 12px off the
     bottom and about 67px tall — the suppliers are the last thing on the
     page and the toast arrives over them. */
  padding:
    2rem
    calc(env(safe-area-inset-right, 0px) + 1.5rem)
    calc(env(safe-area-inset-bottom, 0px) + 7rem)
    calc(env(safe-area-inset-left, 0px) + 1.5rem);
  text-align: center;
}
.brand-stage {
  width: min(280px, 60vw);
  aspect-ratio: 1 / 1;
  margin: 0 0 1.25rem;
}
.brand-stage img {
  width: 100%;
  height: 100%;
  display: block;
}
h1 {
  font-size: clamp(1.75rem, 5vw, 2.5rem);
  font-weight: 700;
  margin: 0 0 0.5rem;
  letter-spacing: -0.02em;
}
.tagline {
  color: var(--text-2);
  max-width: 30rem;
  margin: 0 0 2rem;
}
/* The signup form stacks on phones and shares a row on wider screens. */
form {
  display: flex;
  flex-direction: column;
  /* Stacked, the field's focus ring stands in this gap — 0.5rem left it
     resting on the button below. */
  gap: 0.75rem;
  width: 100%;
  max-width: 24rem;
}
@media (min-width: 520px) {
  form {
    flex-direction: row;
    /* Wider on desktop so the button's full-sentence label sits next to
       a comfortably-sized email input without wrapping. */
    max-width: 32rem;
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
@media (min-width: 520px) {
  input[type="email"] { flex: 1 1 auto; width: auto; }
}
/* The field's only visible label, in the tone body copy is set in. */
input[type="email"]::placeholder { color: var(--text-2); }
input[type="email"]:focus {
  outline: none;
  border-color: var(--accent);
}
/* Keyboard focus, on both controls. The button's ring is white — it stands on
   the accent. */
/* The ring is the whole indicator on a key press, so the border stands down —
   two accent edges 1px apart read as one smeared edge. */
input[type="email"]:focus-visible {
  border-color: var(--border);
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}
${SIGNUP_BUTTON_CSS}
.status {
  min-height: 1.5rem;
  margin-top: 1rem;
  font-size: 0.9rem;
  color: var(--text-2);
  transition: color 0.2s;
}
.status.ok, .status.err { padding: 0.35rem 0.75rem; border-radius: 6px; background: var(--bg); }
.status.ok { color: var(--ok); }
.status.err { color: var(--err); }
@keyframes shake {
  0%, 100% { transform: translateX(0); }
  20%, 60% { transform: translateX(-6px); }
  40%, 80% { transform: translateX(6px); }
}
.signup-btn.shake { animation: shake 0.35s; }
/* One Less Errand, under the form and as wide as it. The player is YouTube's,
   from its no-cookie host, and loads when it nears the viewport. */
.film {
  width: 100%;
  max-width: 24rem;
  aspect-ratio: 16 / 9;
  margin-top: 1rem;
  border-radius: 8px;
  overflow: hidden;
  background: var(--bg);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.3);
}
@media (min-width: 520px) {
  .film { max-width: 32rem; }
}
.film iframe {
  display: block;
  width: 100%;
  height: 100%;
  border: 0;
}
/* Suppliers, under the film: one line of four on a desktop, two rows of two
   on a tablet, one column on a phone. Every logo is white on the blue, sized
   by its own proportions so the four carry about the same visual weight. */
.suppliers {
  width: 100%;
  max-width: 60rem;
  margin-top: 4.5rem;
}
.suppliers h2 {
  font-size: 0.72rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--text-2);
  font-weight: 600;
  margin: 0 0 2rem;
}
.suppliers ul {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 2.25rem;
}
@media (min-width: 560px) {
  .suppliers ul { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 2.5rem 2rem; }
}
@media (min-width: 960px) {
  .suppliers ul { grid-template-columns: repeat(4, minmax(0, 1fr)); }
}
/* One height for every logo row, so the blurbs under a line start level. */
.suppliers li a {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 3rem;
  width: fit-content;
  margin: 0 auto 0.875rem;
  border-radius: 4px;
}
.suppliers li a:focus-visible { outline: 2px solid var(--accent); outline-offset: 6px; }
.suppliers img { display: block; }
.suppliers li p {
  max-width: 17rem;
  margin: 0 auto;
  font-size: 0.875rem;
  line-height: 1.55;
  color: var(--text-2);
}
.suppliers .suppliers-all {
  margin: 2.5rem 0 0;
  font-size: 0.8rem;
  color: var(--text-3);
}
.suppliers-all a { color: var(--accent); text-underline-offset: 3px; }
.suppliers-all a:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; border-radius: 2px; }
`;

const BODY = `<main>
  <div class="brand-stage" aria-hidden="true">
    <img src="/brand/mark.svg" width="1024" height="1024" alt="">
  </div>
  <h1>Home Soda Machine</h1>
  <p class="tagline">
    This is a real project, no timeline, I'll bother you exactly once when
    you can buy one, never otherwise
  </p>
  <form id="signup">
    <input
      type="email"
      name="email"
      placeholder="you@example.com"
      aria-label="Email address"
      required
      autocomplete="email"
    />
    <button type="submit" class="signup-btn" id="signup-btn">
      <span class="label">Tell me when I can buy one</span>
      <span class="spinner" aria-hidden="true"></span>
      <svg class="check" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <polyline points="4 12 10 18 20 6"></polyline>
      </svg>
    </button>
  </form>
  <div id="status" class="status" aria-live="polite"></div>
  <div class="film">
    <iframe
      src="https://www.youtube-nocookie.com/embed/WHO-V2DPTcs?rel=0"
      title="One Less Errand — Cold Soda on Tap at Home"
      loading="lazy"
      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
      referrerpolicy="strict-origin-when-cross-origin"
      allowfullscreen></iframe>
  </div>
  <section class="suppliers" aria-labelledby="suppliers-heading">
    <h2 id="suppliers-heading">Suppliers include</h2>
    <ul>
      <li>
        <a href="https://www.freshwatersystems.com/"><img src="/suppliers/fresh-water-systems.png" width="137" height="48" alt="Fresh Water Systems"></a>
        <p>The food-grade fittings and tubing that carry water, soda, flavor and CO₂ through the machine.</p>
      </li>
      <li>
        <a href="https://jlcpcb.com/"><img src="/suppliers/jlcpcb.svg" width="141" height="31" alt="JLCPCB"></a>
        <p>Makes our circuit boards and fully assembles the main controller that runs the pumps and valves.</p>
      </li>
      <li>
        <a href="https://sendcutsend.com/"><img src="/suppliers/sendcutsend.svg" width="169" height="30" alt="SendCutSend"></a>
        <p>Laser-cuts the quarter-inch 316 stainless end caps of the carbonator tank, and the faucet’s under-counter plate.</p>
      </li>
      <li>
        <a href="https://www.lulu.com/"><img src="/suppliers/lulu.svg" width="106" height="37" alt="Lulu"></a>
        <p>Prints and binds the 32-page install guide, the first thing an owner sees when they open the kit.</p>
      </li>
    </ul>
    <p class="suppliers-all">The <a href="/cost">cost page</a> lists every part of the machine and where it comes from.</p>
  </section>
</main>
<script src="/landing.js" defer></script>
`;

export function mountLandingRoutes(app) {
  app.get("/", (_req, res) => {
    res.set("Content-Type", "text/html; charset=utf-8");
    res.set("Cache-Control", "no-cache");
    res.send(
      renderHead({
        title: "Home Soda Machine",
        pageStyles: PAGE_STYLES,
      }) +
      renderNav({ active: "home" }) +
      BODY +
      renderFooter(),
    );
  });
}
