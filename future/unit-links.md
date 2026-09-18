# Unit links

Every plate carries the unit's own address twice: lettered for a person, coded for a phone.
The lettered one is on the plate. The coded one is not — there is no code on the plate, and no
route behind the address it would carry.

## The two strings

| Reader | String | Where it comes from |
|---|---|---|
| A person | `homesodamachine.com/0001` | `_nameplate_dimensions.unit_url_plain` |
| A scanner | `HTTPS://HOSM.US/0001` | owed — no generator emits it |

`hosm.us` is registered. HOme Soda Machine.

## Twenty characters

A QR's size is a version, and each version is four modules wider per side than the last:
Version 1 is 21×21, Version 2 is 25×25, Version 3 is 29×29. Within a fixed footprint a lower
version is a wider module, and a module on this plate is extrusions of a
[0.2 mm](NAMEPLATE_NOZZLE_D) nozzle.

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

## What is owed

### One. The unit route

`/0001` sits at the root of `homesodamachine.com`, sharing that root with the static landing
mount, so it matches four digits and nothing else rather than as a catch-all.

What it serves is open. The nameplate page has the link carrying everything beyond the two
printed documents — warranty, RMA, troubleshooting, BOM, support contact and ongoing care, per
[`unboxing-and-quickstart.md`](/marketing/unboxing-and-quickstart.md). Whether the per-serial
archive at `logs/<serial>/` is reachable from it is an Open item in
[`finish-pack-ship.md`](/hardware/assembly/finish-pack-ship.md).

### Two. The code on the plate

The lettering stands [78.63 mm](LOCKUP_W) × [57.32 mm](STACK_H) on a plate
[104.53 mm](PLATE_W) × [66.07 mm](PLATE_H), and two Ø[5.8 mm](CBORE_D) screw counterbores
stand in what is left at each side, at mid-height.

A Version 1 code is 21 modules of ink, and the standard carries four modules of clear field
around it. The clear field is bare plate and costs no ink:

| Module | Extrusions | Ink | With its clear field |
|---|---|---|---|
| 0.6 mm | 3 | 12.6 mm | 17.4 mm |
| 0.8 mm | 4 | 16.8 mm | 23.2 mm |
| 1.0 mm | 5 | 21.0 mm | 29.0 mm |

The lettering gives up room, or the plate grows.

Two things the geometry answers:

- **Polarity.** A QR is dark modules on a light field, and an inverted code is not read by
  every scanner. On a black plate with white lettering the code inverts the plate's own
  scheme: the dark modules are plate-black, the field around them a white recess — the
  opposite assignment from the type. The print settings put the filament change at the recess
  floor, and a single change there puts white above black across the whole band. Whether both
  filaments are live per-layer through [3.5 mm](INK_FLOOR)–[4.5 mm](NAMEPLATE_T) is read at the
  slicer.
- **Diagonal modules.** Two dark modules that meet at a corner and nowhere else share no
  edge. Each module carries a bleed so diagonal neighbours do.

### Three. The encoder and its check

`qrcode` is in `tools/cad-venv`; `segno` is not. `qrcode.util.optimal_mode()` takes bytes, not
a string.

The check reads three things: the payload is at most twenty characters, every character is in
the QR alphanumeric set, and the code the encoder built reports version 1. A payload that
drifts to lowercase, or to twenty-one characters, still scans.

## What is Derek's

The plate layout that makes room. What `/0001` serves.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/nameplate/_nameplate_dimensions.py`
- `/hardware/printed-parts/enclosure/nameplate/nameplate.py`
