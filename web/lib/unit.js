import { renderHead, renderFooter } from "./shell.js";
import { iconSvg } from "../contracts/icons.js";

const UNITS = new Set(["0001"]);
const INSTALL_GUIDE = "/docs/install-guide/install-guide.pdf";
const QUICK_START = "/docs/quickstart-codex/quick-start-codex.pdf";
const PAGES = { "": "Your machine", "get-started": "Get started", guides: "Guides" };
const STEPS = [
  ["Mount the faucet", 5],
  ["Add the cold-water tee", 7],
  ["Match the rear connections", 12],
  ["Prepare the cylinder", 14],
  ["Water, then gas, then power", 16],
  ["Fill both flavors", 19],
  ["Chill. Choose. Pour.", 21],
];

function nav(serial, page) {
  return `<header class="unit-header">
    <a class="unit-brand" href="/" aria-label="Home Soda Machine home"><img src="/brand/mark.svg" width="34" height="34" alt="">HOME SODA MACHINE</a>
    <nav class="unit-nav" aria-label="Machine pages">${Object.entries(PAGES).map(([slug, title]) =>
      `<a href="/${serial}${slug ? `/${slug}` : ""}"${slug === page ? ' aria-current="page"' : ""}>${title}</a>`
    ).join("")}</nav>
    <span class="unit-serial">NO. ${serial}</span>
  </header>`;
}

function overview(serial) {
  return `<main class="unit-main" id="content" tabindex="-1">
    <section class="unit-hero" aria-labelledby="unit-title">
      <div class="unit-copy">
        <span class="unit-kicker">Meet the machine</span>
        <h1 id="unit-title">Your soda machine.</h1>
        <p>Chilled carbonated water and two flavors, poured from the faucet in your kitchen.</p>
        <div class="unit-actions"><a class="unit-action" href="/${serial}/get-started">Get started ${iconSvg("arrow-right")}</a></div>
        <a class="unit-link" href="#included">See what’s included ${iconSvg("arrow-down")}</a>
      </div>
      <figure class="unit-hero-art">
        <div class="unit-orbit" aria-hidden="true"></div>
        <img src="/unit/faucet.webp" width="789" height="740" fetchpriority="high" alt="The soda faucet beside a glass of soda and ice">
        <figcaption class="unit-caption">Select a flavor. Press the lever.</figcaption>
      </figure>
    </section>
    <section class="unit-start" aria-labelledby="unit-first-glass">
      <div><h2 id="unit-first-glass">From the box to your first glass.</h2><p class="unit-small unit-muted">Check the kit, make the connections, and get pouring.</p></div>
      <a class="unit-link" href="/${serial}/get-started">See the seven steps ${iconSvg("arrow-right")}</a>
    </section>
    <section class="unit-items" aria-label="Your equipment">
      <div class="unit-item">${iconSvg("snowflake")}<h3>The soda machine</h3><p>Under the counter. Chills and carbonates the water, and holds both flavors.</p></div>
      <div class="unit-item">${iconSvg("glass-water")}<h3>The faucet</h3><p>Above the counter. Choose a flavor on the display and press the lever to pour.</p></div>
      <div class="unit-item">${iconSvg("cube")}<h3>The install kit</h3><p>Plumbing, regulator, cord, tools, and printed guides for the installation.</p></div>
    </section>
    <details id="included"><summary>What’s included, and what you supply</summary>
      <div class="unit-inventory">
        <div><h3>In the box</h3><ul><li>Soda machine and assembled faucet</li><li>Under-counter plate</li><li>Filtered water line and water tees</li><li>CO₂ regulator and tether</li><li>Collet press and power cord</li><li>Cold kit, quick start, and install guide</li></ul></div>
        <div><h3>Have these ready</h3><ul><li>Filled CO₂ cylinder with CGA-320 connection</li><li>SodaStream-compatible concentrate for both flavors</li><li>Adjustable wrench, cup, and towel</li><li>Second wrench for a braided-hose connection</li><li>Prepared counter opening, cold water, and a grounded 120 V outlet</li></ul></div>
      </div>
    </details>
  </main>`;
}

