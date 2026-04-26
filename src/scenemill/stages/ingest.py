from __future__ import annotations

from pathlib import Path

from scenemill.adapters.colmap import list_images, recreate_dir
from scenemill.adapters.rosbag import export_ros1_images, sanitize_topic
from scenemill.schemas.artifacts import FrameSet


def ingest_images(input_path: Path, workspace: Path) -> FrameSet:
    images = list_images(input_path)
    frames_root = workspace / "frames"
    images_dir = frames_root / "images"
    recreate_dir(frames_root)
    images_dir.mkdir(parents=True, exist_ok=True)
    metadata = ["frame_index,source_path,filename\n"]
    for index, src in enumerate(images):
        target = images_dir / src.name
        target.symlink_to(src.resolve())
        metadata.append(f"{index},{src.resolve()},{src.name}\n")
    (frames_root / "frames.csv").write_text("".join(metadata), encoding="utf-8")
    return FrameSet(root=frames_root, images_dir=images_dir, count=len(images))


def ingest_rosbag(input_path: Path, workspace: Path, topic_hint: str | None = None) -> FrameSet:
    frames_root = workspace / "frames"
    export_root = frames_root / "rosbag_images"
    recreate_dir(frames_root)
    counts = export_ros1_images(input_path, export_root)
    if not counts:
        raise RuntimeError(f"No sensor_msgs/Image topics found in {input_path}")

    if topic_hint:
        topic_dir = export_root / sanitize_topic(topic_hint)
    else:
        topic = max(counts, key=counts.get)
        topic_dir = export_root / topic.strip("/").replace("/", "_")
    images = list_images(topic_dir)
    return FrameSet(root=frames_root, images_dir=topic_dir, count=len(images))


def run_ingest(config: dict, workspace: Path) -> FrameSet:
    input_cfg = config.get("input", {})
    input_path = Path(input_cfg["path"]).resolve()
    kind = str(input_cfg.get("kind", "images")).lower()
    if kind == "images":
        return ingest_images(input_path, workspace)
    if kind in {"rosbag", "ros1_bag"}:
        return ingest_rosbag(input_path, workspace, input_cfg.get("image_topic"))
    raise ValueError(f"Unsupported input.kind: {kind}")
