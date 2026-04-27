# 快速开始

## 1. 检查环境

```bash
./scenemill doctor
./scripts/doctor.sh
```

## 2. 跑图片主线

```bash
./scenemill run \
  -c configs/presets/images_da3_3dgut_isaac.yaml \
  --input /path/to/images \
  --workspace runs/my_scene
```

## 3. 验证输出

```bash
./scenemill validate \
  --images-dir runs/my_scene/frames/images \
  --dataset runs/my_scene/colmap_dataset_step_1_train \
  --usdz runs/my_scene/exports/scene_nurec_isaac.usdz \
  --usdz runs/my_scene/exports/scene_lightfield_isaac.usdz
```

优先在 Isaac Sim 打开 `exports/scene_nurec_isaac.usdz`。如果 NuRec 显示有问题，再尝试 LightField 版本。

## Dry Run

```bash
./scenemill run \
  -c configs/presets/images_da3_3dgut_isaac.yaml \
  --input /path/to/images \
  --workspace runs/dry_run \
  --dry-run
```
