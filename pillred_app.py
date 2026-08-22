"""PILL RED Desktop Application Launcher.

Starts the Command Center server and automatically launches the user's default browser
with the PILL RED Causal Verification & Model Evaluation Dashboard.
"""

import os
import sys
import threading
import time
import webbrowser

# Ensure correct base path whether running as script or frozen PyInstaller executable
if getattr(sys, "frozen", False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from command_center.server import start_command_center


def main():
    port = 8080
    print("============================================================")
    print("               🔴 PILL RED COMMAND CENTER")
    print("                    PILLRED-SPEC-1.0")
    print("============================================================")
    print(f"\n[*] Initializing forensic evidence platform on port {port}...")

    # Start server in background daemon thread
    server = start_command_center(port=port)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    time.sleep(0.6)
    target_url = f"http://127.0.0.1:{port}"
    print(f"[✓] Server live! Launching user interface at: {target_url}\n")
    print("[*] Keep this window open while using the dashboard.")
    print("[*] Press Ctrl+C in this window to shut down.\n")

    webbrowser.open(target_url)

    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        print("\n[*] Shutting down PILL RED Command Center.")
        server.server_close()


if __name__ == "__main__":
    main()
