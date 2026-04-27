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
- `docs/` 放 MkDocs 文档站。
- `third_party/` 只放 submodules。
- `runs/`、`tmp/`、`data/`、`aaa/` 是本地目录，默认 ignored。

不要提交 bags、checkpoints、USDZ、COLMAP 生成数据或本地 Codex 状态。
