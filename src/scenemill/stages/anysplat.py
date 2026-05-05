from __future__ import annotations

from pathlib import Path
from typing import Any

from scenemill.adapters import anysplat
from scenemill.adapters.isaac_usd import inject_initial_camera, rewrite_usdz_alignment
from scenemill.config import resolve_project_path
from scenemill.registry import EXPORT_FORMATS
from scenemill.runtime.subprocess import CommandResult, run_command
from scenemill.schemas.artifacts import AnySplatScene, FrameSet


def _optional_path(value: Any) -> Path | None:
    return Path(str(value)) if value else None


def _script_path() -> Path:
    return Path(__file__).resolve().parents[3] / "scripts" / "run_anysplat.py"


def _dry_run_manifest(frames: FrameSet, workspace: Path, config: dict) -> dict[str, Any]:
    any_ws = workspace / "anysplat"
    return {
        "dry_run": True,
        "project": "AnySplat",
        "input_images_dir": str(frames.images_dir),
        "image_count": frames.count,
        "model_id": str(config.get("anysplat", {}).get("model_id", "lhjiang/anysplat")),
        "artifacts": {
            "gaussian_ply": str(any_ws / "gaussians.ply"),
            "camera_intrinsics": str(any_ws / "camera_intrinsics.npy"),
            "camera_intrinsics_pixels": str(any_ws / "camera_intrinsics_pixels.npy"),
            "camera_extrinsics": str(any_ws / "camera_extrinsics.npy"),
        },
        "camera": {
            "alignment_target": "crop_448",
            "network_resolution": [448, 448],
            "preprocessing": [],
        },
    }


def run_anysplat_scene(
    *,
    config: dict,
    frames: FrameSet,
    workspace: Path,
    dry_run: bool,
) -> tuple[AnySplatScene, dict[str, Any]]:
    any_ws = workspace / str(config.get("anysplat", {}).get("workspace_name", "anysplat"))
    any_ws.mkdir(parents=True, exist_ok=True)

    inference_cmd = anysplat.build_inference_command(
        config=config,
        input_images_dir=frames.images_dir,
        workspace=any_ws,
        script_path=_script_path(),
    )
    inference_result = run_command(
        inference_cmd,
        cwd=resolve_project_path(config.get("anysplat", {}).get("root", "third_party/anysplat")),
        log_path=workspace / "logs" / "anysplat_inference.log",
        dry_run=dry_run,
        env_overrides=anysplat.isolated_env_overrides(),
    )
    if inference_result.returncode != 0:
        raise RuntimeError(f"AnySplat inference failed. Inspect {inference_result.log_path}")

    manifest_path = any_ws / "anysplat_manifest.yaml"
    if dry_run:
        anysplat.write_manifest(manifest_path, _dry_run_manifest(frames, workspace, config))

    any_manifest = anysplat.load_manifest(manifest_path)
    artifacts = any_manifest.get("artifacts", {}) if isinstance(any_manifest.get("artifacts"), dict) else {}
    gaussian_ply = _optional_path(artifacts.get("gaussian_ply"))
    if gaussian_ply is None:
        raise ValueError(f"AnySplat manifest missing artifacts.gaussian_ply: {manifest_path}")

    export_dir = Path(config.get("export", {}).get("output_dir") or (workspace / "exports")).resolve()
    export_dir.mkdir(parents=True, exist_ok=True)
    grut_repo = resolve_project_path(config.get("runtime", {}).get("grut_repo", "third_party/3dgrut"))

    export_results: dict[str, CommandResult] = {}
    export_artifacts: dict[str, str] = {}
    exports: dict[str, Path] = {}
    for fmt in anysplat.export_formats(config):
        if fmt not in EXPORT_FORMATS:
            raise ValueError(f"Unsupported AnySplat export format: {fmt}")
        output = export_dir / anysplat.export_filename(fmt)
        cmd = anysplat.build_transcode_command(
            config=config,
            gaussian_ply=gaussian_ply,
            output=output,
            export_format=fmt,
        )
        result = run_command(
            cmd,
            cwd=grut_repo,
            log_path=workspace / "logs" / f"anysplat_export_{fmt}.log",
            dry_run=dry_run,
            env_overrides=anysplat.isolated_env_overrides(),
        )
        export_results[fmt] = result
        export_artifacts[fmt] = str(output)
        exports[fmt] = output
        if result.returncode != 0:
            raise RuntimeError(f"AnySplat export failed for {fmt}. Inspect {result.log_path}")
        if not dry_run and output.exists():
            alignment = rewrite_usdz_alignment(output)
            if not alignment["ok"]:
                raise RuntimeError(f"USDZ alignment failed after rewrite: {output}")
            inject_initial_camera(output)

    any_manifest.setdefault("artifacts", {})["exports"] = export_artifacts
    any_manifest["export_options"] = {
        "apply_coordinate_transform": bool(config.get("anysplat", {}).get("apply_coordinate_transform", True)),
        "coordinate_transform_convention": "3dgrut_to_usdz_omniverse",
        "lightfield_render_order_hint": config.get("anysplat", {}).get(
            "lightfield_render_order_hint", "cameraDistance"
        ),
        "linear_srgb": bool(config.get("anysplat", {}).get("linear_srgb", False)),
    }
    anysplat.write_manifest(manifest_path, any_manifest)

    scene = AnySplatScene(
        workspace=any_ws,
        manifest_path=manifest_path,
        gaussian_ply=gaussian_ply,
        exports=exports,
        camera_intrinsics=_optional_path(artifacts.get("camera_intrinsics")),
        camera_intrinsics_pixels=_optional_path(artifacts.get("camera_intrinsics_pixels")),
        camera_extrinsics=_optional_path(artifacts.get("camera_extrinsics")),
        camera_metadata=any_manifest.get("camera") if isinstance(any_manifest.get("camera"), dict) else None,
    )
    diagnostics = {
        "workspace": str(any_ws),
        "manifest": str(manifest_path),
        "inference": {"returncode": inference_result.returncode, "log": str(inference_result.log_path)},
        "exports": {
            fmt: {"returncode": result.returncode, "log": str(result.log_path), "path": export_artifacts[fmt]}
            for fmt, result in export_results.items()
        },
    }
    return scene, diagnostics
