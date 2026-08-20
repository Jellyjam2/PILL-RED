// Copyright 2026 PILL RED Research
//
// Continuous Graph Laplacian Manifold & Spectral SAT Reduction Engine

use nalgebra::DMatrix;
use pyo3::prelude::*;
use rand::prelude::*;
use rayon::prelude::*;
use std::slice;
use std::sync::Arc;
use std::time::Instant;

// ---------------------------------------------------------------------------
// 1. C-ABI ZERO-COPY FFI MANIFOLD INTERFACE
// ---------------------------------------------------------------------------

#[repr(C)]
pub struct FFIOmegaManifold {
    pub data: *const f32,
    pub rows: usize,
    pub cols: usize,
}

/// Computes Graph Laplacian L = B^T * B and extracts the Fiedler vector v_2
#[no_mangle]
pub unsafe extern "C" fn anneal_gradient_manifold(manifold: FFIOmegaManifold) -> *const f32 {
    if manifold.data.is_null() || manifold.rows == 0 || manifold.cols == 0 {
        return std::ptr::null();
    }

    // Zero-copy array parsing from Python C-contiguous buffer
    let raw_slice = slice::from_raw_parts(manifold.data, manifold.rows * manifold.cols);
    let matrix_b = DMatrix::from_row_slice(manifold.rows, manifold.cols, raw_slice);

    // Compute Graph Laplacian Manifold L = B^T * B
    let matrix_l = matrix_b.transpose() * &matrix_b;

    // Execute symmetric eigen-decomposition
    let decomposition = matrix_l.symmetric_eigen();
    let eigenvectors = decomposition.eigenvectors;

    // Extract continuous gradients from Fiedler vector v_2 (Col 1 if cols > 1, else Col 0)
    let fiedler_col = if manifold.cols > 1 { 1 } else { 0 };
    let mut continuous_gradients = vec![0.0f32; manifold.cols];
    for idx in 0..manifold.cols {
        continuous_gradients[idx] = eigenvectors[(idx, fiedler_col)];
    }

    // FFI Ownership Contract:
    // The returned pointer is owned by the caller across the C-ABI.
    // Callers in Python or C must release it by calling `free_gradient_manifold(ptr, cols)`
    // to reclaim the boxed slice memory.
    let boxed_allocation = continuous_gradients.into_boxed_slice();
    let static_pointer = boxed_allocation.as_ptr();
    std::mem::forget(boxed_allocation);

    static_pointer
}

/// Deallocates memory returned by `anneal_gradient_manifold`.
///
/// # Safety
/// Caller must ensure `ptr` was allocated by `anneal_gradient_manifold` and `len` equals `manifold.cols`.
#[no_mangle]
pub unsafe extern "C" fn free_gradient_manifold(ptr: *mut f32, len: usize) {
    if !ptr.is_null() && len > 0 {
        let _ = Box::from_raw(std::slice::from_raw_parts_mut(ptr, len));
    }
}

// ---------------------------------------------------------------------------
// 2. PARALLEL RAYON ANNEALING ENGINE
// ---------------------------------------------------------------------------

#[pyclass]
pub struct OmegaAnnealer {
    #[pyo3(get, set)]
    pub vars: usize,
}

#[pymethods]
impl OmegaAnnealer {
    #[new]
    pub fn new(vars: usize) -> Self {
        OmegaAnnealer { vars }
    }

    pub fn execute_omega_siege(
        &self,
        clauses: Vec<Vec<i32>>,
        steps: usize,
    ) -> PyResult<(bool, usize, f64)> {
        let start = Instant::now();
        let vars = self.vars;
        let shared_clauses = Arc::new(clauses);

        // Quad-Blade parallel stochastic search across CPU cores
        let results: Vec<usize> = (0..4)
            .into_par_iter()
            .map(|thread_id| {
                let mut rng = StdRng::seed_from_u64(thread_id as u64 + 42);
                let mut assignment = vec![false; vars + 1];
                for v in 1..=vars {
                    assignment[v] = rng.gen();
                }

                let local_clauses = Arc::clone(&shared_clauses);
                let mut current_energy = calculate_energy_internal(&local_clauses, &assignment);
                let mut temp: f64 = 100.0;
                let mut best_energy = current_energy;
                let mut stuck_counter = 0;

                for _ in 0..steps {
                    if current_energy == 0 {
                        return 0;
                    }

                    let v = rng.gen_range(1..=vars);
                    assignment[v] = !assignment[v];
                    let new_energy = calculate_energy_internal(&local_clauses, &assignment);

                    if new_energy < current_energy
                        || rng.gen_bool(
                            (-(new_energy as f64 - current_energy as f64) / temp)
                                .exp()
                                .min(1.0),
                        )
                    {
                        current_energy = new_energy;
                        if current_energy < best_energy {
                            best_energy = current_energy;
                            stuck_counter = 0;
                        }
                    } else {
                        assignment[v] = !assignment[v];
                    }

                    stuck_counter += 1;
                    if stuck_counter > 100_000 {
                        temp = 50.0; // Phoenix reheat
                        stuck_counter = 0;
                    } else {
                        temp *= 0.999995;
                    }
                }
                best_energy
            })
            .collect();

        let absolute_best = *results.iter().min().unwrap_or(&usize::MAX);
        Ok((
            absolute_best == 0,
            absolute_best,
            start.elapsed().as_secs_f64(),
        ))
    }
}

fn calculate_energy_internal(clauses: &[Vec<i32>], assignment: &[bool]) -> usize {
    let mut energy = 0;
    for c in clauses {
        let mut sat = false;
        for &lit in c {
            let var = lit.unsigned_abs() as usize;
            if var < assignment.len() && assignment[var] == (lit > 0) {
                sat = true;
                break;
            }
        }
        if !sat {
            energy += 1;
        }
    }
    energy
}

// ---------------------------------------------------------------------------
// 3. PYO3 PYTHON MODULE REGISTRATION
// ---------------------------------------------------------------------------

#[pymodule]
fn pill_red_core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<OmegaAnnealer>()?;
    Ok(())
}
