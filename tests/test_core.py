from __future__ import annotations

import struct
import tempfile
import unittest
import zipfile
from pathlib import Path

from PIL import Image
import yaml

from scenemill.adapters.colmap import (
    count_colmap_points,
    prepare_colmap_training_dataset,
    prepare_sampled_dataset,
    subsample_colmap_points,
    validate_colmap_dataset,
)
from scenemill.adapters.isaac_usd import validate_usdz_alignment
from scenemill.adapters.rosbag import sanitize_topic
from scenemill.config import deep_merge, load_config
from scenemill.pipeline import run_pipeline
from scenemill.runtime.oom_retry import looks_like_oom
from scenemill.stages import train as train_stage


def write_aligned_member(archive: zipfile.ZipFile, filename: str, data: bytes) -> None:
    base_offset = archive.fp.tell() + 30 + len(filename.encode())
    extra_len = (-base_offset) % 64
    if 0 < extra_len < 4:
        extra_len += 64
    info = zipfile.ZipInfo(filename)
    info.compress_type = zipfile.ZIP_STORED
    if extra_len:
        info.extra = (0xFFFF).to_bytes(2, "little") + (extra_len - 4).to_bytes(2, "little") + b"\0" * (extra_len - 4)
    archive.writestr(info, data)


class SceneMillCoreTests(unittest.TestCase):
    def test_sanitize_topic(self) -> None:
        self.assertEqual(sanitize_topic("/camera/color/image_raw"), "camera_color_image_raw")
        self.assertEqual(sanitize_topic("/"), "root")

    def test_oom_detection(self) -> None:
        self.assertTrue(looks_like_oom("torch.OutOfMemoryError: CUDA out of memory"))
        self.assertTrue(looks_like_oom("/tmp/run.sh: line 3: 225139 已杀死 python train.py"))
        self.assertTrue(looks_like_oom("Killed", 1))
        self.assertTrue(looks_like_oom("", 137))
        self.assertTrue(looks_like_oom("", -9))
        self.assertFalse(looks_like_oom("File not found"))

    def test_train_failure_does_not_require_checkpoint(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace = root / "workspace"

            def fake_run_command(cmd, *, cwd, log_path, dry_run=False, env_overrides=None):
                return train_stage.CommandResult(cmd=cmd, returncode=1, stdout="已杀死", log_path=log_path)

            def fail_find_latest_checkpoint(run_root):
                raise AssertionError("find_latest_checkpoint should not run after train failure")

            original_run_command = train_stage.run_command
            original_find_latest_checkpoint = train_stage.threedgrut.find_latest_checkpoint
            train_stage.run_command = fake_run_command
            train_stage.threedgrut.find_latest_checkpoint = fail_find_latest_checkpoint
            try:
                result, checkpoint = train_stage.run_train(
                    config={
                        "trainer": {"backend": "3dgrut", "experiment_name": "scene"},
                        "runtime": {"run_dir": str(root / "runs"), "grut_repo": str(root)},
                    },
                    dataset_root=root / "dataset",
                    workspace=workspace,
                    dry_run=False,
                )
            finally:
                train_stage.run_command = original_run_command
                train_stage.threedgrut.find_latest_checkpoint = original_find_latest_checkpoint

            self.assertEqual(result.returncode, 1)
            self.assertIsNone(checkpoint)
            self.assertEqual(result.log_path.name, "train_3dgrut_dataset.log")

    def test_deep_merge(self) -> None:
        merged = deep_merge({"a": {"b": 1, "c": 2}}, {"a": {"b": 3}})
        self.assertEqual(merged, {"a": {"b": 3, "c": 2}})

    def test_sampled_dataset(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            images = root / "images"
            images.mkdir()
            for index in range(5):
                (images / f"{index:03d}.png").write_bytes(b"fake")

            dataset = prepare_sampled_dataset(images, root / "workspace", 2)
            self.assertEqual(dataset.image_count, 3)
            self.assertTrue((dataset.images_dir / "000.png").is_symlink())

    def test_colmap_validation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            dataset = Path(tmp)
            (dataset / "images").mkdir()
            sparse = dataset / "sparse" / "0"
            sparse.mkdir(parents=True)
            for name in ["cameras.txt", "images.txt", "points3D.txt"]:
                (sparse / name).write_text("", encoding="utf-8")
            result = validate_colmap_dataset(dataset)
            self.assertTrue(result["ok"])

    def test_colmap_point_subsampling_binary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            sparse = Path(tmp) / "sparse" / "0"
            sparse.mkdir(parents=True)
            points = sparse / "points3D.bin"
            with points.open("wb") as fid:
                fid.write(struct.pack("<Q", 5))
                for point_id in range(1, 6):
                    fid.write(struct.pack("<QdddBBBd", point_id, float(point_id), 0.0, 0.0, 1, 2, 3, 0.1))
                    fid.write(struct.pack("<Q", 0))

            result = subsample_colmap_points(Path(tmp), max_points=2, seed=7)
            self.assertTrue(result["enabled"])
            self.assertEqual(result["original"], 5)
            self.assertEqual(count_colmap_points(Path(tmp)), 2)

    def test_prepare_training_dataset_downsamples_images_and_points(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            dataset = root / "dataset"
            images = dataset / "images"
            sparse = dataset / "sparse" / "0"
            images.mkdir(parents=True)
            sparse.mkdir(parents=True)
            Image.new("RGB", (8, 4), color=(255, 0, 0)).save(images / "000.jpg")
            for name in ["cameras.bin", "images.bin"]:
                (sparse / name).write_bytes(b"fake")
            with (sparse / "points3D.bin").open("wb") as fid:
                fid.write(struct.pack("<Q", 3))
                for point_id in range(1, 4):
                    fid.write(struct.pack("<QdddBBBd", point_id, float(point_id), 0.0, 0.0, 1, 2, 3, 0.1))
                    fid.write(struct.pack("<Q", 0))

            train_root, info = prepare_colmap_training_dataset(
                dataset,
                root / "workspace",
                {"trainer": {"dataset_downsample_factor": 2, "max_colmap_points": 2, "point_sample_seed": 1}},
            )

            self.assertTrue((train_root / "images_2" / "000.jpg").exists())
            with Image.open(train_root / "images_2" / "000.jpg") as image:
                self.assertEqual(image.size, (4, 2))
            self.assertEqual(count_colmap_points(train_root), 2)
            self.assertEqual(info["point_subsample"]["current"], 2)

    def test_usdz_alignment_validation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            aligned = Path(tmp) / "aligned.usdz"
            with zipfile.ZipFile(aligned, "w", compression=zipfile.ZIP_STORED) as archive:
                write_aligned_member(archive, "default.usda", b"#usda 1.0\n")
                write_aligned_member(archive, "gaussians.usdc", b"data")
            self.assertTrue(validate_usdz_alignment(aligned)["ok"])

            unaligned = Path(tmp) / "unaligned.usdz"
            with zipfile.ZipFile(unaligned, "w", compression=zipfile.ZIP_STORED) as archive:
                archive.writestr("default.usda", b"#usda 1.0\n")
            self.assertFalse(validate_usdz_alignment(unaligned)["ok"])

    def test_pipeline_dry_run_writes_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            images = root / "images"
            images.mkdir()
            for index in range(3):
                (images / f"{index:03d}.png").write_bytes(b"fake")

            config = root / "config.yaml"
            config.write_text(
                yaml.safe_dump(
                    {
                        "input": {"kind": "images", "path": str(images)},
                        "geometry": {
                            "backend": "da3",
                            "model": "depth-anything/DA3NESTED-GIANT-LARGE-1.1",
                            "process_res": 504,
                            "process_res_method": "upper_bound_resize",
                            "use_ray_pose": True,
                        },
                        "trainer": {
                            "backend": "3dgrut",
                            "config_name": "apps/colmap_3dgut.yaml",
                            "experiment_name": "dry_scene",
                            "dataset_downsample_factor": 1,
                            "n_iterations": 1,
                        },
                        "export": {"enabled": True, "formats": ["nurec", "lightfield"], "output_dir": None},
                        "runtime": {
                            "workspace": str(root / "workspace"),
                            "da3_env": "da3_recon",
                            "grut_env": "3dgrut_recon",
                            "da3_repo": "third_party/Depth-Anything-3",
                            "grut_repo": "third_party/3dgrut",
                            "cuda": {
                                "home": "/usr/local/cuda-12.4",
                                "arch_list": "8.6",
                                "cc": "/usr/bin/gcc-11",
                                "cxx": "/usr/bin/g++-11",
                            },
                        },
                        "retry": {"frame_steps": [2]},
                        "validation": {"enabled": True},
                    }
                ),
                encoding="utf-8",
            )

            manifest = run_pipeline(config_path=config, dry_run=True)
            manifest_path = root / "workspace" / "scene_manifest.yaml"
            self.assertTrue(manifest_path.exists())
            self.assertEqual(manifest["stages"]["preprocess"]["sampled_images"], 2)
            self.assertIn("exports", manifest["artifacts"])

    def test_load_config_overrides(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = Path(tmp) / "config.yaml"
            config.write_text("input: {kind: images}\nruntime: {}\n", encoding="utf-8")
            loaded = load_config(config, input_path=Path(tmp) / "images", workspace=Path(tmp) / "ws")
            self.assertTrue(str(loaded["input"]["path"]).endswith("images"))
            self.assertTrue(str(loaded["runtime"]["workspace"]).endswith("ws"))


if __name__ == "__main__":
    unittest.main()
