from __future__ import annotations


OOM_PATTERNS = (
    "out of memory",
    "cuda out of memory",
    "cublas_status_alloc_failed",
    "cuda error: out of memory",
    "torch.outofmemoryerror",
)


def looks_like_oom(output: str | None) -> bool:
    lower = (output or "").lower()
    return any(pattern in lower for pattern in OOM_PATTERNS)

