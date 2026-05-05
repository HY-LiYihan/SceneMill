# Manifest Contract

Each run writes:

```text
<workspace>/scene_manifest.yaml
```

This file is SceneMill's stable external contract. Downstream systems such as `image2sim` should read the manifest instead of guessing intermediate paths.

## Important Fields

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

The classic backend also writes:

```yaml
artifacts:
  colmap_dataset: runs/scene/colmap_dataset_step_1
  checkpoint: runs/scene/runs/da3_3dgut_scene/.../ckpt_last.pt
```

The AnySplat backend also writes:

```yaml
artifacts:
  anysplat_manifest: runs/scene/anysplat/anysplat_manifest.yaml
  gaussian_ply: runs/scene/anysplat/gaussians.ply
camera:
  alignment_target: crop_448
```

## Routing Record

```yaml
stages:
  router:
    mode: auto
    selected_backend: classic
    reason: image_count_at_or_above_threshold
    image_count: 16
    threshold: 10
```

Downstream consumers should prefer `artifacts.exports.nurec` and fall back to `artifacts.exports.lightfield` if NuRec is unavailable or displays poorly.
