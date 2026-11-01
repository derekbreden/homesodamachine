// These resources belong to the page, across cache-busted STEP loader imports.
import * as THREE from "three";
import { addStudioLighting, BG_COLOR, TONE_EXPOSURE } from "./scene.js";

export const stepRuntime = {
  materials: new Map(),
  finishes: [],
  finishesReady: null,
  finishesVersion: null,
};

let occtPromise = null;
let thumbnails = null;

// Payload-backed models need no STEP parser. A fallback shares one instance.
export function getOcct() {
  if (!occtPromise) {
    occtPromise = new Promise((resolve, reject) => {
      const script = document.createElement("script");
      script.src = "https://cdn.jsdelivr.net/npm/occt-import-js@0.0.23/dist/occt-import-js.js";
      script.onload = () => Promise.resolve().then(() => window.occtimportjs()).then(resolve, reject);
      script.onerror = () => reject(new Error("Couldn't load the STEP parser"));
      document.head.appendChild(script);
    }).catch(error => { occtPromise = null; throw error; });
  }
  return occtPromise;
}

export function getThumbnailRuntime() {
  if (!thumbnails) {
    const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
    renderer.setPixelRatio(1);
    renderer.setClearColor(BG_COLOR);
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = TONE_EXPOSURE;
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, 1, 1, 1000);
    addStudioLighting(scene, renderer);
    thumbnails = { renderer, scene, camera };
  }
  return thumbnails;
}
