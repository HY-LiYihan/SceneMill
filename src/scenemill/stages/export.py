from __future__ import annotations

from pathlib import Path

from scenemill.adapters import threedgrut
from scenemill.registry import EXPORT_FORMATS
from scenemill.runtime.subprocess import CommandResult, run_command


def run_exports(
    *,
    config: dict,
    checkpoint: Path,
    dataset_root: Path,
    workspace: Path,
    dry_run: bool,
) -> dict[str, CommandResult]:
    export_cfg = config.get("export", {})
    if not export_cfg.get("enabled", True):
        return {}

    formats = [str(item).lower() for item in export_cfg.get("formats", ["nurec", "lightfield"])]
    unsupported = [item for item in formats if item not in EXPORT_FORMATS]
    if unsupported:
        raise ValueError(f"Unsupported export formats: {unsupported}")

    runtime = config.get("runtime", {})
    out_dir = Path(export_cfg.get("output_dir") or (workspace / "exports")).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    grut_repo = Path(runtime.get("grut_repo", "third_party/3dgrut")).resolve()

    results: dict[str, CommandResult] = {}
    for fmt in formats:
        script_format = "standard" if fmt == "lightfield" else "nurec"
        suffix = "lightfield_isaac" if fmt == "lightfield" else "nurec_isaac"
        output = out_dir / f"scene_{suffix}.usdz"
        cmd = threedgrut.build_export_command(
            checkpoint=checkpoint,
            output=output,
            dataset_root=dataset_root,
            export_format=script_format,
            config=config,
        )
        results[fmt] = run_command(
            cmd,
            cwd=grut_repo,
            log_path=workspace / "logs" / f"export_{fmt}.log",
            dry_run=dry_run,
            env_overrides=threedgrut.cuda_env_overrides(config),
        )
    return results

