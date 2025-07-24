from __future__ import annotations

import random

from .ascii_art import validate_pixel_adjacency


def random_bitmap(width: int, height: int) -> list[str]:
    """Return a bitmap with one or two active pixels.

    The returned grid is ``height`` lines by ``width`` characters. Exactly one
    or two ``"1"`` characters are present. If two pixels are active they may be
    horizontally adjacent or separated but are never vertically or diagonally
    adjacent.
    """

    positions = [(r, c) for r in range(height) for c in range(width)]
    first = random.choice(positions)  # noqa: S311 - demo randomness
    coords = [first]

    if random.choice([True, False]):  # noqa: S311 - demo randomness
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
