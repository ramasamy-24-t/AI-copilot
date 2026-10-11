"""Railway entrypoint: migrate, start worker, then serve the API."""
from __future__ import annotations

import os
import subprocess
import sys


def main() -> None:
    storage = os.environ.get("STORAGE_DIR", "/data/storage")
    os.makedirs(storage, exist_ok=True)

    subprocess.check_call(
        [sys.executable, "-m", "alembic", "-c", "backend/alembic.ini", "upgrade", "head"]
    )
    worker = subprocess.Popen([sys.executable, "-m", "app.worker"])
    try:
        port = os.environ.get("PORT", "8000")
        # Bind IPv4. Railway private DNS currently returns IPv4 addresses to nginx.
        os.execvp(
            sys.executable,
            [
                sys.executable,
                "-m",
                "uvicorn",
                "app.main:app",
                "--host",
                "0.0.0.0",
                "--port",
                port,
            ],
        )
    finally:
        worker.terminate()


if __name__ == "__main__":
    main()
