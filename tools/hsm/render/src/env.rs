//! The environment a surface reflects, baked once per process: eleven levels of the studio room,
//! each blurrier than the last, as three.js's PMREMGenerator bakes them for the viewer
//! (shaders/env.wgsl). Levels 0–4 are the mips of one cube, 256 down to 16; levels 5–10 are six
//! more 16² cubes of rising blur, held as one cube array.

use bytemuck::{Pod, Zeroable};
use wgpu::util::DeviceExt;

const SIZES: [u32; 11] = [256, 128, 64, 32, 16, 16, 16, 16, 16, 16, 16];
/// The angular blur of each level, in radians (PMREMGenerator `_createPlanes`).
const SIGMAS: [f64; 11] = [
    0.0,
    1.0 / 128.0,
    1.0 / 64.0,
    1.0 / 32.0,
    1.0 / 16.0,
    0.125,
    0.215,
    0.35,
    0.446,
    0.526,
    0.582,
];
/// The blur `fromScene(room, 0.03)` gives the sharp level before the chain is built.
const SCENE_SIGMA: f64 = 0.03;
const MAX_SAMPLES: usize = 20;
const FORMAT: wgpu::TextureFormat = wgpu::TextureFormat::Rgba16Float;
/// Each step's parameters sit at their own uniform offset.
const STRIDE: u64 = 256;

const SOURCE: &str = include_str!("shaders/env.wgsl");

/// The dodecahedron's vertices PMREMGenerator turns its pole through, one per level.
fn pole(i: usize) -> [f64; 3] {
    let phi = (1.0 + 5f64.sqrt()) / 2.0;
    let inv = 1.0 / phi;
    [
        [-phi, inv, 0.0],
        [phi, inv, 0.0],
        [-inv, 0.0, phi],
        [inv, 0.0, phi],
        [0.0, phi, -inv],
        [0.0, phi, inv],
        [-1.0, 1.0, -1.0],
        [1.0, 1.0, -1.0],
        [-1.0, 1.0, 1.0],
        [1.0, 1.0, 1.0],
    ][i % 10]
}

#[repr(C)]
#[derive(Clone, Copy, Pod, Zeroable)]
struct Params {
    size: u32,
    samples: u32,
    latitudinal: u32,
    pad: u32,
    pole: [f32; 4],
    step: [f32; 4],
    weights: [[f32; 4]; 5],
}

impl Params {
    fn room() -> Params {
        Params {
            size: SIZES[0],
            ..Params::zeroed()
        }
    }

    /// `_halfBlur`: the kernel is laid out in the input level's pixels, three sigmas wide.
    fn half_blur(sigma: f64, size_in: u32, size_out: u32, latitudinal: bool, pole: [f64; 3]) -> Params {
        let pixels = (size_in - 1) as f64;
        let radians_per_pixel = std::f64::consts::PI / (2.0 * pixels);
        let sigma_pixels = sigma / radians_per_pixel;
        let samples = (1 + (3.0 * sigma_pixels).floor() as usize).min(MAX_SAMPLES);
        let mut weights = [0f64; MAX_SAMPLES];
        let mut sum = 0.0;
        for (i, w) in weights.iter_mut().enumerate() {
            let x = i as f64 / sigma_pixels;
            *w = (-x * x / 2.0).exp();
            if i == 0 {
                sum += *w;
            } else if i < samples {
                sum += 2.0 * *w;
            }
        }
        let mut packed = [[0f32; 4]; 5];
        for (i, w) in weights.iter().enumerate() {
            packed[i / 4][i % 4] = (w / sum) as f32;
        }
        Params {
            size: size_out,
            samples: samples as u32,
            latitudinal: latitudinal as u32,
            pad: 0,
            pole: [pole[0] as f32, pole[1] as f32, pole[2] as f32, 0.0],
            step: [radians_per_pixel as f32, 0.0, 0.0, 0.0],
            weights: packed,
        }
    }
}

/// One full chain of levels: the baked one, or the ping-pong it is blurred through.
struct Chain {
    main: wgpu::Texture,
    extra: wgpu::Texture,
}

impl Chain {
    fn new(device: &wgpu::Device, label: &str) -> Chain {
        let texture = |size: u32, layers: u32, mips: u32| {
            device.create_texture(&wgpu::TextureDescriptor {
                label: Some(label),
                size: wgpu::Extent3d {
                    width: size,
                    height: size,
                    depth_or_array_layers: layers,
                },
                mip_level_count: mips,
                sample_count: 1,
                dimension: wgpu::TextureDimension::D2,
                format: FORMAT,
                usage: wgpu::TextureUsages::TEXTURE_BINDING | wgpu::TextureUsages::STORAGE_BINDING,
                view_formats: &[],
            })
        };
        Chain {
            main: texture(256, 6, 5),
            extra: texture(16, 36, 1),
        }
    }

    /// Where a level lives: a mip of the main cube, or a cube's six layers of the array.
    fn place(&self, level: usize) -> (&wgpu::Texture, u32, u32) {
        if level < 5 {
            (&self.main, level as u32, 0)
        } else {
            (&self.extra, 0, 6 * (level as u32 - 5))
        }
    }

    fn view(&self, level: usize, dimension: wgpu::TextureViewDimension) -> wgpu::TextureView {
        let (texture, mip, layer) = self.place(level);
        texture.create_view(&wgpu::TextureViewDescriptor {
            dimension: Some(dimension),
            base_mip_level: mip,
            mip_level_count: Some(1),
            base_array_layer: layer,
            array_layer_count: Some(6),
            ..Default::default()
        })
    }
}

pub struct Environment {
    /// Levels 0–4, as one cube's mips.
    pub main: wgpu::TextureView,
    /// Levels 5–10, as six cubes.
    pub extra: wgpu::TextureView,
}

