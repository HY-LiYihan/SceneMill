from __future__ import annotations

import zipfile
from pathlib import Path
from typing import Any


def usdz_member_offsets(path: Path) -> list[dict[str, Any]]:
    with zipfile.ZipFile(path) as archive:
        rows = []
        for info in archive.infolist():
            data_offset = info.header_offset + 30 + len(info.filename.encode()) + len(info.extra)
            rows.append(
                {
                    "filename": info.filename,
                    "size": info.file_size,
                    "data_offset": data_offset,
                    "aligned_64": data_offset % 64 == 0,
                }
            )
        return rows


def validate_usdz_alignment(path: Path) -> dict[str, Any]:
    members = usdz_member_offsets(path)
    return {"path": str(path), "ok": all(row["aligned_64"] for row in members), "members": members}


def inspect_usd_prims(path: Path) -> dict[str, Any]:
    try:
        from pxr import Usd
    except ImportError:
        return {"path": str(path), "ok": None, "warning": "pxr is not installed in this Python environment"}

    stage = Usd.Stage.Open(str(path))
    if not stage:
        return {"path": str(path), "ok": False, "prims": []}

    prims = [{"path": str(prim.GetPath()), "type": prim.GetTypeName()} for prim in stage.Traverse()]
    types = {row["type"] for row in prims}
    return {
        "path": str(path),
        "ok": True,
        "default_prim": str(stage.GetDefaultPrim().GetPath()) if stage.GetDefaultPrim() else None,
        "prims": prims,
        "has_nurec": "OmniNuRecFieldAsset" in types,
        "has_lightfield": "ParticleField3DGaussianSplat" in types,
    }

