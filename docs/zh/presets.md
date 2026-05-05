# 配置预设

预设位于 `configs/presets/`。

| Preset | 状态 | 用途 |
| --- | --- | --- |
| `images_auto_isaac.yaml` | Stable | 默认图片入口：少于 10 张走 AnySplat，否则走 classic。 |
| `images_da3_3dgut_isaac.yaml` | Stable | 图片目录重建主线。 |
| `rosbag_da3_3dgut_isaac.yaml` | Stable local | ROS1 bag 图像导出加重建主线。 |
| `images_colmap_3dgut_isaac.yaml` | Experimental | 传统 COLMAP 几何前端。 |
| `images_vggt_3dgut_isaac.yaml` | Reserved | 后续 VGGT COLMAP-compatible 前端。 |

`auto` preset 通过 `router.low_view_threshold: 10` 控制后端选择。DA3 preset 默认使用 `dataset_downsample_factor: 4` 和 `max_colmap_points: 200000`，用于稳定处理高分辨率图片和 DA3 稠密点云。
