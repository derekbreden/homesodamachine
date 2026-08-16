// Inline figures for the Updates feed, keyed by the `{{fig:name}}` line that
// pulls them into a post.
//
// Each figure is an SVG written against the shell's own custom properties, so
// it carries the site's palette rather than its own. The drawing language is
// the nav glyphs': no fill, 2px strokes, round caps and joins. Line weight
// carries emphasis — var(--accent) is the live thing, var(--text-2) is context,
// var(--text-3) is superseded.
//
// State is never colour alone. A pass/fail mark carries a glyph and sits in a
// labelled group, so the figure reads the same to a deuteranope, for whom the
// shell's --ok and --err are 2.8 ΔE apart.
//
// Dimensions in these drawings are to scale against a stated scale bar. The
// numbers are the repository's, frozen at the post's date.

const A = 'stroke-linecap="round" stroke-linejoin="round" fill="none"';

// Engineering dimension line: extension ticks at both ends, value above.
function dim(x1, y1, x2, y2, label, side = "top") {
  const mx = (x1 + x2) / 2, my = (y1 + y2) / 2;
  const t = 4;
  const vert = x1 === x2;
  const ticks = vert
    ? `<path d="M${x1 - t} ${y1} L${x1 + t} ${y1} M${x2 - t} ${y2} L${x2 + t} ${y2}" stroke="var(--text-3)" stroke-width="1"/>`
    : `<path d="M${x1} ${y1 - t} L${x1} ${y1 + t} M${x2} ${y2 - t} L${x2} ${y2 + t}" stroke="var(--text-2)" stroke-width="1"/>`;
  const text = vert
    ? `<text x="${mx + 10}" y="${my}" class="uf-dim" dominant-baseline="middle">${label}</text>`
    : `<text x="${mx}" y="${side === "top" ? my - 7 : my + 15}" class="uf-dim" text-anchor="middle">${label}</text>`;
  return `<path d="M${x1} ${y1} L${x2} ${y2}" stroke="var(--text-2)" stroke-width="1"/>${ticks}${text}`;
}

// ── Two machines, to scale in plan ───────────────────────────────────────────
// 0.46 px per mm. Kitchen 317 × 375, thin 223 × 481.
const TWO_MACHINES = `
<svg viewBox="0 0 520 350" class="uf" role="img" aria-label="Plan view of both machines to scale, seen from above with the cabinet's back wall along the top: the counter machine 317 mm wide by 375 mm deep, the thin machine 223 mm wide by 481 mm deep.">
  <text x="60" y="22" class="uf-title">Counter</text>
  <text x="60" y="38" class="uf-sub">the original tree</text>
  <text x="310" y="22" class="uf-title uf-live">Thin</text>
  <text x="310" y="38" class="uf-sub">forked 26 July</text>

  <path d="M40 56 L480 56" stroke="var(--border)" stroke-width="1"/>
  <text x="480" y="50" class="uf-dim" text-anchor="end">cabinet back wall</text>

  <rect x="60" y="56" width="146" height="173" rx="3" stroke="var(--text-2)" stroke-width="2" ${A}/>
  <rect x="310" y="56" width="103" height="221" rx="3" stroke="var(--accent)" stroke-width="2" ${A}/>

  ${dim(60, 249, 206, 249, "317 mm wide")}
  ${dim(310, 297, 413, 297, "223 mm wide")}
  ${dim(222, 56, 222, 229, "375 deep")}
  ${dim(429, 56, 429, 277, "481 deep")}

  <text x="133" y="147" class="uf-lab" text-anchor="middle">0.119 m²</text>
  <text x="361" y="171" class="uf-lab uf-live" text-anchor="middle">0.107 m²</text>

  <path d="M60 330 L152 330" stroke="var(--text-2)" stroke-width="1"/>
  <path d="M60 326 L60 334 M152 326 L152 334" stroke="var(--text-2)" stroke-width="1"/>
  <text x="160" y="334" class="uf-dim">200 mm</text>
</svg>`;

