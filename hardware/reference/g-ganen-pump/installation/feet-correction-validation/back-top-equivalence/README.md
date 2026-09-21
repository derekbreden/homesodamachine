# Back-top geometry equivalence

[`validation.json`](validation.json) binds the regenerated back-top to the
existing H2C v2 archive and its completed support review. The canonical STEP and
STL hashes differ, but their physical geometry is equivalent:

- Native added volume: **0 mm³**; removed volume: **0 mm³**. Both are valid
  single solids with 718 faces and identical bounds.
- Both print meshes have **1,124,732 triangles** in the same corner order.
  After undoing the prior mesh's declared X180 print orientation, 47 corners in
  43 triangles differ by at most **0.000015258789 mm** (15.26 nm).
- The differing triangles lie within X44.279–83.637, Y244.624–307.003,
  Z343–348 mm. [`mesh-corner-witness.json`](mesh-corner-witness.json) records
  every changed coordinate. The native boolean differences contain no solids.

This numerical mesh variation does not change a printable feature. The exact
`enclosure-back-top-black-z018-h2c-v2.gcode.3mf` archive
`304894a1ce538e97c5d48736383fa9801871890e13d9d64435223290079486a1`
and its support ledger remain the reviewed manufacturing inputs. The new
geometry receipt must name this equivalence explicitly; it must not describe
the two canonical meshes as byte-identical. Actual fit and cleanup effort
remain physical assembly observations.

The prior canonical leaf STEP is identified by its qualified receipt hash.
Its bytes were unavailable for this comparison, so the native prior input is
the exact back-top leaf extracted from qualified aggregate STEP `0bf745015…`.
That compact BREP and its extraction manifest are retained here. The prior
print mesh is the exact hash-bound oriented STL used by the staged H2C v2
project. Every input and the archive/support binding are recorded in the report.

`compare.py.txt` and `compare_mesh.py.txt` preserve the executed read-only
reproducers byte for byte, including their frozen input paths. `compare.log`,
`native-summary.json` and `mesh-summary.json` retain their actual results.
These checks build no production geometry and write only the private evidence
directory. The current aggregate assembly has its own independent checks.
