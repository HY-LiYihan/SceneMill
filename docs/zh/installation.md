# 安装

## 前提条件

| 依赖 | 要求 |
| --- | --- |
| GPU | NVIDIA RTX 系列，≥ 8 GB VRAM |
| CUDA | 12.4（`/usr/local/cuda-12.4`） |
| 编译器 | `gcc-11` / `g++-11` |
| conda | Miniconda 或 Anaconda |
| Isaac Sim | 单独安装，用于 USDZ 验证和导入 |

---

## 一键安装（推荐）

```bash
# 1. 克隆（含子模块）
git clone --recursive git@github.com:HY-LiYihan/SceneMill.git
cd SceneMill

# 2. 创建统一 conda 环境（Python 3.11 + PyTorch CUDA 12.4 + DA3 + 3DGUT）
./scripts/create_env.sh
conda activate scenemill

# 3. 安装 SceneMill 本体
./scripts/install_local.sh

# 4. 验证
./scenemill doctor
```

`create_env.sh` 会自动安装 DA3 和 3DGUT 的所有依赖到同一个 `scenemill` 环境中。

---

## 分步安装（自定义环境名或已有环境）

如果你已经有 `da3_recon` 和 `3dgrut_recon` 两个独立环境，可以继续使用，只需在 config 中修改对应的 `da3_env` 和 `grut_env` 字段。

**DA3 环境**（参考 `third_party/Depth-Anything-3/README.md`）：

```bash
conda create -n da3_recon python=3.11 -y
conda activate da3_recon
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
pip install -r third_party/Depth-Anything-3/requirements.txt
```

**3DGUT 环境**（使用子模块自带脚本）：

```bash
cd third_party/3dgrut
bash install_env.sh 3dgrut_recon WITH_GCC11
cd ../..
```

**Isaac Sim 环境**（`env_isaacsim`）：参考 [NVIDIA Isaac Sim 安装文档](https://docs.omniverse.nvidia.com/isaacsim/latest/installation/install_python.html)，将环境命名为 `env_isaacsim`。

---

## 验证安装

```bash
./scenemill doctor
./scripts/doctor.sh
```

预期输出：

```
python: /path/to/conda/envs/scenemill/bin/python
gpu: NVIDIA RTX A5000, 24564 MiB, ...
conda: /path/to/conda/bin/conda
da3_env: true
grut_env: true
isaac_env: true
da3_repo: true
grut_repo: true
```

如果 `da3_env` 或 `grut_env` 显示 `false`，说明 `scenemill` 环境未创建成功，重新运行 `./scripts/create_env.sh`。
