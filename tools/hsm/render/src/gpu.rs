//! The GPU half: one device for the process (Metal on a Mac, Vulkan elsewhere), the viewer's
//! pipelines on it, a scene's arrays uploaded once, and a frame drawn into a 4× multisampled
//! target and read back as RGBA bytes.

use crate::env::{self, Environment};
use crate::scene::{Scene, Segment};
use crate::shadow::ShadowMap;
use anyhow::{Context, Result, anyhow};
use bytemuck::{Pod, Zeroable};
use std::ops::Range;
use std::sync::Mutex;
use wgpu::util::DeviceExt;

/// The viewer's renderer is created `antialias: true`, which is 4× on this Mac.
pub const SAMPLES: u32 = 4;
const COLOR: wgpu::TextureFormat = wgpu::TextureFormat::Rgba8Unorm;
const DEPTH: wgpu::TextureFormat = wgpu::TextureFormat::Depth32Float;
pub const MAX_CLIPS: usize = 8;

const SHADERS: [&str; 4] = [
    include_str!("shaders/common.wgsl"),
    include_str!("shaders/surface.wgsl"),
    include_str!("shaders/line.wgsl"),
    include_str!("shaders/shadow.wgsl"),
];

pub mod flag {
    pub const UNLIT: u32 = 1;
    pub const FRONT_ONLY: u32 = 2;
    pub const BACK_ONLY: u32 = 4;
    pub const NO_FOG: u32 = 8;
}

/// shaders/common.wgsl `View`.
#[repr(C)]
#[derive(Clone, Copy, Pod, Zeroable)]
pub struct ViewUniform {
    pub view_proj: [[f32; 4]; 4],
    pub view: [[f32; 4]; 4],
    pub proj: [[f32; 4]; 4],
    pub eye: [f32; 4],
    pub back: [f32; 4],
    pub screen: [f32; 4],
    pub fog: [f32; 4],
    pub fog_color: [f32; 4],
    pub shadow_center: [f32; 4],
    pub shadow_half: [f32; 4],
    pub clip: [[f32; 4]; MAX_CLIPS],
    pub counts: [u32; 4],
}

/// shaders/common.wgsl `Material`.
#[repr(C)]
#[derive(Clone, Copy, Debug, PartialEq, Pod, Zeroable)]
pub struct Material {
    /// Linear RGB and opacity.
    pub color: [f32; 4],
    /// roughness, metalness, line width in pixels, back-face darkening
    pub params: [f32; 4],
    pub flags: [u32; 4],
}

/// Which of three.js's lists a draw falls in, in the order they are drawn.
#[derive(Clone, Copy, Debug, PartialEq, Eq, PartialOrd, Ord)]
pub enum Layer {
    /// Depth-tested and depth-writing.
    Opaque,
    /// Blended over what is drawn, depth-tested, writing no depth.
    Blend,
    /// Blended over everything, through everything.
    Overlay,
}

#[derive(Clone, Debug)]
pub enum Draw {
    /// One mesh's triangles, in the material at `slot`.
    Surface { mesh: usize, slot: u32 },
    /// A section's cap: one mesh's triangles drawn without the surfaces' depth unit back, so a
    /// solid's cut wins over the coplanar face of a solid it touches, as three.js draws its caps.
    Cap { mesh: usize, slot: u32 },
    /// A run of segments; the instance range carries the bank (see shaders/line.wgsl).
    Lines { instances: Range<u32> },
    Shadow,
}

pub struct Gpu {
    pub device: wgpu::Device,
    pub queue: wgpu::Queue,
    pub adapter: String,
    layout: wgpu::BindGroupLayout,
    sampler: wgpu::Sampler,
    env: Environment,
    surface: [wgpu::RenderPipeline; 3],
    cap: wgpu::RenderPipeline,
    line: [wgpu::RenderPipeline; 3],
    shadow: wgpu::RenderPipeline,
    blank: wgpu::TextureView,
    /// The last frame size's targets, kept for the next picture of that size.
    targets: Mutex<Option<Targets>>,
}

