"""
PILL RED Desktop Application Launcher (Native Window Mode)

Launches the background Command Center engine and presents a clean, dedicated
native Windows desktop interface with custom logo and zero terminal console.
"""

import os
import sys
import threading
import time
import urllib.request
import webbrowser

# Ensure project root is in sys.path
BASE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from command_center.server import start_command_center


def find_and_start_server(start_port: int = 8080, max_attempts: int = 20):
    """Binds to the first available port and starts serving in the background."""
    for offset in range(max_attempts):
        port = start_port + offset
        try:
            server = start_command_center(port=port)
            server_thread = threading.Thread(target=server.serve_forever, daemon=True)
            server_thread.start()
            return server, port
        except OSError:
            continue
    raise RuntimeError("Could not bind Command Center to any available port.")


def wait_for_server(url: str, timeout: float = 5.0):
    start = time.time()
    while time.time() - start < timeout:
        try:
            with urllib.request.urlopen(f"{url}/api/state", timeout=1.0) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            time.sleep(0.1)
    return False


def main():
    # 1. Bind and start backend server
    try:
        server, port = find_and_start_server(start_port=8080)
        server_url = f"http://127.0.0.1:{port}"
    except Exception as e:
        server_url = "http://127.0.0.1:8080"

    # 2. Wait for server readiness
    wait_for_server(server_url, timeout=4.0)

    # 3. Resolve icon path
    icon_path = os.path.join(BASE_DIR, "assets", "icon.ico")
    if not os.path.exists(icon_path):
        icon_path = None

    # 4. Launch clean native desktop application window
    try:
        import webview
        window = webview.create_window(
            title="PILL RED // Forensic Intelligence",
            url=server_url,
            width=1280,
            height=850,
            min_size=(1024, 700),
            background_color="#09090b",
            text_select=True
        )
        webview.start(icon=icon_path)
    except Exception as e:
        # Fallback to default browser if native webview fails
        webbrowser.open(server_url)
        while True:
            time.sleep(1)


if __name__ == "__main__":
    main()
