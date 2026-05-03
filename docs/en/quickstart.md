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
./scenemill run --preset da3 --input /path/to/images --workspace runs/my_scene
```

The terminal streams live progress through each stage:

```
[1/6] Ingest ────────────────────────────────────────────
[2/6] Preprocess  (frame_step=1) ────────────────────────
[3/6] Geometry    (da3) ─────────────────────────────────
[4/6] Train       (3dgrut, 30000 iters) ─────────────────
[5/6] Export      (nurec, lightfield) ───────────────────
[6/6] Validate ──────────────────────────────────────────

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
./scenemill run --preset colmap --input /path/to/images --workspace runs/colmap_scene
./scenemill run --preset rosbag --input /path/to/bag    --workspace runs/bag_scene
```
