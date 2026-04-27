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

脚本会做 editable install、安装开发/文档依赖、初始化 submodules，并应用当前 third-party 兼容补丁。

## 默认环境

| 工具 | 默认值 |
| --- | --- |
| DA3 conda env | `da3_recon` |
| 3DGUT conda env | `3dgrut_recon` |
| Isaac conda env | `env_isaacsim` |
| CUDA | `/usr/local/cuda-12.4` |
| 编译器 | `gcc-11` / `g++-11` |

检查本机状态：

```bash
./scenemill doctor
./scripts/doctor.sh
```
