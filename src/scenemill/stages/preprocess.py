from __future__ import annotations

from pathlib import Path

from scenemill.adapters.colmap import prepare_sampled_dataset
from scenemill.schemas.artifacts import ColmapDataset


def sample_frames_to_colmap_dataset(images_dir: Path, workspace: Path, frame_step: int) -> ColmapDataset:
    return prepare_sampled_dataset(images_dir, workspace, frame_step)

