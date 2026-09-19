# Unit links

Every nameplate carries a unit-specific QR beside the faucet and name. The plate has no
lettered domain or separate serial. Printed instructions can use the full-domain URL.

## The two strings

| Reader | String | Where it comes from |
|---|---|---|
| Written instructions | `homesodamachine.com/0001` | `_nameplate_dimensions.unit_url_plain` |
| Nameplate QR | `HTTPS://HOSM.US/0001` | `_nameplate_dimensions.unit_url` |

## Twenty characters

A QR's size is a version, and each version is four modules wider per side than the last:
Version 1 is 21×21, Version 2 is 25×25, Version 3 is 29×29. Within a fixed footprint a lower
version is a wider module, and a module on this plate is extrusions of a
0.4 mm nozzle.

Length and mode set the version. QR alphanumeric mode packs 5.5 bits per character and covers
`0-9 A-Z space $ % * + - . / :`. One lowercase letter puts the whole payload in byte mode at 8
bits per character. `HTTPS://`, the dot, the slash and the digits are all in the alphanumeric
set; scheme and host are case-insensitive and a digits-only path has no case, so the uppercase
form resolves to the same address.

Measured with the `qrcode` package in `tools/cad-venv`, at 15% error correction:

| Payload | Mode | Version |
|---|---|---|
| `HTTPS://HOSM.US/0001` | alphanumeric | **1 — 21×21** |
| `https://hosm.us/0001` | byte | 2 — 25×25 |
| `HTTPS://HOMESODAMACHINE.COM/0001` | alphanumeric | 2 — 25×25 |
| `https://homesodamachine.com/0001` | byte | 3 — 29×29 |

`HTTPS://` is 8, `HOSM.US` is 7, the slash is 1, the serial is 4. Twenty, against a Version 1
capacity of twenty at 15% error correction. No character is left over.

What stands on that:

- **The serial is four characters.** Letters and digits cost the same in alphanumeric mode —
  four uppercase alphanumerics is 36⁴ = 1,679,616 units, four digits is 10,000. A fifth
  character does not fit.
- **The payload is uppercase.** An encoder handed the lowercase form emits a Version 2 code
  that scans.
- **No `www`, no trailing slash, no query string.**

## The redirect

`hosm.us` serves nothing of its own. `web/lib/short-host.js` answers every request whose Host
is `hosm.us` or `www.hosm.us` with a 301 to the same path on `https://homesodamachine.com`,
carrying path and query through untouched. It is mounted in `web/server.js` ahead of the body
parser and every route, so the short host is answered before anything else is consulted, and
`/.well-known/` stands outside it — certificate validation answers about the host it was asked
about. `web/tests/short-host.test.js` holds it.

Both hosts are one Render service, so the redirect runs in the same process that answers the
canonical host. `hosm.us` is attached to it, verified and certificated, and answers:
`https://hosm.us/0001` is one hop to `https://homesodamachine.com/0001`.

`render.yaml` carries no `domains:` key — the service's custom domains are dashboard-managed.
Service `srv-d7oqj0og4nts7384fgog` carries four. The workspace plan includes two, which
`homesodamachine.com` and `www.homesodamachine.com` hold; the third is $0.25 per month, and the
fourth came with it, because Render adds a `www` redirect to an apex at no charge. What it asks
of the registrar, and what `hosm.us` now answers with on Namecheap's standard nameservers:

| Host | Record | Value |
|---|---|---|
| `@` | A | `216.24.57.1` |
| `www` | CNAME | `homesodamachine.onrender.com` |

Render's edge routes by Host and answers a Host it does not know with a 403, so neither the
redirect nor a certificate challenge reaches anything until the domain is attached there. A
`curl` at the canonical host bearing a `Host:` header for another one proves nothing about this
module; `web/tests/short-host.test.js` against a local boot is what holds it.

## The unit route

`/0001` sits at the root of `homesodamachine.com`, sharing that root with the static landing
mount, so it matches four digits and nothing else rather than as a catch-all.

`web/lib/unit.js` serves registered serials. `/0001` opens the machine overview, including
the soda machine, faucet, install kit, and customer-supplied equipment. `/0001/get-started`
holds the preparation checklist and the seven installation steps, linked to the matching
pages of the install guide. `/0001/guides` opens the quick start, install guide, and care pages.
The checklist's checkmarks are stored in the browser under the serial. Unregistered serials
return 404. `web/tests/unit.test.js` checks the route and its links, and
`web/tests/browser/unit.browser.js` checks navigation, the checklist, and phone layouts.

## The code on the plate

The production [nameplate](/hardware/printed-parts/enclosure/nameplate/README.md) is
104.53 × 38 mm. Its code has 21 × 21 active modules at 1.1 mm, making a 23.1 mm active
square within a 31.9 mm quiet-zone square. White modules are flush in the black PET-GF face.
The artwork prints face-down in two colours through the first 0.72 mm. The QR has 0.02 mm
joins at diagonal-only white contacts to keep the CAD colour interface manifold.

`nameplate.py` explicitly selects version 1, error correction M and alphanumeric mode;
serials outside 0001–9999 are rejected. Its self-test checks the code size and clear field.
A finished physical plate must scan to its own unit before and after installation.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/nameplate/_nameplate_dimensions.py`
