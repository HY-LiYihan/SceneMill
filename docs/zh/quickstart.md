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
./scenemill run --preset da3 --input /path/to/images --workspace runs/my_scene
```

运行过程中终端会实时输出各阶段进度：

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
./scenemill run --preset colmap --input /path/to/images --workspace runs/colmap_scene
./scenemill run --preset rosbag --input /path/to/bag    --workspace runs/bag_scene
```
