from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml


ConfigDict = dict[str, Any]
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def deep_merge(base: ConfigDict, override: ConfigDict) -> ConfigDict:
    merged = deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = deepcopy(value)
    return merged


def load_yaml(path: Path) -> ConfigDict:
    if not path.exists():
        raise FileNotFoundError(f"Config not found: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Config must be a YAML mapping: {path}")
    return data


def load_config(config_path: Path, *, input_path: Path | None = None, workspace: Path | None = None) -> ConfigDict:
    config_path = config_path.resolve()
    config = load_yaml(config_path)
    config["_config_path"] = str(config_path)

    if input_path is not None:
        config.setdefault("input", {})["path"] = str(input_path.resolve())
    if workspace is not None:
        config.setdefault("runtime", {})["workspace"] = str(workspace.resolve())

    return config


def get_config(config: ConfigDict, dotted_key: str, default: Any = None) -> Any:
    current: Any = config
    for key in dotted_key.split("."):
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


def require_config(config: ConfigDict, dotted_key: str) -> Any:
    value = get_config(config, dotted_key)
    if value is None:
        raise ValueError(f"Missing required config key: {dotted_key}")
    return value


def resolve_project_path(value: str | Path) -> Path:
    path = Path(value).expanduser()
    if path.is_absolute():
        return path.resolve()
    return (PROJECT_ROOT / path).resolve()


def parse_int_list(value: Any, *, key: str) -> list[int]:
    if value is None:
        return []
    if isinstance(value, str):
        parts = [part.strip() for part in value.split(",") if part.strip()]
        return [int(part) for part in parts]
    if isinstance(value, list):
        return [int(item) for item in value]
    raise ValueError(f"{key} must be a comma-separated string or list of integers")
