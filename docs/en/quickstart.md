# Quickstart

## Prerequisites

- NVIDIA GPU (RTX series, ≥ 8 GB VRAM)
- CUDA 12.4
- conda (Miniconda or Anaconda)
- Completed [Installation](installation.md)

---

## Step 1: Verify the Environment

```bash
conda activate scenemill
./scenemill doctor
```

Confirm `da3_env`, `grut_env`, and `gpu` all show valid values.

---

## Step 2: Run Your First Scene

```bash
./scenemill run --preset auto --input /path/to/images --workspace runs/my_scene
```

`auto` counts the images first. Fewer than 10 images use AnySplat; 10 or more images use the classic DA3/3DGUT path.

Low-view runs print:

```
[1/7] Ingest
[2/7] Route
[3/7] AnySplat    (low-view)
[4/7] Validate
```

Multi-view runs print:

```
[1/7] Ingest
[2/7] Route
[3/7] Preprocess  (frame_step=1)
[4/7] Geometry    (da3)
[5/7] Train       (3dgrut, 30000 iters)
[6/7] Export      (nurec, lightfield)
[7/7] Validate

✓ Pipeline completed in 42m 13s
  Manifest:   runs/my_scene/scene_manifest.yaml
  NuRec:      runs/my_scene/exports/scene_nurec_isaac.usdz
  LightField: runs/my_scene/exports/scene_lightfield_isaac.usdz
```

---

## Step 3: Validate Outputs

```bash
./scenemill validate \
  --images-dir runs/my_scene/frames/images \
  --dataset runs/my_scene/colmap_dataset_step_1_train \
  --usdz runs/my_scene/exports/scene_nurec_isaac.usdz \
  --usdz runs/my_scene/exports/scene_lightfield_isaac.usdz
```

Open `exports/scene_nurec_isaac.usdz` first in Isaac Sim. Use `scene_lightfield_isaac.usdz` as the fallback.

---

## Dry Run (No GPU Required)

To verify your config without running heavy computation:

```bash
./scenemill run --preset da3 --input /path/to/images --workspace runs/dry_run --dry-run
```

---

## Other Presets

```bash
./scenemill run --preset auto   --input /path/to/images --workspace runs/auto_scene
./scenemill run --preset auto   --backend anysplat --input /path/to/images --workspace runs/anysplat_scene
./scenemill run --preset auto   --backend classic  --input /path/to/images --workspace runs/classic_scene
./scenemill run --preset colmap --input /path/to/images --workspace runs/colmap_scene
./scenemill run --preset rosbag --input /path/to/bag    --workspace runs/bag_scene
```
