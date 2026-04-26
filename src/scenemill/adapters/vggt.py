from __future__ import annotations


def not_implemented_message() -> str:
    return (
        "VGGT is reserved as a SceneMill geometry frontend, but this workspace does not yet "
        "contain a VGGT adapter command. Add the local VGGT repo path and export command before enabling it."
    )

