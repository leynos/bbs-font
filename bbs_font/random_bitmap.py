from __future__ import annotations

import random

from .parser import validate_pixel_adjacency


def _pick_second_pixel(
    first: tuple[int, int], positions: list[tuple[int, int]]
) -> tuple[int, int] | None:
    """Return a valid second pixel from ``positions`` or ``None``."""

    candidates: list[tuple[int, int]] = []
    for pos in positions:
        if pos == first:
            continue
        try:
            validate_pixel_adjacency([first, pos])
        except ValueError:
            continue
        candidates.append(pos)
    if not candidates:
        return None
    return random.choice(candidates)  # noqa: S311 - demo randomness


def random_bitmap(width: int, height: int, two_pixel_prob: float = 0.5) -> list[str]:
    """Return a bitmap with one or two active pixels.

    The returned grid is ``height`` lines by ``width`` characters. Exactly one
    or two ``"1"`` characters are present. If two pixels are active they may be
    horizontally adjacent or separated but are never vertically or diagonally
    adjacent.

    Args:
        width: Width of the bitmap. Must be positive.
        height: Height of the bitmap. Must be positive.
        two_pixel_prob: Probability of generating a second pixel (``0``-``1``).
    """

    if not isinstance(width, int) or not isinstance(height, int):
        raise TypeError("width and height must be integers")
    if width <= 0 or height <= 0:
        raise ValueError("width and height must be positive integers")
    if not (0.0 <= two_pixel_prob <= 1.0):
        raise ValueError("two_pixel_prob must be between 0 and 1 inclusive")

    positions = [(r, c) for r in range(height) for c in range(width)]
    first = random.choice(positions)  # noqa: S311 - demo randomness
    coords = [first]

    if random.random() < two_pixel_prob:  # noqa: S311 - demo randomness
        second = _pick_second_pixel(first, positions)
        if second:
            coords.append(second)

    grid = []
    for row in range(height):
        cells = ["0"] * width
        for y, x in coords:
            if y == row:
                cells[x] = "1"
        grid.append("".join(cells))
    return grid