/// What a frame is drawn into and read back out of.
struct Targets {
    width: u32,
    height: u32,
    msaa: wgpu::TextureView,
    depth: wgpu::TextureView,
    resolve: wgpu::Texture,
    resolve_view: wgpu::TextureView,
    readback: wgpu::Buffer,
    row: u32,
}

impl Targets {
    fn new(device: &wgpu::Device, width: u32, height: u32) -> Targets {
        let extent = wgpu::Extent3d {
            width,
            height,
            depth_or_array_layers: 1,
        };
        let target = |format, samples, usage| {
            device.create_texture(&wgpu::TextureDescriptor {
                label: Some("frame"),
                size: extent,
                mip_level_count: 1,
                sample_count: samples,
                dimension: wgpu::TextureDimension::D2,
                format,
                usage,
                view_formats: &[],
            })
        };
        let msaa = target(COLOR, SAMPLES, wgpu::TextureUsages::RENDER_ATTACHMENT);
        let depth = target(DEPTH, SAMPLES, wgpu::TextureUsages::RENDER_ATTACHMENT);
        let resolve = target(COLOR, 1, wgpu::TextureUsages::RENDER_ATTACHMENT | wgpu::TextureUsages::COPY_SRC);
        let row = (width * 4).next_multiple_of(wgpu::COPY_BYTES_PER_ROW_ALIGNMENT);
        let readback = device.create_buffer(&wgpu::BufferDescriptor {
            label: Some("readback"),
            size: row as u64 * height as u64,
            usage: wgpu::BufferUsages::MAP_READ | wgpu::BufferUsages::COPY_DST,
            mapped_at_creation: false,
        });
        Targets {
            width,
            height,
            msaa: msaa.create_view(&Default::default()),
            depth: depth.create_view(&Default::default()),
            resolve_view: resolve.create_view(&Default::default()),
            resolve,
            readback,
            row,
        }
    }
}

/// A scene's arrays on the device.
pub struct SceneBuffers {
    positions: wgpu::Buffer,
    normals: wgpu::Buffer,
    indices: wgpu::Buffer,
    segments: wgpu::Buffer,
    pub bytes: u64,
}

pub struct Frame<'a> {
    pub width: u32,
    pub height: u32,
    pub view: ViewUniform,
    /// The clear colour, as stored: sRGB-encoded, and alpha.
    pub clear: [f64; 4],
    pub materials: &'a [Material],
    /// Two banks of one material slot per mesh: each mesh's own edges, then the selection's.
    pub edge_slot: &'a [u32],
    /// In draw order.
    pub draws: &'a [(Layer, Draw)],
    pub shadow: Option<&'a ShadowMap>,
}

fn blend_over() -> wgpu::BlendState {
    // three.js NormalBlending with straight alpha.
    wgpu::BlendState {
        color: wgpu::BlendComponent {
            src_factor: wgpu::BlendFactor::SrcAlpha,
            dst_factor: wgpu::BlendFactor::OneMinusSrcAlpha,
            operation: wgpu::BlendOperation::Add,
        },
        alpha: wgpu::BlendComponent {
            src_factor: wgpu::BlendFactor::One,
            dst_factor: wgpu::BlendFactor::OneMinusSrcAlpha,
            operation: wgpu::BlendOperation::Add,
        },
    }
}