// ── The water path, before and after ─────────────────────────────────────────
// Stroke weight is the bore: 3/8 inch runs heavy, 1/4 inch runs light.
function waterNode(x, label, sub) {
  return `<circle cx="${x}" cy="70" r="5" fill="var(--bg)" stroke="var(--text-2)" stroke-width="2"/>
    <text x="${x}" y="52" class="uf-lab" text-anchor="middle">${label}</text>
    ${sub ? `<text x="${x}" y="94" class="uf-sub" text-anchor="middle">${sub}</text>` : ""}`;
}
const WATER_PATH = `
<svg viewBox="0 0 620 250" class="uf" role="img" aria-label="The internal water line before and after: a 3/8 inch run with a 3/8 inch flavor tee becomes a quarter-inch run throughout, with 3/8 inch surviving only as two short stubs at the pump's moulded barbs.">
  <text x="16" y="20" class="uf-title">Before</text>
  <g transform="translate(0,-8)">
    <path d="M80 70 L520 70" stroke="var(--text-3)" stroke-width="7" ${A}/>
    ${waterNode(80, "backflow", "")}
    ${waterNode(230, "flare→barb", "3/8")}
    ${waterNode(380, "tee", "3/8 · flavor")}
    ${waterNode(520, "pump", "")}
    <text x="300" y="118" class="uf-sub" text-anchor="middle">3/8 inch silicone, end to end</text>
  </g>

  <text x="16" y="150" class="uf-title uf-live">After</text>
  <g transform="translate(0,122)">
    <path d="M80 70 L200 70" stroke="var(--text-3)" stroke-width="7" ${A}/>
    <path d="M200 70 L470 70" stroke="var(--accent)" stroke-width="3" ${A}/>
    <path d="M470 70 L520 70" stroke="var(--text-3)" stroke-width="7" ${A}/>
    ${waterNode(80, "backflow", "")}
    ${waterNode(200, "two-fitting stack", "→ 1/4")}
    ${waterNode(380, "union tee", "1/4 · flavor")}
    ${waterNode(520, "pump", "moulded barbs")}
    <text x="335" y="118" class="uf-sub uf-live" text-anchor="middle">1/4 inch from the preventer to the pump</text>
    <text x="495" y="28" class="uf-sub" text-anchor="middle">stub</text>
  </g>
</svg>`;

// ── The solder-paste gap ─────────────────────────────────────────────────────
// 330 surface-mount lead pads, 22 across. A filled square has a paste opening;
// a hollow one does not.
function pasteGrid(total, missing, cols, x0, y0, s, gap) {
  let out = "";
  for (let i = 0; i < total; i++) {
    const c = i % cols, r = (i / cols) | 0;
    const x = x0 + c * (s + gap), y = y0 + r * (s + gap);
    out += i < missing
      ? `<rect x="${x}" y="${y}" width="${s}" height="${s}" rx="1" stroke="var(--warn)" stroke-width="1.2" fill="none"/>`
      : `<rect x="${x}" y="${y}" width="${s}" height="${s}" rx="1" fill="var(--text-3)"/>`;
  }
  return out;
}
const PASTE_PADS = `
<svg viewBox="0 0 620 300" class="uf" role="img" aria-label="330 surface-mount lead pads drawn as squares. 148 of them, drawn hollow, had no opening in the exported paste layer.">
  ${pasteGrid(330, 148, 30, 42, 40, 13, 5)}
  <text x="42" y="26" class="uf-lab">330 surface-mount lead pads</text>

  <g transform="translate(42,258)">
    <rect x="0" y="-10" width="13" height="13" rx="1" stroke="var(--warn)" stroke-width="1.2" fill="none"/>
    <text x="22" y="0" class="uf-lab">148 — no paste opening</text>
    <rect x="230" y="-10" width="13" height="13" rx="1" fill="var(--text-3)"/>
    <text x="252" y="0" class="uf-lab">182 — opening present</text>
  </g>
  <text x="42" y="286" class="uf-sub">Nine integrated circuits would have been placed onto bare metal.</text>
</svg>`;

