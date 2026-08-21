"""PILL RED Browser Connector & Passive Game Observation Service.

Launches and connects to a dedicated game browser window for passive observation:
- Opens game URL in a dedicated browser instance (Chrome, Edge, or Default)
- Provides attachment telemetry and status tracking
- Strict Observation-Only Boundary: Zero automated betting or wagering interactions
"""

import os
import subprocess
import sys
import threading
import time
import webbrowser
from typing import Any, Dict, Optional


class BrowserConnector:
    """Manages launching and monitoring the external game browser window."""

    def __init__(self):
        self.status: str = "DISCONNECTED"
        self.active_url: Optional[str] = None
        self.launched_time: Optional[float] = None
        self.process: Optional[subprocess.Popen] = None
        self.lock = threading.Lock()

    def launch_browser(self, target_url: str) -> Dict[str, Any]:
        """Launches a dedicated browser session targeting the game URL."""
        with self.lock:
            if not target_url or not target_url.strip():
                target_url = "https://www.google.com"

            self.active_url = target_url.strip()
            self.launched_time = time.time()
            self.status = "LAUNCHING"

            # Attempt to launch Microsoft Edge or Chrome with dedicated app/window flag if on Windows
            launched = False
            if sys.platform == "win32":
                # Check Edge or Chrome paths
                edge_path = os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe")
                chrome_path = os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe")

                browser_exe = edge_path if os.path.exists(edge_path) else (chrome_path if os.path.exists(chrome_path) else None)

                if browser_exe:
                    try:
                        # Launch in app mode with remote debugging port for telemetry
                        cmd = [browser_exe, f"--app={self.active_url}", "--remote-debugging-port=9222"]
                        self.process = subprocess.Popen(cmd)
                        launched = True
                        self.status = "ATTACHED_AND_OBSERVING"
                    except Exception as err:
                        print(f"[!] Warning: App-mode launch failed: {err}. Falling back to default browser.")

            if not launched:
                # Fallback to standard Python webbrowser launch
                try:
                    webbrowser.open_new(self.active_url)
                    self.status = "ATTACHED_AND_OBSERVING"
                    launched = True
                except Exception as err:
                    self.status = "ERROR"
                    return {"success": False, "error": str(err), "status": self.status}

            return {
                "success": True,
                "status": self.status,
                "url": self.active_url,
                "launched_at": self.launched_time,
                "observation_mode": "PASSIVE_READ_ONLY"
            }

    def get_status(self) -> Dict[str, Any]:
        """Returns current browser attachment and observation status."""
        with self.lock:
            return {
                "status": self.status,
                "active_url": self.active_url,
                "launched_time": self.launched_time,
                "observation_mode": "PASSIVE_READ_ONLY",
                "zero_wagering_guarantee": True
            }


# Global connector instance
BROWSER_CONNECTOR = BrowserConnector()
