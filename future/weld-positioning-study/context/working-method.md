# Working method for explorers

Every explorer reads this and `shared-context.md`. The coordinator sends each
wave's specific instructions by message; this file holds what stays the same.

## The job

Exploration. The output is a collection of developed possibilities Derek can
understand and think with: possibilities developed, challenged, repaired,
combined, and brought back more useful for that work. No competition, no
winning design, no complete implementation plan. A polished proposal does not
deserve preference over a rough one; a rough one does not deserve preference for
being unusual. Huge unresolved problems are compatible with an idea being worth
bringing back.

Your framing is a way of seeing the **whole** problem, not a subsystem. Every
arrangement you develop connects your viewpoint to the actual gun, wire,
umbilical, tube, endcap, rotator, supports and the way the arrangement is used.
Research whatever components your ideas need.

Take a small number of ideas beyond their first attractive sketch; depth may be
unequal where the ideas demand it. A list of mechanism names with pros and cons
has not done the job. A drawing package or complete parts list is not the goal
either.

**Take it further, break it, fix it.** "It will sway" or "it is too flexible"
is a starting observation. Continue into which motion is free, which force causes
displacement, what happens at each contact, what the reference for "fixed" is,
and whether the support must provide precision continuously or only at certain
moments (setup, dry run, weld, lift-off). A repair might retain a compliance,
control it, temporarily constrain it, or assign precision elsewhere. Point to a
specific conflict in a specific variant; say what a repair changes and what it
leaves uncertain. If you cannot repair it, keep the useful idea and the
unresolved issue visible side by side. Your inability to find a solution is not
proof that a whole family is impossible. Do not hide a serious problem to keep an
idea alive, and do not discard an idea because a serious problem exists.

Preserve an original idea alongside the variants that change it. A replacement
is a branch, not what the originator "must have meant".

Separate Derek's statements, physical facts, manufacturer documentation and
your own assumptions. When an unknown matters, work through plausible
alternatives and label them. Old agent-proposed tolerances, loads, budgets and
geometry are not requirements.

## Showing an arrangement

Show enough mechanism and geometry that Derek can mentally run it: what is
attached to what, what moves relative to what, where the gun and wire are, what
carries the loads, what establishes position, what is free or restrained, what
drives or adjusts each motion, what "fixed" is fixed to, and what happens when a
setting changes. Use sketches, simple motion diagrams, rough dimensions or a
small calculation where they advance that understanding. Label proxies and
assumptions. Elaborate CAD is optional and should not eat the exploration.

Sketches: a simple SVG file (plain lines, arrows and text labels; readable in a
browser, light background) or an ASCII diagram inside the markdown. Use the
orientation scene's frame when it helps: +Z up, tube axis vertical, the dot on
the +X side at the inside corner, tangent along ±Y. The joint is about 232 mm
above the bench on the current rotator feet.

Small calculations can live as `.py` files beside your notes; put the result
and its assumptions in the prose.

## Your files

Your notebook is `future/weld-positioning-study/explorers/<your-name>/`:

- `notebook.md` — your running log: what you tried, what you found, what changed,
  open questions, questions that need Derek's observation. Append each wave.
- `ideas/<short-slug>.md` — one file per materially different arrangement or
  branch, kept current as it develops. A branch that changes an idea gets its own
  file, or its own clearly separated section, so the original stays readable.
  Useful things to make clear, as the idea needs them (not a template to fill):
  the physical idea and what makes it different; how it operates; loads,
  position, freedoms and drives with the reference for "fixed"; what was tried
  to break it and the repairs or branches; printed parts and bought hardware with
  the sourcing evidence that matters; its contribution, its major unresolved
  problems, and which conclusions rest on assumptions or missing measurements.
- `sketches/` — SVG or other sketch files.

Sourcing observations go in `future/weld-positioning-study/sourcing/<your-name>.md`,
one entry per representative part:

```
- **<part>** — <what it does in which idea>
  - Source: <link>  · Observed: 2026-09-28 · Price: $… · Prime: yes/NA
  - Stock/delivery signal: <e.g. "In stock; FREE delivery Wed Sep 30">
  - Volume/interchangeability evidence: <e.g. "2k+ bought past month", "standard 2020 V-slot profile sold by many vendors">
  - Observation vs estimate: <which parts of the above you saw directly>
```

Write only inside the study directory. Do not edit anything else in the repo.

## Browsing

WebSearch and WebFetch are redirected by a hook here; use Derek's Chrome through
the claude-in-chrome tools. Load them in one ToolSearch call:
`select:mcp__claude-in-chrome__tabs_context_mcp,mcp__claude-in-chrome__tabs_create_mcp,mcp__claude-in-chrome__navigate,mcp__claude-in-chrome__get_page_text,mcp__claude-in-chrome__read_page,mcp__claude-in-chrome__find,mcp__claude-in-chrome__javascript_tool,mcp__claude-in-chrome__tabs_close_mcp`

Several agents share this Chrome at once. Call `tabs_context_mcp` once, then
create your **own** tab with `tabs_create_mcp`, pass its tabId on every call, and
never act on another tab. Prefer navigate / get_page_text / find /
javascript_tool over coordinate clicks. Close your tab when you finish a wave.

Read only: never add to cart, buy, sign in, submit a form, accept a dialog or
contact a vendor. Chrome is signed in to Derek's Amazon account (delivering to
Lincoln 68520), so product pages show his real delivery dates. On Amazon only
Prime listings exist for Derek: open a product page, confirm its Prime delivery
signal, and only then read or record it; never read, record or mention a
non-Prime listing. A useful quick check on an Amazon product page:

```js
({price:(document.querySelector('#corePrice_feature_div .a-offscreen, .a-price .a-offscreen')||{}).innerText,
  prime:!!document.querySelector('#primeBadge_feature_div i, i.a-icon-prime, [aria-label*="Prime"]'),
  delivery:(document.querySelector('#mir-layout-DELIVERY_BLOCK, #deliveryBlockMessage')||{}).innerText,
  stock:(document.querySelector('#availability')||{}).innerText,
  bought:(document.querySelector('#social-proofing-faceout-title-tk_bought')||{}).innerText,
  reviews:(document.querySelector('#acrCustomerReviewText')||{}).innerText})
```

Other vendors (McMaster-Carr, Misumi, 80/20, OpenBuilds, Thorlabs, B&H, camera
and lighting shops, hardware stores, hobby motion and 3D-printer suppliers, and
anything else that fits) are all fair game. If the browser cannot be reached,
continue the conceptual work and mark the claim unverified.

## Repo hooks

A post-write hook in this repo may flag "residue" or "underived measurements".
It is aimed at the repo's current-state product documentation. Read its point.
This study's notes legitimately record break/repair work and labelled rough
estimates, because the study asks for them; keep that content, labelled.

## Reporting back

End each wave with a reply to the coordinator of at most ~500 words: your ideas
(one line each with its file path), what developed most, the biggest open
problems, notable sourcing findings, and anything you think the coordinator
should know about breadth or overlap. The files carry the substance.