// ── Three boards and a phone ─────────────────────────────────────────────────
function chip(x, y, w, h, title, sub, live) {
  const c = live ? "var(--accent)" : "var(--text-2)";
  return `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="6" stroke="${c}" stroke-width="2" ${A}/>
    <text x="${x + w / 2}" y="${y + (sub ? h / 2 - 4 : h / 2 + 4)}" class="uf-lab" text-anchor="middle" fill="${c}">${title}</text>
    ${sub ? `<text x="${x + w / 2}" y="${y + h / 2 + 14}" class="uf-sub" text-anchor="middle">${sub}</text>` : ""}`;
}
const THREE_BOARDS = `
<svg viewBox="0 0 620 260" class="uf" role="img" aria-label="The main controller sits between a configuration touchscreen with a rotary knob, a small round flavor display, and an iPhone over Bluetooth.">
  ${chip(230, 100, 160, 60, "main controller", "flow, pumps, valves", true)}
  ${chip(30, 20, 150, 56, "config screen", "round, rotary knob")}
  ${chip(440, 20, 150, 56, "flavor display", "round")}
  ${chip(230, 200, 160, 48, "iPhone", "")}

  <path d="M180 48 L205 48 Q215 48 215 60 L215 118 Q215 130 228 130" stroke="var(--text-3)" stroke-width="1.5" ${A}/>
  <path d="M440 48 L415 48 Q405 48 405 60 L405 118 Q405 130 392 130" stroke="var(--text-3)" stroke-width="1.5" ${A}/>
  <path d="M310 162 L310 198" stroke="var(--text-3)" stroke-width="1.5" ${A}/>

  <text x="196" y="96" class="uf-sub" text-anchor="middle">serial</text>
  <text x="424" y="96" class="uf-sub" text-anchor="middle">serial</text>
  <text x="322" y="184" class="uf-sub">Bluetooth</text>
</svg>`;

// ── The flavor manifold, absorbed ────────────────────────────────────────────
const MANIFOLD_ABSORBED = `
<svg viewBox="0 0 620 300" class="uf" role="img" aria-label="Six separate printed carriers become features of the enclosure's front-top piece: two valve panels and two pump trays printed in its own material.">
  <text x="30" y="22" class="uf-title">Before — six printed carriers</text>
  <g>
    <rect x="30" y="40" width="94" height="40" rx="4" stroke="var(--text-3)" stroke-width="2" ${A}/>
    <text x="77" y="64" class="uf-sub" text-anchor="middle">flavor module</text>
    <rect x="136" y="40" width="70" height="40" rx="4" stroke="var(--text-3)" stroke-width="2" ${A}/>
    <text x="171" y="64" class="uf-sub" text-anchor="middle">tray ×3</text>
    <rect x="218" y="40" width="86" height="40" rx="4" stroke="var(--text-3)" stroke-width="2" ${A}/>
    <text x="261" y="64" class="uf-sub" text-anchor="middle">pump case</text>
  </g>

  <path d="M330 60 L372 60 M362 52 L372 60 L362 68" stroke="var(--text-3)" stroke-width="1.5" ${A}/>

  <text x="396" y="22" class="uf-title uf-live">After — one piece</text>
  <rect x="396" y="40" width="194" height="150" rx="6" stroke="var(--accent)" stroke-width="2" ${A}/>
  <text x="493" y="60" class="uf-lab uf-live" text-anchor="middle">front-top</text>
  <rect x="412" y="72" width="78" height="46" rx="3" stroke="var(--accent)" stroke-width="1.2" ${A} opacity="0.75"/>
  <rect x="498" y="72" width="78" height="46" rx="3" stroke="var(--accent)" stroke-width="1.2" ${A} opacity="0.75"/>
  <text x="451" y="99" class="uf-sub" text-anchor="middle">valve panel</text>
  <text x="537" y="99" class="uf-sub" text-anchor="middle">valve panel</text>
  <rect x="412" y="128" width="78" height="44" rx="3" stroke="var(--accent)" stroke-width="1.2" ${A} opacity="0.75"/>
  <rect x="498" y="128" width="78" height="44" rx="3" stroke="var(--accent)" stroke-width="1.2" ${A} opacity="0.75"/>
  <text x="451" y="154" class="uf-sub" text-anchor="middle">pump tray</text>
  <text x="537" y="154" class="uf-sub" text-anchor="middle">pump tray</text>

  <text x="30" y="118" class="uf-lab">Eight solenoids and both pumps</text>
  <text x="30" y="138" class="uf-lab">shipped on their own carriers.</text>
  <text x="30" y="170" class="uf-sub">Nothing ships under a valve now,</text>
  <text x="30" y="188" class="uf-sub">and nothing is billed for one.</text>
  <text x="396" y="214" class="uf-sub">Printed wall to wall in the piece's</text>
  <text x="396" y="230" class="uf-sub">own material. The manifold lifts out</text>
  <text x="396" y="246" class="uf-sub">as one body, across eight parted</text>
  <text x="396" y="262" class="uf-sub">joints, with the carbonator still</text>
  <text x="396" y="278" class="uf-sub">pressurised.</text>
</svg>`;

