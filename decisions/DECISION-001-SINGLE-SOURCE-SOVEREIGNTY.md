# Architecture Decision Record: DECISION-001

**Title:** Single-Source Sovereignty Invariant for PILL RED  
**Date:** 2026-08-18  
**Status:** ACCEPTED (IMMUTABLE CORE PRINCIPLE)  

---

## Context
PILL RED is an autonomous, foundational research project studying the discrete-continuous manifold duality and spectral properties of combinatorial satisfiability (SAT). Earlier iterations referenced or borrowed code from external projects (`C:\Project_Aether_Cache\`, `spatial_weaver`, `Titan Black Swan`, `Aerow-AudioWave`). These mixed naming conventions and external runtime dependencies violated self-containment.

---

## Decision
1. **Single Source Rule:** `C:\PILL RED\` is the sole, authoritative home for the entire project. Everything we build, discover, test, reject, prove, falsify, modify, or decide belongs to `PILL RED`.
2. **Project Invariant:** *If PILL RED cannot operate from `C:\PILL RED\` on its own, it is not yet a PILL RED component.*
3. **No External Runtime Dependencies:** No PILL RED runtime component may depend on an external project's runtime or folder structure. External source code may be copied, adapted, and rewritten inside `C:\PILL RED\`, but PILL RED owns its implementation end-to-end.
4. **Complete Provenance Preservation:** Every discovery, falsification, experiment, event, and architectural decision must be preserved immutably inside the repository.

---

## Consequences
- Zero coupling to external workspaces.
- Seamless scientific reproducibility on any clean machine.
- Direct, unbroken chain of evidence from raw measurements to formal claims.
