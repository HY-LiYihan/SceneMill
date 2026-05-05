# Pipeline Concepts

SceneMill stages are intentionally narrow:

| Stage | Contract |
| --- | --- |
| Ingest | Produces `frames/` with normalized images and metadata. |
| Router | Selects `anysplat` or `classic` from image count and config. |
| AnySplat | Low-view path that writes `gaussians.ply`, camera estimates, and USDZ exports. |
| Preprocess | Samples frames into `colmap_dataset_step_<N>/images`. |
| Geometry | Produces `sparse/0/cameras.*`, `images.*`, and `points3D.*`. |
| Train Prepare | Creates train-safe assets such as `images_4/` and sampled COLMAP points. |
| Train | Runs 3DGUT and writes checkpoints and metrics. |
| Export | Writes NuRec and LightField USDZ assets. |
| Validate | Checks file completeness, USDZ alignment, and USD prim types when `pxr` is available. |

Each run writes `scene_manifest.yaml` with inputs, routing, commands, logs, retries, artifacts, and validation results.
