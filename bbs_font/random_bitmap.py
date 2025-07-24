from __future__ import annotations

import random


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
        possible = [
            (r, c)
            for r, c in positions
            if (r, c) != first
            and not (
                abs(r - first[0]) <= 1
                and abs(c - first[1]) <= 1
                and not (r == first[0] and abs(c - first[1]) == 1)
            )
        ]
        if possible:
            coords.append(random.choice(possible))  # noqa: S311 - demo randomness

    grid = []
    for r in range(height):
        cells = ["0"] * width
        for yr, xc in coords:
            if yr == r:
                cells[xc] = "1"
        grid.append("".join(cells))
    return grid
