# DA3 -> 3DGUT -> Isaac Workflow

Canonical documentation:

- English: `docs/en/workflows/da3-3dgut-isaac.md`
- 中文: `docs/zh/workflows/da3-3dgut-isaac.md`

Use this workflow when COLMAP is unreliable or you want a feed-forward geometry frontend.

```bash
PYTHONPATH=src python3 -m scenemill.cli run \
  -c configs/presets/images_da3_3dgut_isaac.yaml \
  --input /path/to/images \
  --workspace runs/scene_da3
```

Key behavior:

- DA3 exports a COLMAP-compatible `sparse/0` reconstruction.
- 3DGUT trains from the generated dataset.
- SceneMill exports both NuRec and LightField USDZ assets.
- OOM retries increase `frame_step` according to the preset.

Open `exports/scene_nurec_isaac.usdz` first in Isaac Sim. Use the LightField export as fallback.
