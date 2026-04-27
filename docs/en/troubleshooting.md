# Troubleshooting

## 3DGUT is killed or runs out of memory

Use the DA3 preset defaults:

```yaml
trainer:
  dataset_downsample_factor: 4
  max_colmap_points: 200000
```

DA3 can export millions of COLMAP points. 3DGUT initializes those as Gaussians, so point sampling is often more important than reducing the DA3 inference resolution.

## `images_4` not found

3DGUT expects downsampled image folders to physically exist. SceneMill creates them during `train_prepare` when `dataset_downsample_factor > 1`.

## USD prim validation says `pxr` is missing

The standard Python environment may not include USD bindings. Isaac can still load the USDZ, but prim validation needs `pxr`. Use Isaac's USD libraries or run validation inside an environment that exposes them.

## Hugging Face rate warning

Set `HF_TOKEN` if DA3 model downloads hit rate limits.
