# PGFUN build release checks

The [release manifest](release-manifest.json) binds the print pack, CAD
parameters, numerical checks, compiled controller and current shop guide.
[Release verification](release-verification.json) records executed geometry
and software checks. [Publication verification](publication-verification.json)
records actual served bytes after publication.

The [guide inspection](../gun-positioner-guide/qa-receipt.json) covers all 35
rendered pages, intact command blocks, contents links and PDF bookmarks.

The [print geometry review](../printed-parts/fixtures/pgfun-positioner/geometry-lint-review.json)
records all 60 STLs checked after publication. Exact-point answers beside the
parts describe the required fits, support access and short bridges. The
support manifest and assembly instructions specify their fabrication.

Physical results use [commissioning](commissioning.md) and
[observation](observation.md). Received reducer fits, loaded print retention,
useful small motion, thermal drift, camera noise and independent dry replay
are measured on the assembled device. Numerical checks do not assert those
results or a welding-process acceptance.
