# One Less Errand

A 100-second animated product film. A repeating can-carrying chore resolves into
one quiet glass at the faucet. The closing choices place the faucet in the
viewer's own kitchen.

## Visual language

1920 × 1080, 30 fps. Bright brand cobalt #1749D1, ice #DCE6FF,
white #FFFFFF, warm neutral #F3F0E8, orange #FF9152. Montserrat.
No navy backgrounds. Large isolated subjects, soft studio lighting, matte
surfaces, controlled metallic highlights, gentle contact shadows. Camera
movement has a purpose and settles for each reveal. Text lives in the parent
composition; scene modules supply pictures only. Safe area: x 90–1830,
y 70–930; captions occupy y 970–1040. Bottom-right stays visually quiet.

## Scene contract

Browser ES modules, with Three.js 0.170 from the site's import map.
Each exports an async factory receiving `{ THREE, width, height, palette }`.
Factories return `{ draw(time, shot), dispose? }`, where `time` is seconds
local to that shot and `shot` is the string below. `draw` returns a canvas;
the caller composites it synchronously in the same browser task. Motion is a
pure function of time, with no animation loop or wall clock. Default canvas is
1920 × 1080. Renderer pixel ratio 1 or 1.25; quality must sustain full video
rendering. Each scene owns its renderer, camera, lights and objects.

`errand-scenes.js` exports `createErrandScenes`. Opaque cobalt canvas.
`product-scenes.js` exports `createProductScenes`. Opaque warm-neutral or
cobalt canvas, matching the shot. All actual faucet geometry comes from the
current assembly mesh payloads. No assembly geometry edits.

## Picture clock

| Start | End | Module / shot | Picture |
|---|---|---|---|
| 0 | 6 | errand / single | One beautiful unbranded can; the small wish |
| 6 | 14 | errand / case | The single can becomes a case; store/cart context |
| 14 | 22 | errand / carry | Case moves through simple car and kitchen silhouettes |
| 22 | 30 | errand / repeat | Shelf fills, empties, and the cycle repeats |
| 30 | 36 | product / reveal | Quiet warm counter, sculpted black faucet, empty glass |
| 36 | 46 | product / under | Cabinet cutaway / under-counter machine context |
| 46 | 53 | product / select | Display / lever detail, flavor selection |
| 53 | 63 | product / pour | Same hero angle, animated schematic pour into glass |
| 63 | 71 | product / sculpted | Sculpted beauty angle, slow controlled camera movement |
| 71 | 79 | product / industrial | Matched Industrial angle |
| 79 | 87 | product / finishes | Both finishes, clean matched changes |
| 87 | 94 | product / four | All four combinations in a considered composition |
| 94 | 100 | parent / closing | Quiet hero moment resolving to brand / film title |

Under-counter context can use a simple cabinet silhouette and the real machine
model if practical. The faucet stays the principal subject; the story does not
repeat the machine tour. Pour is designed CG animation, visibly illustrative.

## Sound

Charon Gemini narration, calm and conversational. The chore has a gently
repeating rhythm; the reveal releases it. Subtle original tonal bed and
restrained tactile accents, with space around narration. No borrowed music.
Stereo 48 kHz WAV, 100 seconds. Mix target approximately -17 LUFS, ceiling
-1.5 dBTP. Parent owns narration editing and the final mix.
