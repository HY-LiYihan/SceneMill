# CLI 参考

SceneMill 统一入口：

```bash
./scenemill <command> [options]
```

| 命令 | 用途 |
| --- | --- |
| `run` | 按配置运行完整 pipeline。 |
| `ingest` | 把图片目录或 ROS bag 转成标准 `frames/` workspace。 |
| `geometry` | 生成 COLMAP-compatible dataset。 |
| `train` | 训练配置中的 Gaussian backend。 |
| `export` | 从 checkpoint 导出 Isaac/Omniverse USDZ。 |
| `validate` | 验证图片、COLMAP、USDZ alignment 和 USD prim。 |
| `doctor` | 检查 Python、GPU、conda env、third-party 路径。 |

常用参数：

```bash
--preset PRESET   内置 preset 简称：da3、colmap、rosbag。
-c, --config      SceneMill YAML 配置（与 --preset 互斥）。
--input           覆盖输入路径。
--workspace       覆盖输出 workspace。
--dry-run         只打印命令和写日志，不执行重任务。
```

`--preset` 是推荐的调用方式：

```bash
./scenemill run --preset da3    --input /path/to/images
./scenemill run --preset colmap --input /path/to/images
./scenemill run --preset rosbag --input /path/to/bag
```

需要自定义配置时使用 `-c`：

```bash
./scenemill run -c my_config.yaml --input /path/to/images
```

