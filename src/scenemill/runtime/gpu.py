from __future__ import annotations

import subprocess


def query_nvidia_smi() -> str | None:
    try:
        proc = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=name,memory.total,driver_version",
                "--format=csv,noheader",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    except FileNotFoundError:
        return None
    return proc.stdout.strip() if proc.returncode == 0 else None

