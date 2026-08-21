# 🔄 PILL RED v1.0.0 CLEAN-ROOM REPRODUCTION GUIDE

> **Objective:** Enable any independent third-party auditor to build, test, and verify the PILL RED v1.0.0 release from clean state without prior development configuration.

---

## 1. Prerequisites

* **Python:** `>= 3.8` (Tested on 3.8, 3.10, 3.11, 3.12, 3.14)
* **Rust:** `>= 1.70` with `cargo`

---

## 2. Step-by-Step Reproduction

### Step 1: Clone Repository
```bash
git clone https://github.com/pillred/pillred.git
cd pillred
```

### Step 2: Run Python Master Suite (67 Tests)
```bash
python -m unittest tests/test_receipt_protocol.py tests/test_adversarial_attacks.py tests/test_vectors_conformance.py tests/test_statistical_and_economic_engines.py tests/test_scientific_red_team.py tests/test_passport_engine.py tests/test_failure_recovery.py tests/test_sdk_public_api.py tests/test_cli_verifier.py
```
*Expected Output:* `Ran 67 tests in ~2.3s -> OK`

### Step 3: Run Rust Conformance Suite
```bash
cargo test
```
*Expected Output:* `test test_vector_conformance_rust ... ok`

### Step 4: Build Standalone Rust Release Verifier
```bash
cargo build --release --bin pillred-verify
```
*Binary Output:* `target/release/pillred-verify.exe` (or `target/release/pillred-verify` on Linux/macOS)

### Step 5: Build and Install Distribution Wheel
```bash
python -m pip install build
python -m build
pip install dist/pillred-1.0.0-py3-none-any.whl
```

### Step 6: Zero-Trust Offline Verification
Verify valid test vectors (Exit Code `0` expected):
```bash
pillred verify test_vectors/valid/passport_001.json
```

Verify tampered test vectors (Exit Code `1` expected):
```bash
pillred verify test_vectors/invalid/tampered_passport.json
```

---

## 3. Verifying Cryptographic SHA-256 Checksums

Compare local artifacts against the release checksums:
```bash
# Windows PowerShell
Get-FileHash dist/pillred-1.0.0-py3-none-any.whl -Algorithm SHA256
Get-FileHash dist/pillred-1.0.0.tar.gz -Algorithm SHA256

# Linux / macOS
sha256sum dist/*
```
Verify matching hashes with `release/checksums/SHA256SUMS.txt`.
