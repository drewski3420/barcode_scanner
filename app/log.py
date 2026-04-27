from datetime import datetime

def print_to_log(*args):
  timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  message = " ".join(str(a) for a in args)
  print(f"{timestamp} {message}", flush=True)
