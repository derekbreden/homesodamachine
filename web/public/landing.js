// Landing-page signup: press, loading, success, and error states.

(function () {
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
        status.textContent = "Thanks — I'll be in touch.";
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
