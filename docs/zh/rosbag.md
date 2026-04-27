# ROS Bag 导入

SceneMill 通过可选依赖 `rosbags` 支持 ROS1 image bag。

```bash
./scenemill run \
  -c configs/presets/rosbag_da3_3dgut_isaac.yaml \
  --input /path/to/bag_or_bag_directory \
  --workspace runs/rosbag_scene
```

如果 bag 里有多个图像 topic，在 YAML 里设置 `input.image_topic`。

当前支持 `rgb8`、`bgr8`、`rgba8`、`bgra8`、`mono8`、`8UC1`、`mono16`、`16UC1`。
