import random
from datetime import datetime, timedelta

target_size = 100 * 1024 * 1024  # 100 MB
outfile = "sample_100mb.log"

levels = ["INFO", "WARN", "ERROR"]

messages = {
    "INFO": [
        "Application started",
        "User login successful",
        "Request processed",
        "Background job completed",
    ],
    "WARN": [
        "Slow database response",
        "Cache miss detected",
        "Retry attempt scheduled",
    ],
    "ERROR": [
        "Database connection failed",
        "Payment service timeout",
        "Authentication failed",
        "Invalid API response",
        "Disk write error",
    ],
}

ts = datetime(2026, 10, 1, 0, 0, 0)

size = 0
with open(outfile, "w") as f:
    while size < target_size:
        level = random.choices(
            ["INFO", "WARN", "ERROR"],
            weights=[80, 15, 5]
        )[0]

        line = (
            f"{ts:%Y-%m-%d %H:%M:%S} "
            f"{level} "
            f"{random.choice(messages[level])}\n"
        )

        f.write(line)
        size += len(line.encode())
        ts += timedelta(seconds=1)

print(f"Created {outfile} ({size/1024/1024:.1f} MB)")
