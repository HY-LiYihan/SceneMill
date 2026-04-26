from __future__ import annotations


def conda_run(env_name: str, command: list[str]) -> list[str]:
    if not env_name:
        return command
    return ["conda", "run", "-n", env_name, *command]

