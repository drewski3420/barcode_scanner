import os
import time
from datetime import datetime, timedelta

import config
from display import create_backend
import fetcher
import ui
import input_hid

# Create display backend once at runtime
backend = create_backend()
# Create HID scanner once at runtime (device path via HID_DEVICE env var)
scanner = input_hid.HIDScanner(device_path=os.getenv("HID_DEVICE", None))

def run_main_loop():
  print("Ready! Type a URL and press Enter (simulating QR scan)...")
  running = True
  current_data = None
  last_update = None

  try:
    while running:
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
        rec = fetcher.fetch_record(var_in)
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
    # Ensure backend cleanup if provided
    try:
      backend.quit()
    except Exception:
      pass


if __name__ == "__main__":
  run_main_loop()
