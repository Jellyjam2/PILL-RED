"""Local IPC & Dock Service for RED PILL DOCK Integration.

Provides lightweight HTTP/JSON endpoints for a Rust GUI, Tauri, or browser extension
to stream observed spins to the PILL RED Eyes adapter and query live audit statistics.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import threading
import time
from typing import Any, Dict, Optional

from rng_audit.eyes.adapter import ObservationAdapter, RawObservation
from rng_audit.statistics.session_auditor import MultiSessionAuditor


class DockRequestHandler(BaseHTTPRequestHandler):
    """Handles REST/JSON requests from RED PILL DOCK."""

    adapter = ObservationAdapter()
    observed_records = []
    lock = threading.Lock()

    def do_POST(self):
        """Endpoint to receive new spin observation from DOCK GUI."""
        if self.path == "/api/observe_spin":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            try:
                data = json.loads(body.decode("utf-8"))
                raw = RawObservation(
                    timestamp=data.get("timestamp", time.time()),
                    source_type=data.get("source_type", "dock_gui"),
                    game_title=data.get("game_title", "Unknown"),
                    session_id=data.get("session_id", "DOCK-SESS-001"),
                    raw_symbols=data.get("symbols", []),
                    payout_multiplier=float(data.get("payout_multiplier", 0.0)),
                    bonus_flag=bool(data.get("bonus_event", False)),
                    raw_metadata=data.get("metadata", {})
                )

                with self.lock:
                    rec = self.adapter.normalize(raw)
                    self.observed_records.append(rec)

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                resp = {
                    "status": "RECORDED",
                    "spin_index": rec.spin_index,
                    "total_observed": len(self.observed_records)
                }
                self.wfile.write(json.dumps(resp).encode("utf-8"))

            except Exception as e:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        """Endpoint to query current audit status and statistics."""
        if self.path == "/api/audit_status":
            with self.lock:
                n = len(self.observed_records)
                records = list(self.observed_records)

            if n < 50:
                resp = {
                    "status": "COLLECTING_DATA",
                    "total_spins": n,
                    "minimum_required": 50,
                    "message": "Collecting baseline observations before triggering audit."
                }
            else:
                # Run blinded session audit on collected records (50% discovery / 50% validation)
                split_idx = n // 2
                res = MultiSessionAuditor.audit_game_sessions(
                    discovery_records=records[:split_idx],
                    validation_records=records[split_idx:],
                    alphabet_size=10,
                    house_edge_fraction=0.04
                )
                resp = {
                    "status": "AUDIT_ACTIVE",
                    "total_spins": n,
                    "verdict": res["verdict"],
                    "validation_hit_rate": res["validation_hit_rate"],
                    "baseline_null_rate": res["baseline_null_rate"],
                    "binomial_p_value": res["binomial_p_value"],
                    "wilson_ci_99": res["wilson_ci_99"],
                    "net_expected_value": res["net_expected_value"],
                    "rationale": res["rationale"]
                }

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(resp).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        """Suppress default stdout logging for clean CLI operation."""
        pass


def run_dock_server(port: int = 8765) -> HTTPServer:
    """Starts the Dock service on localhost."""
    server = HTTPServer(("127.0.0.1", port), DockRequestHandler)
    print(f"[*] RED PILL DOCK IPC Service running at http://127.0.0.1:{port}")
    return server
