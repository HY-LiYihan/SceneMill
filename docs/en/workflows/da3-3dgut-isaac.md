# DA3 + 3DGUT + Isaac

This is the recommended SceneMill workflow.

```bash
./scenemill run \
  -c configs/presets/images_da3_3dgut_isaac.yaml \
  --input /path/to/images \
  --workspace runs/scene_da3
```

Key behavior:

- DA3 exports a COLMAP-compatible reconstruction.
- SceneMill samples DA3's dense `points3D.bin` before training.
- SceneMill creates `images_4/` when `dataset_downsample_factor: 4`.
- 3DGUT trains from the prepared dataset.
- Export produces both NuRec and LightField USDZ assets.

Open `exports/scene_nurec_isaac.usdz` first in Isaac Sim.
