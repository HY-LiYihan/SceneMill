from __future__ import annotations

from pathlib import Path

from scenemill.runtime.conda import conda_run


def build_images_to_colmap_command(
    *,
    images_dir: Path,
    sparse_dir: Path,
    model: str,
    conda_env: str,
    process_res: int,
    process_res_method: str,
    use_ray_pose: bool,
) -> list[str]:
    cmd = [
        "da3",
        "images",
        str(images_dir),
        "--model-dir",
        model,
        "--export-dir",
        str(sparse_dir),
        "--export-format",
        "colmap",
        "--device",
        "cuda",
        "--process-res",
        str(process_res),
        "--process-res-method",
        process_res_method,
        "--auto-cleanup",
    ]
    if use_ray_pose:
        cmd.append("--use-ray-pose")
    return conda_run(conda_env, cmd)

