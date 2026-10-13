// Public appliance overview, using the shared Big Blue palette and faucet mark.

import { renderHead, renderNav, renderFooter } from "./shell.js";
import { renderLandingSupport } from "./landing-support.js";

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
  <div class="home-cover">
    <header class="home-masthead home-inner">
      <a class="home-brand" href="/" aria-label="Home Soda Machine home"><img src="/brand/wordmark-reverse.svg" width="1680" height="640" alt="Home Soda Machine"></a>
      <span class="home-stage"><span aria-hidden="true"></span>In development</span>
    </header>
    <section class="home-hero home-inner" aria-labelledby="home-title">
      <div class="home-copy">
        <h1 id="home-title"><span>Soda from a</span> <span>kitchen faucet.</span></h1>
        <p class="home-intro">A dedicated faucet above the counter. A machine below it. Chilled, carbonated soda straight into your glass.</p>
        <a class="home-explore" href="#the-appliance">Explore the appliance <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M12 4v16m-6-6 6 6 6-6"/></svg></a>
      </div>
      <figure class="home-scene">
        <div class="home-scene-stage">
          <img src="/landing/kitchen-scene.webp" width="1800" height="1800" fetchpriority="high" alt="Design illustration of a kitchen with a dedicated soda faucet pouring into a glass above the counter, connected to the soda machine and CO₂ cylinder inside the cabinet below. The ordinary sink faucet is separate.">
        </div>
        <figcaption><span>Above the counter. Below the counter.</span><span>Design illustration</span></figcaption>
      </figure>
    </section>
  </div>

  <section class="home-details" id="the-appliance" aria-labelledby="home-details-title">
    <div class="home-inner">
      <div class="home-section-heading">
        <p class="home-eyebrow">The appliance</p>
        <h2 id="home-details-title">At the counter.<br>In the cabinet.</h2>
      </div>
      <div class="home-parts">
        <article class="home-part">
          <figure class="home-part-art"><img src="/landing/faucet-detail.webp" width="1800" height="1350" loading="lazy" alt="Detail of the dedicated soda faucet’s display and lever, with a glass beneath the outlet."></figure>
          <div class="home-part-copy">
            <p class="home-part-position"><span aria-hidden="true">01</span>Above the counter</p>
            <h3>The soda faucet.</h3>
            <p>Choose one of two flavors on the display. Press the lever to pour into your glass.</p>
          </div>
        </article>
        <article class="home-part">
          <figure class="home-part-art"><img src="/landing/cabinet-detail.webp" width="1800" height="1350" loading="lazy" alt="Detail of the soda machine and a CO₂ cylinder standing beside it inside the kitchen cabinet."></figure>
          <div class="home-part-copy">
            <p class="home-part-position"><span aria-hidden="true">02</span>Below the counter</p>
            <h3>The soda machine.</h3>
            <p>Connected to your cold-water supply, the appliance chills and carbonates the water and holds both flavors. The CO₂ cylinder sits beside it.</p>
          </div>
        </article>
      </div>
    </div>
  </section>

  ${renderLandingSupport()}
</main>
<script src="/landing.js" defer></script>
`;

export function mountLandingRoutes(app) {
  app.get("/", (_req, res) => {
    res.set("Content-Type", "text/html; charset=utf-8");
    res.set("Cache-Control", "no-cache");
    res.send(
      renderHead({
        title: "Home Soda Machine — Soda from a kitchen faucet",
        pageStyles: SIGNUP_BUTTON_CSS,
        pageHead: `<meta name="description" content="Home Soda Machine is a kitchen appliance in development: a machine under the counter and a dedicated faucet above it, for chilled, carbonated soda in your glass.">
<link rel="canonical" href="https://homesodamachine.com/">
<link rel="stylesheet" href="/css/landing.css">
<link rel="stylesheet" href="/css/landing-support.css">`,
      }) +
      renderNav({ active: "home" }) +
      BODY +
      renderFooter(),
    );
  });
}
