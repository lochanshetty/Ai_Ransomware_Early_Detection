from __future__ import annotations

import math
from collections import Counter
from pathlib import Path


def shannon_entropy(data: bytes) -> float:
    """Compute Shannon entropy (bits per byte) for binary data."""

    if not data:
        return 0.0
    counts = Counter(data)
    length = len(data)
    entropy = 0.0
    for count in counts.values():
        probability = count / length
        entropy -= probability * math.log2(probability)
    return entropy


def file_entropy(path: str | Path, sample_size: int = 65536) -> float:
    """Sample-based file entropy; reads up to sample_size bytes."""

    file_path = Path(path)
    if not file_path.is_file():
        return 0.0
    try:
        with file_path.open("rb") as handle:
            chunk = handle.read(sample_size)
    except OSError:
        return 0.0
    return shannon_entropy(chunk)
