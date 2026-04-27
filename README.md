# SceneMill

SceneMill is a robot and Isaac-first reconstruction pipeline. It turns image folders or ROS bags into COLMAP-compatible geometry, 3D Gaussian scenes, and Isaac/Omniverse-ready USDZ assets.

```text
images / ROS bag -> frames -> DA3 COLMAP export -> 3DGUT training -> NuRec + LightField USDZ
```

## Status

| Path | Status | Notes |
| --- | --- | --- |
| Images -> DA3 -> 3DGUT -> NuRec/LightField USDZ | Stable | Primary local workflow. |
| ROS1 bag -> frames -> DA3 -> 3DGUT -> USDZ | Stable local | Requires `rosbags` and image topics. |
| COLMAP frontend | Experimental | Requires `colmap` on `PATH`. |
| VGGT frontend | Reserved | Preset exists; adapter is not enabled yet. |
| OpenSplat / gsplat backend | Future | Planned backend direction. |

## Quick Start

Clone with submodules:

```bash
git clone --recursive git@github.com:HY-LiYihan/SceneMill.git
cd SceneMill
```

Install the local package and docs/dev dependencies:

```bash
./scripts/install_local.sh
```

Check the machine:

```bash
./scenemill doctor
./scripts/doctor.sh
```

Run the stable DA3 + 3DGUT + Isaac path:

```bash
./scenemill run \
  -c configs/presets/images_da3_3dgut_isaac.yaml \
  --input /path/to/images \
  --workspace runs/my_scene
```

Validate outputs:

```bash
./scenemill validate \
  --images-dir runs/my_scene/frames/images \
  --dataset runs/my_scene/colmap_dataset_step_1_train \
  --usdz runs/my_scene/exports/scene_nurec_isaac.usdz \
  --usdz runs/my_scene/exports/scene_lightfield_isaac.usdz
```

Open `exports/scene_nurec_isaac.usdz` first in Isaac Sim. Use `scene_lightfield_isaac.usdz` as the fallback.

## CLI

```bash
./scenemill run       # full configured pipeline
./scenemill ingest    # image folder or ROS bag to frames/
./scenemill geometry  # COLMAP-compatible geometry
./scenemill train     # 3DGUT training
./scenemill export    # Isaac USDZ export
./scenemill validate  # output checks
./scenemill doctor    # local runtime checks
```

Common options:

```bash
-c, --config      SceneMill YAML config
--input           input path override
--workspace       workspace override
--dry-run         print commands without heavy execution
```

## Documentation

Build the MkDocs site locally:

```bash
python3 -m pip install -e ".[docs]"
mkdocs serve
```

Documentation is bilingual under `docs/en/` and `docs/zh/` and uses `mkdocs-static-i18n` for the top-bar language switcher. GitHub Pages is built by `.github/workflows/docs.yml`.

## Repository Layout

```text
configs/       YAML configs and presets
docs/          MkDocs documentation site
patches/       optional legacy third-party patches, not applied by default
scripts/       local setup, doctor, example, and cleanup scripts
src/           SceneMill Python package
tests/         unit tests
third_party/   DA3 and 3DGUT submodules
runs/          local pipeline outputs, ignored
tmp/           local scratch space, ignored
data/          local datasets, ignored
```

## Local Boundaries

Do not commit robot bags, generated COLMAP datasets, checkpoints, USDZ/USD assets, `aaa/`, `runs/`, `tmp/`, or local Codex state. The repository tracks code, configs, docs, tests, scripts, patches, and submodule pointers only.

## Development

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m compileall src tests
mkdocs build --strict
```
