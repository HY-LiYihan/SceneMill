from __future__ import annotations


GEOMETRY_BACKENDS = {"colmap", "da3", "vggt"}
TRAIN_BACKENDS = {"3dgrut"}
EXPORT_FORMATS = {"nurec", "lightfield"}


def validate_backend(name: str, supported: set[str], kind: str) -> str:
    normalized = name.lower()
    if normalized not in supported:
        raise ValueError(f"Unsupported {kind} backend '{name}'. Supported: {sorted(supported)}")
    return normalized

