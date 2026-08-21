// Globals the viewer hangs on window. The main one, __hsm, is the headless-render escape hatch:
// web/public/js/viewer/main.js sets it once the module graph has loaded, and the Puppeteer render
// tools (tools/render/render-step.js, render-dxf.js, render-step-side-by-side.js) read it in-page
// to pose the camera and trigger a render. Its shape is load-bearing for those tools.

/**
 * @typedef {Object} HsmGlobal            window.__hsm
 * @property {*} THREE                    the three.js namespace
 * @property {*} renderer                 WebGLRenderer
 * @property {*} scene
 * @property {*} camera
 * @property {*} controls                 OrbitControls
 * @property {(file: string) => Promise<void>} loadStepFile
 * @property {(file: string) => Promise<void>} loadDxfFile
 * @property {*} currentGroup             mounted model group (getter)
 * @property {string|null} mountedStepFile (getter)
 * @property {string|null} mountedDxfFile  (getter)
 * @property {*} [__baseCamera]           the page's own camera, stashed by
 *                                        tools/render/render-step-posed.js: an --ortho picture
 *                                        replaces `camera` with one of its own, and a page
 *                                        drawing many pictures has to mount the next one
 *                                        against the camera scene.js keeps.
 */

// Two flags other modules set on window, read by boot.js:
//   window.__hsmDeploySoft — live.js sets it so boot.js leaves the deploy refresh to the viewer.
//   window.__hsmLiveDebug  — settings.js toggles the live-reload debug panel.