// ── What the vessel was, six times ───────────────────────────────────────────
// Silhouettes in the order they were live. Only the last one is still in the
// build; the rest are drawn in the weight of things no longer here.
function vesselCell(cx, name, when, shape, live) {
  const c = live ? "var(--accent)" : "var(--text-3)";
  const nameCls = live ? "uf-lab uf-live" : "uf-sub";
  return `<g stroke="${c}" stroke-width="${live ? 2 : 1.5}" ${A}>${shape(cx, c)}</g>
    <text x="${cx}" y="152" class="${nameCls}" text-anchor="middle">${name}</text>
    <text x="${cx}" y="168" class="uf-dim" text-anchor="middle">${when}</text>`;
}
const VESSEL_SHAPES = `
<svg viewBox="0 34 620 176" class="uf" role="img" aria-label="Six vessel geometries in the order they were live: a welded round cylinder, an off-the-shelf air tank, a racetrack body rolled from sheet, a printed plastic sphere, two press-formed half-shells, and finally a commodity stainless tube capped with two laser-cut discs.">
  ${vesselCell(62, "welded tube", "March", (x) => `<rect x="${x - 20}" y="52" width="40" height="66" rx="4"/><path d="M${x - 20} 62 Q${x} 70 ${x + 20} 62"/>`)}
  ${vesselCell(158, "air tank", "16 Apr", (x) => `<rect x="${x - 32}" y="68" width="64" height="34" rx="17"/><path d="M${x + 32} 85 L${x + 40} 85"/>`)}
  ${vesselCell(254, "racetrack", "Apr", (x) => `<rect x="${x - 34}" y="65" width="68" height="40" rx="20"/><path d="M${x - 14} 65 L${x - 14} 105 M${x + 14} 65 L${x + 14} 105"/>`)}
  ${vesselCell(350, "printed sphere", "17–23 Apr", (x) => `<circle cx="${x}" cy="85" r="30"/><path d="M${x - 8} 55 L${x + 8} 55"/>`)}
  ${vesselCell(446, "half-shells", "Apr", (x) => `<path d="M${x} 55 A30 30 0 0 1 ${x} 115"/><path d="M${x - 3} 55 A30 30 0 0 0 ${x - 3} 115"/><path d="M${x - 1} 55 L${x - 1} 115"/>`)}
  ${vesselCell(542, "tube + discs", "24 Apr", (x) => `<rect x="${x - 21}" y="60" width="42" height="50"/><rect x="${x - 26}" y="52" width="52" height="9" rx="2"/><rect x="${x - 26}" y="109" width="52" height="9" rx="2"/>`, true)}

  <path d="M40 190 L560 190" stroke="var(--border)" stroke-width="1"/>
  <path d="M552 186 L560 190 L552 194" stroke="var(--border)" stroke-width="1" ${A}/>
  <text x="542" y="184" class="uf-dim" text-anchor="middle">kept</text>
</svg>`;

