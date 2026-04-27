# Overview

SceneMill packages the reconstruction workflow into a reproducible local CLI.

Its stable production path is:

```text
images or ROS bag -> frames -> DA3 geometry -> 3DGUT Gaussian training -> Isaac USDZ
```

## Support Matrix

| Capability | Status | Notes |
| --- | --- | --- |
| Images -> DA3 -> 3DGUT -> NuRec/LightField USDZ | Stable | Primary local workflow. |
| ROS1 bag -> frames -> DA3 -> 3DGUT -> USDZ | Stable local | Requires `rosbags` and image topics. |
| COLMAP frontend | Experimental | Requires `colmap` on `PATH`. |
| VGGT frontend | Reserved | Preset exists, adapter is not enabled yet. |
| OpenSplat / gsplat backend | Future | Documented as a backend direction only. |

SceneMill keeps third-party algorithms in `third_party/` submodules and wraps them through adapters rather than forking their source.
