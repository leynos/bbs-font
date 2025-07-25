from __future__ import annotations

from bbs_font.ascii_art import bitmap_to_ascii, validate_ascii
from bbs_font.random_bitmap import random_bitmap


def test_random_bitmap_validity() -> None:
    for _ in range(100):
        bitmap = random_bitmap(6, 4)
        ones = sum(row.count("1") for row in bitmap)
        assert ones in (1, 2)

        coords = [
            (r, c)
            for r, row in enumerate(bitmap)
            for c, ch in enumerate(row)
            if ch == "1"
        ]
        if len(coords) == 2:
            (y0, x0), (y1, x1) = coords
            vertically_adjacent = abs(y0 - y1) == 1 and x0 == x1
            diagonally_adjacent = abs(y0 - y1) == 1 and abs(x0 - x1) == 1
            assert not (vertically_adjacent or diagonally_adjacent)

        art = bitmap_to_ascii(bitmap)
        validate_ascii(art, bitmap)