// ── The first hour on a bench ────────────────────────────────────────────────
// Two labelled groups, each row carrying its own glyph. Position and mark say
// which side a row is on; colour only agrees with them.
const TICK = `<path d="M0 4 L3 7.5 L9 -1" stroke="var(--ok)" stroke-width="2" ${A}/>`;
const CROSS = `<path d="M0 0 L8 8 M8 0 L0 8" stroke="var(--err)" stroke-width="2" ${A}/>`;
function benchRows(items, x, y, mark) {
  return items.map((t, i) =>
    `<g transform="translate(${x},${y + i * 22})">${mark}</g>
     <text x="${x + 18}" y="${y + i * 22 + 8}" class="uf-lab">${t}</text>`).join("");
}
const BENCH = `
<svg viewBox="0 0 620 300" class="uf" role="img" aria-label="Ten subsystems answered on the bench; five did not. Every one that did not is on the same I²C bus.">
  <rect x="20" y="20" width="290" height="262" rx="8" stroke="var(--border)" stroke-width="1" fill="none"/>
  <rect x="326" y="20" width="274" height="262" rx="8" stroke="var(--border)" stroke-width="1" fill="none"/>

  <text x="40" y="44" class="uf-title">Answered — 10</text>
  <text x="346" y="44" class="uf-title">Unreachable — 5</text>

  ${benchRows([
    "power rails", "the microcontroller", "USB-C flashing",
    "WiFi — 15 networks", "RS485 loopback — 6 of 6", "buzzer",
    "status LEDs", "gas divider — 3020 mV", "compressor interlock",
    "both pump drivers, on a real pump",
  ], 40, 62, TICK)}

  ${benchRows([
    "I/O expander 1", "I/O expander 2", "real-time clock",
    "12 valve outputs", "10 reed inputs",
  ], 346, 62, CROSS)}

  <path d="M346 190 L580 190" stroke="var(--border)" stroke-width="1"/>
  <text x="346" y="212" class="uf-sub">All five sit on one I²C bus.</text>
  <text x="346" y="232" class="uf-sub">The drill file carried 135 holes</text>
  <text x="346" y="250" class="uf-sub">where the board had 152 vias —</text>
  <text x="346" y="268" class="uf-sub">partial-span vias were dropped.</text>
</svg>`;

// ── The whole span, in things that happened ──────────────────────────────────
// Days from 2026-03-07, the first commit, to 2026-08-15, across 540px. Every
// mark carries a <title>, so the ones without a drawn label are still readable
// on hover; the seven carrying labels are the physical inflections.
const T_X = (d) => +(40 + (d / 161) * 540).toFixed(1);
const MARKS = [
  [0, "The repo opens on a machine already pouring under the sink"],
  [15, "Production printer, workbench and the domain", "Printer and workshop", "up"],
  [37, "Handheld fiber laser welder arrives"],
  [41, "An ice maker is torn down and its refrigerant circuit traced", "Ice maker opened", "down"],
  [48, "The vessel settles on tube and discs; stock ordered"],
  [53, "homesodamachine.com goes live"],
  [57, "The first of forty NPT threads is hand-tapped", "First thread tapped", "up"],
  [58, "First video published"],
  [63, "First clean carbon-fibre faucet shell, on the ninth attempt"],
  [68, "Ten laser-cut stainless under-counter plates delivered"],
  [84, "The first flavor reservoir holds water with no weep", "Water stays in", "down"],
  [102, "The enclosure is split in two to fit the print bed"],
  [112, "The first PCB fab run is ordered", "First boards ordered", "up"],
  [130, "Ten assembled controller boards ordered"],
  [141, "The hardware tree is forked into a second machine"],
  [149, "The board is powered up; one bus does not answer", "Board on the bench", "down"],
  [159, "The CAD tree gets a build system"],
  [161, "The first enclosure panel prints in glass-filled PET", "Glass fibre", "up"],
];
const MONTHS_T = [[0, "Mar"], [25, "Apr"], [55, "May"], [86, "Jun"], [116, "Jul"], [147, "Aug"]];

