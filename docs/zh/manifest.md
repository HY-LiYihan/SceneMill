# Manifest 契约

每次运行都会写：

```text
<workspace>/scene_manifest.yaml
```

这个文件是 SceneMill 对外的稳定契约。`image2sim` 等下游系统应该读取 manifest，而不是猜测中间目录。

## 关键字段

```yaml
artifacts:
  selected_backend: anysplat
  frames_dir: runs/scene/frames
  exports:
    nurec: runs/scene/exports/scene_nurec_isaac.usdz
    lightfield: runs/scene/exports/scene_lightfield_isaac.usdz
  gaussian_ply: runs/scene/anysplat/gaussians.ply
  camera_intrinsics: runs/scene/anysplat/camera_intrinsics.npy
  camera_intrinsics_pixels: runs/scene/anysplat/camera_intrinsics_pixels.npy
  camera_extrinsics: runs/scene/anysplat/camera_extrinsics.npy
```

classic backend 会额外写：

```yaml
artifacts:
  colmap_dataset: runs/scene/colmap_dataset_step_1
  checkpoint: runs/scene/runs/da3_3dgut_scene/.../ckpt_last.pt
```

AnySplat backend 会额外写：

```yaml
artifacts:
  anysplat_manifest: runs/scene/anysplat/anysplat_manifest.yaml
  gaussian_ply: runs/scene/anysplat/gaussians.ply
camera:
  alignment_target: crop_448
```

## 路由记录

```yaml
stages:
  router:
    mode: auto
    selected_backend: classic
    reason: image_count_at_or_above_threshold
    image_count: 16
    threshold: 10
```

下游应优先使用 `artifacts.exports.nurec`，失败或显示异常时再尝试 `artifacts.exports.lightfield`。
