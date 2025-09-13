import os
import time
from datetime import datetime, timedelta
import signal
import threading

import config
from display import create_backend
import fetcher
import ui
import input_hid
from flask import Flask, jsonify

# Create display backend once at runtime
backend = create_backend()
# Create HID scanner once at runtime (device path via HID_DEVICE env var)
scanner = input_hid.HIDScanner(device_path=config.HID_DEVICE) #os.getenv("HID_DEVICE", None))
# Event set by signal handler so run_main_loop can exit cleanly when systemd stops the service.
stop_event = threading.Event()
def _handle_signal(signum, frame):
  print(f"Received signal {signum}, shutting down.")
  stop_event.set()
# Ensure SIGTERM (systemd stop) and SIGINT are handled.
signal.signal(signal.SIGTERM, _handle_signal)
signal.signal(signal.SIGINT, _handle_signal)

# Simple health endpoint served in a background thread so it doesn't interfere
# with the main display/input loop. Returns a small JSON object describing
# whether the app appears to be running and whether the HID scanner thread is alive.
_health_app = Flask(__name__)

@_health_app.route("/health")
def _health():
  try:
    scanner_alive = getattr(scanner, "_thread", None) is not None and scanner._thread.is_alive()
  except Exception:
    scanner_alive = False
  backend_name = getattr(getattr(backend, "__class__", None), "__name__", None)
  return jsonify({
    "status": "ok" if not stop_event.is_set() else "stopping",
    "running": not stop_event.is_set(),
    "scanner_alive": scanner_alive,
    "backend": backend_name,
    "pid": os.getpid()
  })

def _run_health_server():
  # Run a small threaded Flask server on port 8000 bound to all interfaces.
  # Use threaded=True to allow concurrent requests; runs in a daemon thread.
  _health_app.run(host="0.0.0.0", port=8000, threaded=True)

_health_thread = threading.Thread(target=_run_health_server, daemon=True)
_health_thread.start()

def run_main_loop():
  #print("Ready! Type a URL and press Enter (simulating QR scan)...")
  running = True
  current_data = None
  last_update = None

  try:
    while running and not stop_event.is_set():
      # Handle pygame events if applicable
      if not config.USE_TFT and hasattr(backend, "pygame"):
        for event in backend.pygame.event.get():
          if event.type == backend.pygame.QUIT:
            running = False

      # Timeout handling: fade to idle and clear state
      if current_data and last_update:
        if datetime.now() - last_update > timedelta(minutes=config.TIMEOUT_MINUTES):
          try:
            album, artist, section, code, cover_img = current_data
            curr_img = ui.display_album(album, artist, section, code, cover_img)
            ui.fade_to_idle(curr_img, backend)
          except Exception as e:
            print(f"Error during fade to idle: {e}")
          current_data = None
          last_update = None

      # Draw current or idle
      if not current_data:
        backend.display(ui.draw_idle())
      else:
        album, artist, section, code, cover_img = current_data
        backend.display(ui.display_album(album, artist, section, code, cover_img))

      # Non-blocking input from HID scanner
      try:
        var_in = scanner.get_scan_nowait()
      except Exception as e:
        var_in = None

      if var_in:
        #print(f"Fetching {var_in}")
        rec = fetcher.fetch_record(var_in)
        #print(rec)
        if rec:
          current_data = (rec.title, rec.artists, rec.section, rec.code, rec.cover_img)
          last_update = datetime.now()
        else:
          print("Failed to fetch record for input:", var_in)
          current_data = None

      time.sleep(0.1)
  except KeyboardInterrupt:
    pass
  except Exception as e:
    print(f"Error in main loop: {e}")
  finally:
    # Ensure scanner and backend cleanup if provided. scanner.stop() is best-effort.
    try:
      scanner.stop()
    except Exception:
      pass
    try:
      backend.quit()
    except Exception:
      pass


if __name__ == "__main__":
  run_main_loop()
