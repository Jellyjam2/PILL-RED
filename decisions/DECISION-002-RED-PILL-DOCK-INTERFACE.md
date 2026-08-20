# Architecture Decision Record: DECISION-002

**Title:** Native Visual Command Interface: RED PILL DOCK  
**Date:** 2026-08-18  
**Status:** ACCEPTED (IMPLEMENTED & OPERATIONAL)  

---

## Context
A powerful visual command interface is required to inspect real-time continuous manifold dynamics, 3D particle attractors, interactive wireframe meshes, spectral Laplacian eigenspaces ($\mathbf{L}_B$), and CDCL solver telemetry in real time.

---

## Decision
1. **Name:** The native visual command interface is officially named **RED PILL DOCK**.
2. **Location:** `C:\PILL RED\red_pill_dock\`.
3. **Substrate:** Built directly on Rust `eframe` (0.27+) and `egui`, completely self-contained within `C:\PILL RED\red_pill_dock`.
4. **Scope:** RED PILL DOCK is not an attachment to an external engine. It is the sovereign visual interface of RED PILL, housing:
   - 7 particle attractor manifolds (Lorenz, Thomas, Hopf Fibration, Golden Ratio, Curl Noise, N-Body Gravity, Sovereign Swarm).
   - Interactive 3D Orbit Camera & Spatial Wireframe Mesh projection.
   - Spectral SAT research diagnostics ($\mathbf{L}_B$, $\Delta_F$, Degeneracy Gating, CDCL Conflict Metrics).
   - Research Repository Explorer across `benchmarks/`, `experiments/`, and `evidence/`.

---

## Consequences
- RED PILL DOCK compiles natively with zero warnings and zero external runtime dependencies.
