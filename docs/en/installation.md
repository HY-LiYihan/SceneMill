# Installation

## Clone

```bash
git clone --recursive git@github.com:HY-LiYihan/SceneMill.git
cd SceneMill
```

If the repository was cloned without submodules:

```bash
git submodule update --init --recursive
```

## Local Install

SceneMill is designed to run with the existing local conda environments used by DA3, 3DGUT, and Isaac Sim.

```bash
./scripts/install_local.sh
```

This installs SceneMill in editable mode with development and documentation dependencies and initializes submodules. `third_party/` is left pristine; SceneMill handles compatibility in its own wrappers and export post-processing.

## Expected Local Environments

The default presets expect:

| Tool | Default |
| --- | --- |
| DA3 conda env | `da3_recon` |
| 3DGUT conda env | `3dgrut_recon` |
| Isaac conda env | `env_isaacsim` |
| CUDA | `/usr/local/cuda-12.4` |
| Compiler | `gcc-11` / `g++-11` |

### Creating the conda environments

**DA3 (`da3_recon`)** — follow the setup instructions in `third_party/Depth-Anything-3/README.md`, then rename or create the env as `da3_recon`:

```bash
conda create -n da3_recon python=3.10
conda activate da3_recon
cd third_party/Depth-Anything-3
pip install -r requirements.txt
```

**3DGUT (`3dgrut_recon`)** — use the install script bundled with the submodule:

```bash
cd third_party/3dgrut
bash install_env.sh 3dgrut_recon
```

**Isaac Sim (`env_isaacsim`)** — follow the [NVIDIA Isaac Sim installation guide](https://docs.omniverse.nvidia.com/isaacsim/latest/installation/install_python.html) and create the env named `env_isaacsim`.

Run:

```bash
./scenemill doctor
./scripts/doctor.sh
```

