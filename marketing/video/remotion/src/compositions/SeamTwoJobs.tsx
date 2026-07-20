import React from "react";
import { AbsoluteFill, Audio, interpolate, Sequence, useCurrentFrame } from "remotion";
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { sfx } from "../sound/cues";
import { cold, margin, shop, tracking, type as T, VIDEO } from "../style/tokens";
import { grotesk, mono } from "../style/fonts";
import { countTo, drawOn, fadeIn } from "../motion/draw";
import { eases } from "../motion/easings";
import { BlueprintGrid } from "../components/shop/BlueprintGrid";
import { RevisionStamp } from "../components/shop/RevisionStamp";
import { HandNote } from "../components/shop/HandNote";
import { ColdField } from "../components/cold/ColdField";
import { Bubbles } from "../components/cold/Bubbles";
import { Specimen } from "../components/shared/Specimen";

/**
 * "The Seam Does Two Jobs" — the faucet episode. Seven beats, cross-dissolved.
 *
 * FACTS are centralised in F (provisional, from research) so the verified
 * fact-check sheet lands in one edit. Captions are added once the script is set.
 */
// Facts verified against the repo + git history (fact-check pass).
const F = {
  valve: "harvested self-closing valve",
  valvePrice: "≈ $32", // Westbrass A2031-NL-62, bom.md (current authoritative SKU)
  attempts: 21, // PET-CF print attempts 1–21, print-log.md
  quote: "beautiful everywhere except where the supports were", // Derek, print-log.md:208
  joint: "20 mm slip-fit", // two 20 mm joints along the gooseneck, touch_flo_shell.py:305
  display: "1.47″ touchscreen", // Waveshare ESP32-S3-Touch-LCD-1.47, bom.md:18
  material: "PET-CF",
  lastPrint: "mid-June", // last print activity 2026-06-14
};

const W = VIDEO.width;
const H = VIDEO.height;
const TRANS = 18;
const B = { open: 300, valve: 420, fight: 540, split: 480, pivot: 420, converge: 480, close: 330 };
export const SEAM_DURATION = Object.values(B).reduce((a, b) => a + b, 0) - 6 * TRANS;

const Svg: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <AbsoluteFill>
    <svg width="100%" height="100%" viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="none">
      {children}
    </svg>
  </AbsoluteFill>
);

const Kicker: React.FC<{ text: string; color?: string; at?: number }> = ({ text, color = cold.teal, at = 0 }) => {
  const f = useCurrentFrame() - at;
  return (
    <div
      style={{
        position: "absolute",
        left: margin,
        bottom: margin,
        fontFamily: mono,
        color,
        fontSize: T.kicker,
        letterSpacing: tracking.kicker,
        textTransform: "uppercase",
        opacity: fadeIn(f, 0, 12),
      }}
    >
      {text}
    </div>
  );
};

/* ---------------- B1 — COLD OPEN ---------------- */
const BeatOpen: React.FC = () => (
  <AbsoluteFill style={{ backgroundColor: cold.bg2 }}>
    <ColdField />
    <Specimen src="assets/faucet/assembly.png" size={880} cy="46%" push={0.09} glow="rgba(46,197,192,0.30)" fade={26} />
    <Bubbles count={16} />
    <Kicker text="Episode 02 · The Faucet" at={12} />
  </AbsoluteFill>
);

