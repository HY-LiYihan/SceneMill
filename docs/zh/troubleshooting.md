# 常见问题

## 3DGUT 被 killed 或 OOM

优先使用 DA3 preset 默认值：

```yaml
trainer:
  dataset_downsample_factor: 4
  max_colmap_points: 200000
```

DA3 可能导出数百万 COLMAP points。3DGUT 会把这些点初始化成高斯，所以采样点云通常比降低 DA3 推理分辨率更关键。

## 找不到 `images_4`

3DGUT 不会自动 resize 图片；它要求 `images_4/` 真实存在。SceneMill 会在 `dataset_downsample_factor > 1` 时于 `train_prepare` 阶段创建。

## USD prim validation 提示缺少 `pxr`

普通 Python 环境可能没有 USD bindings。Isaac 仍可能能加载 USDZ，但 prim 类型验证需要 `pxr`。

## Hugging Face rate warning

如果 DA3 下载模型遇到限速，设置 `HF_TOKEN`。
