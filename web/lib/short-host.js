// The short host. `hosm.us` is the host a nameplate QR encodes, and it serves
// nothing of its own: every request it receives is redirected to the same path
// on `homesodamachine.com`, which is the host a person reads off the same plate.
//
// The two strings are on the plate for different readers and are the length they
// are for that reason — `HTTPS://HOSM.US/0001` is twenty characters, which is a
// Version 1 QR, the smallest there is. `future/unit-links.md` carries the budget.
//
// Both hosts are custom domains on one Render service, so this redirect runs in
// the same process that answers the canonical host. A request arrives here
// already terminated at Render's edge under the short host's own certificate.

const CANONICAL_ORIGIN = "https://homesodamachine.com";

// `www` is included because a scanner or a typist may reach for it, not because
// anything emits it. It costs a DNS record and nothing here.
const SHORT_HOSTS = new Set(["hosm.us", "www.hosm.us"]);

// `/.well-known/` stands outside the redirect. Certificate validation and any
// other host-scoped protocol answers about the host it was asked about, and a
// redirect to a different host answers about the wrong one.
const WELL_KNOWN = "/.well-known/";

export function mountShortHost(app) {
  app.use((req, res, next) => {
    const host = (req.hostname || "").toLowerCase();
    if (!SHORT_HOSTS.has(host)) return next();
    if (req.path.startsWith(WELL_KNOWN)) return next();

    // `originalUrl` is the raw request target — path and query, already
    // percent-encoded — so the redirect carries both through untouched.
    // A permanent redirect caches indefinitely by default; an hour keeps the
    // saved round trip within a session and leaves the target movable.
    res.set("Cache-Control", "public, max-age=3600");
    res.redirect(301, CANONICAL_ORIGIN + req.originalUrl);
  });
}
