# Development

## Local Checks

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m compileall src tests
mkdocs build --strict
```

## Repository Boundaries

- `src/scenemill/` contains product code.
- `configs/` contains stable and experimental presets.
- `docs/` contains the MkDocs site.
- `third_party/` contains submodules only.
- `runs/`, `tmp/`, `data/`, and `aaa/` are local-only and ignored.

Do not commit bags, checkpoints, USDZ assets, generated COLMAP datasets, or local Codex state.
