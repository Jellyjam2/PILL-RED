# 🛡️ PILL RED Security Policy

## Security Model & Invariants

PILL RED enforces the following low-level security and safety guarantees across its computational boundary:

1. **Zero Dynamic Allocation in Hot Loops:**
   - Inner protocol serialization and parsing utilizes `heapless::Vec<i16, 512>`.
   - All stack boundaries are formally verified using Kani bounded model checking.

2. **Cryptographic Memory Hygiene:**
   - Sensitive key material, state vectors, and clause containers implement the `Zeroize` trait.
   - Memory is scrubbed upon `Drop` to prevent leakage into crash dumps or cold boot vectors.

3. **FFI Boundary Integrity:**
   - Raw pointers passed across the Python/Rust boundary (`FFIOmegaManifold`) are strictly bounds-checked for null pointers, zero rows, and zero columns.
   - Memory allocated in Rust is explicitly managed via boxed static slices to prevent double-free and use-after-free vulnerabilities.

4. **Hardware Thread Isolation:**
   - Low-level worker threads are isolated and pinned using OS-level thread affinity masks (`SetThreadAffinityMask`) to prevent cross-core cache invalidation and side-channel timing contamination.
