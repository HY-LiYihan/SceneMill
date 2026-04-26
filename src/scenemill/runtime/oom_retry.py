from __future__ import annotations


OOM_PATTERNS = (
    "out of memory",
    "cuda out of memory",
    "cublas_status_alloc_failed",
    "cuda error: out of memory",
    "torch.outofmemoryerror",
    "killed",
    "sigkill",
    "已杀死",
)


def looks_like_oom(output: str | None, returncode: int | None = None) -> bool:
    if returncode in {-9, 137}:
        return True
    lower = (output or "").lower()
    return any(pattern in lower for pattern in OOM_PATTERNS)
