"""
HID scanner helper.

HIDScanner provides a simple, non-blocking interface to barcode scanners that act
as HID keyboard devices. It uses the 'evdev' library when available and falls
back to reading lines from stdin if evdev or a suitable device is not present.

Usage:
  scanner = HIDScanner(device_path=None)  # optional HID device path via HID_DEVICE env var
  code = scanner.get_scan_nowait()  # returns a scanned string or None
  scanner.stop()  # stop background thread on shutdown
"""

import sys
import threading
import queue
import time
import os

try:
    from evdev import InputDevice, list_devices, categorize, ecodes
    HAS_EVDEV = True
except Exception:
    InputDevice = None
    list_devices = None
    categorize = None
    ecodes = None
    HAS_EVDEV = False


class HIDScanner:
    def __init__(self, device_path: str | None = None, queue_size: int = 32):
        self.queue: "queue.Queue[str]" = queue.Queue(maxsize=queue_size)
        self._running = True
        self._device_path = device_path or os.getenv("HID_DEVICE", None)
        self._thread = threading.Thread(target=self._read_loop, daemon=True)
        self._thread.start()

    def _find_device(self):
        if not HAS_EVDEV:
            return None
        try:
            if self._device_path:
                return InputDevice(self._device_path)
            for path in list_devices():
                try:
                    dev = InputDevice(path)
                except Exception:
                    continue
                caps = dev.capabilities()
                # Accept any device that reports EV_KEY capability (keyboard-like)
                if ecodes.EV_KEY in caps:
                    return dev
        except Exception:
            return None
        return None

    def _read_loop(self):
        # If evdev not available or no device found, fall back to stdin lines.
        dev = self._find_device()
        if not dev:
            # fallback: read newline-terminated scans from stdin
            while self._running:
                try:
                    line = sys.stdin.readline()
                except Exception:
                    line = ""
                if not line:
                    time.sleep(0.05)
                    continue
                s = line.strip()
                if s:
                    try:
                        self.queue.put_nowait(s)
                    except queue.Full:
                        pass
            return

        # Read events from evdev device and accumulate characters until ENTER
        buf: list[str] = []
        shift = False
        try:
            for event in dev.read_loop():
                if not self._running:
                    break
                if event.type != ecodes.EV_KEY:
                    continue
                keyevent = categorize(event)
                # keyevent.keycode can be a list or a string
                keycode = keyevent.keycode
                if isinstance(keycode, list):
                    keycode = keycode[0]
                # only consider key down events (avoid repeats/ups producing chars twice)
                if keyevent.keystate == keyevent.key_down:
                    if keycode in ("KEY_LEFTSHIFT", "KEY_RIGHTSHIFT"):
                        shift = True
                        continue
                    if keycode == "KEY_ENTER":
                        if buf:
                            try:
                                self.queue.put_nowait("".join(buf))
                            except queue.Full:
                                pass
                            buf = []
                        continue
                    ch = self._map_keycode_to_char(keycode, shift)
                    if ch:
                        buf.append(ch)
                elif keyevent.keystate == keyevent.key_up:
                    if keycode in ("KEY_LEFTSHIFT", "KEY_RIGHTSHIFT"):
                        shift = False
        except Exception:
            # On any device/read error, simply exit the loop (thread will end).
            return

    def _map_keycode_to_char(self, keycode: str, shift: bool) -> str | None:
        if not keycode:
            return None
        if not keycode.startswith("KEY_"):
            return None
        k = keycode[4:]
        # Letters
        if len(k) == 1 and k.isalpha():
            ch = k.lower()
            return ch.upper() if shift else ch
        # Digits (KEY_1 .. KEY_0)
        if k.isdigit():
            return k
        # Numeric row special keys when shift is not pressed (basic set)
        specials = {
            "MINUS": "-",
            "EQUAL": "=",
            "SLASH": "/",
            "DOT": ".",
            "COMMA": ",",
            "SPACE": " ",
            "KPENTER": "\n",
            "ENTER": "\n",
            "DOT": ".",
            "SEMICOLON": ";",
            "APOSTROPHE": "'",
            "LEFTBRACE": "[",
            "RIGHTBRACE": "]",
            "BACKSLASH": "\\",
        }
        val = specials.get(k)
        if val:
            return val
        # Fallback: try to use the trailing fragment as a lower-case token
        if k.isalpha():
            ch = k.lower()
            return ch.upper() if shift else ch
        return None

    def get_scan_nowait(self) -> str | None:
        try:
            return self.queue.get_nowait()
        except queue.Empty:
            return None

    def stop(self):
        self._running = False
        try:
            self._thread.join(timeout=1.0)
        except Exception:
            pass
