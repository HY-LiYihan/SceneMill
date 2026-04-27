# Isaac USDZ Validation

SceneMill validates:

- image count
- COLMAP files
- USDZ 64-byte member alignment
- NuRec and LightField prim types when USD Python bindings are available

```bash
./scenemill validate \
  --images-dir runs/my_scene/frames/images \
  --dataset runs/my_scene/colmap_dataset_step_1_train \
  --usdz runs/my_scene/exports/scene_nurec_isaac.usdz \
  --usdz runs/my_scene/exports/scene_lightfield_isaac.usdz
```

Expected prim markers:

| Format | Expected type |
| --- | --- |
| NuRec | `Volume` and `OmniNuRecFieldAsset` |
| LightField | `ParticleField3DGaussianSplat` |
