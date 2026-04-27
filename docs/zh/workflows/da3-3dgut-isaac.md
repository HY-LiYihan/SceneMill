# DA3 + 3DGUT + Isaac

这是 SceneMill 当前推荐主线：

```bash
./scenemill run \
  -c configs/presets/images_da3_3dgut_isaac.yaml \
  --input /path/to/images \
  --workspace runs/scene_da3
```

关键行为：

- DA3 导出 COLMAP-compatible reconstruction。
- SceneMill 会在训练前采样 DA3 生成的稠密 `points3D.bin`。
- 当 `dataset_downsample_factor: 4` 时，SceneMill 会生成真实存在的 `images_4/`。
- 3DGUT 使用训练准备后的 dataset。
- 导出 NuRec 和 LightField 两种 USDZ。

Isaac Sim 中优先打开 `exports/scene_nurec_isaac.usdz`。
