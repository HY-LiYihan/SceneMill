# Pipeline 概念

SceneMill 的每个 stage 都有明确产物契约：

| Stage | 契约 |
| --- | --- |
| Ingest | 生成标准 `frames/` 图片与 metadata。 |
| Router | 根据图片数量和配置选择 `anysplat` 或 `classic`。 |
| AnySplat | 少图路径，生成 `gaussians.ply`、相机估计和 USDZ export。 |
| Preprocess | 抽帧到 `colmap_dataset_step_<N>/images`。 |
| Geometry | 生成 `sparse/0/cameras.*`、`images.*`、`points3D.*`。 |
| Train Prepare | 生成训练安全数据，比如 `images_4/` 和采样后的 COLMAP points。 |
| Train | 运行 3DGUT，写 checkpoint 和 metrics。 |
| Export | 导出 NuRec 和 LightField USDZ。 |
| Validate | 检查文件完整性、USDZ 64-byte alignment，以及可用时检查 USD prim 类型。 |

每次运行都会写 `scene_manifest.yaml`，记录输入、路由、命令、日志、重试、产物和验证结果。
