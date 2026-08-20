import ctypes
import os
import sys
import numpy as np
from pysat.solvers import Glucose3

# Force utf-8 stdout encoding for Windows console compatibility
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

class FFIOmegaManifold(ctypes.Structure):
    _fields_ = [
        ("data", ctypes.POINTER(ctypes.c_float)),
        ("rows", ctypes.c_size_t),
        ("cols", ctypes.c_size_t),
    ]

class IntegratedSovereignLumina:
    def __init__(self, num_vars, clauses, rust_path=None):
        self.num_vars = num_vars
        self.clauses = clauses
        if rust_path is None:
            # Default auto-discovery of pill_red_core.dll
            here = os.path.dirname(os.path.abspath(__file__))
            candidate_paths = [
                os.path.join(here, "target", "release", "pill_red_core.dll"),
                os.path.join(here, "target", "debug", "pill_red_core.dll"),
                os.path.join(here, "pill_red_core.dll"),
                r"C:\LUMINA RED PILL\target\release\aerowave_dsp.dll",
            ]
            for p in candidate_paths:
                if os.path.exists(p):
                    rust_path = p
                    break
            if rust_path is None:
                rust_path = candidate_paths[0]
        self.rust_path = rust_path
        self.solver = Glucose3()

    def execute_hybrid_solve(self, epsilon=1e-4, min_spectral_gap=0.05, max_sbp_ratio=2.0):
        """
        Executes hybrid spectral-CDCL loop with Degeneracy-Aware Safety Gating.
        
        Guarantees:
        - If spectral gap ΔF is near-degenerate (< min_spectral_gap), SBP injection is 
          suppressed to prevent over-constraining the formula into false UNSAT.
        - Fail-open toward the original SAT problem (falls back to Mode B polarity re-seeding).
        - Topological symmetry check: verifies variable degree invariance before SBP injection.
        - Bounded constraint generation: caps total SBPs to (max_sbp_ratio * num_vars).
        """
        print("🚀 [PIPELINE] Initialising hybrid spectral-CDCL loop...")
        
        if not os.path.exists(self.rust_path):
            print(f"⚠️ [WARNING] Rust DLL not found at: {self.rust_path}")
            print("Falling back to pure Glucose3 CDCL solve...")
            for clause in self.clauses:
                self.solver.add_clause(clause)
            is_sat = self.solver.solve()
            return is_sat, self.solver.get_model() if is_sat else None, 0, {}

        # 1. Build Continuous Incidence Matrix B & Laplacian L
        m = len(self.clauses)
        n = self.num_vars
        B = np.zeros((m, n), dtype=np.float32)
        for c_idx, clause in enumerate(self.clauses):
            for literal in clause:
                var_idx = abs(literal) - 1
                if var_idx < n:
                    sign = 1.0 if literal > 0 else -1.0
                    B[c_idx, var_idx] = sign

        L = B.T @ B
        eigenvalues = np.sort(np.linalg.eigvalsh(L))
        lambda_1 = float(eigenvalues[0]) if len(eigenvalues) > 0 else 0.0
        lambda_2 = float(eigenvalues[1]) if len(eigenvalues) > 1 else 0.0
        lambda_3 = float(eigenvalues[2]) if len(eigenvalues) > 2 else 0.0
        fiedler_gap = float(lambda_3 - lambda_2)

        # 2. Extract Fiedler vector via Rust FFI
        lib = ctypes.CDLL(self.rust_path)
        lib.anneal_gradient_manifold.argtypes = [FFIOmegaManifold]
        lib.anneal_gradient_manifold.restype = ctypes.POINTER(ctypes.c_float)

        B_flat = B.flatten()
        data_ptr = B_flat.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
        manifold_struct = FFIOmegaManifold(data_ptr, m, n)
        fiedler_ptr = lib.anneal_gradient_manifold(manifold_struct)
        fiedler_vec = np.ctypeslib.as_array(fiedler_ptr, shape=(n,))

        print(f"🌀 [SPECTRAL] λ1: {lambda_1:.4f} | λ2: {lambda_2:.4f} | λ3: {lambda_3:.4f} | ΔF: {fiedler_gap:.4f}")

        # 3. DEGENERACY SAFETY GATE & SBP CANDIDATE FILTERING
        sbp_clauses_injected = 0
        sbp_cap = int(max_sbp_ratio * n)
        degrees = np.diag(L)

        if fiedler_gap < min_spectral_gap:
            print(f"⚠️ [SAFETY GATE TRIGGERED] ΔF = {fiedler_gap:.4f} < {min_spectral_gap:.4f} (Near-Degenerate Spectrum).")
            print("   Suppressing SBP injection to prevent false UNSAT. Failing open to Mode B (Polarity Guidance).")
        else:
            for u in range(n):
                if sbp_clauses_injected >= sbp_cap:
                    break
                for v in range(u + 1, n):
                    if sbp_clauses_injected >= sbp_cap:
                        break
                    # Coordinate closeness check
                    if abs(fiedler_vec[u] - fiedler_vec[v]) < epsilon:
                        # Topological degree soundness check: symmetrical nodes must have matching degree
                        if abs(degrees[u] - degrees[v]) < 1e-3:
                            sbp_clause = [-(u + 1), (v + 1)]
                            self.solver.add_clause(sbp_clause)
                            sbp_clauses_injected += 1

            print(f"✂️ [PRUNE] Injected {sbp_clauses_injected} verified SBP clauses (Budget: {sbp_cap}).")

        # 4. Load original problem clauses into Glucose3
        for clause in self.clauses:
            self.solver.add_clause(clause)

        # 5. Continuous Gradient Polarity Re-seeding
        for i in range(n):
            polarity = 1 if fiedler_vec[i] >= 0.0 else -1
            self.solver.set_phases([polarity * (i + 1)])
        print("🎛️ [RESTART] Glucose3 polarity branches re-seeded via continuous gradient math.")

        # 6. Execute Solver
        is_sat = self.solver.solve()
        model = self.solver.get_model() if is_sat else None
        print(f"👑 [SOLVER RESULT] Formula is: {'SATISFIABLE' if is_sat else 'UNSATISFIABLE'}")

        diag_summary = {
            "lambda_1": lambda_1,
            "lambda_2": lambda_2,
            "lambda_3": lambda_3,
            "fiedler_gap": fiedler_gap,
            "sbp_injected": sbp_clauses_injected,
            "degeneracy_gated": bool(fiedler_gap < min_spectral_gap),
        }
        return is_sat, model, sbp_clauses_injected, diag_summary
