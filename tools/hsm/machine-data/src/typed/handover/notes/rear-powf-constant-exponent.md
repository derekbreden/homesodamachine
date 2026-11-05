# powf with a constant exponent differs between opt levels (from agent `rear`)

At opt-level >= 1, LLVM rewrites `x.powf(2.)` (a constant exponent) to `x * x`. macOS libm
`pow(x, 2.0)` differs from `x * x` in the last bit for 2597 of 2,000,000 random doubles, e.g.
x = 23.03655421175654: pow gives 530.6828299511978, x*x gives 530.682829951198.

Interop's `binary("pow")` (what the generated code calls for `**`) always calls libm `pow`, so
typed code that writes `x.powf(2.)` matches the generated code at opt 0 and not at opt 3.
`x.powf(std::hint::black_box(2.))` keeps the libm call (checked with `rustc -O` on this Mac).
Same class as the sin/cos -> __sincos_stret merge.
