# Overview

SceneMill packages the reconstruction workflow into a reproducible local CLI.

The default production path is now the auto router:

```text
images or ROS bag -> frames -> backend router -> AnySplat or DA3/3DGUT -> Isaac USDZ
```

The rule is intentionally simple: fewer than 10 images use AnySplat for fast low-view reconstruction; 10 or more images use the classic DA3/COLMAP -> 3DGUT training path. Users can still force `anysplat` or `classic`.

## Support Matrix

| Capability | Status | Notes |
| --- | --- | --- |
| Images -> auto router -> NuRec/LightField USDZ | Stable | Default entrypoint with backend selection. |
| Few images / single image -> AnySplat -> Gaussian PLY -> USDZ | Stable local | Low-view fast reconstruction, useful for image2sim backgrounds. |
| Images -> DA3 -> 3DGUT -> NuRec/LightField USDZ | Stable | Classic multi-view quality path. |
| ROS1 bag -> frames -> DA3 -> 3DGUT -> USDZ | Stable local | Requires `rosbags` and image topics. |
| COLMAP frontend | Experimental | Requires `colmap` on `PATH`. |
| VGGT frontend | Reserved | Preset exists, adapter is not enabled yet. |
| OpenSplat / gsplat backend | Future | Documented as a backend direction only. |

SceneMill keeps third-party algorithms in `third_party/` submodules and wraps them through adapters rather than forking their source.
