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
--preset PRESET   Built-in preset shorthand: da3, colmap, rosbag.
-c, --config      SceneMill YAML config (mutually exclusive with --preset).
--input           Input path override.
--workspace       Workspace path override.
--dry-run         Print commands and write dry-run logs without heavy execution.
```

`--preset` is the recommended way to invoke the pipeline:

```bash
./scenemill run --preset da3    --input /path/to/images
./scenemill run --preset colmap --input /path/to/images
./scenemill run --preset rosbag --input /path/to/bag
```

Use `-c` when you need a custom config file:

```bash
./scenemill run -c my_config.yaml --input /path/to/images
```

