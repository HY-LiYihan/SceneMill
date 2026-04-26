from __future__ import annotations

from pathlib import Path
from typing import Any

from scenemill.adapters.colmap import prepare_colmap_training_dataset, validate_colmap_dataset
from scenemill.config import get_config, load_config, parse_int_list
from scenemill.runtime.gpu import query_nvidia_smi
from scenemill.runtime.oom_retry import looks_like_oom
from scenemill.schemas.manifest import append_retry, new_manifest, set_artifact, update_stage, write_manifest
from scenemill.stages.export import run_exports
from scenemill.stages.geometry import run_geometry
from scenemill.stages.ingest import run_ingest
from scenemill.stages.preprocess import sample_frames_to_colmap_dataset
from scenemill.stages.train import run_train
from scenemill.stages.validate import validate_outputs


def _manifest_path(workspace: Path) -> Path:
    return workspace / "scene_manifest.yaml"


def _retry_steps(config: dict[str, Any]) -> list[int]:
    retry_steps = parse_int_list(get_config(config, "retry.frame_steps", [1, 2, 5, 10, 15, 20]), key="retry.frame_steps")
    if not retry_steps:
        raise ValueError("retry.frame_steps must not be empty")
    return retry_steps


def run_pipeline(
    *,
    config_path: Path,
    input_path: Path | None = None,
    workspace: Path | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    config = load_config(config_path, input_path=input_path, workspace=workspace)
    workspace_path = Path(get_config(config, "runtime.workspace", workspace or "runs/scenemill_run")).resolve()
    workspace_path.mkdir(parents=True, exist_ok=True)
    (workspace_path / "logs").mkdir(parents=True, exist_ok=True)

    manifest = new_manifest(config=config, workspace=workspace_path)
    manifest["dry_run"] = dry_run
    manifest["gpu"] = query_nvidia_smi()
    write_manifest(manifest, _manifest_path(workspace_path))

    frames = run_ingest(config, workspace_path)
    update_stage(
        manifest,
        "ingest",
        {"frames_root": str(frames.root), "images_dir": str(frames.images_dir), "image_count": frames.count},
    )
    set_artifact(manifest, "frames_dir", str(frames.root))
    write_manifest(manifest, _manifest_path(workspace_path))

    last_error = ""
    for frame_step in _retry_steps(config):
        print(f"\n=== SceneMill frame_step={frame_step} ===")
        dataset = sample_frames_to_colmap_dataset(frames.images_dir, workspace_path, frame_step)
        update_stage(
            manifest,
            "preprocess",
            {
                "frame_step": frame_step,
                "dataset_root": str(dataset.root),
                "sampled_images": dataset.image_count,
            },
        )
        set_artifact(manifest, "colmap_dataset", str(dataset.root))
        write_manifest(manifest, _manifest_path(workspace_path))

        geometry_result = run_geometry(config=config, dataset=dataset, workspace=workspace_path, dry_run=dry_run)
        if geometry_result and geometry_result.returncode != 0:
            last_error = geometry_result.stdout
            update_stage(
                manifest,
                "geometry",
                {"returncode": geometry_result.returncode, "log": str(geometry_result.log_path), "frame_step": frame_step},
            )
            if looks_like_oom(last_error, geometry_result.returncode):
                append_retry(manifest, {"stage": "geometry", "frame_step": frame_step, "reason": "oom"})
                write_manifest(manifest, _manifest_path(workspace_path))
                continue
            write_manifest(manifest, _manifest_path(workspace_path))
            raise RuntimeError(f"Geometry stage failed. Inspect {geometry_result.log_path}")

        if not dry_run:
            validate_colmap_dataset(dataset.root)
            train_dataset_root, train_prep = prepare_colmap_training_dataset(dataset.root, workspace_path, config)
        else:
            train_dataset_root = dataset.root
            train_prep = {"dataset_root": str(dataset.root), "dry_run": True}
        update_stage(
            manifest,
            "geometry",
            {
                "backend": get_config(config, "geometry.backend", "da3"),
                "returncode": geometry_result.returncode if geometry_result else 0,
                "log": str(geometry_result.log_path) if geometry_result else None,
                "frame_step": frame_step,
            },
        )
        update_stage(manifest, "train_prepare", train_prep)
        write_manifest(manifest, _manifest_path(workspace_path))

        train_result, checkpoint = run_train(
            config=config,
            dataset_root=train_dataset_root,
            workspace=workspace_path,
            dry_run=dry_run,
        )
        update_stage(
            manifest,
            "train",
            {
                "returncode": train_result.returncode,
                "log": str(train_result.log_path),
                "checkpoint": str(checkpoint) if checkpoint else None,
                "frame_step": frame_step,
            },
        )
        write_manifest(manifest, _manifest_path(workspace_path))

        if train_result.returncode != 0:
            last_error = train_result.stdout
            if looks_like_oom(last_error, train_result.returncode):
                append_retry(manifest, {"stage": "train", "frame_step": frame_step, "reason": "oom"})
                write_manifest(manifest, _manifest_path(workspace_path))
                continue
            raise RuntimeError(f"Train stage failed. Inspect {train_result.log_path}")

        if checkpoint is None:
            raise RuntimeError(f"Train stage finished without a checkpoint. Inspect {train_result.log_path}")

        set_artifact(manifest, "checkpoint", str(checkpoint))
        write_manifest(manifest, _manifest_path(workspace_path))

        export_results = run_exports(
            config=config,
            checkpoint=checkpoint,
            dataset_root=train_dataset_root,
            workspace=workspace_path,
            dry_run=dry_run,
        )
        export_artifacts: dict[str, str] = {}
        export_returncodes: dict[str, int] = {}
        for fmt, result in export_results.items():
            export_returncodes[fmt] = result.returncode
            output_dir = Path(get_config(config, "export.output_dir") or (workspace_path / "exports")).resolve()
            suffix = "lightfield_isaac" if fmt == "lightfield" else "nurec_isaac"
            export_artifacts[fmt] = str(output_dir / f"scene_{suffix}.usdz")
            if result.returncode != 0:
                raise RuntimeError(f"Export stage failed for {fmt}. Inspect {result.log_path}")

        update_stage(manifest, "export", {"returncodes": export_returncodes, "artifacts": export_artifacts})
        set_artifact(manifest, "exports", export_artifacts)

        if not dry_run and get_config(config, "validation.enabled", True):
            validation = validate_outputs(
                images_dir=frames.images_dir,
                dataset_root=train_dataset_root,
                usdz_paths=[Path(path) for path in export_artifacts.values()],
            )
            manifest["validation"] = validation

        write_manifest(manifest, _manifest_path(workspace_path))
        print("\nSceneMill pipeline completed successfully.")
        print(f"Manifest: {_manifest_path(workspace_path)}")
        return manifest

    manifest["failed"] = True
    manifest["last_error_tail"] = last_error[-4000:]
    write_manifest(manifest, _manifest_path(workspace_path))
    raise RuntimeError("All retry frame steps failed")
