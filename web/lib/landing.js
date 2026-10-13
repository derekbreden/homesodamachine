// Public appliance overview, using the shared Big Blue palette and faucet mark.

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

const BODY = `<main class="home-main">
  <div class="home-wrap">
    <section class="home-hero" aria-labelledby="home-title">
      <div class="home-copy">
        <p class="home-brand"><img src="/brand/mark.svg" width="40" height="40" alt="">Home Soda Machine</p>
        <h1 id="home-title">Cold soda<span class="home-title-dot">.</span><br>From a kitchen faucet.</h1>
        <p class="home-intro">A machine under the counter. A dedicated faucet above it. Together, they put cold, carbonated soda in your glass.</p>
        <p class="home-stage">A kitchen appliance in development.</p>
        <a class="home-explore" href="#how-it-fits">See how it fits <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M12 4v16m-6-6 6 6 6-6"/></svg></a>
      </div>
      <figure class="home-illustration">
        <img src="/landing/kitchen-overview.svg" width="1000" height="860" fetchpriority="high" alt="A cutaway kitchen illustration: a dedicated soda faucet and a glass above the counter, connected to the soda machine and a CO₂ cylinder in the cabinet below.">
        <div class="home-figure-label home-figure-label--faucet" aria-hidden="true"><span>Above the counter</span><strong>The faucet</strong></div>
        <div class="home-figure-label home-figure-label--machine" aria-hidden="true"><span>Below the counter</span><strong>The machine</strong></div>
        <figcaption>Illustration of the appliance.</figcaption>
      </figure>
    </section>

    <section class="home-anatomy" id="how-it-fits" aria-labelledby="home-fit-title">
      <h2 id="home-fit-title">How it fits in the kitchen.</h2>
      <dl class="home-parts">
        <div>
          <dt><span>Above the counter</span>A faucet for your soda.</dt>
          <dd>Choose one of two flavors on the faucet display. Press the lever to pour chilled, carbonated soda straight into a glass.</dd>
        </div>
        <div>
          <dt><span>Below the counter</span>The appliance in the cabinet.</dt>
          <dd>The machine connects to your cold-water supply, chills and carbonates the water, and holds both flavors. A CO₂ cylinder sits beside it.</dd>
        </div>
      </dl>
    </section>

    <section class="home-film-section" aria-labelledby="home-film-title">
      <div class="home-film-copy">
        <p class="home-section-label">The short film</p>
        <h2 id="home-film-title">One Less Errand.</h2>
        <p>A short film about soda at home.</p>
      </div>
      <div class="film">
        <iframe
          src="https://www.youtube-nocookie.com/embed/WHO-V2DPTcs?rel=0"
          title="One Less Errand — Cold Soda on Tap at Home"
          loading="lazy"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
          referrerpolicy="strict-origin-when-cross-origin"
          allowfullscreen></iframe>
      </div>
    </section>

    <section class="suppliers" aria-labelledby="suppliers-heading">
      <h2 id="suppliers-heading">Suppliers include</h2>
      <ul>
        <li>
          <a href="https://www.freshwatersystems.com/"><img src="/suppliers/fresh-water-systems.png" width="137" height="48" loading="lazy" alt="Fresh Water Systems"></a>
          <p>The food-grade fittings and tubing that carry water, soda, flavor and CO₂ through the machine.</p>
        </li>
        <li>
          <a href="https://jlcpcb.com/"><img src="/suppliers/jlcpcb.svg" width="141" height="31" loading="lazy" alt="JLCPCB"></a>
          <p>Makes our circuit boards and fully assembles the main controller that runs the pumps and valves.</p>
        </li>
        <li>
          <a href="https://sendcutsend.com/"><img src="/suppliers/sendcutsend.svg" width="169" height="30" loading="lazy" alt="SendCutSend"></a>
          <p>Laser-cuts the quarter-inch 316 stainless end caps of the carbonator tank, and the faucet’s under-counter plate.</p>
        </li>
        <li>
          <a href="https://www.lulu.com/"><img src="/suppliers/lulu.svg" width="106" height="37" loading="lazy" alt="Lulu"></a>
          <p>Prints and binds the 32-page, full-color install guide that comes with every machine.</p>
        </li>
      </ul>
      <p class="suppliers-all">The <a href="/cost">cost page</a> lists every part of the machine and where it comes from.</p>
    </section>

    <section class="home-availability" aria-labelledby="home-availability-title">
      <div>
        <h2 id="home-availability-title">When it’s ready.</h2>
        <p>I’ll email you once when you can buy one. No timeline, no other messages.</p>
      </div>
      <div class="home-signup">
        <form id="signup">
          <label for="signup-email">Email address</label>
          <div class="home-signup-controls">
            <input type="email" id="signup-email" name="email" placeholder="you@example.com" required autocomplete="email" aria-describedby="status">
            <button type="submit" class="signup-btn" id="signup-btn">
              <span class="label">Notify me</span>
              <span class="spinner" aria-hidden="true"></span>
              <svg class="check" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" aria-hidden="true"><polyline points="4 12 10 18 20 6"></polyline></svg>
            </button>
          </div>
        </form>
        <div id="status" class="status" aria-live="polite"></div>
      </div>
    </section>
  </div>
</main>
<script src="/landing.js" defer></script>
`;

export function mountLandingRoutes(app) {
  app.get("/", (_req, res) => {
    res.set("Content-Type", "text/html; charset=utf-8");
    res.set("Cache-Control", "no-cache");
    res.send(
      renderHead({
        title: "Home Soda Machine — Cold soda from a kitchen faucet",
        pageStyles: SIGNUP_BUTTON_CSS,
        pageHead: `<meta name="description" content="Home Soda Machine is a kitchen appliance in development: a machine under the counter and a dedicated faucet above it, for cold, carbonated soda in your glass.">
<link rel="canonical" href="https://homesodamachine.com/">
<link rel="stylesheet" href="/css/landing.css">`,
      }) +
      renderNav({ active: "home" }) +
      BODY +
      renderFooter(),
    );
  });
}
