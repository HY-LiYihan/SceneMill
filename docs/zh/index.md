# 项目介绍

SceneMill 是一个机器人与 Isaac 优先的本地重建 pipeline。

默认主线现在是 auto router：

```text
图片或 ROS bag -> frames -> 路由选择 -> AnySplat 或 DA3/3DGUT -> Isaac USDZ
```

路由规则很直接：少于 10 张图默认走 AnySplat 快速低视角重建；10 张及以上默认走经典 DA3/COLMAP -> 3DGUT 训练主线。用户也可以显式强制 `anysplat` 或 `classic`。

## 支持矩阵

| 能力 | 状态 | 说明 |
| --- | --- | --- |
| 图片 -> auto router -> NuRec/LightField USDZ | Stable | 默认入口，自动选择低视角或经典主线。 |
| 少图/单图 -> AnySplat -> Gaussian PLY -> USDZ | Stable local | 低视角快速重建，适合 image2sim 背景。 |
| 图片 -> DA3 -> 3DGUT -> NuRec/LightField USDZ | Stable | 多视角经典高质量主线。 |
| ROS1 bag -> frames -> DA3 -> 3DGUT -> USDZ | Stable local | 需要 `rosbags` 和图像 topic。 |
| COLMAP frontend | Experimental | 需要本机 `colmap`。 |
| VGGT frontend | Reserved | preset 已保留，adapter 尚未启用。 |
| OpenSplat / gsplat backend | Future | 后续 backend 方向。 |

SceneMill 不深度 fork 第三方算法，而是通过 `third_party/` submodule 和 adapters 封装它们。
