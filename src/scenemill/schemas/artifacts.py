from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class FrameSet:
    root: Path
    images_dir: Path
    count: int


@dataclass(slots=True)
class ColmapDataset:
    root: Path
    images_dir: Path
    sparse_dir: Path
    frame_step: int
    image_count: int


@dataclass(slots=True)
class AnySplatScene:
    workspace: Path
    manifest_path: Path
    gaussian_ply: Path
    exports: dict[str, Path]
    camera_intrinsics: Path | None = None
    camera_intrinsics_pixels: Path | None = None
    camera_extrinsics: Path | None = None
    camera_metadata: dict[str, Any] | None = None
