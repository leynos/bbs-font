from __future__ import annotations

from pathlib import Path

import pytest
from hypothesis import given
from hypothesis import strategies as st

from bbs_font.ascii_art import bitmap_to_ascii, validate_ascii

DATA_DIR = Path(__file__).parent / "data"


@pytest.mark.parametrize(
    "input_file,expected_file",
    [
        ("example1_input.txt", "example1_output.txt"),
        ("example2_input.txt", "example2_output.txt"),
    ],
)
def test_examples(input_file: str, expected_file: str) -> None:
    bitmap = (DATA_DIR / input_file).read_text().splitlines()
    expected = (DATA_DIR / expected_file).read_text().rstrip("\n")
    art = bitmap_to_ascii(bitmap)
    assert art == expected
    validate_ascii(art, len(bitmap[0]), len(bitmap))


@pytest.mark.parametrize(
    "bitmap",
    [
        ["1", "0"],
        ["10"],
        ["01"],
    ],
)
def test_edge_cases(bitmap: list[str]) -> None:
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
