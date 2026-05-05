from __future__ import annotations

from dataclasses import dataclass

from scenemill.registry import ROUTER_MODES, SCENE_BACKENDS, validate_backend
from scenemill.schemas.artifacts import FrameSet


@dataclass(slots=True)
class RouteDecision:
    selected_backend: str
    mode: str
    reason: str
    image_count: int
    threshold: int

    def as_dict(self) -> dict[str, int | str]:
        return {
            "mode": self.mode,
            "selected_backend": self.selected_backend,
            "reason": self.reason,
            "image_count": self.image_count,
            "threshold": self.threshold,
        }


def choose_scene_backend(config: dict, frames: FrameSet) -> RouteDecision:
    router = config.get("router", {})
    mode = validate_backend(str(router.get("mode", "auto")), ROUTER_MODES, "router mode")
    threshold = int(router.get("low_view_threshold", 10))
    if threshold < 1:
        raise ValueError("router.low_view_threshold must be >= 1")

    if mode == "anysplat":
        return RouteDecision(
            selected_backend="anysplat",
            mode=mode,
            reason="forced_anysplat",
            image_count=frames.count,
            threshold=threshold,
        )
    if mode == "classic":
        return RouteDecision(
            selected_backend="classic",
            mode=mode,
            reason="forced_classic",
            image_count=frames.count,
            threshold=threshold,
        )

    if frames.count < threshold:
        selected = validate_backend(
            str(router.get("low_view_backend", "anysplat")),
            SCENE_BACKENDS,
            "low-view scene backend",
        )
        return RouteDecision(
            selected_backend=selected,
            mode=mode,
            reason="image_count_below_threshold",
            image_count=frames.count,
            threshold=threshold,
        )
    selected = validate_backend(
        str(router.get("classic_backend", "classic")),
        SCENE_BACKENDS,
        "classic scene backend",
    )
    return RouteDecision(
        selected_backend=selected,
        mode=mode,
        reason="image_count_at_or_above_threshold",
        image_count=frames.count,
        threshold=threshold,
    )