struct Step {
    params: Params,
    /// None for the room itself.
    source: Option<(bool, usize)>,
    target: (bool, usize),
}

pub fn bake(device: &wgpu::Device, queue: &wgpu::Queue) -> Environment {
    let module = device.create_shader_module(wgpu::ShaderModuleDescriptor {
        label: Some("env"),
        source: wgpu::ShaderSource::Wgsl(SOURCE.into()),
    });
    let pipeline = |entry: &str| {
        device.create_compute_pipeline(&wgpu::ComputePipelineDescriptor {
            label: Some(entry),
            layout: None,
            module: &module,
            entry_point: Some(entry),
            compilation_options: Default::default(),
            cache: None,
        })
    };
    let room = pipeline("room");
    let blur = pipeline("blur");
    let sampler = device.create_sampler(&wgpu::SamplerDescriptor {
        label: Some("env"),
        mag_filter: wgpu::FilterMode::Linear,
        min_filter: wgpu::FilterMode::Linear,
        ..Default::default()
    });

    // `true` is the baked chain, `false` the ping-pong.
    let mut steps = vec![Step {
        params: Params::room(),
        source: None,
        target: (true, 0),
    }];
    let blur_level = |steps: &mut Vec<Step>, from: usize, to: usize, sigma: f64, pole: [f64; 3]| {
        steps.push(Step {
            params: Params::half_blur(sigma, SIZES[from], SIZES[to], true, pole),
            source: Some((true, from)),
            target: (false, to),
        });
        steps.push(Step {
            params: Params::half_blur(sigma, SIZES[to], SIZES[to], false, pole),
            source: Some((false, to)),
            target: (true, to),
        });
    };
    blur_level(&mut steps, 0, 0, SCENE_SIGMA, [0.0, 1.0, 0.0]);
    let n = SIGMAS.len();
    for i in 1..n {
        let sigma = (SIGMAS[i] * SIGMAS[i] - SIGMAS[i - 1] * SIGMAS[i - 1]).sqrt();
        blur_level(&mut steps, i - 1, i, sigma, pole(n - i - 1));
    }

    let mut bytes = vec![0u8; steps.len() * STRIDE as usize];
    for (i, s) in steps.iter().enumerate() {
        let at = i * STRIDE as usize;
        bytes[at..at + size_of::<Params>()].copy_from_slice(bytemuck::bytes_of(&s.params));
    }
    let uniforms = device.create_buffer_init(&wgpu::util::BufferInitDescriptor {
        label: Some("env params"),
        contents: &bytes,
        usage: wgpu::BufferUsages::UNIFORM,
    });

    let baked = Chain::new(device, "env");
    let ping = Chain::new(device, "env ping");
    let chain = |which: bool| if which { &baked } else { &ping };
    let mut encoder = device.create_command_encoder(&wgpu::CommandEncoderDescriptor { label: Some("env") });
    for (i, s) in steps.iter().enumerate() {
        let target = chain(s.target.0).view(s.target.1, wgpu::TextureViewDimension::D2Array);
        let source = s.source.map(|(w, l)| chain(w).view(l, wgpu::TextureViewDimension::Cube));
        let params = wgpu::BufferBinding {
            buffer: &uniforms,
            offset: i as u64 * STRIDE,
            size: wgpu::BufferSize::new(size_of::<Params>() as u64),
        };
        let pipeline = if source.is_some() { &blur } else { &room };
        let mut entries = vec![
            wgpu::BindGroupEntry {
                binding: 2,
                resource: wgpu::BindingResource::TextureView(&target),
            },
            wgpu::BindGroupEntry {
                binding: 3,
                resource: wgpu::BindingResource::Buffer(params),
            },
        ];
        if let Some(source) = &source {
            entries.push(wgpu::BindGroupEntry {
                binding: 0,
                resource: wgpu::BindingResource::TextureView(source),
            });
            entries.push(wgpu::BindGroupEntry {
                binding: 1,
                resource: wgpu::BindingResource::Sampler(&sampler),
            });
        }
        let group = device.create_bind_group(&wgpu::BindGroupDescriptor {
            label: None,
            layout: &pipeline.get_bind_group_layout(0),
            entries: &entries,
        });
        let mut pass = encoder.begin_compute_pass(&wgpu::ComputePassDescriptor {
            label: None,
            timestamp_writes: None,
        });
        pass.set_pipeline(pipeline);
        pass.set_bind_group(0, &group, &[]);
        let groups = s.params.size.div_ceil(8);
        pass.dispatch_workgroups(groups, groups, 6);
    }
    queue.submit([encoder.finish()]);

    Environment {
        main: baked.main.create_view(&wgpu::TextureViewDescriptor {
            dimension: Some(wgpu::TextureViewDimension::Cube),
            ..Default::default()
        }),
        extra: baked.extra.create_view(&wgpu::TextureViewDescriptor {
            dimension: Some(wgpu::TextureViewDimension::CubeArray),
            ..Default::default()
        }),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn kernels_fit_and_normalise() {
        for i in 1..SIGMAS.len() {
            let sigma = (SIGMAS[i] * SIGMAS[i] - SIGMAS[i - 1] * SIGMAS[i - 1]).sqrt();
            for (from, to) in [(SIZES[i - 1], SIZES[i]), (SIZES[i], SIZES[i])] {
                let p = Params::half_blur(sigma, from, to, true, pole(0));
                assert!(p.samples >= 1 && p.samples as usize <= MAX_SAMPLES);
                let w: Vec<f32> = p.weights.iter().flatten().copied().collect();
                let total = w[0] + 2.0 * w[1..p.samples as usize].iter().sum::<f32>();
                assert!((total - 1.0).abs() < 1e-5, "level {i}: {total}");
            }
        }
    }
}
