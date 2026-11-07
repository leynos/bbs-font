"""Tests for rendering bitmaps to ASCII art and validating the result."""

from __future__ import annotations

from pathlib import Path

import pytest
from hypothesis import given
from hypothesis import strategies as st

from bbs_font.ascii_art import (
    AsciiArtValidationError,
    bitmap_to_ascii,
    validate_ascii,
)
from bbs_font.parser import parse_and_validate_bitmap

DATA_DIR = Path(__file__).parent / "data"


@pytest.mark.parametrize(
    "input_file,expected_file",
    [
        ("example1_input.txt", "example1_output.txt"),
        ("example2_input.txt", "example2_output.txt"),
        ("example3_input.txt", "example3_output.txt"),
        ("example4_input.txt", "example4_output.txt"),
    ],
)
def test_examples(input_file: str, expected_file: str) -> None:
    """Render each example bitmap to its expected art, which must validate."""
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
    """Render small edge-case bitmaps to art that validates against them."""
    art = bitmap_to_ascii(bitmap)
    validate_ascii(art, bitmap)


def test_two_horizontally_adjacent_blocks() -> None:
    """Render two blocks side by side to art that validates."""
    bitmap = [
        "110",
        "000",
    ]
    art = bitmap_to_ascii(bitmap)
    validate_ascii(art, bitmap)


def test_two_non_adjacent_blocks() -> None:
    """Render two blocks that do not touch to art that validates."""
    bitmap = [
        "100",
        "001",
    ]
    art = bitmap_to_ascii(bitmap)
    validate_ascii(art, bitmap)


@st.composite
def random_bitmap(draw: st.DrawFn) -> list[str]:
    """Draw a small grid holding one block, or two that are not diagonal neighbours."""
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
            diagonally_adjacent = abs(r - first[0]) == 1 and abs(c - first[1]) == 1
            if diagonally_adjacent:
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
    """Render any drawn bitmap to art that validates against it."""
    art = bitmap_to_ascii(bitmap)
    validate_ascii(art, bitmap)


def test_invalid_characters() -> None:
    """Reject a row holding a character other than ``0`` and ``1``."""
    with pytest.raises(ValueError):
        parse_and_validate_bitmap(["10A"])


def test_empty_row() -> None:
    """Reject a bitmap that contains an empty row."""
    with pytest.raises(ValueError):
        parse_and_validate_bitmap([""])


def test_vertical_adjacency() -> None:
    """Render two vertically stacked blocks to art that validates."""
    bitmap = [
        "10",
        "10",
    ]
    art = bitmap_to_ascii(bitmap)
    validate_ascii(art, bitmap)


def test_bottom_line_slash_validation() -> None:
    """Ensure slash counts include the bottom line."""

    bitmap = [
        "0000",
        "0100",
        "0100",
    ]
    art = bitmap_to_ascii(bitmap)

    lines = art.splitlines()
    bottom = list(lines[-1])
    for i, ch in enumerate(bottom):
        if ch in {"/", "\\"}:
            bottom[i] = "_"
            break
    bad_art = "\n".join([*lines[:-1], "".join(bottom)])

    with pytest.raises(AsciiArtValidationError):
        validate_ascii(bad_art, bitmap)