/* ---------------- B2 — THE JOB (the valve) ---------------- */
const BeatValve: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ opacity: fadeIn(f, 0, 18) }}>
      <BlueprintGrid />
      <Specimen src="assets/faucet/valve.png" size={560} cx="32%" cy="52%" glow="rgba(127,212,255,0.22)" fade={16} />
      <Svg>
        <path d="M 560 500 L 980 430" fill="none" stroke={shop.dim} strokeWidth={2} {...drawOn(f, { start: 24, duration: 16 })} />
        <path d="M 560 640 L 980 720" fill="none" stroke={shop.dim} strokeWidth={2} {...drawOn(f, { start: 40, duration: 16 })} />
      </Svg>
      <div style={{ position: "absolute", left: 1000, top: 405, width: 720, opacity: fadeIn(f, 36, 12) }}>
        <div style={{ fontFamily: mono, color: shop.cyan, fontSize: T.leader, letterSpacing: tracking.leader }}>
          {`A real ${F.valve}, ${F.valvePrice}`}
        </div>
      </div>
      <div style={{ position: "absolute", left: 1000, top: 690, width: 760, opacity: fadeIn(f, 52, 12) }}>
        <div style={{ fontFamily: grotesk, color: shop.ink, fontSize: T.h2, fontWeight: 700, lineHeight: 1.02, letterSpacing: -0.5 }}>
          The shell has one job:
          <br /> make it look finished.
        </div>
      </div>
    </AbsoluteFill>
  );
};

/* ---------------- B3 — THE SURFACE FIGHT ---------------- */
const BeatFight: React.FC = () => {
  const f = useCurrentFrame();
  const n = Math.round(countTo(f, { start: 10, duration: 44 }, F.attempts));
  const quoteO = fadeIn(f, 150, 22);
  // rotate-and-drop: a piece rotates so its "ugly" face lands on the bed line
  const rot = interpolate(f, [70, 120], [-28, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: eases.settle });
  return (
    <AbsoluteFill style={{ opacity: fadeIn(f, 0, 18) }}>
      <BlueprintGrid />
      {/* attempt counter */}
      <div style={{ position: "absolute", left: margin, top: margin }}>
        <div style={{ fontFamily: mono, color: shop.cyan, fontSize: T.kicker, letterSpacing: tracking.kicker, textTransform: "uppercase" }}>
          Print attempts
        </div>
        <div style={{ fontFamily: grotesk, color: shop.ink, fontSize: 150, fontWeight: 800, lineHeight: 1, fontVariantNumeric: "tabular-nums" }}>
          {String(n).padStart(2, "0")}
        </div>
      </div>
      {/* rotate-and-drop piece over a bed line */}
      <Specimen src="assets/faucet/shell-bottom.png" size={440} cx="70%" cy="44%" rotate={rot} push={0} glow="rgba(127,212,255,0.18)" fade={14} />
      <Svg>
        <line x1={1090} y1={720} x2={1620} y2={720} stroke={shop.dim} strokeWidth={2.5} opacity={fadeIn(f, 60, 10)} />
        {[0, 1, 2, 3, 4, 5, 6, 7].map((i) => (
          <line key={i} x1={1100 + i * 66} y1={720} x2={1080 + i * 66} y2={742} stroke={shop.dim} strokeWidth={1.4} opacity={fadeIn(f, 66, 10)} />
        ))}
        <text x={1355} y={772} textAnchor="middle" fontFamily={mono} fontSize={T.leader} fill={shop.dim} opacity={fadeIn(f, 74, 10)}>
          the print bed
        </text>
      </Svg>
      {/* the quote — the craft peak */}
      <div style={{ position: "absolute", left: margin, right: margin, bottom: 150, opacity: quoteO }}>
        <div style={{ fontFamily: grotesk, color: shop.ink, fontSize: 68, fontWeight: 700, lineHeight: 1.08, maxWidth: 1400, letterSpacing: -0.5 }}>
          &ldquo;{F.quote}.&rdquo;
        </div>
      </div>
    </AbsoluteFill>
  );
};

