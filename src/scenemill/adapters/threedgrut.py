from __future__ import annotations

from pathlib import Path

from scenemill.runtime.conda import conda_run


def cuda_env_overrides(config: dict) -> dict[str, str]:
    cuda = config.get("runtime", {}).get("cuda", {})
    return {
        "CUDA_HOME": str(cuda.get("home", "/usr/local/cuda-12.4")),
        "TORCH_CUDA_ARCH_LIST": str(cuda.get("arch_list", "8.6")),
        "CC": str(cuda.get("cc", "/usr/bin/gcc-11")),
        "CXX": str(cuda.get("cxx", "/usr/bin/g++-11")),
    }


def build_train_command(
    *,
    dataset_root: Path,
    run_dir: Path,
    config: dict,
) -> list[str]:
    trainer = config.get("trainer", {})
    runtime = config.get("runtime", {})
    cmd = [
        "python",
        "train.py",
        "--config-name",
        str(trainer.get("config_name", "apps/colmap_3dgut.yaml")),
        f"path={dataset_root}",
        f"out_dir={run_dir}",
        f"experiment_name={trainer.get('experiment_name', 'da3_3dgut_scene')}",
        f"dataset.downsample_factor={trainer.get('dataset_downsample_factor', 1)}",
        f"n_iterations={trainer.get('n_iterations', 30000)}",
        "export_usd.enabled=false",
    ]
    optimizer_type = trainer.get("optimizer_type")
    if optimizer_type:
        cmd.append(f"optimizer.type={optimizer_type}")
    return conda_run(str(runtime.get("grut_env", "3dgrut_recon")), cmd)


def build_export_command(
    *,
    checkpoint: Path,
    output: Path,
    dataset_root: Path | None,
    export_format: str,
    config: dict,
) -> list[str]:
    runtime = config.get("runtime", {})
    cmd = [
        "python",
        "-m",
        "threedgrut.export.scripts.export_usd",
        "-c",
        str(checkpoint),
        "-o",
        str(output),
        "--format",
        export_format,
    ]
    if dataset_root:
        cmd.extend(["--dataset", str(dataset_root)])
    return conda_run(str(runtime.get("grut_env", "3dgrut_recon")), cmd)


def find_latest_checkpoint(run_root: Path) -> Path:
    candidates = sorted(run_root.glob("*/ckpt_last.pt"), key=lambda path: path.stat().st_mtime)
    if not candidates:
        raise FileNotFoundError(f"No ckpt_last.pt found under {run_root}")
    return candidates[-1]

