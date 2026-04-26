# SceneMill

SceneMill is a robot/Isaac-first reconstruction pipeline. It turns ROS bags or image folders into COLMAP-compatible geometry, 3D Gaussian scenes, and Isaac/Omniverse-ready USDZ assets.

The first supported production path is:

```text
ROS bag / images -> frames -> DA3 COLMAP export -> 3DGUT training -> NuRec + LightField USDZ
```

## Why This Exists

SceneMill wraps the reconstruction workflow into a reproducible CLI + YAML pipeline instead of one-off shell commands. It is designed around robot data and Isaac Sim handoff, while keeping the geometry frontend pluggable for COLMAP, VGGT, DA3, and future methods.

Related ecosystems:

- NVIDIA Isaac reconstruction workflow: smartphone or image capture to COLMAP, 3DGUT, and Isaac Sim.
- Nerfstudio/Splatfacto: general NeRF/3DGS framework.
- VGGT, MASt3R, DA3: feed-forward geometry frontends that can replace or augment COLMAP.
- 3DGUT/NuRec: Isaac/Omniverse-oriented Gaussian rendering and USDZ export.

## Quick Start

Clone with third-party submodules:

```bash
git clone --recursive git@github.com:HY-LiYihan/SceneMill.git
cd SceneMill
```

If you cloned without `--recursive`:

```bash
git submodule update --init --recursive
```

Apply the compatibility patches used by the current SceneMill workflow:

```bash
./scripts/apply_third_party_patches.sh
```

The patches currently fix DA3 CLI argument naming and make 3DGUT USDZ packages 64-byte aligned for Isaac/Kit.

Use the DA3 + 3DGUT + Isaac preset on an image directory:

```bash
PYTHONPATH=src python3 -m scenemill.cli run \
  -c configs/presets/images_da3_3dgut_isaac.yaml \
  --input /path/to/images \
  --workspace runs/my_scene
```

For the current recovered bag image export:

```bash
PYTHONPATH=src python3 -m scenemill.cli run \
  -c configs/presets/images_da3_3dgut_isaac.yaml \
  --input /home/hclab/photo2usd/aaa/DataBag_2026-04-24-20-40-09/exported_images/camera_color_image_raw \
  --workspace /home/hclab/photo2usd/runs/databag_scene
```

Dry-run the same pipeline without launching heavy model/training jobs:

```bash
PYTHONPATH=src python3 -m scenemill.cli run \
  -c configs/presets/images_da3_3dgut_isaac.yaml \
  --input /path/to/images \
  --workspace runs/dry_run \
  --dry-run
```

After packaging/installing, the same commands are available as:

```bash
scenemill run -c configs/presets/images_da3_3dgut_isaac.yaml --input /path/to/images --workspace runs/my_scene
```

## CLI

- `scenemill run`: run the full configured pipeline.
- `scenemill ingest`: convert input data into a standard `frames/` workspace.
- `scenemill geometry`: generate or validate a COLMAP-compatible dataset.
- `scenemill train`: train 3DGUT from a COLMAP dataset.
- `scenemill export`: export NuRec and/or LightField USDZ from a checkpoint.
- `scenemill validate`: validate images, COLMAP files, USDZ alignment, and USD prims.
- `scenemill doctor`: check local conda envs, GPU, and third-party repo paths.

## Outputs

Every run writes:

- `scene_manifest.yaml`: input, runtime, retries, artifacts, logs, validation results.
- `frames/`: normalized frame/image view of the input.
- `colmap_dataset_step_<N>/`: sampled COLMAP-compatible dataset.
- `runs/`: 3DGUT training outputs and checkpoints.
- `exports/scene_nurec_isaac.usdz`: recommended Isaac/Omniverse asset.
- `exports/scene_lightfield_isaac.usdz`: standard `ParticleField3DGaussianSplat` fallback.

## Runtime Defaults

The default configs match this machine:

- DA3 env: `da3_recon`
- 3DGUT env: `3dgrut_recon`
- Isaac env: `env_isaacsim`
- CUDA: `/usr/local/cuda-12.4`
- CUDA arch: `8.6`
- Compiler: `/usr/bin/gcc-11`, `/usr/bin/g++-11`

The retry policy defaults to `frame_steps: [1, 2, 5, 10, 15, 20]` so GPU OOM automatically retries with fewer images.

## Project Layout

```text
configs/            YAML configs and presets
src/scenemill/      CLI, pipeline, stages, adapters, runtime helpers, schemas
workflows/          Human workflow notes
tests/              Unit tests
third_party/        External DA3 and 3DGUT checkouts
data/               Local data scratch
runs/               SceneMill run outputs
```
