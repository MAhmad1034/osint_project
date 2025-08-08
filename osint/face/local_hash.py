from __future__ import annotations

from PIL import Image
import imagehash


def phash_distance(path_a: str, path_b: str) -> int:
    with Image.open(path_a) as a, Image.open(path_b) as b:
        return imagehash.phash(a) - imagehash.phash(b)


def is_probably_duplicate(path_a: str, path_b: str, threshold: int = 5) -> bool:
    return phash_distance(path_a, path_b) <= threshold