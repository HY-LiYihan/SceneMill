# VGGT -> 3DGUT -> Isaac Workflow

Canonical status is documented in `docs/en/presets.md` and `docs/zh/presets.md`.

This is the intended second geometry frontend.

The preset exists at:

```text
configs/presets/images_vggt_3dgut_isaac.yaml
```

Current status:

- The SceneMill interface reserves `geometry.backend: vggt`.
- The concrete VGGT command adapter is intentionally not enabled until a local VGGT repo and COLMAP export command are added.
- Once enabled, it must produce the same contract as DA3: `images/` plus `sparse/0/cameras.*`, `images.*`, and `points3D.*`.
