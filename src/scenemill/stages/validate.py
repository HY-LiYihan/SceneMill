from __future__ import annotations

from pathlib import Path
from typing import Any

from scenemill.adapters.colmap import list_images, validate_colmap_dataset
from scenemill.adapters.isaac_usd import inspect_usd_prims, validate_usdz_alignment


def validate_images(images_dir: Path) -> dict[str, Any]:
    images = list_images(images_dir)
    return {"ok": True, "count": len(images), "path": str(images_dir)}


def validate_outputs(
    *,
    images_dir: Path | None = None,
    dataset_root: Path | None = None,
    usdz_paths: list[Path] | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {}
    if images_dir:
        result["images"] = validate_images(images_dir)
    if dataset_root:
        result["colmap"] = validate_colmap_dataset(dataset_root)
    if usdz_paths:
        result["usdz"] = []
        for path in usdz_paths:
            if not path.exists():
                result["usdz"].append({"path": str(path), "ok": False, "missing": True})
                continue
            alignment = validate_usdz_alignment(path)
            prims = inspect_usd_prims(path)
            result["usdz"].append({"path": str(path), "alignment": alignment, "prims": prims})
    return result

