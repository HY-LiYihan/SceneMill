# Isaac USDZ 验证

SceneMill 会验证：

- 图片数量
- COLMAP 文件完整性
- USDZ 内部 payload 64-byte alignment
- 可用 `pxr` 时检查 NuRec 和 LightField prim 类型

```bash
./scenemill validate \
  --images-dir runs/my_scene/frames/images \
  --dataset runs/my_scene/colmap_dataset_step_1_train \
  --usdz runs/my_scene/exports/scene_nurec_isaac.usdz \
  --usdz runs/my_scene/exports/scene_lightfield_isaac.usdz
```

预期 prim 标记：

| 格式 | 预期类型 |
| --- | --- |
| NuRec | `Volume` 和 `OmniNuRecFieldAsset` |
| LightField | `ParticleField3DGaussianSplat` |
