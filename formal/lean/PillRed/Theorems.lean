import PillRed

namespace PillRed

/-- Theorem P1: Commitment Binding Theorem in Lean 4 -/
theorem commitment_binding_thm (r1 r2 : PredictionReceipt) :
  ValidSingleReceipt r1 →
  r1.commit_hash = computeCommitHash r2 →
  r1.prediction = r2.prediction ∧ r1.commit_timestamp = r2.commit_timestamp := by
  intro h_valid h_eq
  have h_commit := h_valid.2.1
  rw [h_commit] at h_eq
  have h_col := commit_hash_collision_resistant r1 r2 h_eq
  exact ⟨h_col.1, h_col.2.2⟩

/-- Theorem P2: Temporal Precedence Soundness Theorem in Lean 4 -/
theorem temporal_precedence_soundness_thm (r : PredictionReceipt) (t_e t_r : Timestamp) :
  ValidSingleReceipt r →
  r.event_timestamp = some t_e →
  r.resolution_timestamp = some t_r →
  (r.commit_timestamp < t_e) ∧ (t_e ≤ t_r) := by
  intro h_valid h_event h_resolve
  have h_temp := h_valid.2.2.1
  dsimp [ValidTemporalPrecedence] at h_temp
  rw [h_event, h_resolve] at h_temp
  exact h_temp

/-- Theorem P3: Inductive Hash Linkage Soundness in Lean 4 -/
theorem chain_linkage_soundness_thm (r_curr r_prev : PredictionReceipt) (rest : List PredictionReceipt) (root : Hash) :
  ValidChain (r_curr :: r_prev :: rest) root →
  r_curr.previous_receipt_hash = r_prev.receipt_hash.getD r_prev.commit_hash := by
  intro h_chain
  cases h_chain with
  | step _ _ _ _ _ h_link _ =>
    exact h_link

/-- Theorem P4: Claim Discipline (NotProven is strictly distinct from Verified) in Lean 4 -/
theorem claim_discipline_thm (p : ModelAuditPassport) :
  p.statistical_claim = EvidentiaryStatus.NotProven →
  p.statistical_claim ≠ EvidentiaryStatus.Verified := by
  intro h_not_proven
  rw [h_not_proven]
  intro h_contra
  contradiction

end PillRed
