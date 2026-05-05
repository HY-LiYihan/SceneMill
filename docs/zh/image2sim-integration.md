# image2sim 集成

`image2sim` 把 SceneMill 当作静态背景重建后端使用。

职责边界：

| 系统 | 负责内容 |
| --- | --- |
| SceneMill | 背景重建：AnySplat、DA3/3DGUT、NuRec/LightField USDZ。 |
| image2sim | 物体检测、分割、Seed3D 资产、DA3 pose 信号、SceneGraph、Isaac 合成。 |

推荐调用方式：

```bash
./scenemill run --preset auto \
  --input runs/example/background/anysplat_input/images \
  --workspace runs/example/background/scenemill
```

`image2sim` 应读取：

```yaml
artifacts:
  selected_backend: anysplat
  exports:
    nurec: ...
    lightfield: ...
  gaussian_ply: ...
  camera_intrinsics_pixels: ...
  camera_extrinsics: ...
```

注意：AnySplat 和 SceneMill 输出的是静态视觉背景。物体的动态刚体、碰撞、质量、摩擦和 6DoF 重定位继续由 `image2sim` 的 SceneGraph/export 负责。
