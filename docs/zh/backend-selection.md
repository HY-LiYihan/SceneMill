# Backend 选择

SceneMill 的默认入口是 `auto`：

```bash
./scenemill run --preset auto --input /path/to/images --workspace runs/scene
```

## 自动路由规则

| 图片数量 | 默认 backend | 说明 |
| --- | --- | --- |
| `< 10` | `anysplat` | 低视角快速重建，输出 Gaussian PLY 和 Isaac USDZ。 |
| `>= 10` | `classic` | DA3/COLMAP 几何 + 3DGRUT 训练 + NuRec/LightField USDZ。 |

路由结果写入 `scene_manifest.yaml`：

```yaml
stages:
  router:
    mode: auto
    selected_backend: anysplat
    reason: image_count_below_threshold
    image_count: 1
    threshold: 10
```

## 强制选择

```bash
./scenemill run --preset auto --backend anysplat --input /path/to/images
./scenemill run --preset auto --backend classic  --input /path/to/images
```

经典 preset 仍然强制走 classic：

```bash
./scenemill run --preset da3 --input /path/to/images
./scenemill run --preset colmap --input /path/to/images
```

## 何时用 AnySplat

- 单图或少量 ego 图片。
- 需要快速得到静态视觉背景。
- 上游系统会另外处理物体、物理和交互，比如 `image2sim`。

## 何时用 classic

- 有稳定多视角序列。
- 更看重多视角一致性和训练式 3D Gaussian 质量。
- 需要 DA3/COLMAP 几何数据集作为后续研究产物。