/* ---------------- B4 — THE SPLIT (three pieces) ---------------- */
const piece = (name: string, src: string, px: number, py: number) => ({ name, src, px, py });
const PIECES = [
  piece("TOP", "assets/faucet/shell-top.png", 1360, 320),
  piece("MIDDLE", "assets/faucet/shell-middle.png", 980, 500),
  piece("BOTTOM", "assets/faucet/shell-bottom.png", 600, 700),
];
const BeatSplit: React.FC = () => {
  const f = useCurrentFrame();
  const whole = interpolate(f, [0, 40, 70], [0, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ opacity: fadeIn(f, 0, 16) }}>
      <BlueprintGrid />
      {/* one piece, then it becomes three */}
      <Specimen src="assets/faucet/shell-whole.png" size={620} cx="50%" cy="50%" push={0} opacity={whole} fade={10} />
      {PIECES.map((p, i) => (
        <Specimen
          key={p.name}
          src={p.src}
          size={430}
          cx={`${p.px}px`}
          cy={`${p.py}px`}
          push={0}
          fade={14}
          at={64 + i * 12}
          glow="rgba(127,212,255,0.20)"
        />
      ))}
      <Svg>
        {PIECES.map((p, i) => (
          <text
            key={p.name}
            x={p.px}
            y={p.py + 150}
            textAnchor="middle"
            fontFamily={mono}
            fontSize={T.leader}
            letterSpacing={tracking.stamp}
            fill={shop.cyan}
            opacity={fadeIn(f, 92 + i * 12, 12)}
          >
            {p.name}
          </text>
        ))}
        {/* two joint callouts between the three pieces */}
        <g opacity={fadeIn(f, 150, 16)}>
          <circle cx={1170} cy={410} r={9} fill="none" stroke={shop.weld} strokeWidth={2.5} />
          <path d="M 1170 410 L 1330 250" fill="none" stroke={shop.weld} strokeWidth={2} />
          <text x={1345} y={250} fontFamily={mono} fontSize={T.leader} fill={shop.weldSoft}>{`${F.joint} joint`}</text>
          <circle cx={790} cy={600} r={9} fill="none" stroke={shop.weld} strokeWidth={2.5} />
          <path d="M 790 600 L 470 700" fill="none" stroke={shop.weld} strokeWidth={2} />
          <text x={250} y={706} fontFamily={mono} fontSize={T.leader} fill={shop.weldSoft}>{`${F.joint} joint`}</text>
        </g>
      </Svg>
      <div style={{ position: "absolute", left: margin, top: margin, opacity: fadeIn(f, 8, 14) }}>
        <div style={{ fontFamily: mono, color: shop.cyan, fontSize: T.kicker, letterSpacing: tracking.kicker, textTransform: "uppercase" }}>
          Split for clean surfaces
        </div>
        <div style={{ fontFamily: grotesk, color: shop.ink, fontSize: 78, fontWeight: 800, lineHeight: 1, letterSpacing: -1 }}>
          One part → three
        </div>
      </div>
    </AbsoluteFill>
  );
};

/* ---------------- B5 — BUTTON → SCREEN ---------------- */
const BeatPivot: React.FC = () => {
  const f = useCurrentFrame();
  const strike = interpolate(f, [70, 92], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: eases.settle });
  const arrow = drawOn(f, { start: 100, duration: 20 });
  return (
    <AbsoluteFill style={{ opacity: fadeIn(f, 0, 16) }}>
      <BlueprintGrid />
      <div style={{ position: "absolute", left: margin, top: margin, opacity: fadeIn(f, 6, 12) }}>
        <div style={{ fontFamily: mono, color: shop.cyan, fontSize: T.kicker, letterSpacing: tracking.kicker, textTransform: "uppercase" }}>
          The control moved
        </div>
        <div style={{ fontFamily: grotesk, color: shop.ink, fontSize: 78, fontWeight: 800, lineHeight: 1, letterSpacing: -1 }}>
          Button → screen
        </div>
      </div>
      <Svg>
        {/* LEFT: the button, struck out */}
        <g opacity={fadeIn(f, 20, 14)}>
          <circle cx={470} cy={620} r={95} fill="rgba(12,27,44,0.6)" stroke={shop.ink} strokeWidth={3} />
          <circle cx={470} cy={620} r={62} fill="none" stroke={shop.dim} strokeWidth={2} />
          <text x={470} y={770} textAnchor="middle" fontFamily={mono} fontSize={T.leader} fill={shop.dim}>a push button</text>
        </g>
        <g opacity={strike}>
          <line x1={360} y1={520} x2={580} y2={720} stroke={shop.weld} strokeWidth={6} strokeLinecap="round" />
        </g>
        {/* arrow */}
        <path d="M 610 620 L 1120 620" fill="none" stroke={shop.dim} strokeWidth={3} markerEnd="" {...arrow} />
        <g opacity={fadeIn(f, 118, 8)}>
          <path d="M 1100 600 L 1140 620 L 1100 640" fill="none" stroke={shop.dim} strokeWidth={3} />
        </g>
        {/* RIGHT: the screen, glowing */}
        <g opacity={fadeIn(f, 128, 16)}>
          <rect x={1210} y={520} width={300} height={210} rx={18} fill="rgba(46,197,192,0.14)" stroke={cold.teal} strokeWidth={3} />
          <rect x={1240} y={556} width={240} height={40} rx={6} fill={cold.teal} opacity={0.5} />
          <rect x={1240} y={614} width={180} height={30} rx={6} fill={cold.teal} opacity={0.32} />
          <rect x={1240} y={660} width={210} height={30} rx={6} fill={cold.teal} opacity={0.32} />
          <text x={1360} y={790} textAnchor="middle" fontFamily={mono} fontSize={T.leader} fill={cold.teal}>{`a ${F.display}`}</text>
        </g>
      </Svg>
    </AbsoluteFill>
  );
};

