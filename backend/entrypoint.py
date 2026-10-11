"""Root entrypoint: fix volume ownership, then drop to the health user."""
from __future__ import annotations

import os
import pwd
import sys


def _chown_tree(path: str, uid: int, gid: int) -> None:
    os.makedirs(path, exist_ok=True)
    for root, dirs, files in os.walk(path):
        os.chown(root, uid, gid)
        for name in dirs:
            os.chown(os.path.join(root, name), uid, gid)
        for name in files:
            os.chown(os.path.join(root, name), uid, gid)


def main() -> None:
    user = pwd.getpwnam("health")
    storage = os.environ.get("STORAGE_DIR", "/data/storage")
    _chown_tree(storage, user.pw_uid, user.pw_gid)
    os.chown("/data", user.pw_uid, user.pw_gid)

    os.setgid(user.pw_gid)
    os.setuid(user.pw_uid)
    os.environ["HOME"] = user.pw_dir
    os.chdir("/app")

    os.execvp(sys.executable, [sys.executable, "/app/backend/start_railway.py"])


if __name__ == "__main__":
    main()
