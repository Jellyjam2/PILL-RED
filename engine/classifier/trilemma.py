"""Trilemma Epistemic Classifier for PILL RED v2.0.

Classifies candidate evaluation verdicts into Outcomes A, B, C, D, or UNKNOWN.
"""

from engine.interfaces import CrucibleVerdict, TrilemmaOutcome


class TrilemmaClassifier:
    """Classifies empirical gate results into the 5-state epistemic taxonomy."""

    @classmethod
    def classify_verdict(cls, verdict: CrucibleVerdict) -> CrucibleVerdict:
        """Assigns the formal TrilemmaOutcome and structural rationale to a verdict."""
        gates = verdict.gates

        d1 = gates.get("D1")
        d2 = gates.get("D2")
        d3 = gates.get("D3")
        d4 = gates.get("D4")
        d5 = gates.get("D5")
        d6 = gates.get("D6")
        d7 = gates.get("D7")

        if not all([d1, d2, d3, d4, d5, d6, d7]):
            verdict.classification = TrilemmaOutcome.UNKNOWN
            verdict.confidence = 0.0
            verdict.primary_failure_mechanism = "INCOMPLETE_GATE_DATA"
            verdict.rationale = "Crucible did not record all 7 gate metrics."
            return verdict

        # 1. Check for OUTCOME B: Circularity / Hidden Search
        if not d7.passed:
            verdict.classification = TrilemmaOutcome.OUTCOME_B
            verdict.confidence = 0.99
            verdict.primary_failure_mechanism = "CIRCULAR_NP_SEARCH"
            verdict.rationale = (
                f"Candidate failed Gate D7: executed {int(d7.metric_value)} internal SAT search steps "
                f"during construction, re-encoding the original search problem."
            )
            return verdict

        # 2. Check for OUTCOME C: State / Precision / Resource Blowup
        if not d2.passed or not d4.passed or not d5.passed:
            failed_gates = [g.gate_id for g in [d2, d4, d5] if not g.passed]
            verdict.classification = TrilemmaOutcome.OUTCOME_C
            verdict.confidence = 0.95
            verdict.primary_failure_mechanism = "EXPONENTIAL_RESOURCE_BLOWUP"
            verdict.rationale = (
                f"Candidate failed resource bounds ({', '.join(failed_gates)}): "
                f"Memory={d2.metric_value:.1f}KB (max {d2.threshold:.1f}KB), "
                f"ExtractionTime={d4.metric_value:.1f}ms, ConditionNum={d5.metric_value:.2e}."
            )
            return verdict

        # 3. Check for OUTCOME A: Information Collapse on Adversarial Cycles
        if not d1.passed or not d6.passed:
            verdict.classification = TrilemmaOutcome.OUTCOME_A
            verdict.confidence = 0.98
            verdict.primary_failure_mechanism = "INFORMATION_COLLAPSE"
            verdict.rationale = (
                f"Candidate representation is computationally tractable (D2-D5 passed), but "
                f"observable collapsed on adversarial expander collisions: "
                f"Separation Δ = {d1.metric_value:.6f} (threshold {d1.threshold:.6f}). "
                f"Global parity defect was projected away into a blind quotient."
            )
            return verdict

        # 4. Check for OUTCOME D: Survived All Gates
        if verdict.all_gates_passed:
            verdict.classification = TrilemmaOutcome.OUTCOME_D
            verdict.confidence = 0.90
            verdict.primary_failure_mechanism = "NONE_SURVIVED_CRUCIBLE"
            verdict.rationale = (
                f"Candidate passed all 7 gates (D1–D7) on the tested adversarial family with "
                f"mean separation Δ = {verdict.mean_separation:.4f}. "
                f"Flagged for next-level adversarial escalation (Q8 Level + 1)."
            )
            return verdict

        # Fallback: Inconclusive
        verdict.classification = TrilemmaOutcome.UNKNOWN
        verdict.confidence = 0.50
        verdict.primary_failure_mechanism = "INDETERMINATE_SIGNATURE"
        verdict.rationale = "Gate measurements produced an unclassified combination of margins."
        return verdict
