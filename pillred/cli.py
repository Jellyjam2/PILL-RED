"""
PILL RED Command Line Interface & Public Offline Verifier.
Executes zero-trust cryptographic, statistical, and economic audits directly from the terminal.
"""

import argparse
import json
import os
import sys
from typing import Any, Dict, List

from pillred.protocol.spec import PROTOCOL_VERSION
from pillred.protocol.passport import ModelAuditPassport
from pillred.protocol.verifier import ZeroTrustVerifier


BANNER = f"""======================================================================
               PILL RED PUBLIC OFFLINE VERIFIER
                       {PROTOCOL_VERSION}
======================================================================"""


def _verify_receipt_file(r_dict: Dict[str, Any], filepath: str) -> int:
    rid = r_dict.get("receipt_id", "UNKNOWN")
    mid = r_dict.get("model_id", "UNKNOWN")
    target = r_dict.get("target_event", "UNKNOWN")
    pred = r_dict.get("prediction")
    outcome = r_dict.get("actual_outcome")

    print(BANNER)
    print(f"Target File:  {filepath}")
    print(f"Target Type:  SINGLE PREDICTION RECEIPT ({rid})")
    print(f"Model ID:     {mid}")
    print(f"Event:        {target} | Pred: {pred} | Reality: {outcome}\n")

    is_valid, violations = ZeroTrustVerifier.verify_single_receipt(r_dict)

    if is_valid:
        print("Commitment Hash ....... VERIFIED")
        if outcome is not None:
            print("Temporal Integrity .... VERIFIED (t_commit < t_event <= t_resolve)")
            print("Settlement Hash ....... VERIFIED")
            print(f"Scoring Alignment ..... VERIFIED (is_hit: {r_dict.get('is_hit')})")
        else:
            print("Settlement Status ..... PENDING (Unsettled Commitment)")
        print("----------------------------------------------------------------------")
        print("RESULT: PROVENANCE VERIFIED (100% Intact)")
        return 0
    else:
        print("Commitment Hash ....... REJECTED")
        print("Violations Detected:")
        for v in violations:
            print(f"  [X] {v}")
        print("----------------------------------------------------------------------")
        print("RESULT: INTEGRITY VIOLATION (Receipt Compromised)")
        return 1


def _verify_chain_file(chain_list: List[Dict[str, Any]], filepath: str) -> int:
    count = len(chain_list)
    mid = chain_list[0].get("model_id", "UNKNOWN") if count > 0 else "UNKNOWN"

    print(BANNER)
    print(f"Target File:  {filepath}")
    print(f"Target Type:  PREDICTION RECEIPT CHAIN ({count:,} Receipts)")
    print(f"Model ID:     {mid}\n")

    is_valid, violations, merkle_root = ZeroTrustVerifier.verify_chain(chain_list)

    if is_valid:
        print(f"Receipt Count ......... VERIFIED ({count:,} Records)")
        print(f"Temporal Precedence ... VERIFIED (Strictly Causal)")
        print(f"Sequential Chaining ... VERIFIED (Intact Hash Links)")
        print(f"Merkle Root Seal ...... VERIFIED (0x{merkle_root[:16]}...{merkle_root[-16:]})")
        print("----------------------------------------------------------------------")
        print("RESULT: EVIDENCE PRESERVED (All Receipts Cryptographically Verified)")
        return 0
    else:
        print("Chain Verification .... FAILED")
        print(f"Violations Detected ({len(violations)}):")
        for v in violations[:10]:
            print(f"  [X] {v}")
        if len(violations) > 10:
            print(f"  ... and {len(violations) - 10} more violations.")
        print("----------------------------------------------------------------------")
        print("RESULT: INTEGRITY VIOLATION (Chain Severed or Corrupted)")
        return 1


def _verify_passport_file(p_dict: Dict[str, Any], filepath: str) -> int:
    ident = p_dict.get("identity", {})
    mid = ident.get("model_id", "UNKNOWN")
    mver = ident.get("model_version", "1.0.0")
    domain = ident.get("target_domain", "UNKNOWN")
    p_hash = p_dict.get("passport_hash", "")
    conclusions = p_dict.get("evidentiary_conclusions", {})

    print(BANNER)
    print(f"Target File:  {filepath}")
    print(f"Target Type:  MODEL AUDIT PASSPORT ({ident.get('passport_id', 'UNKNOWN')})")
    print(f"Model:        {mid} (v{mver}) | Domain: {domain}\n")

    is_valid, violations = ModelAuditPassport.verify_passport(p_dict)

    prov_status = conclusions.get("provenance", "UNKNOWN")
    stat_claim = conclusions.get("statistical_claim", "UNKNOWN")
    econ_claim = conclusions.get("economic_claim", "UNKNOWN")
    overall = conclusions.get("overall_status", "UNKNOWN")

    # Extract key numbers
    prov_sec = p_dict.get("provenance", {})
    stat_sec = p_dict.get("statistical_evidence", {}).get("measured", {})
    econ_sec = p_dict.get("economic_evidence", {}).get("measured", {})

    total_r = prov_sec.get("total_receipts", 0)
    acc = stat_sec.get("accuracy", 0.0)
    delta = stat_sec.get("delta_over_baseline", 0.0)
    p_val = stat_sec.get("p_value", 1.0)
    pnl = econ_sec.get("net_pnl", 0.0)
    roi = econ_sec.get("roi_percentage", 0.0)

    if is_valid:
        print(f"Provenance ............. {prov_status} ({total_r:,} Receipts)")
        print(f"Temporal Integrity ..... VERIFIED (t_commit < t_event <= t_resolve)")
        print(f"Chain Integrity ........ VERIFIED (Intact Sequential Hashes)")
        print(f"Merkle Root ............ VERIFIED ({prov_sec.get('merkle_root', '')[:16]}...)")
        print(f"Statistical Evidence ... MEASURED / {stat_claim} (Acc: {acc*100:.1f}%, Delta: {delta*100:+.1f}%, p: {p_val:.4f})")
        print(f"Economic Evidence ...... MEASURED / {econ_claim} (Net PnL: ${pnl:+,.2f}, ROI: {roi:+.1f}%)")
        print(f"Passport Seal .......... VERIFIED (0x{p_hash[:16]}...{p_hash[-16:]})")
        print("----------------------------------------------------------------------")
        print(f"OVERALL VERDICT: {overall} (PROVENANCE: {prov_status})")
        return 0
    else:
        print("Passport Seal ......... COMPROMISED")
        print("Violations Detected:")
        for v in violations:
            print(f"  [X] {v}")
        print("----------------------------------------------------------------------")
        print("OVERALL VERDICT: INTEGRITY_VIOLATION (Passport Tampered)")
        return 1


