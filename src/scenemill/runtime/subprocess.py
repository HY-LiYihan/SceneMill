from __future__ import annotations

import os
import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class CommandResult:
    cmd: list[str]
    returncode: int
    stdout: str
    log_path: Path


def printable_command(cmd: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in cmd)


def run_command(
    cmd: list[str],
    *,
    cwd: Path | None,
    log_path: Path,
    dry_run: bool = False,
    env_overrides: dict[str, str] | None = None,
) -> CommandResult:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    printable = printable_command(cmd)
    print(f"\n$ {printable}")
    print(f"log: {log_path}")

    if dry_run:
        log_path.write_text(f"[dry-run]\n{printable}\n", encoding="utf-8")
        return CommandResult(cmd=cmd, returncode=0, stdout="", log_path=log_path)

    env = os.environ.copy()
    # If a virtualenv or non-base conda env is active, its bin dir sits first in PATH
    # and causes `conda run -n <other_env>` to resolve to the wrong Python.
    # Strip only the active env's bin dir so conda itself remains reachable.
    active_env = env.pop("VIRTUAL_ENV", None) or env.get("CONDA_PREFIX", "")
    conda_base = env.get("_CONDA_ROOT", "")
    if active_env and active_env != conda_base:
        active_bin = os.path.join(active_env, "bin")
        env["PATH"] = os.pathsep.join(
            p for p in env.get("PATH", "").split(os.pathsep)
            if p != active_bin
        )
    if env_overrides:
        env.update(env_overrides)

    lines: list[str] = []
    with open(log_path, "w", encoding="utf-8") as log_file:
        proc = subprocess.Popen(
            cmd,
            cwd=str(cwd) if cwd else None,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        for line in proc.stdout:
            sys.stdout.write(line)
            sys.stdout.flush()
            log_file.write(line)
            log_file.flush()
            lines.append(line)
        proc.wait()

    stdout = "".join(lines)
    return CommandResult(cmd=cmd, returncode=proc.returncode, stdout=stdout, log_path=log_path)

