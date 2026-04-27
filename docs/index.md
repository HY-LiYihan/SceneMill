# SceneMill

SceneMill is a robot and Isaac-first reconstruction pipeline that turns real captures into COLMAP-compatible geometry, 3D Gaussian scenes, and Isaac/Omniverse-ready USDZ assets.

Choose a language:

- [English documentation](en/index.md)
- [中文文档](zh/index.md)

The first stable path is:

```text
images / ROS bag -> frames -> DA3 COLMAP export -> 3DGUT training -> NuRec + LightField USDZ
```
