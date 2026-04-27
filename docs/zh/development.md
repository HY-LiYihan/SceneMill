# 开发指南

## 本地检查

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m compileall src tests
mkdocs build --strict
```

## 仓库边界

- `src/scenemill/` 放产品代码。
- `configs/` 放稳定和实验配置。
- `docs/en/` 和 `docs/zh/` 放不同语言的 MkDocs 页面。
- `third_party/` 只放 submodules。
- `runs/`、`tmp/`、`data/`、`aaa/` 是本地目录，默认 ignored。

不要提交 bags、checkpoints、USDZ、COLMAP 生成数据或本地 Codex 状态。

## 文档站

SceneMill 使用 `mkdocs-static-i18n` 的 folder layout。`mkdocs.yml` 里的导航路径保持语言无关，例如 `quickstart.md`；插件会自动解析到 `docs/en/quickstart.md` 或 `docs/zh/quickstart.md`，并生成 Material 顶部语言切换按钮。
