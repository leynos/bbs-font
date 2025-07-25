from __future__ import annotations

from pathlib import Path

import pytest
from hypothesis import given
from hypothesis import strategies as st

from bbs_font.ascii_art import bitmap_to_ascii, validate_ascii
from bbs_font.parser import parse_and_validate_bitmap

DATA_DIR = Path(__file__).parent / "data"


@pytest.mark.parametrize(
    "input_file,expected_file",
    [
        ("example1_input.txt", "example1_output.txt"),
        ("example2_input.txt", "example2_output.txt"),
        ("example3_input.txt", "example3_output.txt"),
    ],
)
def test_examples(input_file: str, expected_file: str) -> None:
    bitmap = (DATA_DIR / input_file).read_text().splitlines()
    expected = (DATA_DIR / expected_file).read_text().rstrip("\n")
    art = bitmap_to_ascii(bitmap)
    assert art == expected
    validate_ascii(art, bitmap)


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
    validate_ascii(art, bitmap)


def test_two_horizontally_adjacent_blocks() -> None:
    bitmap = [
        "110",
        "000",
    ]
    art = bitmap_to_ascii(bitmap)
    validate_ascii(art, bitmap)


def test_two_non_adjacent_blocks() -> None:
    bitmap = [
        "100",
        "001",
    ]
    art = bitmap_to_ascii(bitmap)
    validate_ascii(art, bitmap)


@st.composite
def random_bitmap(draw: st.DrawFn) -> list[str]:
    height = draw(st.integers(min_value=2, max_value=6))
    width = draw(st.integers(min_value=1, max_value=6))

    positions = [(r, c) for r in range(height) for c in range(width)]
    first = draw(st.sampled_from(positions))

    coords = [first]
    if draw(st.booleans()):
        possible = []
        for r, c in positions:
            if (r, c) == first:
                continue
            vertically_adjacent = abs(r - first[0]) == 1 and c == first[1]
            diagonally_adjacent = abs(r - first[0]) == 1 and abs(c - first[1]) == 1
            if vertically_adjacent or diagonally_adjacent:
                continue
            possible.append((r, c))
        if possible:
            coords.append(draw(st.sampled_from(possible)))

    grid = []
    for row in range(height):
        cells = ["0"] * width
        for y, x in coords:
            if y == row:
                cells[x] = "1"
        grid.append("".join(cells))
    return grid


@given(random_bitmap())
def test_random_bitmaps(bitmap: list[str]) -> None:
    art = bitmap_to_ascii(bitmap)
    validate_ascii(art, bitmap)


def test_invalid_characters() -> None:
    with pytest.raises(ValueError):
        parse_and_validate_bitmap(["10A"])


def test_empty_row() -> None:
    with pytest.raises(ValueError):
        parse_and_validate_bitmap([""])


def test_vertical_adjacency_error() -> None:
    with pytest.raises(ValueError):
        parse_and_validate_bitmap(["10", "10"])
