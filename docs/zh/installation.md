# 安装

## 克隆仓库

```bash
git clone --recursive git@github.com:HY-LiYihan/SceneMill.git
cd SceneMill
```

如果 clone 时没有带 submodule：

```bash
git submodule update --init --recursive
```

## 本地安装

SceneMill 首版优先适配当前本机 conda/CUDA/Isaac 工作流：

```bash
./scripts/install_local.sh
```

脚本会做 editable install、安装开发/文档依赖并初始化 submodules。`third_party/` 会保持干净；SceneMill 会在自己的 wrapper 和导出后处理中处理兼容问题。

## 默认环境

| 工具 | 默认值 |
| --- | --- |
| DA3 conda env | `da3_recon` |
| 3DGUT conda env | `3dgrut_recon` |
| Isaac conda env | `env_isaacsim` |
| CUDA | `/usr/local/cuda-12.4` |
| 编译器 | `gcc-11` / `g++-11` |

### 创建 conda 环境

**DA3 (`da3_recon`)** — 参考 `third_party/Depth-Anything-3/README.md`，将环境命名为 `da3_recon`：

```bash
conda create -n da3_recon python=3.10
conda activate da3_recon
cd third_party/Depth-Anything-3
pip install -r requirements.txt
```

**3DGUT (`3dgrut_recon`)** — 使用 submodule 自带的安装脚本：

```bash
cd third_party/3dgrut
bash install_env.sh 3dgrut_recon
```

**Isaac Sim (`env_isaacsim`)** — 参考 [NVIDIA Isaac Sim 安装文档](https://docs.omniverse.nvidia.com/isaacsim/latest/installation/install_python.html)，将环境命名为 `env_isaacsim`。

检查本机状态：

```bash
./scenemill doctor
./scripts/doctor.sh
```

