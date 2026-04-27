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
- `docs/en/` and `docs/zh/` contain localized MkDocs pages.
- `third_party/` contains submodules only.
- `runs/`, `tmp/`, `data/`, and `aaa/` are local-only and ignored.

Do not commit bags, checkpoints, USDZ assets, generated COLMAP datasets, or local Codex state.

## Documentation

SceneMill uses `mkdocs-static-i18n` with the folder layout. Keep navigation paths language-neutral in `mkdocs.yml` such as `quickstart.md`; the plugin resolves them to `docs/en/quickstart.md` or `docs/zh/quickstart.md` and creates the Material top-bar language switcher.
