# ROS Bag Ingest

SceneMill supports ROS1 image bag ingest through the optional `rosbags` dependency.

```bash
./scenemill run \
  -c configs/presets/rosbag_da3_3dgut_isaac.yaml \
  --input /path/to/bag_or_bag_directory \
  --workspace runs/rosbag_scene
```

If the bag has multiple image topics, set `input.image_topic` in the YAML config.

Supported encodings include `rgb8`, `bgr8`, `rgba8`, `bgra8`, `mono8`, `8UC1`, `mono16`, and `16UC1`.
