from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

from scenemill.config import get_config, resolve_project_path
from scenemill.runtime.conda import conda_run


def build_inference_command(
    *,
    config: dict,
    input_images_dir: Path,
    workspace: Path,
    script_path: Path,
) -> list[str]:
    anysplat = config.get("anysplat", {})
    runtime = config.get("runtime", {})
    cmd = [
        str(script_path),
        "--anysplat-root",
        str(resolve_project_path(anysplat.get("root", "third_party/anysplat"))),
        "--input-images-dir",
        str(input_images_dir.resolve()),
        "--workspace",
        str(workspace.resolve()),
        "--model-id",
        str(anysplat.get("model_id", "lhjiang/anysplat")),
    ]
    if bool(anysplat.get("direct_single_image", True)):
        cmd.append("--direct-single-image")
    if bool(anysplat.get("save_preview", False)):
        cmd.append("--save-preview")
    return conda_run(str(runtime.get("anysplat_env", anysplat.get("conda_env", "anysplat"))), cmd)


def export_formats(config: dict) -> list[str]:
    anysplat = config.get("anysplat", {})
    formats = anysplat.get("export_formats")
    if formats is None:
        formats = get_config(config, "export.formats", ["nurec", "lightfield"])
    return [str(item).lower() for item in formats]


def export_filename(export_format: str) -> str:
    suffix = "lightfield_isaac" if export_format == "lightfield" else f"{export_format}_isaac"
    return f"scene_{suffix}.usdz"


def build_transcode_command(
    *,
    config: dict,
    gaussian_ply: Path,
    output: Path,
    export_format: str,
) -> list[str]:
    anysplat = config.get("anysplat", {})
    runtime = config.get("runtime", {})
    script_format = "lightfield" if export_format == "lightfield" else export_format
    cmd = [
        "python",
        "-m",
        "threedgrut.export.scripts.transcode",
        str(gaussian_ply.resolve()),
        "-o",
        str(output.resolve()),
        "--format",
        script_format,
    ]
    if bool(anysplat.get("apply_coordinate_transform", True)):
        cmd.append("--apply-coordinate-transform")
    if export_format == "lightfield":
        hint = anysplat.get("lightfield_render_order_hint", "cameraDistance")
        if hint:
            cmd.extend(["--render-order-hint", str(hint)])
        if bool(anysplat.get("linear_srgb", False)):
            cmd.append("--linear-srgb")
    return conda_run(str(runtime.get("grut_env", "scenemill")), cmd)


def isolated_env_overrides() -> dict[str, str]:
    return {
        "PYTHONNOUSERSITE": "1",
        "HF_HUB_DISABLE_XET": os.environ.get("HF_HUB_DISABLE_XET", "1"),
    }


def load_manifest(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"AnySplat manifest not found: {path}")
    manifest = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(manifest, dict):
        raise ValueError(f"AnySplat manifest must be a YAML mapping: {path}")
    return manifest


def write_manifest(path: Path, manifest: dict[str, Any]) -> None:
    path.write_text(yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True), encoding="utf-8")