const TIMELINE = `
<svg viewBox="0 34 620 176" class="uf" role="img" aria-label="A timeline from 7 March to 15 August 2026 marking eighteen events, from the workshop purchase through the first hand-tapped thread, the first watertight reservoir, the first boards ordered, and the controller board's first hour on a bench.">
  <path d="M40 98 L580 98" stroke="var(--text-3)" stroke-width="1.5" stroke-linecap="round"/>

  ${/* The plain days go down first. Two of them fall within a few days of a
        labelled one, close enough that the dots touch, and a grey circle laid
        over an accented one leaves a wedge of itself showing. */""}
  ${MARKS.filter(([, , label]) => !label).map(([d, title]) =>
    `<g><title>${title}</title>
      <circle cx="${T_X(d)}" cy="98" r="3" fill="var(--text-3)"/></g>`).join("")}

  ${MARKS.filter(([, , label]) => label).map(([d, title, label, side]) => {
    const x = T_X(d);
    const dot = `<g><title>${title}</title>
      <circle cx="${x}" cy="98" r="5" fill="var(--accent)" stroke="var(--bg)" stroke-width="2"/></g>`;
    const anchor = x > 590 ? "end" : x < 40 ? "start" : "middle";
    const tx = anchor === "end" ? x + 6 : x;
    return side === "up"
      ? `${dot}<path d="M${x} 91 L${x} 70" stroke="var(--accent)" stroke-width="1"/>
         <text x="${tx}" y="62" class="uf-lab uf-live" text-anchor="${anchor}">${label}</text>`
      : `${dot}<path d="M${x} 105 L${x} 128" stroke="var(--accent)" stroke-width="1"/>
         <text x="${tx}" y="142" class="uf-lab uf-live" text-anchor="${anchor}">${label}</text>`;
  }).join("")}

  <path d="M40 172 L580 172" stroke="var(--border)" stroke-width="1"/>
  ${MONTHS_T.map(([d, m]) =>
    `<path d="M${T_X(d)} 168 L${T_X(d)} 176" stroke="var(--border)" stroke-width="1"/>
     <text x="${T_X(d)}" y="190" class="uf-dim" text-anchor="middle">${m}</text>`).join("")}
</svg>`;

// ── Fifteen attempts at one part ─────────────────────────────────────────────
// Outcomes as the print log records them. Four states, each with its own glyph,
// so the strip reads without colour.
const PL_GLYPH = {
  fail: `<path d="M-6 -6 L6 6 M6 -6 L-6 6" stroke="var(--err)" stroke-width="2" ${A}/>`,
  part: `<path d="M-7 0 L7 0" stroke="var(--warn)" stroke-width="2.5" ${A}/>`,
  ok: `<path d="M-7 0 L-2 5 L7 -6" stroke="var(--ok)" stroke-width="2.5" ${A}/>`,
  none: `<circle r="4" stroke="var(--text-3)" stroke-width="1.5" fill="none"/>`,
};
const PL = [
  "fail", "fail", "fail", "fail", "part", "none",
  "ok", "fail", "ok",
  "part", "part", "part", "part", "ok", "none",
];
const PRINT_LOG = `
<svg viewBox="0 0 620 170" class="uf" role="img" aria-label="Fifteen print attempts at the faucet shell. The first six produced no part, the seventh worked, the eighth failed when a support tower fused into the faucet, and attempts ten to fifteen printed while the joint clearances were tuned.">
  ${PL.map((state, i) => {
    const x = 30 + i * 38, cx = x + 15;
    return `<rect x="${x}" y="50" width="30" height="30" rx="4"
        stroke="var(--border)" stroke-width="1" fill="none"/>
      <g transform="translate(${cx},65)">${PL_GLYPH[state]}</g>
      <text x="${cx}" y="98" class="uf-dim" text-anchor="middle">${i + 1}</text>`;
  }).join("")}

  <path d="M273 32 L273 46" stroke="var(--text-2)" stroke-width="1"/>
  <text x="273" y="26" class="uf-sub" text-anchor="middle">0.6 mm tungsten-carbide nozzle, 9 May</text>

  <g transform="translate(30,132)">
    <g transform="translate(8,0)">${PL_GLYPH.fail}</g><text x="22" y="4" class="uf-sub">no part</text>
    <g transform="translate(118,0)">${PL_GLYPH.part}</g><text x="132" y="4" class="uf-sub">printed, not right</text>
    <g transform="translate(288,0)">${PL_GLYPH.ok}</g><text x="302" y="4" class="uf-sub">printed clean</text>
    <g transform="translate(418,0)">${PL_GLYPH.none}</g><text x="432" y="4" class="uf-sub">outcome unrecorded</text>
  </g>
</svg>`;