impl Gpu {
    pub fn new() -> Result<Gpu> {
        let mut desc = wgpu::InstanceDescriptor::new_without_display_handle();
        desc.backends = if cfg!(target_os = "macos") { wgpu::Backends::METAL } else { wgpu::Backends::VULKAN };
        let instance = wgpu::Instance::new(desc);
        let adapter = pollster::block_on(instance.request_adapter(&wgpu::RequestAdapterOptions {
            power_preference: wgpu::PowerPreference::HighPerformance,
            ..Default::default()
        }))
        .context("no GPU adapter")?;
        let name = adapter.get_info().name;
        let (device, queue) = pollster::block_on(adapter.request_device(&wgpu::DeviceDescriptor {
            label: Some("hsm render"),
            required_limits: adapter.limits(),
            memory_hints: wgpu::MemoryHints::MemoryUsage,
            ..Default::default()
        }))
        .context("no GPU device")?;
        // A validation error is reported by the frame's own error scope; an uncaught one is a bug
        // in this crate, and is logged rather than taking the daemon down with it.
        device.on_uncaptured_error(std::sync::Arc::new(|e| eprintln!("hsm render: wgpu: {e}")));

        let env = env::bake(&device, &queue);
        let source: String = SHADERS.concat();
        let module = device.create_shader_module(wgpu::ShaderModuleDescriptor {
            label: Some("render"),
            source: wgpu::ShaderSource::Wgsl(source.into()),
        });
        let vis = wgpu::ShaderStages::VERTEX | wgpu::ShaderStages::FRAGMENT;
        let storage = |binding| wgpu::BindGroupLayoutEntry {
            binding,
            visibility: vis,
            ty: wgpu::BindingType::Buffer {
                ty: wgpu::BufferBindingType::Storage { read_only: true },
                has_dynamic_offset: false,
                min_binding_size: None,
            },
            count: None,
        };
        let texture = |binding, view_dimension| wgpu::BindGroupLayoutEntry {
            binding,
            visibility: vis,
            ty: wgpu::BindingType::Texture {
                sample_type: wgpu::TextureSampleType::Float { filterable: true },
                view_dimension,
                multisampled: false,
            },
            count: None,
        };
        let layout = device.create_bind_group_layout(&wgpu::BindGroupLayoutDescriptor {
            label: Some("frame"),
            entries: &[
                wgpu::BindGroupLayoutEntry {
                    binding: 0,
                    visibility: vis,
                    ty: wgpu::BindingType::Buffer {
                        ty: wgpu::BufferBindingType::Uniform,
                        has_dynamic_offset: false,
                        min_binding_size: wgpu::BufferSize::new(size_of::<ViewUniform>() as u64),
                    },
                    count: None,
                },
                storage(1),
                texture(2, wgpu::TextureViewDimension::Cube),
                texture(3, wgpu::TextureViewDimension::CubeArray),
                wgpu::BindGroupLayoutEntry {
                    binding: 4,
                    visibility: vis,
                    ty: wgpu::BindingType::Sampler(wgpu::SamplerBindingType::Filtering),
                    count: None,
                },
                storage(5),
                storage(6),
                texture(7, wgpu::TextureViewDimension::D2),
            ],
        });
        let pipeline_layout = device.create_pipeline_layout(&wgpu::PipelineLayoutDescriptor {
            label: Some("frame"),
            bind_group_layouts: &[Some(&layout)],
            immediate_size: 0,
        });
        let float3 = |location| {
            [wgpu::VertexAttribute {
                format: wgpu::VertexFormat::Float32x3,
                offset: 0,
                shader_location: location,
            }]
        };
        let (pos_attr, nrm_attr) = (float3(0), float3(1));
        let surface_buffers = [
            Some(wgpu::VertexBufferLayout {
                array_stride: 12,
                step_mode: wgpu::VertexStepMode::Vertex,
                attributes: &pos_attr,
            }),
            Some(wgpu::VertexBufferLayout {
                array_stride: 12,
                step_mode: wgpu::VertexStepMode::Vertex,
                attributes: &nrm_attr,
            }),
        ];
        let make = |label: &str,
                    vs: &str,
                    fs: &str,
                    buffers: &[Option<wgpu::VertexBufferLayout>],
                    layer: Layer,
                    bias: bool,
                    coverage: bool| {
            let (write, compare) = match layer {
                Layer::Opaque => (true, wgpu::CompareFunction::LessEqual),
                Layer::Blend => (false, wgpu::CompareFunction::LessEqual),
                Layer::Overlay => (false, wgpu::CompareFunction::Always),
            };
            device.create_render_pipeline(&wgpu::RenderPipelineDescriptor {
                label: Some(label),
                layout: Some(&pipeline_layout),
                vertex: wgpu::VertexState {
                    module: &module,
                    entry_point: Some(vs),
                    compilation_options: Default::default(),
                    buffers,
                },
                primitive: wgpu::PrimitiveState {
                    topology: wgpu::PrimitiveTopology::TriangleList,
                    front_face: wgpu::FrontFace::Ccw,
                    cull_mode: None,
                    ..Default::default()
                },
                depth_stencil: Some(wgpu::DepthStencilState {
                    format: DEPTH,
                    depth_write_enabled: Some(write),
                    depth_compare: Some(compare),
                    stencil: Default::default(),
                    // polygonOffset(1, 1): surfaces sit a depth unit back of their own edges.
                    bias: if bias {
                        wgpu::DepthBiasState {
                            constant: 1,
                            slope_scale: 1.0,
                            clamp: 0.0,
                        }
                    } else {
                        Default::default()
                    },
                }),
                multisample: wgpu::MultisampleState {
                    count: SAMPLES,
                    mask: !0,
                    alpha_to_coverage_enabled: coverage,
                },
                fragment: Some(wgpu::FragmentState {
                    module: &module,
                    entry_point: Some(fs),
                    compilation_options: Default::default(),
                    targets: &[Some(wgpu::ColorTargetState {
                        format: COLOR,
                        blend: (layer != Layer::Opaque).then(blend_over),
                        write_mask: wgpu::ColorWrites::ALL,
                    })],
                }),
                multiview_mask: None,
                cache: None,
            })
        };
        let surface = [Layer::Opaque, Layer::Blend, Layer::Overlay].map(|layer| {
            make("surface", "vs_surface", "fs_surface", &surface_buffers, layer, layer != Layer::Overlay, false)
        });
        let line = [Layer::Opaque, Layer::Blend, Layer::Overlay]
            .map(|layer| make("line", "vs_line", "fs_line", &[], layer, false, layer != Layer::Overlay));
        let cap = make("cap", "vs_surface", "fs_surface", &surface_buffers, Layer::Opaque, false, false);
        let shadow = make("shadow", "vs_shadow", "fs_shadow", &[], Layer::Blend, false, false);
        let sampler = device.create_sampler(&wgpu::SamplerDescriptor {
            label: Some("linear"),
            mag_filter: wgpu::FilterMode::Linear,
            min_filter: wgpu::FilterMode::Linear,
            mipmap_filter: wgpu::MipmapFilterMode::Linear,
            ..Default::default()
        });
        let blank = device
            .create_texture_with_data(
                &queue,
                &wgpu::TextureDescriptor {
                    label: Some("no shadow"),
                    size: wgpu::Extent3d {
                        width: 1,
                        height: 1,
                        depth_or_array_layers: 1,
                    },
                    mip_level_count: 1,
                    sample_count: 1,
                    dimension: wgpu::TextureDimension::D2,
                    format: wgpu::TextureFormat::R8Unorm,
                    usage: wgpu::TextureUsages::TEXTURE_BINDING,
                    view_formats: &[],
                },
                wgpu::util::TextureDataOrder::LayerMajor,
                &[0],
            )
            .create_view(&Default::default());
        Ok(Gpu {
            device,
            queue,
            adapter: name,
            layout,
            sampler,
            env,
            surface,
            cap,
            line,
            shadow,
            blank,
            targets: Mutex::new(None),
        })
    }