function setup() {
  return `<main class="unit-main" id="content" tabindex="-1">
    <div class="unit-page-heading"><span class="unit-kicker">Get started</span><h1>Your first glass starts here.</h1><p>Have the kit and your supplies ready, then follow the same seven steps as the printed guide.</p></div>
    <div class="unit-setup-grid">
      <fieldset class="unit-checks"><legend>Before you connect anything</legend>
        <label class="unit-check"><input type="checkbox" name="kit"><span>The kit is unpacked<small>Machine, faucet, and install kit</small></span></label>
        <label class="unit-check"><input type="checkbox" name="supplies"><span>My supplies are ready<small>Filled cylinder, concentrate, wrenches, cup, towel</small></span></label>
        <label class="unit-check"><input type="checkbox" name="location"><span>The location is prepared<small>Counter opening, cabinet space, water, and outlet</small></span></label>
        <a class="unit-link" href="${INSTALL_GUIDE}#page=3" target="_blank" rel="noopener">See the complete preparation list ${iconSvg("arrow-up-right")}</a>
      </fieldset>
      <ol class="unit-route">${STEPS.map(([title, page], i) => `<li><a href="${INSTALL_GUIDE}#page=${page}" target="_blank" rel="noopener"><span class="unit-num" aria-hidden="true">${i + 1}</span><span>${title}</span>${iconSvg("arrow-up-right")}</a></li>`).join("")}</ol>
    </div>
  </main>`;
}

function guides() {
  return `<main class="unit-main" id="content" tabindex="-1">
    <div class="unit-page-heading"><span class="unit-kicker">Keep these handy</span><h1>Guides for your machine.</h1></div>
    <div class="unit-guides">
      <div class="unit-book" aria-hidden="true"><img src="/brand/mark.svg" width="44" height="44" alt=""><b>Install<br>guide</b><span>From the box<br>to your first glass.</span></div>
      <div class="unit-guide-list"><h2>The same guides that came in the box.</h2><p>Open the whole booklet or jump straight to the part you need.</p>
        ${[
          [QUICK_START, "file", "Quick start", "Seven steps on one illustrated sheet"],
          [INSTALL_GUIDE, "book", "Install guide", "24 pages · Both water connections · Care"],
          [`${INSTALL_GUIDE}#page=22`, "droplets", "After installation", "Refilling, cleaning, and first checks"],
        ].map(([href, icon, title, detail]) => `<a class="unit-document" href="${href}" target="_blank" rel="noopener">${iconSvg(icon)}<span>${title}<span class="unit-small unit-muted">${detail}</span></span>${iconSvg("arrow-up-right", "unit-arrow")}</a>`).join("")}
      </div>
    </div>
  </main>`;
}

export function mountUnitRoutes(app) {
  app.get(/^\/(\d{4})(?:\/(get-started|guides))?\/?$/, (req, res, next) => {
    const serial = req.params[0];
    if (!UNITS.has(serial)) return next();
    const page = req.params[1] || "";
    const canonicalPath = `/${serial}${page ? `/${page}` : ""}`;
    if (req.path !== canonicalPath) {
      const query = req.originalUrl.slice(req.path.length);
      return res.redirect(301, canonicalPath + query);
    }
    res.set("Cache-Control", "no-cache");
    res.type("html").send(
      renderHead({
        title: `${PAGES[page]} · ${serial} · Home Soda Machine`,
        fontStylesheet: "https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500&display=swap",
        themeColor: "#101623",
        pageHead: `<meta name="description" content="Your soda machine, what’s included, and seven steps from installation to your first glass.">
<link rel="canonical" href="https://homesodamachine.com${canonicalPath}">
<link rel="stylesheet" href="/css/unit.css">
<script src="/unit.js" defer></script>`,
      }) +
      `<div class="unit-page" data-unit="${serial}"><a class="unit-skip" href="#content">Skip to content</a>` +
      nav(serial, page) +
      (page === "get-started" ? setup() : page === "guides" ? guides() : overview(serial)) +
      `<footer class="unit-footer"><span>HOME SODA MACHINE · ${serial}</span><a class="unit-link" href="/${serial}/guides">Quick start &amp; install guide ${iconSvg("arrow-right")}</a></footer></div>` +
      renderFooter(),
    );
  });
}
