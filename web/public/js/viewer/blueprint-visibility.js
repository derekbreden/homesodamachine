// An opaque component-ID image determines which complete components Blueprint draws.
import * as THREE from 'three';

function setIdColor(_renderer, _scene, _camera, _geometry, ink) {
  const id = this.userData.componentId;
  ink.uniforms.componentColor.value.set(id & 255, (id >> 8) & 255, (id >> 16) & 255).multiplyScalar(1 / 255);
  ink.uniformsNeedUpdate = true;
}

export function createBlueprintExposure() {
  const idScene = new THREE.Scene(), proxies = new WeakMap();
  const ink = new THREE.ShaderMaterial({
    uniforms: { componentColor: { value: new THREE.Vector3() } },
    vertexShader: `
      #include <clipping_planes_pars_vertex>
      void main() {
        vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
        gl_Position = projectionMatrix * mvPosition;
        #include <clipping_planes_vertex>
      }`,
    fragmentShader: `
      uniform vec3 componentColor;
      #include <clipping_planes_pars_fragment>
      void main() {
        #include <clipping_planes_fragment>
        gl_FragColor = vec4(componentColor, 1.0);
      }`,
    side: THREE.DoubleSide, blending: THREE.NoBlending, clipping: true,
  });
  const target = new THREE.WebGLRenderTarget(1, 1, { minFilter: THREE.NearestFilter, magFilter: THREE.NearestFilter });
  const size = new THREE.Vector2(), color = new THREE.Color();
  let pixels, busy = false, closed = false;

  function dispose() {
    closed = true;
    if (busy) return;
    ink.dispose();
    target.dispose();
    pixels = null;
  }

  async function exposedComponents(renderer, camera, solids, owner, current) {
    const names = [null], ids = new Map();
    busy = true;
    try {
      for (const solid of solids) {
        if (!solid.visible) continue;
        const name = owner(solid);
        let id = ids.get(name);
        if (!id) { id = names.length; names.push(name); ids.set(name, id); }
        let proxy = proxies.get(solid);
        if (!proxy) {
          proxy = new THREE.Mesh(solid.geometry, ink);
          proxy.matrixAutoUpdate = false;
          proxy.onBeforeRender = setIdColor;
          proxies.set(solid, proxy);
        }
        solid.updateWorldMatrix(true, false);
        proxy.matrix.copy(solid.matrixWorld);
        proxy.matrixWorldNeedsUpdate = true;
        proxy.geometry = solid.geometry;
        proxy.userData.componentId = id;
        idScene.add(proxy);
      }
      renderer.getDrawingBufferSize(size);
      target.setSize(size.x, size.y);
      const previous = renderer.getRenderTarget(), alpha = renderer.getClearAlpha();
      renderer.getClearColor(color);
      try {
        renderer.setRenderTarget(target);
        renderer.setClearColor(0, 0);
        renderer.render(idScene, camera);
      } finally {
        renderer.setRenderTarget(previous);
        renderer.setClearColor(color, alpha);
        idScene.clear();
      }
      const length = size.x * size.y * 4;
      if (pixels?.length !== length) pixels = new Uint8Array(length);
      await renderer.readRenderTargetPixelsAsync(target, 0, 0, size.x, size.y, pixels);
      const seen = new Uint8Array(names.length);
      let slice = performance.now();
      for (let start = 0; start < length; start += 262144) {
        if (closed || !current()) return null;
        const end = Math.min(length, start + 262144);
        for (let i = start; i < end; i += 4) seen[pixels[i] | pixels[i + 1] << 8 | pixels[i + 2] << 16] = 1;
        if (performance.now() - slice >= 4 && end < length) {
          await new Promise(resolve => setTimeout(resolve, 0));
          slice = performance.now();
        }
      }
      return new Set(names.filter((_name, id) => id && seen[id]));
    } finally {
      busy = false;
      if (closed) dispose();
    }
  }
  return { exposedComponents, dispose };
}