    pub fn upload(&self, scene: &Scene) -> SceneBuffers {
        let buffer = |label: &str, bytes: &[u8], usage| {
            // A scene with nothing in an array still binds something.
            let pad = [0u8; 32];
            self.device.create_buffer_init(&wgpu::util::BufferInitDescriptor {
                label: Some(label),
                contents: if bytes.is_empty() { &pad } else { bytes },
                usage,
            })
        };
        let positions = buffer("positions", bytemuck::cast_slice(&scene.positions), wgpu::BufferUsages::VERTEX);
        let normals = buffer("normals", bytemuck::cast_slice(&scene.normals), wgpu::BufferUsages::VERTEX);
        let indices = buffer("indices", bytemuck::cast_slice(&scene.indices), wgpu::BufferUsages::INDEX);
        let segments = buffer(
            "segments",
            bytemuck::cast_slice::<Segment, u8>(&scene.segments),
            wgpu::BufferUsages::STORAGE,
        );
        let bytes = positions.size() + normals.size() + indices.size() + segments.size();
        SceneBuffers {
            positions,
            normals,
            indices,
            segments,
            bytes,
        }
    }

    /// Draw `frame` over `scene` and read it back: `width × height × 4` bytes, top row first,
    /// colour as stored (sRGB-encoded, alpha straight from the blend).
    pub fn draw(&self, scene: &Scene, buffers: &SceneBuffers, frame: &Frame) -> Result<Vec<u8>> {
        let device = &self.device;
        let scope = device.push_error_scope(wgpu::ErrorFilter::Validation);
        let (w, h) = (frame.width, frame.height);
        let extent = wgpu::Extent3d {
            width: w,
            height: h,
            depth_or_array_layers: 1,
        };
        let mut kept = self.targets.lock().unwrap_or_else(|e| e.into_inner());
        if !kept.as_ref().is_some_and(|t| t.width == w && t.height == h) {
            *kept = Some(Targets::new(device, w, h));
        }
        let targets = kept.as_ref().expect("made above");

        let uniform = device.create_buffer_init(&wgpu::util::BufferInitDescriptor {
            label: Some("view"),
            contents: bytemuck::bytes_of(&frame.view),
            usage: wgpu::BufferUsages::UNIFORM,
        });
        let storage = |label: &str, bytes: &[u8]| {
            let pad = [0u8; 48];
            device.create_buffer_init(&wgpu::util::BufferInitDescriptor {
                label: Some(label),
                contents: if bytes.is_empty() { &pad } else { bytes },
                usage: wgpu::BufferUsages::STORAGE,
            })
        };
        let materials = storage("materials", bytemuck::cast_slice(frame.materials));
        let edge_slot = storage("edge slots", bytemuck::cast_slice(frame.edge_slot));
        let shadow = frame.shadow.map(|m| {
            let data: Vec<u8> = m.levels.concat();
            device
                .create_texture_with_data(
                    &self.queue,
                    &wgpu::TextureDescriptor {
                        label: Some("shadow"),
                        size: wgpu::Extent3d {
                            width: m.width,
                            height: m.height,
                            depth_or_array_layers: 1,
                        },
                        mip_level_count: m.levels.len() as u32,
                        sample_count: 1,
                        dimension: wgpu::TextureDimension::D2,
                        format: wgpu::TextureFormat::R8Unorm,
                        usage: wgpu::TextureUsages::TEXTURE_BINDING,
                        view_formats: &[],
                    },
                    wgpu::util::TextureDataOrder::LayerMajor,
                    &data,
                )
                .create_view(&Default::default())
        });
        let group = device.create_bind_group(&wgpu::BindGroupDescriptor {
            label: Some("frame"),
            layout: &self.layout,
            entries: &[
                wgpu::BindGroupEntry {
                    binding: 0,
                    resource: uniform.as_entire_binding(),
                },
                wgpu::BindGroupEntry {
                    binding: 1,
                    resource: materials.as_entire_binding(),
                },
                wgpu::BindGroupEntry {
                    binding: 2,
                    resource: wgpu::BindingResource::TextureView(&self.env.main),
                },
                wgpu::BindGroupEntry {
                    binding: 3,
                    resource: wgpu::BindingResource::TextureView(&self.env.extra),
                },
                wgpu::BindGroupEntry {
                    binding: 4,
                    resource: wgpu::BindingResource::Sampler(&self.sampler),
                },
                wgpu::BindGroupEntry {
                    binding: 5,
                    resource: buffers.segments.as_entire_binding(),
                },
                wgpu::BindGroupEntry {
                    binding: 6,
                    resource: edge_slot.as_entire_binding(),
                },
                wgpu::BindGroupEntry {
                    binding: 7,
                    resource: wgpu::BindingResource::TextureView(shadow.as_ref().unwrap_or(&self.blank)),
                },
            ],
        });

        let mut encoder = device.create_command_encoder(&wgpu::CommandEncoderDescriptor { label: Some("frame") });
        {
            let [r, g, b, a] = frame.clear;
            let mut pass = encoder.begin_render_pass(&wgpu::RenderPassDescriptor {
                label: Some("frame"),
                color_attachments: &[Some(wgpu::RenderPassColorAttachment {
                    view: &targets.msaa,
                    depth_slice: None,
                    resolve_target: Some(&targets.resolve_view),
                    ops: wgpu::Operations {
                        load: wgpu::LoadOp::Clear(wgpu::Color { r, g, b, a }),
                        store: wgpu::StoreOp::Discard,
                    },
                })],
                depth_stencil_attachment: Some(wgpu::RenderPassDepthStencilAttachment {
                    view: &targets.depth,
                    depth_ops: Some(wgpu::Operations {
                        load: wgpu::LoadOp::Clear(1.0),
                        store: wgpu::StoreOp::Discard,
                    }),
                    stencil_ops: None,
                }),
                timestamp_writes: None,
                occlusion_query_set: None,
                multiview_mask: None,
            });
            pass.set_bind_group(0, &group, &[]);
            pass.set_vertex_buffer(0, buffers.positions.slice(..));
            pass.set_vertex_buffer(1, buffers.normals.slice(..));
            pass.set_index_buffer(buffers.indices.slice(..), wgpu::IndexFormat::Uint32);
            #[derive(PartialEq, Clone, Copy)]
            enum Bound {
                None,
                Surface(Layer),
                Cap,
                Line(Layer),
                Shadow,
            }
            let mut bound = Bound::None;
            for (layer, draw) in frame.draws {
                let want = match draw {
                    Draw::Surface { .. } => Bound::Surface(*layer),
                    Draw::Cap { .. } => Bound::Cap,
                    Draw::Lines { .. } => Bound::Line(*layer),
                    Draw::Shadow => Bound::Shadow,
                };
                if want != bound {
                    pass.set_pipeline(match want {
                        Bound::Surface(l) => &self.surface[l as usize],
                        Bound::Cap => &self.cap,
                        Bound::Line(l) => &self.line[l as usize],
                        Bound::Shadow => &self.shadow,
                        Bound::None => unreachable!(),
                    });
                    bound = want;
                }
                match draw {
                    Draw::Surface { mesh, slot } | Draw::Cap { mesh, slot } => {
                        let m = &scene.meshes[*mesh];
                        if !m.indices.is_empty() {
                            pass.draw_indexed(m.indices.clone(), m.vertices.start as i32, *slot..*slot + 1);
                        }
                    }
                    Draw::Lines { instances } => {
                        if !instances.is_empty() {
                            pass.draw(0..18, instances.clone());
                        }
                    }
                    Draw::Shadow => {
                        if frame.shadow.is_some() {
                            pass.draw(0..6, 0..1);
                        }
                    }
                }
            }
        }

        let (row, readback) = (targets.row, &targets.readback);
        encoder.copy_texture_to_buffer(
            wgpu::TexelCopyTextureInfo {
                texture: &targets.resolve,
                mip_level: 0,
                origin: wgpu::Origin3d::ZERO,
                aspect: wgpu::TextureAspect::All,
            },
            wgpu::TexelCopyBufferInfo {
                buffer: readback,
                layout: wgpu::TexelCopyBufferLayout {
                    offset: 0,
                    bytes_per_row: Some(row),
                    rows_per_image: Some(h),
                },
            },
            extent,
        );
        self.queue.submit([encoder.finish()]);
        if let Some(e) = pollster::block_on(scope.pop()) {
            return Err(anyhow!("the frame failed validation: {e}"));
        }
        let slice = readback.slice(..);
        let (tx, rx) = std::sync::mpsc::channel();
        slice.map_async(wgpu::MapMode::Read, move |r| {
            let _ = tx.send(r);
        });
        device
            .poll(wgpu::PollType::wait_indefinitely())
            .map_err(|e| anyhow!("waiting on the frame: {e}"))?;
        rx.recv()?.map_err(|e| anyhow!("reading the frame back: {e}"))?;
        let mapped = slice.get_mapped_range().map_err(|e| anyhow!("reading the frame back: {e}"))?;
        let mut out = Vec::with_capacity((w * h * 4) as usize);
        for y in 0..h as usize {
            let at = y * row as usize;
            out.extend_from_slice(&mapped[at..at + (w * 4) as usize]);
        }
        drop(mapped);
        readback.unmap();
        Ok(out)
    }
}
