from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

from scenemill.config import load_config
from scenemill.logging import configure_logging
from scenemill.pipeline import run_pipeline
from scenemill.runtime.gpu import query_nvidia_smi
from scenemill.stages.export import run_exports
from scenemill.stages.geometry import run_geometry
from scenemill.stages.ingest import run_ingest
from scenemill.stages.preprocess import sample_frames_to_colmap_dataset
from scenemill.stages.train import run_train
from scenemill.stages.validate import validate_outputs


PRESET_ALIASES: dict[str, str] = {
    "da3":    "configs/presets/images_da3_3dgut_isaac.yaml",
    "colmap": "configs/presets/images_colmap_3dgut_isaac.yaml",
    "rosbag": "configs/presets/rosbag_da3_3dgut_isaac.yaml",
}


def _print_yaml(data: Any) -> None:
    print(yaml.safe_dump(data, sort_keys=False, allow_unicode=True))


def _resolve_config(args: argparse.Namespace) -> Path:
    """Return the config path, resolving --preset to its full path."""
    preset = getattr(args, "preset", None)
    config = getattr(args, "config", None)
    if preset:
        return Path(PRESET_ALIASES[preset])
    if config:
        return config
    return Path("configs/default.yaml")


def _add_common_config_args(parser: argparse.ArgumentParser) -> None:
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-c", "--config", type=Path, default=None, help="SceneMill YAML config file.")
    group.add_argument(
        "--preset",
        choices=list(PRESET_ALIASES),
        metavar="PRESET",
        help=f"Built-in preset shorthand. One of: {', '.join(PRESET_ALIASES)}.",
    )
    parser.add_argument("--input", type=Path, default=None, help="Input path override.")
    parser.add_argument("--workspace", type=Path, default=None, help="Workspace path override.")
    parser.add_argument("--dry-run", action="store_true", help="Print commands and write dry-run logs without heavy execution.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose logging.")


def cmd_run(args: argparse.Namespace) -> int:
    configure_logging(args.verbose)
    run_pipeline(config_path=_resolve_config(args), input_path=args.input, workspace=args.workspace, dry_run=args.dry_run)
    return 0


def cmd_ingest(args: argparse.Namespace) -> int:
    configure_logging(args.verbose)
    config = load_config(_resolve_config(args), input_path=args.input, workspace=args.workspace)
    workspace = Path(config.get("runtime", {}).get("workspace", args.workspace or "runs/scenemill_ingest")).resolve()
    result = run_ingest(config, workspace)
    _print_yaml({"frames_root": str(result.root), "images_dir": str(result.images_dir), "count": result.count})
    return 0


def cmd_geometry(args: argparse.Namespace) -> int:
    configure_logging(args.verbose)
    config = load_config(_resolve_config(args), input_path=args.input, workspace=args.workspace)
    workspace = Path(config.get("runtime", {}).get("workspace", args.workspace or "runs/scenemill_geometry")).resolve()
    images_dir = Path(args.images_dir).resolve()
    dataset = sample_frames_to_colmap_dataset(images_dir, workspace, args.frame_step)
    result = run_geometry(config=config, dataset=dataset, workspace=workspace, dry_run=args.dry_run)
    _print_yaml(
        {
            "dataset_root": str(dataset.root),
            "sampled_images": dataset.image_count,
            "returncode": result.returncode if result else 0,
            "log": str(result.log_path) if result else None,
        }
    )
    return result.returncode if result else 0


def cmd_train(args: argparse.Namespace) -> int:
    configure_logging(args.verbose)
    config = load_config(_resolve_config(args), input_path=args.input, workspace=args.workspace)
    workspace = Path(config.get("runtime", {}).get("workspace", args.workspace or "runs/scenemill_train")).resolve()
    result, checkpoint = run_train(config=config, dataset_root=args.dataset.resolve(), workspace=workspace, dry_run=args.dry_run)
    _print_yaml({"returncode": result.returncode, "log": str(result.log_path), "checkpoint": str(checkpoint)})
    return result.returncode


