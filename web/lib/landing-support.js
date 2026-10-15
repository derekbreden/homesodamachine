// Supporting film, source acknowledgements and the one-time availability signup.

const PLAY = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M8 5.5v13l10-6.5z"/></svg>';
const ARROW = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M5 12h14m-6-6 6 6-6 6"/></svg>';

export function renderLandingSupport() {
  return `<section class="home-support-film" aria-labelledby="home-support-film-title">
  <div class="home-support-inner home-support-film-grid">
    <div class="home-support-film-media" data-home-film-player>
      <a class="home-support-film-poster" href="https://www.youtube.com/watch?v=pqmQbZIAzfQ" data-home-film-open aria-label="Play One Less Errand, a 36-second animated design preview">
        <img src="/landing/film-poster.webp" width="1440" height="810" loading="lazy" alt="">
        <span class="home-support-film-play" aria-hidden="true">${PLAY}<span>Play film</span></span>
      </a>
    </div>
    <div class="home-support-film-copy">
      <p class="home-support-eyebrow">The short film</p>
      <h2 id="home-support-film-title">One Less Errand.</h2>
      <p class="home-support-film-intro">A familiar routine of carrying cans home, and a different ending: cold soda on tap.</p>
      <p class="home-support-film-meta">Animated design preview <span aria-hidden="true">·</span> 0:36</p>
      <a class="home-support-text-link" href="https://www.youtube.com/watch?v=pqmQbZIAzfQ">Watch on YouTube ${ARROW}</a>
    </div>
  </div>
</section>

<footer class="home-support-footer">
  <div class="home-support-inner">
    <section class="home-support-suppliers" aria-labelledby="home-support-suppliers-title">
      <div class="home-support-suppliers-heading">
        <h2 id="home-support-suppliers-title">Suppliers include</h2>
        <a class="home-support-text-link" href="/cost">Parts &amp; costs ${ARROW}</a>
      </div>
      <ul class="home-support-supplier-list">
        <li>
          <a class="home-support-supplier-logo home-support-supplier-logo--fws" href="https://www.freshwatersystems.com/"><img src="/suppliers/fresh-water-systems.png" width="137" height="48" loading="lazy" alt="Fresh Water Systems"></a>
          <p>Food-grade fittings and tubing.</p>
        </li>
        <li>
          <a class="home-support-supplier-logo home-support-supplier-logo--jlc" href="https://jlcpcb.com/"><img src="/suppliers/jlcpcb.svg" width="141" height="31" loading="lazy" alt="JLCPCB"></a>
          <p>Circuit boards and controller assembly.</p>
        </li>
        <li>
          <a class="home-support-supplier-logo home-support-supplier-logo--scs" href="https://sendcutsend.com/"><img src="/suppliers/sendcutsend.svg" width="169" height="30" loading="lazy" alt="SendCutSend"></a>
          <p>Precision-cut stainless steel parts.</p>
        </li>
        <li>
          <a class="home-support-supplier-logo home-support-supplier-logo--lulu" href="https://www.lulu.com/"><img src="/suppliers/lulu.svg" width="106" height="37" loading="lazy" alt="Lulu"></a>
          <p>The printed installation guide.</p>
        </li>
      </ul>
    </section>

    <section class="home-support-availability" aria-labelledby="home-support-availability-title">
      <div class="home-support-availability-copy">
        <h2 id="home-support-availability-title">When it’s ready.</h2>
        <p>I’ll email you once when you can buy one.<br>No timeline, no other messages.</p>
      </div>
      <div class="home-support-signup">
        <form id="signup">
          <label for="signup-email">Email address</label>
          <div class="home-support-signup-controls">
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

    <div class="home-support-closure">
      <a class="home-support-identity" href="/" aria-label="Home Soda Machine home"><img src="/brand/wordmark-reverse.svg" width="168" height="64" loading="lazy" alt="Home Soda Machine"></a>
      <p>A kitchen appliance in development.</p>
      <nav class="home-support-links" aria-label="Project"><a href="/updates">Follow the build</a><a href="/3d">Explore the design</a></nav>
    </div>
  </div>
</footer>`;
}
