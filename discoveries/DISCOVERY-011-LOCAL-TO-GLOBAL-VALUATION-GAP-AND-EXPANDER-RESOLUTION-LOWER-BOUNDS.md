# Discovery Record: DISCOVERY-011

**Discovery ID:** `DISCOVERY-011`  
**Title:** The Local-to-Global Valuation Gap on High-Girth Expander Collision Families  
**Date Discovered:** 2026-08-19  
**Producing Experiment:** `EXP-PHASE18-GLOBAL-VALUATION-CRUCIBLE-001` (Phase XVIII)  
**Epistemic Classification:** Controlled Empirical Boundary Characterization  

---

## 1. Description of the Empirical Discovery

1. **The Local-to-Global Valuation Gap on Tested Expander Families:**
   - In 10 adversarial collision pairs generated over 3-regular expander graphs ($N=20 \dots 36, g=5 \dots 7$), the local information content of SAT and UNSAT instances was identical for all tested local polynomial valuation operators of radius $R < \lfloor g/2 \rfloor$:
     $$I_{\text{local}}(S) \equiv I_{\text{local}}(U)$$
   - The ground-truth satisfiability difference was mediated entirely by the global parity charge homological sum:
     $$\sum_{v \in V} q(v) \equiv \begin{cases} 0 \pmod 2 & \text{SAT} \\ 1 \pmod 2 & \text{UNSAT} \end{cases}$$
2. **Empirical Exponential Resolution Hardness:**
   - On the UNSAT instances, CDCL resolution conflicts scaled exponentially ($435 \to 6,038$) as graph vertices increased ($N = 20 \to 36$).
3. **Epistemic Scope (Constitution Rule 006 Bounded Claims):**
   - This experiment demonstrates that bounded-radius/local VPTI projectors cannot distinguish the tested SAT/UNSAT expander collision families, and that successful separation in these families requires information extending beyond the tested local witness radius.
   - This empirical observation is consistent with known treewidth, locality, and resolution lower bounds, but does not itself constitute a general complexity lower-bound theorem.

---

## 2. Epistemic Impact on PILL RED
- Formally delineates the boundary of local polynomial valuation representations: local witness projectors cannot decide global interacting valuation contradictions on high-girth expander topologies without non-local cycle invariants.

---

## 3. Evidence & Records
- **Experiment Record:** `experiments/017_GLOBAL_VALUATION/EXP_PHASE18_GLOBAL_VALUATION_CRUCIBLE_001.md`
- **Falsification Record:** `falsifications/FALSIFICATION-005-LOCAL-VALUATION-PROJECTORS-BLIND-TO-GLOBAL-EXPANDER-VALUATIONS.md`
- **Dataset:** `evidence/BENCHMARK_RECORDS/EXP_PHASE18_GLOBAL_VALUATION_DATASET.json`
- **Plot:** `evidence/RELEASE_EVIDENCE/phase18_global_valuation_boundary.png`
