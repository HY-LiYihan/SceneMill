from __future__ import annotations

import shutil
from pathlib import Path

from scenemill.schemas.artifacts import ColmapDataset


IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}


def list_images(images_dir: Path) -> list[Path]:
    images = sorted(path for path in images_dir.iterdir() if path.is_file() and path.suffix.lower() in IMAGE_EXTS)
    if not images:
        raise FileNotFoundError(f"No images found in {images_dir}")
    return images


def recreate_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def prepare_sampled_dataset(images_dir: Path, workspace: Path, frame_step: int) -> ColmapDataset:
    images = list_images(images_dir)
    dataset_root = workspace / f"colmap_dataset_step_{frame_step}"
    sampled_images_dir = dataset_root / "images"
    sparse_dir = dataset_root / "sparse" / "0"
    recreate_dir(dataset_root)
    sampled_images_dir.mkdir(parents=True, exist_ok=True)

    for src in images[::frame_step]:
        target = sampled_images_dir / src.name
        target.symlink_to(src.resolve())

    return ColmapDataset(
        root=dataset_root,
        images_dir=sampled_images_dir,
        sparse_dir=sparse_dir,
        frame_step=frame_step,
        image_count=len(list(sampled_images_dir.iterdir())),
    )


def validate_colmap_dataset(dataset_root: Path) -> dict[str, object]:
    sparse_root = dataset_root / "sparse" / "0"
    checks = {
        "images_dir": (dataset_root / "images").exists(),
        "cameras": (sparse_root / "cameras.bin").exists() or (sparse_root / "cameras.txt").exists(),
        "images": (sparse_root / "images.bin").exists() or (sparse_root / "images.txt").exists(),
        "points3D": (sparse_root / "points3D.bin").exists() or (sparse_root / "points3D.txt").exists(),
    }
    missing = [name for name, ok in checks.items() if not ok]
    result = {"ok": not missing, "missing": missing, "sparse_dir": str(sparse_root)}
    if missing:
        raise RuntimeError(f"COLMAP dataset is incomplete at {dataset_root}; missing: {missing}")
    return result


def build_colmap_commands(dataset: ColmapDataset, config: dict) -> list[list[str]]:
    geometry = config.get("geometry", {})
    database_path = dataset.root / "database.db"
    matcher = str(geometry.get("matcher", "sequential")).lower()
    matcher_command = "sequential_matcher" if matcher == "sequential" else "exhaustive_matcher"

    feature_cmd = [
        "colmap",
        "feature_extractor",
        "--database_path",
        str(database_path),
        "--image_path",
        str(dataset.images_dir),
        "--ImageReader.single_camera",
        "1" if geometry.get("single_camera", True) else "0",
    ]
    camera_model = geometry.get("camera_model")
    if camera_model:
        feature_cmd.extend(["--ImageReader.camera_model", str(camera_model)])

    return [
        feature_cmd,
        ["colmap", matcher_command, "--database_path", str(database_path)],
        [
            "colmap",
            "mapper",
            "--database_path",
            str(database_path),
            "--image_path",
            str(dataset.images_dir),
            "--output_path",
            str(dataset.root / "sparse"),
        ],
    ]
