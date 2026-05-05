# 快速开始

## 前提条件

- NVIDIA GPU（RTX 系列，≥ 8 GB VRAM）
- CUDA 12.4
- conda（Miniconda 或 Anaconda）
- 已完成 [安装](installation.md)

---

## 第一步：验证环境

```bash
conda activate scenemill
./scenemill doctor
```

预期输出中 `da3_env`、`grut_env`、`gpu` 均为有效值。

---

## 第二步：跑第一个场景

```bash
./scenemill run --preset auto --input /path/to/images --workspace runs/my_scene
```

`auto` 会先统计图片数量。少于 10 张图时走 AnySplat，10 张及以上走经典 DA3/3DGUT 主线。

少图时终端会输出：

```
[1/7] Ingest
[2/7] Route
[3/7] AnySplat    (low-view)
[4/7] Validate
```

多图时终端会输出：

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

## 第三步：验证输出

```bash
./scenemill validate \
  --images-dir runs/my_scene/frames/images \
  --dataset runs/my_scene/colmap_dataset_step_1_train \
  --usdz runs/my_scene/exports/scene_nurec_isaac.usdz \
  --usdz runs/my_scene/exports/scene_lightfield_isaac.usdz
```

优先在 Isaac Sim 打开 `exports/scene_nurec_isaac.usdz`。如果 NuRec 显示有问题，再尝试 LightField 版本。

---

## Dry Run（不需要 GPU）

在没有 GPU 或只想验证配置时，加 `--dry-run` 只打印命令而不执行：

```bash
./scenemill run --preset da3 --input /path/to/images --workspace runs/dry_run --dry-run
```

---

## 其他 preset

```bash
./scenemill run --preset auto   --input /path/to/images --workspace runs/auto_scene
./scenemill run --preset auto   --backend anysplat --input /path/to/images --workspace runs/anysplat_scene
./scenemill run --preset auto   --backend classic  --input /path/to/images --workspace runs/classic_scene
./scenemill run --preset colmap --input /path/to/images --workspace runs/colmap_scene
./scenemill run --preset rosbag --input /path/to/bag    --workspace runs/bag_scene
```
