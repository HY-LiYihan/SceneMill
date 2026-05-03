# Installation

## Prerequisites

| Dependency | Requirement |
| --- | --- |
| GPU | NVIDIA RTX series, ≥ 8 GB VRAM |
| CUDA | 12.4 (`/usr/local/cuda-12.4`) |
| Compiler | `gcc-11` / `g++-11` |
| conda | Miniconda or Anaconda |
| Isaac Sim | Separate install, for USDZ validation and import |

---

## One-command Install (Recommended)

```bash
# 1. Clone with submodules
git clone --recursive git@github.com:HY-LiYihan/SceneMill.git
cd SceneMill

# 2. Create unified conda environment (Python 3.11 + PyTorch CUDA 12.4 + DA3 + 3DGUT)
./scripts/create_env.sh
conda activate scenemill

# 3. Install SceneMill
./scripts/install_local.sh

# 4. Verify
./scenemill doctor
```

`create_env.sh` installs all DA3 and 3DGUT dependencies into a single `scenemill` environment.

---

## Manual Install (Custom Environment Names)

If you already have separate `da3_recon` and `3dgrut_recon` environments, you can keep using them by updating `da3_env` and `grut_env` in your config.

**DA3 environment** (see `third_party/Depth-Anything-3/README.md`):

```bash
conda create -n da3_recon python=3.11 -y
conda activate da3_recon
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
pip install -r third_party/Depth-Anything-3/requirements.txt
```

**3DGUT environment** (using the bundled install script):

```bash
cd third_party/3dgrut
bash install_env.sh 3dgrut_recon WITH_GCC11
cd ../..
```

**Isaac Sim environment** (`env_isaacsim`): follow the [NVIDIA Isaac Sim installation guide](https://docs.omniverse.nvidia.com/isaacsim/latest/installation/install_python.html) and name the environment `env_isaacsim`.

---

## Verify Installation

```bash
./scenemill doctor
./scripts/doctor.sh
```

Expected output:

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

If `da3_env` or `grut_env` shows `false`, the `scenemill` environment was not created successfully. Re-run `./scripts/create_env.sh`.
