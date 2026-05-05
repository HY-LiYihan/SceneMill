# image2sim Integration

`image2sim` uses SceneMill as its static background reconstruction backend.

Responsibilities:

| System | Responsibility |
| --- | --- |
| SceneMill | Background reconstruction: AnySplat, DA3/3DGUT, NuRec/LightField USDZ. |
| image2sim | Object detection, segmentation, Seed3D assets, DA3 pose signals, SceneGraph, Isaac composition. |

Recommended call:

```bash
./scenemill run --preset auto \
  --input runs/example/background/anysplat_input/images \
  --workspace runs/example/background/scenemill
```

`image2sim` should read:

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

SceneMill and AnySplat output static visual backgrounds. Dynamic rigid bodies, collisions, mass, friction, and 6DoF object relocalization remain `image2sim` SceneGraph/export responsibilities.
