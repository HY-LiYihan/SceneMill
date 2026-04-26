from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


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