export const FIGURES = {
  "print-log": {
    caption: "Every attempt at the faucet shell inside these four weeks, as the print log records it. Attempts ten to fifteen all produced parts; what was being tuned by then was the fit of the joints, not the printing.",
    svg: PRINT_LOG,
  },
  "timeline": {
    caption: "Eighteen events across 2026, from the first commit on 7 March to 15 August. Hover a mark for the ones without a label.",
    svg: TIMELINE,
  },
  "vessel-shapes": {
    caption: "What the pressure vessel was, in the order it was those things. The last is the one that was ordered.",
    svg: VESSEL_SHAPES,
  },
  "bench": {
    caption: "The controller board's first hour powered up. The fab drilled exactly what it was sent.",
    svg: BENCH,
  },
  "two-machines": {
    caption: "Both machines in plan, to scale. The thin edition gives up 94 mm across the cabinet and takes 106 mm back in depth.",
    svg: TWO_MACHINES,
  },
  "water-path": {
    caption: "The internal water line before and after. Three-eighths survives only as two short stubs, because the pump's barbs are moulded into its head.",
    svg: WATER_PATH,
  },
  "paste-pads": {
    caption: "The exported paste layer covered only rectangular pads. A stencil cut from that file would have left 148 of 330 lead pads dry.",
    svg: PASTE_PADS,
  },
  "three-boards": {
    caption: "One project, three firmware targets, and a phone.",
    svg: THREE_BOARDS,
  },
  "manifold-absorbed": {
    caption: "Six printed carriers become features of the piece above them.",
    svg: MANIFOLD_ABSORBED,
  },
};

export const FIGURE_CSS = `
.up-fig { margin: 1.8rem 0; padding: 0; }
/* A drawing's type scales with its viewBox, so below the width the labels were
   drawn for the figure scrolls in its own track rather than shrinking them. */
.up-fig-scroll { overflow-x: auto; overscroll-behavior-x: contain; max-width: 100%;
  border: 1px solid var(--border); border-radius: 8px; background: var(--surface); }
/* Once it actually scrolls it takes the tab order, and takes the site's ring
   with it rather than the browser's own amber one. */
.up-fig-scroll:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
.up-fig svg.uf { width: 100%; min-width: 34rem; height: auto; display: block; padding: .5rem 0; }
.up-fig img { width: 100%; height: auto; display: block; border-radius: 8px; border: 1px solid var(--border); }
.up-fig figcaption { margin: .6rem 0 0; font-size: .82rem; line-height: 1.5; color: var(--text-2); }

svg.uf text { font-family: inherit; }
svg.uf .uf-title { font-size: 13px; font-weight: 600; fill: var(--text); }
svg.uf .uf-lab { font-size: 12px; fill: var(--text); }
svg.uf .uf-sub { font-size: 11px; fill: var(--text-2); }
svg.uf .uf-dim { font-size: 10px; fill: var(--text-2); font-variant-numeric: tabular-nums; }
svg.uf .uf-live { fill: var(--accent); }
`;
