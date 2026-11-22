// A settled assembly keeps its unmarked color on the GPU so picking only redraws the marks.
import * as THREE from "three";

export function createSelectionFrame(renderer, scene, marks) {
  let texture = null, valid = false;
  const layer = new THREE.Scene();
  layer.add(marks);
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute("position", new THREE.Float32BufferAttribute([-1, -1, 0, 3, -1, 0, -1, 3, 0], 3));
  const material = new THREE.RawShaderMaterial({
    glslVersion: THREE.GLSL3, depthTest: false, depthWrite: false,
    uniforms: { frame: { value: null } },
    vertexShader: `in vec3 position;
      void main() { gl_Position = vec4(position, 1.0); }`,
    fragmentShader: `precision highp float;
      uniform highp sampler2D frame;
      out vec4 pixel;
      void main() { pixel = texelFetch(frame, ivec2(gl_FragCoord.xy), 0); }`,
  });
  const backdrop = new THREE.Mesh(geometry, material);
  backdrop.visible = false;
  backdrop.frustumCulled = false;
  backdrop.layers.enableAll();
  layer.add(backdrop);
  scene.add(layer);

  function release() {
    valid = false;
    texture?.dispose();
    texture = material.uniforms.frame.value = null;
  }

  function draw(camera, worldChanged) {
    // A Find or inspection mark above the picker keeps its usual depth and ordering.
    if (scene.children.some(child => child.visible && child.renderOrder > marks.renderOrder && child.children.length)) {
      valid = false;
      renderer.render(scene, camera);
      return;
    }
    const gl = renderer.getContext();
    const width = gl.drawingBufferWidth, height = gl.drawingBufferHeight;
    if (!width || !height) return;
    if (texture?.image.width !== width || texture.image.height !== height) {
      release();
      texture = new THREE.FramebufferTexture(width, height);
      material.uniforms.frame.value = texture;
    }
    const capture = !valid || worldChanged;
    if (capture) {
      layer.visible = false;
      try {
        renderer.render(scene, camera);
        renderer.copyFramebufferToTexture(texture);
        valid = true;
      } finally {
        layer.visible = true;
      }
      if (!marks.children.some(group => group.children.length)) return;
    }

    // Pick fills and lines ignore depth. Copy the resolved screen colors verbatim and
    // blend the same marks with the assembly's fog and the canvas's usual antialiasing.
    const autoClear = renderer.autoClear;
    backdrop.visible = !capture;
    layer.fog = scene.fog;
    renderer.autoClear = !capture && autoClear;
    try {
      renderer.render(layer, camera);
    } finally {
      renderer.autoClear = autoClear;
      backdrop.visible = false;
    }
  }

  return { layer, draw, release, invalidate() { valid = false; } };
}
