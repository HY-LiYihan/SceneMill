# Quickstart

## 1. Check the Machine

```bash
./scenemill doctor
./scripts/doctor.sh
```

## 2. Run the Stable Image Pipeline

```bash
./scenemill run --preset da3 --input /path/to/images --workspace runs/my_scene
```

## 3. Validate Outputs

```bash
./scenemill validate \
  --images-dir runs/my_scene/frames/images \
  --dataset runs/my_scene/colmap_dataset_step_1_train \
  --usdz runs/my_scene/exports/scene_nurec_isaac.usdz \
  --usdz runs/my_scene/exports/scene_lightfield_isaac.usdz
```

The recommended Isaac asset is `exports/scene_nurec_isaac.usdz`. Use `scene_lightfield_isaac.usdz` as the fallback.

## Dry Run

```bash
./scenemill run --preset da3 --input /path/to/images --workspace runs/dry_run --dry-run
```
