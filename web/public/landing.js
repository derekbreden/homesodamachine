// The film loads on activation; the availability form sends one-time signups.

(function () {
  const player = document.querySelector("[data-home-film-player]");
  const poster = document.querySelector("[data-home-film-open]");
  if (!player || !poster) return;

  poster.addEventListener("click", (event) => {
    // Preserve the anchor's normal open-in-new-tab and no-JavaScript behavior.
    if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    const frame = document.createElement("iframe");
    frame.src = "https://www.youtube-nocookie.com/embed/o3l6Vcl-nLU?rel=0&autoplay=1";
    frame.title = "One Less Errand — Cold Soda on Tap at Home";
    frame.allow = "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share";
    frame.referrerPolicy = "strict-origin-when-cross-origin";
    frame.allowFullscreen = true;
    frame.tabIndex = 0;
    player.replaceChildren(frame);
    frame.focus();
  });
})();

(function () {
  const form = document.getElementById("signup");
  const btn = document.getElementById("signup-btn");
  const status = document.getElementById("status");
  if (!form || !btn || !status) return;

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
        status.textContent = "Thanks — I'll email you when it's available.";
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
})();
