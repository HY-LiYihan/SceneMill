from __future__ import annotations

import random
import shutil
import struct
from pathlib import Path

from PIL import Image

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


def count_colmap_points(dataset_root: Path) -> int | None:
    sparse_root = dataset_root / "sparse" / "0"
    points_bin = sparse_root / "points3D.bin"
    points_txt = sparse_root / "points3D.txt"
    if points_bin.exists():
        with points_bin.open("rb") as fid:
            data = fid.read(8)
        return struct.unpack("<Q", data)[0] if len(data) == 8 else None
    if points_txt.exists():
        return sum(
            1
            for line in points_txt.read_text(encoding="utf-8").splitlines()
            if line and not line.startswith("#")
        )
    return None


def _subsample_points3d_bin(path: Path, *, max_points: int, seed: int) -> tuple[int, int]:
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with path.open("rb") as src:
        total_points = struct.unpack("<Q", src.read(8))[0]
        if total_points <= max_points:
            return total_points, total_points

        selected = set(random.Random(seed).sample(range(total_points), max_points))
        with tmp_path.open("wb") as dst:
            dst.write(struct.pack("<Q", max_points))
            for index in range(total_points):
                point_data = src.read(43)
                if len(point_data) != 43:
                    raise ValueError(f"Unexpected EOF while reading {path}")
                track_len_data = src.read(8)
                if len(track_len_data) != 8:
                    raise ValueError(f"Unexpected EOF while reading {path}")
                track_len = struct.unpack("<Q", track_len_data)[0]
                track_data = src.read(8 * track_len)
                if len(track_data) != 8 * track_len:
                    raise ValueError(f"Unexpected EOF while reading {path}")
                if index in selected:
                    dst.write(point_data)
                    dst.write(track_len_data)
                    dst.write(track_data)

    tmp_path.replace(path)
    return total_points, max_points


def _subsample_points3d_txt(path: Path, *, max_points: int, seed: int) -> tuple[int, int]:
    lines = path.read_text(encoding="utf-8").splitlines()
    points = [line for line in lines if line and not line.startswith("#")]
    total_points = len(points)
    if total_points <= max_points:
        return total_points, total_points

    selected_indexes = sorted(random.Random(seed).sample(range(total_points), max_points))
    selected = [points[index] for index in selected_indexes]
    with path.open("w", encoding="utf-8") as fid:
        fid.write("# 3D point list with one line of data per point:\n")
        fid.write("#   POINT3D_ID, X, Y, Z, R, G, B, ERROR, TRACK[] as (IMAGE_ID, POINT2D_IDX)\n")
        fid.write(f"# Number of points: {len(selected)}, mean track length: unknown\n")
        for line in selected:
            fid.write(line + "\n")
    return total_points, len(selected)


def subsample_colmap_points(dataset_root: Path, *, max_points: int, seed: int = 42) -> dict[str, int | str | bool]:
    sparse_root = dataset_root / "sparse" / "0"
    points_bin = sparse_root / "points3D.bin"
    points_txt = sparse_root / "points3D.txt"
    if points_bin.exists():
        original, current = _subsample_points3d_bin(points_bin, max_points=max_points, seed=seed)
        return {"enabled": original > current, "format": "bin", "original": original, "current": current}
    if points_txt.exists():
        original, current = _subsample_points3d_txt(points_txt, max_points=max_points, seed=seed)
        return {"enabled": original > current, "format": "txt", "original": original, "current": current}
    raise FileNotFoundError(f"No points3D.bin or points3D.txt found under {sparse_root}")


def create_downsampled_images(dataset_root: Path, *, factor: int, quality: int = 95) -> dict[str, int | str | bool]:
    if factor <= 1:
        return {"enabled": False, "factor": factor, "count": 0, "images_dir": str(dataset_root / "images")}

    source_dir = dataset_root / "images"
    output_dir = dataset_root / f"images_{factor}"
    output_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    for source in list_images(source_dir):
        target = output_dir / source.name
        with Image.open(source) as image:
            width, height = image.size
            resized = image.resize(
                (max(1, round(width / factor)), max(1, round(height / factor))),
                Image.Resampling.LANCZOS,
            )
            resized.save(target, quality=quality)
        count += 1
    return {"enabled": True, "factor": factor, "count": count, "images_dir": str(output_dir)}


def prepare_colmap_training_dataset(dataset_root: Path, workspace: Path, config: dict) -> tuple[Path, dict[str, object]]:
    trainer = config.get("trainer", {})
    downsample_factor = int(trainer.get("dataset_downsample_factor", 1))
    max_points_value = trainer.get("max_colmap_points")
    max_points = int(max_points_value) if max_points_value else None
    point_seed = int(trainer.get("point_sample_seed", 42))

    if downsample_factor <= 1 and not max_points:
        return dataset_root, {
            "dataset_root": str(dataset_root),
            "image_downsample": {"enabled": False, "factor": downsample_factor},
            "point_subsample": {"enabled": False, "current": count_colmap_points(dataset_root)},
        }

    train_root = workspace / f"{dataset_root.name}_train"
    recreate_dir(train_root)
    shutil.copytree(dataset_root / "sparse", train_root / "sparse")
    (train_root / "images").mkdir(parents=True, exist_ok=True)
    for source in list_images(dataset_root / "images"):
        target = train_root / "images" / source.name
        target.symlink_to(source.resolve())

    image_info = create_downsampled_images(train_root, factor=downsample_factor)
    if max_points:
        point_info = subsample_colmap_points(train_root, max_points=max_points, seed=point_seed)
    else:
        point_info = {"enabled": False, "current": count_colmap_points(train_root)}

    return train_root, {
        "dataset_root": str(train_root),
        "source_dataset_root": str(dataset_root),
        "image_downsample": image_info,
        "point_subsample": point_info,
    }


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
