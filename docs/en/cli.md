# CLI Reference

SceneMill exposes one CLI entrypoint:

```bash
./scenemill <command> [options]
```

| Command | Purpose |
| --- | --- |
| `run` | Run the full configured pipeline. |
| `ingest` | Convert image folders or ROS bags into a standard `frames/` workspace. |
| `geometry` | Build a COLMAP-compatible dataset. |
| `train` | Train the configured Gaussian backend. |
| `export` | Export Isaac/Omniverse USDZ assets from a checkpoint. |
| `validate` | Validate images, COLMAP files, USDZ alignment, and USD prims. |
| `doctor` | Check local Python, GPU, conda envs, and third-party repo paths. |

Common options:

```bash
-c, --config      SceneMill YAML config.
--input           Input path override.
--workspace       Workspace path override.
--dry-run         Print commands and write dry-run logs without heavy execution.
```
