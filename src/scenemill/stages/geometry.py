from __future__ import annotations

from pathlib import Path

from scenemill.adapters import da3, vggt
from scenemill.adapters.colmap import build_colmap_commands, validate_colmap_dataset
from scenemill.registry import GEOMETRY_BACKENDS, validate_backend
from scenemill.runtime.subprocess import CommandResult, run_command
from scenemill.schemas.artifacts import ColmapDataset


def run_geometry(
    *,
    config: dict,
    dataset: ColmapDataset,
    workspace: Path,
    dry_run: bool,
) -> CommandResult | None:
    geometry = config.get("geometry", {})
    backend = validate_backend(str(geometry.get("backend", "da3")), GEOMETRY_BACKENDS, "geometry")
    if backend == "colmap":
        colmap_env = str(geometry.get("colmap_env") or "")
        colmap_bin = str(geometry.get("colmap_bin") or "colmap")
        (dataset.root / "sparse").mkdir(parents=True, exist_ok=True)
        last_result: CommandResult | None = None
        for index, cmd in enumerate(
            build_colmap_commands(dataset, config, colmap_bin=colmap_bin, colmap_env=colmap_env),
            start=1,
        ):
            last_result = run_command(
                cmd,
                cwd=dataset.root,
                log_path=workspace / "logs" / f"geometry_colmap_step_{dataset.frame_step}_{index}.log",
                dry_run=dry_run,
            )
            if last_result.returncode != 0:
                return last_result
        if not dry_run:
            validate_colmap_dataset(dataset.root)
        return last_result
    if backend == "vggt":
        raise NotImplementedError(vggt.not_implemented_message())

    runtime = config.get("runtime", {})
    cmd = da3.build_images_to_colmap_command(
        images_dir=dataset.images_dir,
        sparse_dir=dataset.sparse_dir,
        model=str(geometry.get("model", "depth-anything/DA3NESTED-GIANT-LARGE-1.1")),
        conda_env=str(runtime.get("da3_env", "da3_recon")),
        process_res=int(geometry.get("process_res", 504)),
        process_res_method=str(geometry.get("process_res_method", "upper_bound_resize")),
        use_ray_pose=bool(geometry.get("use_ray_pose", True)),
    )
    return run_command(
        cmd,
        cwd=Path(runtime.get("da3_repo", "third_party/Depth-Anything-3")).resolve(),
        log_path=workspace / "logs" / f"geometry_da3_step_{dataset.frame_step}.log",
        dry_run=dry_run,
    )
