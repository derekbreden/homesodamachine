# East-wall tube snap fit print

The coupon is a crop of the production back-top solid. It retains the complete
wall behind the fill-tube seat, the corbel and the free wing. The source
[`inputs.json`](inputs.json) sets the crop and [`coupon.rs`](coupon.rs) exports
the closed print mesh; [`parts/geometry.json`](parts/geometry.json) binds it to
the production solid.

The [Mark1 print](prints/2026-11-19-mark1/print-job.json) uses the back-top's
ceiling-down direction, PET-GF recipe and textured plate. The slice has no
removable supports. A cooling tower gives the small spring time between layers.

Seat the quarter-inch reservoir fill tube through the mouth. Observe the free
wing during insertion and release, how securely the tube stays seated, and
whether the corbel and wing print cleanly. The physical fit and cleanup await
that observation.