def cmd_export(args: argparse.Namespace) -> int:
    configure_logging(args.verbose)
    config = load_config(_resolve_config(args), input_path=args.input, workspace=args.workspace)
    workspace = Path(config.get("runtime", {}).get("workspace", args.workspace or "runs/scenemill_export")).resolve()
    results = run_exports(
        config=config,
        checkpoint=args.checkpoint.resolve(),
        dataset_root=args.dataset.resolve() if args.dataset else args.dataset,
        workspace=workspace,
        dry_run=args.dry_run,
    )
    _print_yaml({fmt: {"returncode": result.returncode, "log": str(result.log_path)} for fmt, result in results.items()})
    return max((result.returncode for result in results.values()), default=0)


def cmd_validate(args: argparse.Namespace) -> int:
    data = validate_outputs(
        images_dir=args.images_dir.resolve() if args.images_dir else None,
        dataset_root=args.dataset.resolve() if args.dataset else None,
        usdz_paths=[path.resolve() for path in args.usdz],
    )
    _print_yaml(data)
    return 0


def _conda_env_exists(env_name: str) -> bool | None:
    if not shutil.which("conda"):
        return None
    proc = subprocess.run(["conda", "env", "list"], text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    return env_name in proc.stdout


def cmd_doctor(args: argparse.Namespace) -> int:
    config = load_config(_resolve_config(args), input_path=args.input, workspace=args.workspace)
    runtime = config.get("runtime", {})
    checks = {
        "python": sys.executable,
        "gpu": query_nvidia_smi(),
        "conda": shutil.which("conda"),
        "da3_env": _conda_env_exists(str(runtime.get("da3_env", "da3_recon"))),
        "grut_env": _conda_env_exists(str(runtime.get("grut_env", "3dgrut_recon"))),
        "isaac_env": _conda_env_exists(str(runtime.get("isaac_env", "env_isaacsim"))),
        "da3_repo": Path(runtime.get("da3_repo", "third_party/Depth-Anything-3")).resolve().exists(),
        "grut_repo": Path(runtime.get("grut_repo", "third_party/3dgrut")).resolve().exists(),
    }
    _print_yaml(checks)
    return 0 if checks["conda"] else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="scenemill", description="SceneMill reconstruction pipeline CLI.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run the full configured pipeline.")
    _add_common_config_args(run_parser)
    run_parser.set_defaults(func=cmd_run)

    ingest_parser = subparsers.add_parser("ingest", help="Ingest images or ROS bag data into a frames workspace.")
    _add_common_config_args(ingest_parser)
    ingest_parser.set_defaults(func=cmd_ingest)

    geometry_parser = subparsers.add_parser("geometry", help="Build a COLMAP-compatible dataset.")
    _add_common_config_args(geometry_parser)
    geometry_parser.add_argument("--images-dir", type=Path, required=True)
    geometry_parser.add_argument("--frame-step", type=int, default=1)
    geometry_parser.set_defaults(func=cmd_geometry)

    train_parser = subparsers.add_parser("train", help="Train the configured Gaussian backend.")
    _add_common_config_args(train_parser)
    train_parser.add_argument("--dataset", type=Path, required=True, help="COLMAP-compatible dataset root.")
    train_parser.set_defaults(func=cmd_train)

    export_parser = subparsers.add_parser("export", help="Export Isaac/Omniverse USDZ assets from a checkpoint.")
    _add_common_config_args(export_parser)
    export_parser.add_argument("--checkpoint", type=Path, required=True)
    export_parser.add_argument("--dataset", type=Path, default=None)
    export_parser.set_defaults(func=cmd_export)

    validate_parser = subparsers.add_parser("validate", help="Validate images, COLMAP datasets, and USDZ assets.")
    validate_parser.add_argument("--images-dir", type=Path, default=None)
    validate_parser.add_argument("--dataset", type=Path, default=None)
    validate_parser.add_argument("--usdz", type=Path, action="append", default=[])
    validate_parser.set_defaults(func=cmd_validate)

    doctor_parser = subparsers.add_parser("doctor", help="Check local runtime dependencies.")
    _add_common_config_args(doctor_parser)
    doctor_parser.set_defaults(func=cmd_doctor)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())

