"""
PILL RED Zero-Trust Offline Receipt Verifier (CLI Tool)
Usage:
    python tools/verify_receipt.py <path_to_receipts.json>
"""

import json
import sys
import os

# Add root directory to pythonpath
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pillred.protocol.verifier import ZeroTrustVerifier


def main():
    if len(sys.argv) < 2:
        print("Usage: python tools/verify_receipt.py <path_to_receipts.json>")
        sys.exit(1)

    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"[-] Error: File '{file_path}' does not exist.")
        sys.exit(1)

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    receipts = data if isinstance(data, list) else [data]
    print(f"\n[*] 🔴 PILL RED Zero-Trust Offline Audit")
    print(f"[*] Auditing {len(receipts)} receipt(s) in: {file_path}")
    print("=" * 60)

    is_valid, violations, merkle_root = ZeroTrustVerifier.verify_chain(receipts)

    for idx, r in enumerate(receipts, start=1):
        status_icon = "✓" if (r.get("is_hit") is not None) else "🔒"
        res_str = f"HIT" if r.get("is_hit") else "MISS"
        print(f"[{status_icon}] Receipt #{idx:03d} | ID: {r.get('receipt_id')} | Pred: {r.get('prediction')} vs Actual: {r.get('actual_outcome')} ({res_str})")

    print("=" * 60)
    if is_valid:
        print(f"[✓] PROVENANCE AUDIT PASSED: 100% Tamper-Evident & Causal Integrity Intact")
        print(f"[*] Verified Merkle Root: {merkle_root}")
        print(f"[*] Temporal Precedence: Strictly Verified (t_commit < t_event)")
    else:
        print(f"[✗] PROVENANCE AUDIT FAILED! {len(violations)} Violation(s) Detected:")
        for v in violations:
            print(f"    - {v}")

    print("=" * 60)
    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()
