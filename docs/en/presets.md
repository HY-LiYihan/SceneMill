# Presets

Presets live in `configs/presets/`.

| Preset | Status | Use |
| --- | --- | --- |
| `images_da3_3dgut_isaac.yaml` | Stable | Primary image-folder reconstruction path. |
| `rosbag_da3_3dgut_isaac.yaml` | Stable local | ROS1 bag image export plus primary reconstruction path. |
| `images_colmap_3dgut_isaac.yaml` | Experimental | Traditional COLMAP geometry frontend. |
| `images_vggt_3dgut_isaac.yaml` | Reserved | Future VGGT COLMAP-compatible frontend. |

The DA3 presets default to `dataset_downsample_factor: 4` and `max_colmap_points: 200000` for 3DGUT stability on high-resolution image captures.
