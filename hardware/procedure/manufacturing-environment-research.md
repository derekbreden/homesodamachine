# Manufacturing Environment Research

This document defines the procedure for a research agent that establishes the manufacturing environment — the verified specifications of the 3D printer, materials, and hardware inventory. Its output is `hardware/manufacturing-environment.md`, the single source of truth for all physical manufacturing constraints.

**This step exists because assumed constraints propagate unchallenged through every downstream step.** A "typical 256mm print bed" assumption shaped an entire enclosure split strategy, tongue-and-groove joint engineering, and multi-piece architecture — and the actual printer had a 325x320mm bed. No downstream step questions constraints it receives. The only defense is verifying constraints at the source, before any design work begins.

This step runs once at the start of the project and is updated whenever the manufacturing environment changes (new printer, new materials, etc.). It does NOT run at the start of every part design — it produces a shared document that all parts reference.

---

## What the orchestrator must provide to the agent

- Printer make and model (e.g., "Bambu Lab H2C")
- Materials on hand or planned (e.g., "PETG, PETG-CF")
- Any non-obvious hardware inventory (magnets, fasteners, springs, etc.)

## What the agent must research and document

1. **Printer specifications** — look up the manufacturer's published specs for the exact model provided. Document: build volume (W x D x H for each nozzle configuration if multi-nozzle), nozzle diameter(s), heated bed capability, enclosure, maximum print temperature, and any other relevant capabilities. **Cite the source URL.**
2. **Material properties** — look up datasheets for each material. Document: tensile strength, heat deflection temperature, recommended print temperature, shrinkage rate, layer adhesion characteristics. **Cite the source URL.**
3. **Practical print constraints** — derived from specs, not assumed. Maximum single-piece dimensions in each axis (accounting for bed clips, purge area, etc. — these are often smaller than the raw build volume). Recommended minimum wall thickness for structural parts. Tolerance expectations.
4. **Hardware inventory** — document what fasteners, magnets, springs, inserts, etc. are available, with specific dimensions.

## Agent prompt must include

- The printer make and model (from user)
- The materials list (from user)
- Instruction to look up manufacturer specifications from the official website or datasheet
- Instruction to cite every number with a source URL
- Instruction to NOT use "typical," "standard," or "common" values — every number must be specific to the actual hardware
- Instruction to save to `hardware/manufacturing-environment.md`

## Agent prompt must NOT include

- Assumed dimensions for any equipment ("most FDM printers are...")
- Guidance toward any particular conclusion about what will or won't fit

## Quality gate

- Every dimensional constraint cites a specific source (manufacturer spec page URL, material datasheet URL)
- Build volume matches the manufacturer's published spec for the exact model provided
- No "typical" or "standard" values appear anywhere in the document
- The orchestrator verifies the key numbers against their own knowledge of the hardware
