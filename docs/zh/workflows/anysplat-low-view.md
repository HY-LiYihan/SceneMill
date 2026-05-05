# AnySplat 低视角工作流

AnySplat 是 SceneMill 的少图默认 backend。它适合单图或少量图片，目标是快速得到 Isaac 可加载的静态视觉背景。

```bash
./scenemill run --preset auto --backend anysplat \
  --input /path/to/images \
  --workspace runs/anysplat_scene
```

## 产物

```text
runs/anysplat_scene/
  frames/images/
  anysplat/
    anysplat_manifest.yaml
    gaussians.ply
    camera_intrinsics.npy
    camera_intrinsics_pixels.npy
    camera_extrinsics.npy
  exports/
    scene_nurec_isaac.usdz
    scene_lightfield_isaac.usdz
  scene_manifest.yaml
```

## 坐标和相机

AnySplat wrapper 会记录 448x448 网络输入对应的裁剪元数据、像素内参和外参。下游系统可以使用这些信息对齐 ego camera。

## 局限

- AnySplat 输出是静态视觉背景。
- 物体交互、碰撞、动态刚体和真实尺度不由 AnySplat 单独解决。
- 在 `image2sim` 中，物体 pose、scale 和支撑关系仍由 DA3、mask-depth 优化和 SceneGraph 处理。
