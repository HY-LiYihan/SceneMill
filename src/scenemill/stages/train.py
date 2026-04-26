from __future__ import annotations

from pathlib import Path

from scenemill.adapters import threedgrut
from scenemill.registry import TRAIN_BACKENDS, validate_backend
from scenemill.runtime.subprocess import CommandResult, run_command


def run_train(
    *,
    config: dict,
    dataset_root: Path,
    workspace: Path,
    dry_run: bool,
) -> tuple[CommandResult, Path | None]:
    trainer = config.get("trainer", {})
    backend = validate_backend(str(trainer.get("backend", "3dgrut")), TRAIN_BACKENDS, "trainer")
    if backend != "3dgrut":
        raise ValueError(f"Unsupported trainer backend: {backend}")

    runtime = config.get("runtime", {})
    run_dir = Path(runtime.get("run_dir") or (workspace / "runs")).resolve()
    experiment_name = str(trainer.get("experiment_name", "da3_3dgut_scene"))
    cmd = threedgrut.build_train_command(dataset_root=dataset_root, run_dir=run_dir, config=config)
    result = run_command(
        cmd,
        cwd=Path(runtime.get("grut_repo", "third_party/3dgrut")).resolve(),
        log_path=workspace / "logs" / f"train_3dgrut_{dataset_root.name}.log",
        dry_run=dry_run,
        env_overrides=threedgrut.cuda_env_overrides(config),
    )
    if result.returncode != 0:
        return result, None

    if dry_run:
        checkpoint = run_dir / experiment_name / "dry_run" / "ckpt_last.pt"
    else:
        checkpoint = threedgrut.find_latest_checkpoint(run_dir / experiment_name)
    return result, checkpoint