def verify_file(filepath: str) -> int:
    """Verifies any PILL RED JSON artifact (receipt, chain, or passport)."""
    if not os.path.exists(filepath):
        print(f"[Error] File not found: {filepath}", file=sys.stderr)
        return 2

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"[Error] Failed to parse JSON in {filepath}: {e}", file=sys.stderr)
        return 2

    if isinstance(data, dict):
        if "passport_hash" in data:
            return _verify_passport_file(data, filepath)
        elif "commit_hash" in data:
            return _verify_receipt_file(data, filepath)
        else:
            print(f"[Error] Unrecognized PILL RED schema in {filepath}", file=sys.stderr)
            return 2
    elif isinstance(data, list):
        return _verify_chain_file(data, filepath)
    else:
        print(f"[Error] Invalid JSON root in {filepath} (expected dict or list)", file=sys.stderr)
        return 2


def inspect_file(filepath: str) -> int:
    """Inspects and summarizes a PILL RED JSON artifact without full cryptographic verification."""
    if not os.path.exists(filepath):
        print(f"[Error] File not found: {filepath}", file=sys.stderr)
        return 2

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"[Error] Failed to parse JSON in {filepath}: {e}", file=sys.stderr)
        return 2

    print(BANNER)
    print(f"Inspect Target: {filepath}")

    if isinstance(data, dict) and "passport_hash" in data:
        print(f"Type: MODEL AUDIT PASSPORT")
        print(f"Model ID:        {data.get('identity', {}).get('model_id')}")
        print(f"Domain:          {data.get('identity', {}).get('target_domain')}")
        print(f"Total Receipts:  {data.get('provenance', {}).get('total_receipts')}")
        print(f"Merkle Root:     {data.get('provenance', {}).get('merkle_root')}")
        print(f"Passport Seal:   {data.get('passport_hash')}")
        print(f"Conclusions:     {data.get('evidentiary_conclusions')}")
    elif isinstance(data, dict) and "commit_hash" in data:
        print(f"Type: PREDICTION RECEIPT")
        print(f"Receipt ID:      {data.get('receipt_id')}")
        print(f"Model ID:        {data.get('model_id')}")
        print(f"Target Event:    {data.get('target_event')}")
        print(f"Prediction:      {data.get('prediction')} (Confidence: {data.get('confidence')})")
        print(f"Outcome:         {data.get('actual_outcome')} (Hit: {data.get('is_hit')})")
        print(f"Commit Hash:     {data.get('commit_hash')}")
        print(f"Receipt Hash:    {data.get('receipt_hash')}")
    elif isinstance(data, list):
        print(f"Type: RECEIPT CHAIN")
        print(f"Length:          {len(data):,} Receipts")
        if data:
            print(f"First ID:        {data[0].get('receipt_id')}")
            print(f"Last ID:         {data[-1].get('receipt_id')}")
    return 0


def main(args=None):
    parser = argparse.ArgumentParser(
        prog="pillred",
        description="PILL RED: Universal Cryptographic Evidence & Model Audit CLI."
    )
    parser.add_argument("--version", action="version", version=f"pillred 1.0.0 ({PROTOCOL_VERSION})")

    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # verify
    verify_parser = subparsers.add_parser("verify", help="Zero-Trust Offline Verification of a receipt, chain, or passport")
    verify_parser.add_argument("file", help="Path to JSON file (receipt.json, chain.json, passport.json)")

    # inspect
    inspect_parser = subparsers.add_parser("inspect", help="Display metadata of a PILL RED artifact")
    inspect_parser.add_argument("file", help="Path to JSON file")

    parsed = parser.parse_args(args)

    if parsed.command == "verify":
        sys.exit(verify_file(parsed.file))
    elif parsed.command == "inspect":
        sys.exit(inspect_file(parsed.file))
    else:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()
