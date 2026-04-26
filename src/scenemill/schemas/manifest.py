from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from scenemill import __version__


def new_manifest(*, config: dict[str, Any], workspace: Path) -> dict[str, Any]:
    return {
        "project": "SceneMill",
        "version": __version__,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "workspace": str(workspace),
        "config_path": config.get("_config_path"),
        "input": config.get("input", {}),
        "runtime": config.get("runtime", {}),
        "stages": {},
        "retries": [],
        "artifacts": {},
        "validation": {},
    }


def write_manifest(manifest: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True), encoding="utf-8")


def update_stage(manifest: dict[str, Any], stage: str, data: dict[str, Any]) -> None:
    existing = manifest.setdefault("stages", {}).setdefault(stage, {})
    existing.update(data)
    existing["updated_at"] = datetime.now(timezone.utc).isoformat()


def set_artifact(manifest: dict[str, Any], key: str, value: Any) -> None:
    manifest.setdefault("artifacts", {})[key] = value


def append_retry(manifest: dict[str, Any], data: dict[str, Any]) -> None:
    entry = dict(data)
    entry["time"] = datetime.now(timezone.utc).isoformat()
    manifest.setdefault("retries", []).append(entry)

