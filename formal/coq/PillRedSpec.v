(** * Formal Model of the PILL RED Evidence Protocol (PILLRED-SPEC-1.0) in Coq *)

Require Import Coq.Strings.String.
Require Import Coq.Lists.List.
Require Import Coq.ZArith.ZArith.
Require Import Coq.Reals.Reals.
Import ListNotations.

Open Scope string_scope.
Open Scope R_scope.

(** Core Data Types for Cryptographic Protocol Entities *)

Definition Hash := string.
Definition Timestamp := R.
Definition ModelID := string.
Definition EventID := string.
Definition PredictionValue := string.
Definition OutcomeValue := string.

(** 1. Prediction Receipt Record *)
Record PredictionReceipt : Type := mkReceipt {
  receipt_id : string;
  protocol_version : string;
  model_id : ModelID;
  target_event : EventID;
  prediction : PredictionValue;
  confidence : R;
  commit_timestamp : Timestamp;
  previous_receipt_hash : Hash;
  commit_hash : Hash;
  nonce : string;
  
  (* Settlement fields *)
  actual_outcome : option OutcomeValue;
  event_timestamp : option Timestamp;
  resolution_timestamp : option Timestamp;
  payout_multiplier : option R;
  receipt_hash : option Hash;
  is_hit : option bool
}.

(** 2. Four-State Evidentiary Status *)
Inductive EvidentiaryStatus : Type :=
  | StatusVerified : EvidentiaryStatus
  | StatusMeasured : EvidentiaryStatus
  | StatusInferred : EvidentiaryStatus
  | StatusNotProven : EvidentiaryStatus.

(** 3. Model Audit Passport Record *)
Record ModelAuditPassport : Type := mkPassport {
  passport_id : string;
  passport_model_id : ModelID;
  merkle_root : Hash;
  total_receipts : nat;
  provenance_status : EvidentiaryStatus;
  statistical_claim : EvidentiaryStatus;
  economic_claim : EvidentiaryStatus;
  passport_hash : Hash
}.
