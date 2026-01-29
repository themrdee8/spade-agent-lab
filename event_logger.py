from datetime import datetime

def log_event(percepts):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] EVENT LOG:")
    print(f"  Temperature: {percepts['temperature']}°C")
    print(f"  Smoke Level: {percepts['smoke_level']}")
    print(f"  Damage Severity: {percepts['damage_severity']}")
    print("-" * 40)