/* ---------------- B6 — CONVERGENCE (the payoff) ---------------- */
const BeatConverge: React.FC = () => {
  const f = useCurrentFrame();
  // two shell-wall brackets slide together around the screen
  const gap = interpolate(f, [40, 110], [220, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: eases.settle });
  const seamGlow = fadeIn(f, 108, 16);
  const titleO = fadeIn(f, 150, 24);
  const cx = 960;
  const cy = 470;
  return (
    <AbsoluteFill style={{ backgroundColor: cold.bg2 }}>
      <ColdField />
      <Bubbles count={10} />
      <Svg>
        {/* the captured screen */}
        <g opacity={fadeIn(f, 20, 16)}>
          <rect x={cx - 120} y={cy - 82} width={240} height={164} rx={14} fill="rgba(46,197,192,0.16)" stroke={cold.teal} strokeWidth={3} />
          <rect x={cx - 92} y={cy - 52} width={184} height={30} rx={6} fill={cold.teal} opacity={0.5} />
          <rect x={cx - 92} y={cy - 8} width={140} height={24} rx={6} fill={cold.teal} opacity={0.34} />
          <rect x={cx - 92} y={cy + 30} width={160} height={24} rx={6} fill={cold.teal} opacity={0.34} />
        </g>
        {/* upper shell wall bracket, sliding down */}
        <g transform={`translate(0 ${-gap})`}>
          <path
            d={`M ${cx - 220} ${cy - 150} L ${cx + 220} ${cy - 150} L ${cx + 220} ${cy - 96} L ${cx + 150} ${cy - 96} L ${cx + 150} ${cy - 110} L ${cx - 150} ${cy - 110} L ${cx - 150} ${cy - 96} L ${cx - 220} ${cy - 96} Z`}
            fill="rgba(20,40,60,0.55)"
            stroke={cold.chill}
            strokeWidth={3}
          />
        </g>
        {/* lower shell wall bracket, sliding up */}
        <g transform={`translate(0 ${gap})`}>
          <path
            d={`M ${cx - 220} ${cy + 150} L ${cx + 220} ${cy + 150} L ${cx + 220} ${cy + 96} L ${cx + 150} ${cy + 96} L ${cx + 150} ${cy + 110} L ${cx - 150} ${cy + 110} L ${cx - 150} ${cy + 96} L ${cx - 220} ${cy + 96} Z`}
            fill="rgba(20,40,60,0.55)"
            stroke={cold.chill}
            strokeWidth={3}
          />
        </g>
        {/* the seam glows */}
        <line x1={cx - 150} y1={cy - 103} x2={cx + 150} y2={cy - 103} stroke={shop.weld} strokeWidth={5} opacity={seamGlow} />
        <line x1={cx - 150} y1={cy + 103} x2={cx + 150} y2={cy + 103} stroke={shop.weld} strokeWidth={5} opacity={seamGlow} />
        <text x={cx} y={cy + 250} textAnchor="middle" fontFamily={mono} fontSize={T.leader} letterSpacing={tracking.stamp} fill={shop.weldSoft} opacity={seamGlow}>
          THE SEAM CLAMPS THE SCREEN · NO FASTENERS
        </text>
      </Svg>
      {/* the title reveal */}
      <AbsoluteFill style={{ justifyContent: "flex-end", alignItems: "center" }}>
        <div style={{ marginBottom: 120, textAlign: "center", opacity: titleO }}>
          <div style={{ fontFamily: grotesk, color: cold.chill, fontSize: 108, fontWeight: 800, lineHeight: 1, letterSpacing: -1.5 }}>
            The Seam Does Two Jobs
          </div>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

/* ---------------- B7 — HONEST CLOSER ---------------- */
const BeatClose: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ backgroundColor: cold.bg2 }}>
      <ColdField />
      <Specimen src="assets/faucet/assembly.png" size={820} cy="48%" push={0.05} glow="rgba(46,197,192,0.26)" fade={22} />
      <Bubbles count={12} />
      <HandNote text={`still not finished — one surface defect left, nothing printed since ${F.lastPrint}`} at={40} width={620} />
      <RevisionStamp at={70} rev="—" part="FAUCET" sheet="PROTO" />
    </AbsoluteFill>
  );
};

