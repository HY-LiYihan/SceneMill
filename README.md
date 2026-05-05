# SceneMill

[![CI](https://github.com/HY-LiYihan/SceneMill/actions/workflows/test.yml/badge.svg)](https://github.com/HY-LiYihan/SceneMill/actions/workflows/test.yml)
[![Docs](https://github.com/HY-LiYihan/SceneMill/actions/workflows/docs.yml/badge.svg)](https://hy-liyihan.github.io/SceneMill/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

面向机器人和 Isaac Sim 的本地场景重建 pipeline。输入图片目录或 ROS bag，输出可直接导入 Isaac Sim 的 USDZ 资产。

**[📖 中文文档](https://hy-liyihan.github.io/SceneMill/zh/)** | [English Docs](https://hy-liyihan.github.io/SceneMill/)

```
图片 / ROS bag  →  auto 路由  →  AnySplat 或 DA3/3DGUT  →  NuRec + LightField USDZ
```

默认规则：少于 10 张图片走 AnySplat 快速低视角重建；10 张及以上走经典 DA3/COLMAP + 3DGUT 主线。

---

## 快速开始

**第一步：克隆并安装**

```bash
git clone --recursive git@github.com:HY-LiYihan/SceneMill.git
cd SceneMill
./scripts/create_env.sh          # 创建统一 conda 环境 scenemill
conda activate scenemill
./scripts/install_local.sh       # 安装 SceneMill 本体
```

**第二步：验证环境**

```bash
./scenemill doctor
```

**第三步：跑第一个场景**

```bash
./scenemill run --preset auto --input /path/to/images --workspace runs/my_scene
```

**第四步：验证输出**

```bash
./scenemill validate \
  --images-dir runs/my_scene/frames/images \
  --dataset runs/my_scene/colmap_dataset_step_1_train \
  --usdz runs/my_scene/exports/scene_nurec_isaac.usdz \
  --usdz runs/my_scene/exports/scene_lightfield_isaac.usdz
```

在 Isaac Sim 中打开 `exports/scene_nurec_isaac.usdz`。

---

## 支持矩阵

| 路径 | 状态 | 说明 |
| --- | --- | --- |
| 图片 → auto router → NuRec/LightField USDZ | **Stable** | 默认入口 |
| 少图/单图 → AnySplat → Gaussian PLY → USDZ | **Stable local** | 低视角快速重建 |
| 图片 → DA3 → 3DGUT → NuRec/LightField USDZ | **Stable** | 多视角经典主线 |
| ROS1 bag → frames → DA3 → 3DGUT → USDZ | **Stable** | 需要 `rosbags` |
| COLMAP 前端 | Experimental | 需要本机 `colmap` |
| VGGT 前端 | Reserved | preset 已保留，adapter 尚未启用 |

---

## CLI 速查

```bash
./scenemill run --preset auto   --input /path/to/images   # 自动选择 AnySplat 或 classic
./scenemill run --preset auto   --backend anysplat --input /path/to/images
./scenemill run --preset auto   --backend classic  --input /path/to/images
./scenemill run --preset da3    --input /path/to/images   # DA3/3DGUT classic
./scenemill run --preset colmap --input /path/to/images   # COLMAP 前端
./scenemill run --preset rosbag --input /path/to/bag      # ROS bag
./scenemill run --preset da3    --input /path/to/images --dry-run  # 只打印命令

./scenemill ingest    # 仅导入帧
./scenemill geometry  # 仅几何重建
./scenemill train     # 仅训练
./scenemill export    # 仅导出 USDZ
./scenemill validate  # 验证输出
./scenemill doctor    # 检查本机依赖
```

常用参数：

```
--preset PRESET   内置预设：auto / da3 / colmap / rosbag
-c, --config      自定义 YAML 配置（与 --preset 互斥）
--backend         覆盖 backend：auto / anysplat / classic
--input           输入路径
--workspace       输出目录
--dry-run         只打印命令，不执行重计算
```

---

## 环境要求

| 依赖 | 要求 |
| --- | --- |
| GPU | NVIDIA RTX 系列，≥ 8 GB VRAM |
| CUDA | 12.4 |
| conda | Miniconda 或 Anaconda |
| Isaac Sim | 单独安装，用于 USDZ 验证和导入 |

---

## 文档

完整文档见 **[https://hy-liyihan.github.io/SceneMill/](https://hy-liyihan.github.io/SceneMill/)**，包含：

- [安装指南](https://hy-liyihan.github.io/SceneMill/zh/installation/)
- [快速开始](https://hy-liyihan.github.io/SceneMill/zh/quickstart/)
- [Backend 选择](https://hy-liyihan.github.io/SceneMill/zh/backend-selection/)
- [CLI 参考](https://hy-liyihan.github.io/SceneMill/zh/cli/)
- [配置预设](https://hy-liyihan.github.io/SceneMill/zh/presets/)
- [ROS Bag 导入](https://hy-liyihan.github.io/SceneMill/zh/rosbag/)
- [Isaac USDZ 验证](https://hy-liyihan.github.io/SceneMill/zh/isaac-validation/)
- [常见问题](https://hy-liyihan.github.io/SceneMill/zh/troubleshooting/)

本地预览文档：

```bash
mkdocs serve
```

---

## 开发

```bash
PYTHONPATH=src python -m pytest tests/ -v
PYTHONPATH=src python -m compileall src tests
mkdocs build --strict
```

仓库边界：不提交 bag、checkpoint、USDZ、COLMAP 生成数据或本地运行结果。

---

## 目录结构

```
configs/       YAML 配置和预设
docs/          MkDocs 文档站（中英双语）
scripts/       安装、检查、测试脚本
src/           SceneMill Python 包
tests/         单元测试
third_party/   AnySplat、DA3 和 3DGUT 子模块
patches/       第三方兼容补丁（默认不应用）
runs/          本地运行输出（ignored）
data/          本地数据集（ignored）
```
