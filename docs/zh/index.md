# 项目介绍

SceneMill 是一个机器人与 Isaac 优先的本地重建 pipeline。

稳定主线是：

```text
图片或 ROS bag -> frames -> DA3 几何 -> 3DGUT 高斯训练 -> Isaac USDZ
```

## 支持矩阵

| 能力 | 状态 | 说明 |
| --- | --- | --- |
| 图片 -> DA3 -> 3DGUT -> NuRec/LightField USDZ | Stable | 第一主线。 |
| ROS1 bag -> frames -> DA3 -> 3DGUT -> USDZ | Stable local | 需要 `rosbags` 和图像 topic。 |
| COLMAP frontend | Experimental | 需要本机 `colmap`。 |
| VGGT frontend | Reserved | preset 已保留，adapter 尚未启用。 |
| OpenSplat / gsplat backend | Future | 后续 backend 方向。 |

SceneMill 不深度 fork 第三方算法，而是通过 `third_party/` submodule 和 adapters 封装它们。