export const SeamTwoJobs: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: cold.bg2 }}>
      <TransitionSeries>
        <TransitionSeries.Sequence durationInFrames={B.open}><BeatOpen /></TransitionSeries.Sequence>
        <TransitionSeries.Transition presentation={fade()} timing={linearTiming({ durationInFrames: TRANS })} />
        <TransitionSeries.Sequence durationInFrames={B.valve}><BeatValve /></TransitionSeries.Sequence>
        <TransitionSeries.Transition presentation={fade()} timing={linearTiming({ durationInFrames: TRANS })} />
        <TransitionSeries.Sequence durationInFrames={B.fight}><BeatFight /></TransitionSeries.Sequence>
        <TransitionSeries.Transition presentation={fade()} timing={linearTiming({ durationInFrames: TRANS })} />
        <TransitionSeries.Sequence durationInFrames={B.split}><BeatSplit /></TransitionSeries.Sequence>
        <TransitionSeries.Transition presentation={fade()} timing={linearTiming({ durationInFrames: TRANS })} />
        <TransitionSeries.Sequence durationInFrames={B.pivot}><BeatPivot /></TransitionSeries.Sequence>
        <TransitionSeries.Transition presentation={fade()} timing={linearTiming({ durationInFrames: TRANS })} />
        <TransitionSeries.Sequence durationInFrames={B.converge}><BeatConverge /></TransitionSeries.Sequence>
        <TransitionSeries.Transition presentation={fade()} timing={linearTiming({ durationInFrames: TRANS })} />
        <TransitionSeries.Sequence durationInFrames={B.close}><BeatClose /></TransitionSeries.Sequence>
      </TransitionSeries>

      {/* sound cues, absolute-timed to the beat boundaries */}
      <Sequence from={276}><Audio src={sfx.whoosh} volume={0.4} /></Sequence>
      <Sequence from={740}><Audio src={sfx.ding} volume={0.4} /></Sequence>
      <Sequence from={2064}><Audio src={sfx.whoosh} volume={0.45} /></Sequence>
      <Sequence from={2214}><Audio src={sfx.sting} volume={0.6} /></Sequence>
      <Sequence from={2602}><Audio src={sfx.stampThud} volume={0.7} /></Sequence>
    </AbsoluteFill>
  );
};
