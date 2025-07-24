from __future__ import annotations

import random

from .ascii_art import validate_pixel_adjacency


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

    if width <= 0 or height <= 0:
        raise ValueError("width and height must be positive integers")

    positions = [(r, c) for r in range(height) for c in range(width)]
    first = random.choice(positions)  # noqa: S311 - demo randomness
    coords = [first]

    if random.random() < two_pixel_prob:  # noqa: S311 - demo randomness
        possible = []
        for pos in positions:
            if pos == first:
                continue
            try:
                validate_pixel_adjacency([first, pos])
            except ValueError:
                continue
            possible.append(pos)
        if possible:
            coords.append(random.choice(possible))  # noqa: S311 - demo randomness

    grid = []
    for row in range(height):
        cells = ["0"] * width
        for y, x in coords:
            if y == row:
                cells[x] = "1"
        grid.append("".join(cells))
    return grid
