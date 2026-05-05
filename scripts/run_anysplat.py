#!/usr/bin/env python3
"""Run AnySplat inference for SceneMill.

This wrapper keeps AnySplat imports inside the `anysplat` conda environment.
SceneMill calls it as a subprocess and consumes the YAML manifest it writes.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import torch
import yaml
from PIL import Image


IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}
NETWORK_SIZE = 448


def _list_images(images_dir: Path) -> list[Path]:
    images = sorted(path for path in images_dir.iterdir() if path.is_file() and path.suffix.lower() in IMAGE_EXTS)
    if not images:
        raise FileNotFoundError(f"No images found in {images_dir}")
    return images


def _path_or_none(path: Path | None) -> str | None:
    return str(path) if path is not None else None


def _preprocess_metadata(path: Path) -> dict:
    with Image.open(path) as image:
        if image.mode == "RGBA":
            image = image.convert("RGB")
        width, height = image.size

    if width > height:
        resized_height = NETWORK_SIZE
        resized_width = int(width * (resized_height / height))
    else:
        resized_width = NETWORK_SIZE
        resized_height = int(height * (resized_width / width))

    left = (resized_width - NETWORK_SIZE) // 2
    top = (resized_height - NETWORK_SIZE) // 2
    right = left + NETWORK_SIZE
    bottom = top + NETWORK_SIZE
    scale_x = resized_width / width
    scale_y = resized_height / height

    return {
        "image_path": str(path),
        "original_size": [int(width), int(height)],
        "resized_size": [int(resized_width), int(resized_height)],
        "crop_box_resized_px": [int(left), int(top), int(right), int(bottom)],
        "crop_box_source_px": [
            float(left / scale_x),
            float(top / scale_y),
            float(right / scale_x),
            float(bottom / scale_y),
        ],
        "network_resolution": [NETWORK_SIZE, NETWORK_SIZE],
    }


def _intrinsics_to_pixels(intrinsics: np.ndarray, width: int, height: int) -> np.ndarray:
    pixels = intrinsics.copy()
    pixels[..., 0, 0] *= width
    pixels[..., 0, 2] *= width
    pixels[..., 1, 1] *= height
    pixels[..., 1, 2] *= height
    return pixels


def main() -> int:
    parser = argparse.ArgumentParser(description="Run AnySplat and export Gaussian PLY for SceneMill.")
    parser.add_argument("--anysplat-root", required=True, type=Path)
    parser.add_argument("--input-images-dir", required=True, type=Path)
    parser.add_argument("--workspace", required=True, type=Path)
    parser.add_argument("--model-id", default="lhjiang/anysplat")
    parser.add_argument("--direct-single-image", action="store_true")
    parser.add_argument("--save-preview", action="store_true")
    args = parser.parse_args()

    anysplat_root = args.anysplat_root.resolve()
    input_images_dir = args.input_images_dir.resolve()
    workspace = args.workspace.resolve()
    workspace.mkdir(parents=True, exist_ok=True)

    if not anysplat_root.exists():
        raise FileNotFoundError(f"AnySplat root not found: {anysplat_root}")
    sys.path.insert(0, str(anysplat_root))

    from src.misc.image_io import save_interpolated_video
    from src.model.model.anysplat import AnySplat
    from src.model.ply_export import export_ply
    from src.utils.image import process_image

    image_paths = _list_images(input_images_dir)
    if len(image_paths) == 1 and not args.direct_single_image:
        raise ValueError("AnySplat received one image but --direct-single-image is disabled")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = AnySplat.from_pretrained(args.model_id).to(device)
    model.eval()
    for param in model.parameters():
        param.requires_grad = False

    preprocessing = [_preprocess_metadata(path) for path in image_paths]
    images = [process_image(str(path)) for path in image_paths]
    images_tensor = torch.stack(images, dim=0).unsqueeze(0).to(device)
    batch, views, _, height, width = images_tensor.shape

    with torch.no_grad():
        gaussians, pred_context_pose = model.inference((images_tensor + 1) * 0.5)

    ply_path = workspace / "gaussians.ply"
    export_ply(
        gaussians.means[0],
        gaussians.scales[0],
        gaussians.rotations[0],
        gaussians.harmonics[0],
        gaussians.opacities[0],
        ply_path,
    )

    intrinsics = pred_context_pose["intrinsic"].detach().cpu().numpy()
    extrinsics = pred_context_pose["extrinsic"].detach().cpu().numpy()
    intrinsics_pixels = _intrinsics_to_pixels(intrinsics, width, height)

    intrinsics_path = workspace / "camera_intrinsics.npy"
    intrinsics_pixels_path = workspace / "camera_intrinsics_pixels.npy"
    extrinsics_path = workspace / "camera_extrinsics.npy"
    np.save(str(intrinsics_path), intrinsics)
    np.save(str(intrinsics_pixels_path), intrinsics_pixels)
    np.save(str(extrinsics_path), extrinsics)

    rgb_preview_path = None
    depth_preview_path = None
    if args.save_preview and views > 1:
        rgb_preview, depth_preview = save_interpolated_video(
            pred_context_pose["extrinsic"],
            pred_context_pose["intrinsic"],
            batch,
            height,
            width,
            gaussians,
            str(workspace),
            model.decoder,
        )
        rgb_preview_path = Path(rgb_preview)
        depth_preview_path = Path(depth_preview)

    manifest = {
        "project": "AnySplat",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "model_id": args.model_id,
        "anysplat_root": str(anysplat_root),
        "input_images_dir": str(input_images_dir),
        "image_count": len(image_paths),
        "direct_single_image": bool(args.direct_single_image),
        "device": str(device),
        "artifacts": {
            "gaussian_ply": str(ply_path),
            "camera_intrinsics": str(intrinsics_path),
            "camera_intrinsics_pixels": str(intrinsics_pixels_path),
            "camera_extrinsics": str(extrinsics_path),
            "rgb_preview": _path_or_none(rgb_preview_path),
            "depth_preview": _path_or_none(depth_preview_path),
        },
        "camera": {
            "alignment_target": "crop_448",
            "intrinsics_convention": "normalized_and_pixel_pinhole",
            "extrinsics_convention": "anysplat_camera_to_world_3dgrut",
            "network_resolution": [int(width), int(height)],
            "preprocessing": preprocessing,
        },
    }
    manifest_path = workspace / "anysplat_manifest.yaml"
    manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True), encoding="utf-8")

    print(json.dumps({"manifest": str(manifest_path), "gaussian_ply": str(ply_path)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
