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

This installs SceneMill in editable mode with development and documentation dependencies, initializes submodules, and applies the current third-party compatibility patches.

## Expected Local Environments

The default presets expect:

| Tool | Default |
| --- | --- |
| DA3 conda env | `da3_recon` |
| 3DGUT conda env | `3dgrut_recon` |
| Isaac conda env | `env_isaacsim` |
| CUDA | `/usr/local/cuda-12.4` |
| Compiler | `gcc-11` / `g++-11` |

Run:

```bash
./scenemill doctor
./scripts/doctor.sh
```
