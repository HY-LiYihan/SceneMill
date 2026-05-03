from __future__ import annotations

import zipfile
from pathlib import Path
from typing import Any


def _write_aligned_member(
    archive: zipfile.ZipFile,
    filename: str,
    data: bytes,
    source_info: zipfile.ZipInfo | None = None,
) -> None:
    filename_bytes = filename.encode("utf-8")
    base_offset = archive.fp.tell() + 30 + len(filename_bytes)
    extra_len = (-base_offset) % 64
    if 0 < extra_len < 4:
        extra_len += 64

    info = zipfile.ZipInfo(filename)
    info.compress_type = zipfile.ZIP_STORED
    info.external_attr = 0o644 << 16
    if source_info:
        info.date_time = source_info.date_time
        info.comment = source_info.comment
        info.external_attr = source_info.external_attr
        info.create_system = source_info.create_system
    if extra_len:
        info.extra = (0xFFFF).to_bytes(2, "little") + (extra_len - 4).to_bytes(2, "little") + b"\0" * (extra_len - 4)

    archive.writestr(info, data)


def rewrite_usdz_alignment(path: Path) -> dict[str, Any]:
    members: list[tuple[zipfile.ZipInfo, bytes]] = []
    with zipfile.ZipFile(path, "r") as source:
        for info in source.infolist():
            members.append((info, source.read(info.filename)))

    tmp_path = path.with_name(f"{path.name}.aligned.tmp")
    with zipfile.ZipFile(tmp_path, "w", compression=zipfile.ZIP_STORED) as target:
        for info, data in members:
            _write_aligned_member(target, info.filename, data, info)

    tmp_path.replace(path)
    return validate_usdz_alignment(path)


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


def inject_initial_camera(path: Path) -> dict[str, Any]:
    """Inject a UsdRender.Settings prim pointing to camera_0000 as the initial viewport camera."""
    try:
        from pxr import Sdf, Usd, UsdRender
    except ImportError:
        return {"ok": False, "warning": "pxr not available — skipping initial camera injection"}

    members: list[tuple[zipfile.ZipInfo, bytes]] = []
    with zipfile.ZipFile(path, "r") as zf:
        for info in zf.infolist():
            members.append((info, zf.read(info.filename)))

    usda_idx = next((i for i, (info, _) in enumerate(members) if info.filename.endswith(".usda")), None)
    if usda_idx is None:
        return {"ok": False, "warning": "no .usda found in USDZ"}

    info, usda_data = members[usda_idx]
    stage = Usd.Stage.CreateInMemory()
    stage.GetRootLayer().ImportFromString(usda_data.decode("utf-8"))

    camera_path = Sdf.Path("/World/Cameras/camera_0000")
    if not stage.GetPrimAtPath(camera_path):
        return {"ok": False, "warning": f"camera prim not found: {camera_path}"}

    render_settings = UsdRender.Settings.Define(stage, "/Render/Settings")
    render_settings.GetCameraRel().AddTarget(camera_path)

    new_usda = stage.GetRootLayer().ExportToString()
    members[usda_idx] = (info, new_usda.encode("utf-8"))

    tmp_path = path.with_name(f"{path.name}.cam.tmp")
    with zipfile.ZipFile(tmp_path, "w", compression=zipfile.ZIP_STORED) as target:
        for m_info, data in members:
            _write_aligned_member(target, m_info.filename, data, m_info)
    tmp_path.replace(path)

    return {"ok": True, "camera": str(camera_path)}


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
