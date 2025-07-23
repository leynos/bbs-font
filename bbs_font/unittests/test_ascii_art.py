from __future__ import annotations

import pytest
from hypothesis import given
from hypothesis import strategies as st

from bbs_font.ascii_art import bitmap_to_ascii, validate_ascii


@pytest.mark.parametrize(
    "bitmap",
    [
        ["0000", "0100", "0000"],
        ["0000", "0010", "0000"],
    ],
)
def test_examples(bitmap: list[str]) -> None:
    art = bitmap_to_ascii(bitmap)
    validate_ascii(art, len(bitmap[0]), len(bitmap))


@st.composite
def random_bitmap(draw: st.DrawFn) -> list[str]:
    height = draw(st.integers(min_value=2, max_value=6))
    width = draw(st.integers(min_value=1, max_value=6))
    row = draw(st.integers(min_value=0, max_value=height - 1))
    col = draw(st.integers(min_value=0, max_value=width - 1))
    grid = []
    for r in range(height):
        cells = ["0"] * width
        if r == row:
            cells[col] = "1"
        grid.append("".join(cells))
    return grid


@given(random_bitmap())
def test_random_bitmaps(bitmap: list[str]) -> None:
    art = bitmap_to_ascii(bitmap)
    validate_ascii(art, len(bitmap[0]), len(bitmap))
