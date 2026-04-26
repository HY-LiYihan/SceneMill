from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image


def sanitize_topic(topic: str) -> str:
    return re.sub(r"[^a-zA-Z0-9._-]+", "_", topic.strip("/")) or "root"


def image_from_msg(msg: Any) -> Image.Image:
    height = int(msg.height)
    width = int(msg.width)
    encoding = str(msg.encoding).lower()
    data = bytes(msg.data)

    if encoding == "rgb8":
        arr = np.frombuffer(data, dtype=np.uint8).reshape(height, width, 3)
        return Image.fromarray(arr, mode="RGB")
    if encoding == "bgr8":
        arr = np.frombuffer(data, dtype=np.uint8).reshape(height, width, 3)
        return Image.fromarray(arr[:, :, ::-1], mode="RGB")
    if encoding == "rgba8":
        arr = np.frombuffer(data, dtype=np.uint8).reshape(height, width, 4)
        return Image.fromarray(arr, mode="RGBA")
    if encoding == "bgra8":
        arr = np.frombuffer(data, dtype=np.uint8).reshape(height, width, 4)
        return Image.fromarray(arr[:, :, [2, 1, 0, 3]], mode="RGBA")
    if encoding in {"mono8", "8uc1"}:
        arr = np.frombuffer(data, dtype=np.uint8).reshape(height, width)
        return Image.fromarray(arr, mode="L")
    if encoding in {"mono16", "16uc1"}:
        arr = np.frombuffer(data, dtype=np.uint16).reshape(height, width)
        return Image.fromarray(arr)
    raise ValueError(f"unsupported encoding: {msg.encoding}")


def export_ros1_images(bag_dir: Path, output_dir: Path) -> dict[str, int]:
    try:
        from rosbags.rosbag1 import Reader
        from rosbags.typesys import Stores, get_typestore
    except ImportError as exc:
        raise RuntimeError("ROS bag ingest requires the optional 'rosbags' dependency") from exc

    typestore = get_typestore(Stores.ROS1_NOETIC)
    bag_files = sorted(bag_dir.glob("data_*.bag")) if bag_dir.is_dir() else [bag_dir]
    if not bag_files:
        raise FileNotFoundError(f"No ROS1 bag files found under {bag_dir}")

    counts: dict[str, int] = defaultdict(int)
    output_dir.mkdir(parents=True, exist_ok=True)

    for bag_file in bag_files:
        with Reader(bag_file) as reader:
            image_connections = [conn for conn in reader.connections if conn.msgtype == "sensor_msgs/msg/Image"]
            image_topics = {conn.topic for conn in image_connections}
            for conn, _, rawdata in reader.messages():
                if conn.topic not in image_topics:
                    continue
                msg = typestore.deserialize_ros1(rawdata, conn.msgtype)
                image = image_from_msg(msg)
                topic_dir = output_dir / sanitize_topic(conn.topic)
                topic_dir.mkdir(parents=True, exist_ok=True)
                stamp = f"{msg.header.stamp.sec}_{msg.header.stamp.nanosec:09d}"
                index = counts[conn.topic]
                image.save(topic_dir / f"{index:06d}_{stamp}.png")
                counts[conn.topic] += 1

    return dict(counts)

