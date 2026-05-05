# Backend Selection

SceneMill's default entrypoint is `auto`:

```bash
./scenemill run --preset auto --input /path/to/images --workspace runs/scene
```

## Auto Routing Rule

| Image count | Default backend | Notes |
| --- | --- | --- |
| `< 10` | `anysplat` | Low-view fast reconstruction, producing Gaussian PLY and Isaac USDZ. |
| `>= 10` | `classic` | DA3/COLMAP geometry plus 3DGUT training and NuRec/LightField USDZ export. |

The decision is written to `scene_manifest.yaml`:

```yaml
stages:
  router:
    mode: auto
    selected_backend: anysplat
    reason: image_count_below_threshold
    image_count: 1
    threshold: 10
```

## Force A Backend

```bash
./scenemill run --preset auto --backend anysplat --input /path/to/images
./scenemill run --preset auto --backend classic  --input /path/to/images
```

Classic presets still force the classic path:

```bash
./scenemill run --preset da3 --input /path/to/images
./scenemill run --preset colmap --input /path/to/images
```

## Use AnySplat When

- You have one or a few ego-view images.
- You need a fast static visual background.
- Another system handles objects, physics, and interaction, such as `image2sim`.

## Use Classic When

- You have a stable multi-view sequence.
- Multi-view consistency and trained 3D Gaussian quality matter more.
- You need the DA3/COLMAP geometry dataset as a research artifact.
